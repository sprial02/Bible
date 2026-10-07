import os

def merge_bibles(source_dir, target_dir):
    # c:\bible 디렉터리 안의 파일 목록 가져오기
    target_files = os.listdir(target_dir)
    
    # d:\eng_bible 디렉터리 안의 파일 목록 가져오기
    source_files = os.listdir(source_dir)
    
    for source_file in source_files:
        # d:\eng_bible에 있는 파일명과 c:\bible에 있는 파일명 비교
        for target_file in target_files:
            if source_file.endswith(".txt") and target_file.endswith(".txt"):
                if source_file.split("_")[-1] == target_file.split("_")[-1]:
                    source_path = os.path.join(source_dir, source_file)
                    target_path = os.path.join(target_dir, target_file)
                    with open(source_path, "r", encoding="utf-8") as sf:
                        source_content = sf.read()
                    with open(target_path, "a", encoding="utf-8") as tf:
                        tf.write("\n\n" + source_content)

# 변경하려는 디렉토리 설정
source_dir = "D:/eng_bible"
target_dir = "C:/bible"

# 성경 파일 병합 함수 호출
merge_bibles(source_dir, target_dir)
