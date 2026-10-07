import fitz  # PyMuPDF

def pdf_to_text(pdf_path, output_html):
    # PDF 문서 열기
    document = fitz.open(pdf_path)
    
    # HTML 파일 생성
    with open(output_html, "w", encoding="utf-8") as html_file:
        html_file.write("<html><head><meta charset='UTF-8'><title>PDF to Text</title></head><body>\n")
        
        # 각 페이지의 텍스트 추출
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text = page.get_text("text")
            html_file.write(f"<h1>Page {page_num + 1}</h1>\n")
            html_file.write("<pre>\n")
            html_file.write(text)
            html_file.write("</pre>\n")
        
        html_file.write("</body></html>")

# 사용 예제
pdf_path = "1-1.pdf"
output_html = "1-1.html"
pdf_to_text(pdf_path, output_html)
