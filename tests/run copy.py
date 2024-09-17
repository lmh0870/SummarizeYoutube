from src.lib.logging_config import logger

# 상수 정의
TOKEN_FILE = "token.json"
DB_FILE = "liked_videos.db"

# 로깅 설정
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# token.json 파일에서 인증 정보 로드
def load_credentials():
    try:
        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)
        return token_data
    except FileNotFoundError:
        logger.error(
            f"{TOKEN_FILE} 파일을 찾을 수 없습니다. src/update_token.py를 실행하여 토큰을 생성해주세요."
        )
    except json.JSONDecodeError:
        logger.error(f"{TOKEN_FILE} 파일의 형식이 올바르지 않습니다.")
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
        # 좋아요 표시한 동영상 재생목록 ID 가져오기
        channels_response = (
            youtube.channels().list(part="contentDetails", mine=True).execute()
        )

        likes_playlist_id = channels_response["items"][0]["contentDetails"][
            "relatedPlaylists"
        ]["likes"]

        # 좋아요 표시한 동영상 가져오기
        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=likes_playlist_id,
            maxResults=max_results,
            pageToken=page_token,
        )
        response = request.execute()

        # 동영상 세부 정보 가져오기
        video_ids = [
            item["contentDetails"]["videoId"] for item in response.get("items", [])
        ]
        videos_response = (
            youtube.videos()
            .list(part="snippet,contentDetails,statistics", id=",".join(video_ids))
            .execute()
        )

        return videos_response.get("items", []), response.get("nextPageToken")
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


def create_connection():
    return sqlite3.connect(DB_FILE)


def create_table(conn):
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS liked_videos (
        id TEXT PRIMARY KEY,
        title TEXT,
        description TEXT,
        published_at TEXT,
        channel_title TEXT,
        thumbnail_url TEXT,
        tags TEXT,
        category_id TEXT,
        video_url TEXT,
        duration TEXT
    )
    """
    )
    conn.commit()


def insert_video(conn, video):
    cursor = conn.cursor()
    cursor.execute(
        """
    INSERT OR REPLACE INTO liked_videos
    (id, title, description, published_at, channel_title, thumbnail_url, tags, category_id, video_url, duration)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            video["id"],
            video["snippet"]["title"],
            video["snippet"]["description"],
            video["snippet"]["publishedAt"],
            video["snippet"]["channelTitle"],
            video["snippet"]["thumbnails"]["medium"]["url"],
            ",".join(video["snippet"].get("tags", [])),
            video["snippet"]["categoryId"],
            f"https://www.youtube.com/watch?v={video['id']}",
            video["contentDetails"]["duration"],
        ),
    )
    conn.commit()


def main():
    # YouTube 서비스 객체 얻기
    youtube = get_youtube_service()
    if not youtube:
        return

    with create_connection() as conn:
        create_table(conn)

        all_liked_videos = []
        next_page_token = None
        max_results = 50  # 한 번에 가져올 최대 동영상 수
        max_pages = 0  # 모든 페이지 가져오기

        page_count = 0
        while True:
            liked_videos, next_page_token = get_liked_videos(
                youtube, max_results, next_page_token
            )
            for video in liked_videos:
                insert_video(conn, video)
            all_liked_videos.extend(liked_videos)
            page_count += 1

            print(
                f"페이지 {page_count}: {len(liked_videos)}개의 동영상을 가져와 저장했습니다."
            )

            if not next_page_token or (max_pages != 0 and page_count >= max_pages):
                break

        if all_liked_videos:
            print(
                f"총 {len(all_liked_videos)}개의 좋아요 표시한 동영상을 찾아 저장했습니다."
            )

            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM liked_videos ORDER BY published_at ASC LIMIT 5"
            )
            oldest_videos = cursor.fetchall()

            print("\n가장 오래된 좋아요 표시한 동영상 5개:")
            for video in oldest_videos:
                print(f"제목: {video[1]}")
                print(f"채널: {video[4]}")
                print(f"게시일: {video[3]}")
                print(f"재생 시간: {video[9] if len(video) > 9 else '정보 없음'}")
                print(f"카테고리 ID: {video[7] if len(video) > 7 else '정보 없음'}")
                print(f"태그: {video[6] if len(video) > 6 else '정보 없음'}")
                print("---")
        else:
            print("좋아요 표시한 동영상을 찾지 못했습니다.")

    conn.close()


if __name__ == "__main__":
    main()
