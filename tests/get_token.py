import os
import json
from google_auth_oauthlib.flow import Flow
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
from datetime import datetime

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# OAuth 2.0 인증 흐름 설정
flow = Flow.from_client_config(
    {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    },
    scopes=["https://www.googleapis.com/auth/youtube.force-ssl"],
)

flow.redirect_uri = REDIRECT_URI

# 인증 URL 생성
auth_url, _ = flow.authorization_url(prompt="consent")

print(f"다음 URL을 브라우저에서 열어 인증을 진행하세요: {auth_url}")

# 사용자로부터 인증 코드 입력 받기
full_url = input("인증 후 리디렉션된 전체 URL을 입력하세요: ").strip()

# URL에서 코드 추출
parsed_url = urlparse(full_url)
code = parse_qs(parsed_url.query).get("code", [None])[0]

if not code:
    print("URL에서 인증 코드를 찾을 수 없습니다. 올바른 URL을 입력했는지 확인해주세요.")
else:
    # 토큰 교환 시도
    try:
        flow.fetch_token(code=code)
        refresh_token = flow.credentials.refresh_token

        # JSON 파일로 저장
        data = {
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }

        filename = (
            f"youtube_credentials_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"인증 정보가 {filename}에 저장되었습니다.")
        print(f"REFRESH_TOKEN={refresh_token}")
    except Exception as e:
        print(f"오류 발생: {e}")
        print("인증 과정을 다시 시도해주세요.")
