from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import os
import re
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Path to the directory containing Bible text files
bible_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bible")

# Dictionary to hold abbreviations for Bible books
# 약어 매핑
abbreviations = {
    "창": "창세기", "출": "출애굽기", "레": "레위기", "민": "민수기", "신": "신명기",
    "수": "여호수아", "삿": "사사기", "룻": "룻기", "삼상": "사무엘상", "삼하": "사무엘하",
    "왕상": "열왕기상", "왕하": "열왕기하", "대상": "역대상", "대하": "역대하", "스": "에스라",
    "느": "느헤미야", "에": "에스더", "욥": "욥기", "시": "시편", "잠": "잠언",
    "전": "전도서", "아": "아가", "사": "이사야", "렘": "예레미야", "애": "예레미야애가",
    "겔": "에스겔", "단": "다니엘", "호": "호세아", "욜": "요엘", "암": "아모스",
    "옵": "오바댜", "욘": "요나", "미": "미가", "나": "나훔", "합": "하박국",
    "습": "스바냐", "학": "학개", "슥": "스가랴", "말": "말라기",
    "마": "마태복음", "막": "마가복음", "눅": "누가복음", "요": "요한복음",
    "행": "사도행전", "롬": "로마서", "고전": "고린도전서", "고후": "고린도후서",
    "갈": "갈라디아서", "엡": "에베소서", "빌": "빌립보서", "골": "골로새서",
    "살전": "데살로니가전서", "살후": "데살로니가후서", "딤전": "디모데전서",
    "딤후": "디모데후서", "딛": "디도서", "몬": "빌레몬서", "히": "히브리서",
    "약": "야고보서", "벧전": "베드로전서", "벧후": "베드로후서",
    "요일": "요한일서", "요이": "요한이서", "요삼": "요한삼서", "유": "유다서",
    "계": "요한계시록"
}
version_names = ["한글개역", "한글흠정역", "새번역", "KJV_한글KJV"]

def sanitize_input(value, max_length=20):
    # 허용된 문자: 한글, 영어, 숫자, 공백, 콜론, 쉼표, 대시
    allowed_chars = re.compile(r'^[가-힣a-zA-Z0-9\s:,-]+$')
    if len(value) > max_length:
        raise ValueError(f"Invalid input: Length of input should not exceed {max_length} characters.")
    if not allowed_chars.match(value):
        raise ValueError("Invalid input: Only Korean characters, English letters, numbers, spaces, colons, commas, and dashes are allowed.")
    return value

@app.route('/')
def index():
    versions = version_names
    return render_template('index.html', versions=versions)

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    versions = data.get('versions', [])
    search_type = data.get('type')
    value = data.get('value')

    logging.debug(f"Search request: versions={versions}, search_type={search_type}, value={value}")

    if not versions:
        versions = ["한글개역"]
    # 입력값 정제
    try:
        value = sanitize_input(value)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if search_type == 'verse':
        results = search_by_verse(versions, value)
    elif search_type == 'content':
        results = search_by_content(versions, value)
    else:
        results = []

    logging.debug(f"Search completed with {len(results)} results.")
    return jsonify(results)


