import os
import shutil
import glob

source = "/Volumes/Storage/아린"
destination = "/Volumes/Storage/아린/0"

# 대상 폴더가 없으면 생성
if not os.path.exists(destination):
    os.makedirs(destination)

# 모든 파일 경로 가져오기
all_files = glob.glob(os.path.join(source, "**", "*"), recursive=True)

# 파일 이동
for file_path in all_files:
    # 파일인 경우에만 처리
    if os.path.isfile(file_path):
        # 대상 폴더 내부의 파일은 건너뛰기
        if file_path.startswith(destination):
            continue

        # 파일 이름만 추출
        file_name = os.path.basename(file_path)

        # 대상 경로 생성
        dst_path = os.path.join(destination, file_name)

        # 동일한 이름의 파일이 있는 경우 처리
        counter = 1
        while os.path.exists(dst_path):
            name, ext = os.path.splitext(file_name)
            dst_path = os.path.join(destination, f"{name}_{counter}{ext}")
            counter += 1

        # 파일 이동
        shutil.move(file_path, dst_path)

# 남은 빈 폴더 삭제
for root, dirs, files in os.walk(source, topdown=False):
    for dir_name in dirs:
        dir_path = os.path.join(root, dir_name)
        if dir_path != destination:
            try:
                os.rmdir(dir_path)
            except OSError:
                pass  # 폴더가 비어있지 않으면 무시

print("모든 파일이 성공적으로 이동되었고, 빈 폴더가 삭제되었습니다.")
