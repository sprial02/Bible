from flask import Flask, request, jsonify, render_template_string, send_file
import os
import re
import logging

app = Flask(__name__)

# 로깅 설정: 콘솔과 파일 모두에 로그 출력
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()])

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

# 성경 버전 명칭
version_names = ["한글개역", "개역개정", "바른성경", "한글KJV", "한글흠정역", "개역개정4판"]

# 텍스트 파일 경로
bible_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bible")

@app.route('/')
def index():
    versions = version_names
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>성경 말씀 구절 / 단어 검색</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: '맑은 고딕', sans-serif;
                    margin: 20px;
                }
                .container {
                    max-width: 1200px;
                    margin: auto;
                }
                .search-box {
                    margin-bottom: 10px;
                    border: 1px solid black;
                    padding: 10px;
                    background-color: #f9f9f9;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    table-layout: fixed;
                }
                table, th, td {
                    border: none;
                }
                th, td {
                    padding: 10px;
                    text-align: center;
                    font-size: 10pt;
                    word-wrap: break-word;
                    white-space: pre-line;
                    overflow: hidden;
                    border-bottom: 1px solid black;
                }
                th.version, td.version {
                    width: 15%;
                }
                th.book, td.book {
                    width: 20%;
                }
                th.chapter-verse, td.chapter-verse {
                    width: 10%;
                }
                td.content {
                    text-align: left;
                    background-color: white;
                }
                h2 {
                    margin-bottom: 10px;
                }
                select, input[type="text"] {
                    width: 100%;
                    padding: 5px;
                    margin: 5px 0;
                    font-size: 12pt;
                    box-sizing: border-box;
                }
                button {
                    padding: 5px 10px;
                    font-size: 12pt;
                    margin-top: 5px;
                    width: 100%;
                }
                p {
                    font-size: 12pt;
                }
                .highlight {
                    background-color: yellow;
                    font-weight: bold;
                }
                .loader {
                    border: 8px solid #f3f3f3;
                    border-radius: 50%;
                    border-top: 8px solid #3498db;
                    width: 40px;
                    height: 40px;
                    display: inline-block;
                    position: relative;
                    margin: 10px auto;
                }
                .loader-text {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-size: 12px;
                    font-weight: bold;
                    animation: none;
                }
                .hidden {
                    display: none;
                }
                @media screen and (max-width: 768px) {
                    .container {
                        margin: 0 10px;
                    }
                    th, td {
                        padding: 8px;
                        font-size: 9pt;
                    }
                }
                @media screen and (max-width: 480px) {
                    .container {
                        margin: 0 5px;
                    }
                    th, td {
                        padding: 5px;
                        font-size: 8pt;
                    }
                    th.version, td.version,
                    th.book, td.book,
                    th.chapter-verse, td.chapter-verse {
                        display: none;
                    }
                    td.content {
                        white-space: nowrap;
                        text-overflow: ellipsis;
                    }
                    button {
                        font-size: 10pt;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h3>< 성경 말씀 구절 / 단어 검색 ></h3>
                <div class="search-box">
                    <h3>■ 성경 버전 선택 [기본: 한글KJV]</h3>
                    <form id="searchForm">
                        <select id="versions" name="versions" multiple>
                            {% for version in versions %}
                                <option value="{{ version }}" {% if version == '한글KJV' %}selected{% endif %}>{{ version }}</option>
                            {% endfor %}
                        </select>
                        <br>
                        <h3>■ 성경 구절 검색</h3>
                        <label for="verse">구절 검색:</label>
                        <input type="text" id="verse" name="verse" placeholder="예: 창1:10, 요3:16, 마1, 신1:10/15">
                        <button type="button" id="verseSearchButton">검색</button>
                        <div class="loader hidden" id="loader-content">
                            <div class="loader-text" id="loaderText-content">0s</div>
                        </div>
                        <br>
                        <h3>■ 성경 내용 검색</h3>
                        <label for="content">내용 검색:</label>
                        <input type="text" id="content" name="content" placeholder="예: 사랑, 믿음, 소망">
                        <button type="button" id="contentSearchButton">검색</button>
                    </form>
                </div>
                <div class="results">
                    <h3>■ 검색 결과</h3>
                    <p id="count">찾았음: 0 개</p>
                    <table id="resultsTable">
                        <thead>
                            <tr>
                                <th class="version">버전</th>
                                <th class="book">성경</th>
                                <th class="chapter-verse">장:절</th>
                                <th>내용</th>
                            </tr>
                        </thead>
                        <tbody>
                        </tbody>
                    </table>
                </div>
                <br>
                <a href="/download">
                    <h3>성경 검색 프로그램 다운로드</h3>
                </a>
            </div>
            <script>
                document.getElementById('verseSearchButton').addEventListener('click', function(event) {
                    search('verse');
                });

                document.getElementById('contentSearchButton').addEventListener('click', function(event) {
                    search('content');
                });

                document.getElementById('verse').addEventListener('keypress', function(event) {
                    if (event.key === 'Enter') {
                        event.preventDefault();
                        search('verse');
                    }
                });

                document.getElementById('content').addEventListener('keypress', function(event) {
                    if (event.key === 'Enter') {
                        event.preventDefault();
                        search('content');
                    }
                });

                function search(type) {
                    let versions = Array.from(document.getElementById('versions').selectedOptions).map(option => option.value);
                    let value = (type === 'verse') ? document.getElementById('verse').value : document.getElementById('content').value;

                    if (versions.length === 0) {
                        versions = ['한글KJV'];
                    }

                    // 로딩 애니메이션 표시
                    let loader = document.getElementById('loader-content');
                    let loaderText = document.getElementById('loaderText-content');
                    loader.classList.remove('hidden');
                    let startTime = Date.now();

                    let timer = setInterval(() => {
                        let elapsedTime = Math.floor((Date.now() - startTime) / 1000);
                        loaderText.innerText = `${elapsedTime}s`;
                    }, 1000);

                    fetch('/search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ versions: versions, type: type, value: value })
                    })
                    .then(response => {
                        clearInterval(timer);
                        loader.classList.add('hidden');
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        let tableBody = document.querySelector('#resultsTable tbody');
                        tableBody.innerHTML = '';
                        if (data.length === 0) {
                            let row = document.createElement('tr');
                            row.innerHTML = `<td colspan="4">결과가 없습니다.</td>`;
                            tableBody.appendChild(row);
                        } else {
                            data.forEach(result => {
                                let row = document.createElement('tr');
                                let content = result[3];
                                if (type === 'content') {
                                    let regex = new RegExp(value, 'gi');
                                    content = content.replace(regex, match => `<span class="highlight">${match}</span>`);
                                }
                                row.innerHTML = `<td class="version">${result[0]}</td><td class="book">${result[1]}</td><td class="chapter-verse">${result[2]}</td><td class="content">${content}</td>`;
                                tableBody.appendChild(row);
                            });
                        }
                        document.getElementById('count').innerText = `찾았음: ${data.length} 개`;
                    })
                    .catch(error => {
                        clearInterval(timer);
                        loader.classList.add('hidden');
                        console.error('Error:', error);
                    });
                }
            </script>
        </body>
        </html>
    ''', versions=versions)

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    versions = data.get('versions', [])
    search_type = data.get('type')
    value = data.get('value')

    logging.debug(f"Search request: versions={versions}, search_type={search_type}, value={value}")

    if not versions:
        versions = ["한글KJV"]

    if search_type == 'verse':
        results = search_by_verse(versions, value)
    elif search_type == 'content':
        results = search_by_content(versions, value)
    else:
        results = []

    logging.debug(f"Search completed.")
    return jsonify(results)

def search_by_verse2(versions, query):
    logging.debug(f"search_by_verse called with versions={versions}, query={query}")
    results = []
    try:
        verses = query.split(",")
        for vc in verses:
            vc = vc.strip()
            match = re.match(r"(\D+)(\d*):?(\d*/?\d*)", vc)
            if match:
                book = match.group(1)
                chapter = match.group(2)
                verse_range = match.group(3)
                book = abbreviations.get(book, book)
                logging.debug(f"Searching for book={book}, chapter={chapter}, verse_range={verse_range}")

                for version in versions:
                    file_path = os.path.join(bible_dir, f"{version}_{book}.txt")
                    logging.debug(f"Checking file: {file_path}")
                    if not os.path.exists(file_path):
                        logging.warning(f"File not found: {file_path}")
                        continue

                    with open(file_path, 'r', encoding='utf-8') as file:
                        lines = [line.strip() for line in file if line.strip()]
                        if chapter and '/' in verse_range:
                            start_verse, end_verse = map(int, verse_range.split('/'))
                            for line in lines:
                                parts = line.split(maxsplit=1)
                                if len(parts) != 2:
                                    continue
                                chapter_verse, content = parts
                                line_chapter, line_verse = map(int, chapter_verse.split(':'))
                                if line_chapter == int(chapter) and start_verse <= line_verse <= end_verse:
                                    results.append((version, book, chapter_verse, content))
                        elif chapter and verse_range:
                            for line in lines:
                                parts = line.split(maxsplit=1)
                                if len(parts) != 2:
                                    continue
                                chapter_verse, content = parts
                                if line.startswith(f"{chapter}:{verse_range} "):
                                    results.append((version, book, chapter_verse, content))
                        elif chapter:
                            for line in lines:
                                parts = line.split(maxsplit=1)
                                if len(parts) != 2:
                                    continue
                                chapter_verse, content = parts
                                if line.startswith(f"{chapter}:"):
                                    results.append((version, book, chapter_verse, content))
                        else:
                            for line in lines:
                                parts = line.split(maxsplit=1)
                                if len(parts) != 2:
                                    continue
                                chapter_verse, content = parts
                                results.append((version, book, chapter_verse, content))
    except Exception as e:
        logging.error('Error occurred in search_by_verse', exc_info=True)
    return results

def search_by_content(versions, query):
    logging.debug(f"search_by_content called with versions={versions}, query={query}")
    results = []
    try:
        # 여러 구절을 따옴표 또는 공백으로 구분하여 처리
        if query.startswith("+"):
            queries = [query[1:]]
        else:
            queries = re.findall(r'"[^"]+"|\S+', query)
        for q in queries:
            q = q.strip('"')  # 따옴표 제거
            for version in versions:
                for filename in os.listdir(bible_dir):
                    if filename.startswith(version) and filename.endswith(".txt"):
                        book = filename.split("_", 1)[1].split(".")[0]
                        file_path = os.path.join(bible_dir, filename)
                        logging.debug(f"Checking file: {file_path}")
                        with open(file_path, 'r', encoding='utf-8') as file:
                            lines = file.readlines()
                            for line in lines:
                                if q in line:
                                    chapter_verse, content = line.strip().split(maxsplit=1)
                                    if q in content:
                                        results.append((version, book, chapter_verse, content))
    except Exception as e:
        logging.error('Error occurred in search_by_content', exc_info=True)
    return results

@app.route('/download')
def download():
    file_path = "c:/bible/bible_find.zip"
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    print(f'* Serving Flask app "web"\n* Debug mode: on')
    app.run(debug=True, host='0.0.0.0')
