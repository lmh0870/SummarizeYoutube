# 유튜브 좋아요 동영상 추출기

이 프로젝트는 유튜브에서 사용자가 좋아요 표시한 동영상의 제목과 링크를 자동으로 추출하고 관리합니다.

## 기능

- YouTube API를 사용하여 사용자의 좋아요 표시한 동영상 목록 가져오기
- 동영상 제목과 링크 추출 및 저장
- 로깅 기능을 통한 프로그램 실행 상태 모니터링

## 설치

1. 필요한 패키지를 설치합니다:
   ```
   pip install -r requirements.txt
   ```

## 사용 방법

1. `src/main.py` 파일을 실행하여 프로그램을 시작합니다:

   ```
   python src/main.py
   ```

2. 프로그램이 자동으로 좋아요 표시한 동영상을 업데이트합니다.
3. 콘솔에 표시되는 로그 메시지로 진행 상황을 확인할 수 있습니다.

## 프로젝트 구조

- `src/main.py`: 메인 실행 파일
- `src/scripts/update_liked_videos.py`: 좋아요 표시한 동영상 업데이트 스크립트
- `src/lib/video_manager.py`: 동영상 관리 클래스 (VideoManager)
- `src/lib/logging_config.py`: 로깅 설정

## 주의사항

- YouTube API 키가 필요합니다. 사용 전 적절한 API 키를 설정해야 합니다.
- 인터넷 연결이 필요합니다.
- API 사용량 제한에 주의하세요.
