import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수에서 API 키 가져오기
api_key = os.getenv("API_KEY")

if not api_key:
    raise ValueError("YOUTUBE_API_KEY가 환경 변수에 설정되지 않았습니다.")

url = "https://www.youtube.com/@sa_caffeine"

# URL에서 사용자 이름 추출
username = url.split("@")[-1]

# YouTube API 클라이언트 생성
youtube = build("youtube", "v3", developerKey=api_key)

try:
    # 채널 검색 요청
    request = youtube.search().list(part="id", type="channel", q=username, maxResults=1)
    response = request.execute()

    # 채널 ID 추출
    if "items" in response and response["items"]:
        channel_id = response["items"][0]["id"]["channelId"]
        print(f"채널 ID: {channel_id}")
    else:
        print(f"'{username}' 사용자 이름에 해당하는 채널을 찾을 수 없습니다.")

except Exception as e:
    print(f"오류 발생: {str(e)}")
