import re
import logging
from flask import (
    Flask,
    render_template,
    render_template_string,
    request,
    jsonify,
    send_file,
    send_from_directory,
)
import os
import markdown
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Path to the directory containing Bible text files
bible_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bible")

# Markdown 파일들이 저장된 디렉터리 경로 설정
markdown_dir = "C:/Bible/obsidian_notes"

# Dictionary to hold abbreviations for Bible books
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
    "계": "요한계시록",
}

version_names = ["한글개역", "한글흠정역", "새번역", "KJV_한글KJV"]


def sanitize_input(value, max_length=100):
    # 허용된 문자: 한글, 영어, 숫자, 공백, 콜론, 쉼표, 대시
    allowed_chars = re.compile(r"^[가-힣a-zA-Z0-9\s:,-]+$")

    # 입력값 길이 제한
    if len(value) > max_length:
        raise ValueError(
            f"Invalid input: Length of input should not exceed {max_length} characters."
        )

    # 허용된 문자 검사
    if not allowed_chars.match(value):
        raise ValueError(
            "Invalid input: Only Korean characters, English letters, numbers, spaces, colons, commas, and dashes are allowed."
        )

    # 연속적인 3개 이상의 동일한 문자 방지
    if re.search(r"(.)\1{2,}", value):
        raise ValueError(
            "Invalid input: More than two consecutive identical characters are not allowed."
        )

    # 16진수 패턴 방지
    if re.search(r"\\x[0-9a-fA-F]{2}", value):
        raise ValueError("Invalid input: Hexadecimal values are not allowed.")

    return value


@app.route("/")
@app.route("/index.html")
def index():
    # 성경 버전 정보와 Markdown 파일 목록을 모두 전달
    versions = version_names
    markdown_files = [f for f in os.listdir(markdown_dir) if f.endswith(".md")]

    # 디버깅 로그
    app.logger.debug(f"Markdown files: {markdown_files}")

    # 템플릿으로 데이터 전달
    return render_template("index.html", versions=versions, files=markdown_files)


@app.route("/page2")
def page2():
    return render_template("page2.html")


@app.route('/search', methods=['POST'])
def search():
    data = request.json
    versions = data.get('versions', [])
    search_type = data.get('type')
    value = data.get('value')

    logging.debug(f"[START] /search versions={versions}, type={search_type}, value={value}")

    if not versions:
        versions = ["한글개역"]

    try:
        value = sanitize_input(value)
        logging.debug(f"[OK] sanitized value={value}")
    except ValueError as e:
        logging.exception("[ERROR] sanitize_input failed")
        return jsonify({"error": str(e)}), 400

    try:
        if search_type == 'verse':
            logging.debug("[RUN] search_by_verse")
            results = search_by_verse(versions, value)
        elif search_type == 'content':
            logging.debug("[RUN] search_by_content")
            results = search_by_content(versions, value)
        else:
            results = []

        logging.debug(f"[DONE] search completed count={len(results)}")
        return jsonify(results)

    except Exception:
        logging.exception("[ERROR] search route failed")
        return jsonify({"error": "검색 중 오류가 발생했습니다."}), 500



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
                chapter = match.group(2) if match.group(2) else ""
                verse_start = match.group(3) if match.group(3) else ""
                verse_end = match.group(4) if match.group(4) else ""
                book = abbreviations.get(book, book)

                for version in versions:
                    if version == "새번역":
                        file_path = os.path.join(bible_dir, f"새번역_{book}.txt")
                    elif version == "KJV_한글KJV":
                        file_path = os.path.join(bible_dir, f"KJV_한글KJV_{book}.txt")
                    else:
                        file_path = os.path.join(bible_dir, f"{version}_{book}.txt")

                    if not os.path.exists(file_path):
                        logging.warning(f"File not found: {file_path}")
                        continue

                    with open(file_path, "r", encoding="utf-8") as file:
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
                                line_chapter, line_verse = map(
                                    int, chapter_verse.split(":")
                                )
                            except ValueError:
                                logging.warning(
                                    f"Invalid chapter_verse format: {chapter_verse}"
                                )
                                continue

                            if (
                                line_chapter == int(chapter)
                                and start_verse <= line_verse <= end_verse
                            ):
                                results.append((version, book, chapter_verse, content))

                    elif chapter:
                        for line in lines:
                            parts = line.split(maxsplit=1)
                            if len(parts) != 2:
                                continue

                            chapter_verse, content = parts
                            try:
                                if line.startswith(f"{chapter}:"):
                                    results.append((version, book, chapter_verse, content))
                            except ValueError:
                                logging.warning(
                                    f"Invalid chapter_verse format: {chapter_verse}"
                                )
                                continue

                    else:
                        for line in lines:
                            parts = line.split(maxsplit=1)
                            if len(parts) != 2:
                                continue

                            chapter_verse, content = parts
                            results.append((version, book, chapter_verse, content))

    except Exception:
        logging.error("Error occurred in search_by_verse", exc_info=True)

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
            logging.debug(f"[VERSION] {version}")
            for filename in os.listdir(bible_dir):
                if filename.startswith(version) and filename.endswith(".txt"):
                    file_path = os.path.join(bible_dir, filename)
                    logging.debug(f"[OPEN] {file_path}")

                    with open(file_path, 'r', encoding='utf-8') as file:
                        for line in file:
                            if " " not in line:
                                continue

                            parts = line.strip().split(maxsplit=1)
                            if len(parts) != 2:
                                continue

                            chapter_verse, content = parts
                            if condition == "AND":
                                if all(q in content for q in queries):
                                    results.append((version, filename, chapter_verse, content))
                            elif condition == "OR":
                                if any(q in content for q in queries):
                                    results.append((version, filename, chapter_verse, content))
                            else:
                                if queries[0] in content:
                                    results.append((version, filename, chapter_verse, content))

                    logging.debug(f"[DONE FILE] {file_path}")

    except Exception:
        logging.exception("Error occurred in search_by_content")

    return results



@app.route("/download")
def download():
    file_path = "C:/Bible/download/bible_find.zip"
    return send_file(file_path, as_attachment=True)


study_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "study")


@app.route("/obsidian_notes/<path:filename>")
def get_markdown(filename):
    # 파일 경로 구성
    file_path = os.path.join(markdown_dir, filename)

    # 파일이 존재하는지 확인
    if not os.path.exists(file_path):
        app.logger.error(f"File not found: {file_path}")
        return "파일을 찾을 수 없습니다.", 404

    # 파일 읽기 및 HTML로 변환
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Markdown을 HTML로 변환
    html_content = markdown.markdown(content)

    # 렌더링된 HTML 반환
    return render_template_string(f"<html><body>{html_content}</body></html>")


# Flask에서 static 경로로 이미지 서빙
@app.route("/obsidian_notes/img/<path:filename>")
def serve_img(filename):
    # 이미지가 저장된 디렉터리 경로
    image_dir = os.path.join(markdown_dir, "img")

    # 디버깅 로그 출력
    app.logger.debug(f"Serving image from {os.path.join(image_dir, filename)}")

    # 이미지를 서빙
    return send_from_directory(image_dir, filename)


@app.route("/study/<path:filename>")
def study(filename):
    return send_from_directory(study_dir, filename)


if __name__ == "__main__":
    print('* Serving Flask app "web"\n* Debug mode: on')
    app.run(debug=False, host="127.0.0.1", port=5500)
