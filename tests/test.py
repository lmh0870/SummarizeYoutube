import os
from googleapiclient.discovery import build

# YouTube API 키
API_KEY = os.getenv("API_KEY")


# YouTube API 클라이언트 생성
youtube = build("youtube", "v3", developerKey=API_KEY)


def get_channel_videos(channel_id, max_results=50):
    videos = []
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=max_results,
        order="date",
        type="video",
    )

    response = request.execute()

    for item in response["items"]:
        video = {
            "title": item["snippet"]["title"],
            "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
            "link": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
        }
        videos.append(video)

    return videos


# 채널 ID를 입력하세요
channel_id = "UCA7J-sgaaGD6BQKX4tYAn_g"

# 동영상 정보 가져오기
videos = get_channel_videos(channel_id)

# 결과 출력
for video in videos:
    print(f"제목: {video['title']}")
    print(f"썸네일: {video['thumbnail']}")
    print(f"링크: {video['link']}")
    print("---")
