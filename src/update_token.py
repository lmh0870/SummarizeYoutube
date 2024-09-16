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

        filename = "token.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"인증 정보가 {filename}에 저장되었습니다.")
        print(f"REFRESH_TOKEN={refresh_token}")
    except Exception as e:
        print(f"오류 발생: {e}")
        print("인증 과정을 다시 시도해주세요.")
