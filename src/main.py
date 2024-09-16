import os
import json
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError


# token.json 파일에서 인증 정보 로드
def load_credentials():
    try:
        with open("token.json", "r") as f:
            token_data = json.load(f)
        return token_data
    except FileNotFoundError:
        print(
            "token.json 파일을 찾을 수 없습니다. src/update_token.py를 실행하여 토큰을 생성해주세요."
        )
        return None


def get_youtube_service():
    token_data = load_credentials()
    if not token_data:
        return None

    try:
        credentials = Credentials.from_authorized_user_info(
            {
                "client_id": token_data["client_id"],
                "client_secret": token_data["client_secret"],
                "refresh_token": token_data["refresh_token"],
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        )
        return build("youtube", "v3", credentials=credentials)
    except RefreshError as e:
        print(f"리프레시 토큰 오류: {e}")
        print("새로운 리프레시 토큰을 얻어야 합니다. src/update_token.py를 실행하세요.")
        return None
    except Exception as e:
        print(f"YouTube 서비스 객체 생성 중 오류 발생: {e}")
        return None


def get_liked_videos(youtube, max_results=50, page_token=None):
    try:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            myRating="like",
            maxResults=max_results,
            pageToken=page_token,
        )
        response = request.execute()
        return response.get("items", []), response.get("nextPageToken")
    except Exception as e:
        print(f"좋아요 표시한 동영상을 가져오는 중 오류 발생: {e}")
        if "invalid_grant" in str(e):
            print(
                "리프레시 토큰이 만료되었거나 유효하지 않습니다. 새로운 토큰을 얻어야 합니다."
            )
        return [], None


def save_to_file(videos, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    print(f"결과가 {filename}에 저장되었습니다.")


def main():
    # YouTube 서비스 객체 얻기
    youtube = get_youtube_service()
    if not youtube:
        return

    all_liked_videos = []
    next_page_token = None
    max_results = int(input("한 번에 가져올 동영상 수를 입력하세요 (최대 50): "))
    max_pages = int(input("가져올 페이지 수를 입력하세요 (모든 페이지는 0): "))

    page_count = 0
    while True:
        liked_videos, next_page_token = get_liked_videos(
            youtube, max_results, next_page_token
        )
        all_liked_videos.extend(liked_videos)
        page_count += 1

        print(f"페이지 {page_count}: {len(liked_videos)}개의 동영상을 가져왔습니다.")

        if not next_page_token or (max_pages != 0 and page_count >= max_pages):
            break

    if all_liked_videos:
        print(f"총 {len(all_liked_videos)}개의 좋아요 표시한 동영상을 찾았습니다.")

        save_option = input("결과를 파일로 저장하시겠습니까? (y/n): ").lower()
        if save_option == "y":
            filename = f"liked_videos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_to_file(all_liked_videos, filename)

        print_option = input("결과를 화면에 출력하시겠습니까? (y/n): ").lower()
        if print_option == "y":
            for video in all_liked_videos:
                print(f"제목: {video['snippet']['title']}")
                print(f"동영상 ID: {video['id']}")
                print(f"조회수: {video['statistics']['viewCount']}")
                print("---")
    else:
        print("좋아요 표시한 동영상을 찾지 못했습니다.")


if __name__ == "__main__":
    main()