def search_by_verse(versions, query):
    logging.debug(f"search_by_verse called with versions={versions}, query={query}")
    results = []
    query = sanitize_input(query)
    try:
        verses = query.split(",")
        for vc in verses:
            vc = vc.strip()
            match = re.match(r"(\D+)(\d+)?(?::(\d+)(?:-(\d+))?)?", vc)
            if match:
                book = match.group(1).strip()
                chapter = match.group(2) if match.group(2) else ''
                verse_start = match.group(3) if match.group(3) else ''
                verse_end = match.group(4) if match.group(4) else ''
                book = abbreviations.get(book, book)
                for version in versions:
                    if version == '새번역':
                        file_path = os.path.join(bible_dir, f"새번역_{book}.txt")
                    elif version == 'KJV_한글KJV':
                        file_path = os.path.join(bible_dir, f"KJV_한글KJV_{book}.txt")
                    else:
                        file_path = os.path.join(bible_dir, f"{version}_{book}.txt")

                    if not os.path.exists(file_path):
                        logging.warning(f"File not found: {file_path}")
                        continue

                    with open(file_path, 'r', encoding='utf-8') as file:
                        lines = [line.strip() for line in file if line.strip()]
                        if chapter and verse_start:
                            if verse_end:
                                start_verse = int(verse_start)
                                end_verse = int(verse_end)
                            else:
                                start_verse = end_verse = int(verse_start)
                            
                            for line in lines:
                                parts = line.split(maxsplit=1)
                                if len(parts) != 2:
                                    continue
                                chapter_verse, content = parts
                                try:
                                    line_chapter, line_verse = map(int, chapter_verse.split(':'))
                                except ValueError:
                                    logging.warning(f"Invalid chapter_verse format: {chapter_verse}")
                                    continue
                                if line_chapter == int(chapter) and start_verse <= line_verse <= end_verse:
                                    results.append((version, book, chapter_verse, content))
                        elif chapter:
                            for line in lines:
                                parts = line.split(maxsplit=1)
                                if len(parts) != 2:
                                    continue
                                chapter_verse, content = parts
                                try:
                                    line_chapter, line_verse = map(int, chapter_verse.split(':'))
                                    if line.startswith(f"{chapter}:"):
                                        results.append((version, book, chapter_verse, content))
                                except ValueError:
                                    logging.warning(f"Invalid chapter_verse format: {chapter_verse}")
                                    continue
                        else:
                            for line in lines:
                                parts = line.split(maxsplit=1)
                                if len(parts) != 2:
                                    continue
                                chapter_verse, content = parts
                                try:
                                    results.append((version, book, chapter_verse, content))
                                except ValueError:
                                    logging.warning(f"Invalid chapter_verse format: {chapter_verse}")
                                    continue
    except Exception as e:
        logging.error('Error occurred in search_by_verse', exc_info=True)
    return results


def search_by_content(versions, query):
    logging.debug(f"search_by_content called with versions={versions}, query={query}")
    results = []
    query = sanitize_input(query)
    try:
        if " and " in query:
            condition = "AND"
            queries = [q.strip() for q in query.split(" and ")]
        elif " or " in query:
            condition = "OR"
            queries = [q.strip() for q in query.split(" or ")]
        else:
            condition = "SINGLE"
            queries = [query.strip()]

        for version in versions:
            for filename in os.listdir(bible_dir):
                if filename.startswith(version) and filename.endswith(".txt"):
                    book = filename[len(version) + 1:].split(".")[0]
                    file_path = os.path.join(bible_dir, f"{version}_{book}.txt")

                    if not os.path.exists(file_path):
                        logging.warning(f"File not found: {file_path}")
                        continue

                    with open(file_path, 'r', encoding='utf-8') as file:
                        lines = file.readlines()
                        for line in lines:
                            if " " not in line:
                                continue
                            parts = line.strip().split(maxsplit=1)
                            if len(parts) != 2:
                                continue
                            chapter_verse, content = parts
                            if condition == "AND":
                                if all(q in content for q in queries):
                                    results.append((version, book, chapter_verse, content))
                            elif condition == "OR":
                                if any(q in content for q in queries):
                                    results.append((version, book, chapter_verse, content))
                            else:
                                if queries[0] in content:
                                    results.append((version, book, chapter_verse, content))
    except Exception as e:
        logging.error('Error occurred in search_by_content', exc_info=True)
    return results

@app.route('/download')
def download():
    file_path = "C:/Bible/download/bible_find.zip"
    return send_file(file_path, as_attachment=True)

study_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "study")

@app.route('/study/<path:filename>')
def study(filename):
    return send_from_directory(study_dir, filename)

if __name__ == '__main__':
    print(f'* Serving Flask app "web2"\n* Debug mode: on')
    app.run(debug=True, host='0.0.0.0', port=5500)
