import os
import subprocess
import warnings
import whisper
import srt
import logging
from typing import List, Dict
from urllib.parse import urlparse, parse_qs
import glob
import json

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


# 상수 정의
VIDEO_URL = "https://www.youtube.com/watch?v=l2hsDu1Rf2A"


# URL에서 비디오 ID 추출
def get_video_id(url: str) -> str:
    query = urlparse(url).query
    return parse_qs(query)["v"][0]


VIDEO_ID = get_video_id(VIDEO_URL)
VIDEO_PATH = f"{VIDEO_ID}"  # 확장자 제거
AUDIO_PATH = f"{VIDEO_ID}.mp3"
SRT_PATH = f"{VIDEO_ID}.srt"

# 로깅 설정
logging.basicConfig(level=logging.INFO)


# Step 1: 유튜브 비디오 다운로드
def download_video(url: str, output_path: str) -> str:
    if os.path.exists(output_path + ".mp4") or os.path.exists(output_path + ".webm"):
        logging.info(f"비디오 파일이 이미 존재합니다: {output_path}")
        return get_video_file_path(output_path)
    try:
        result = subprocess.run(
            ["yt-dlp", "-o", output_path + ".%(ext)s", url],
            check=True,
            capture_output=True,
            text=True,
        )
        logging.info(f"yt-dlp 출력: {result.stdout}")
        return get_video_file_path(output_path)
    except subprocess.CalledProcessError as e:
        logging.error(f"yt-dlp 오류: {e.output}")
        raise Exception(f"유튜브 비디오 다운로드 실패: {e}")


def get_video_file_path(output_path):
    base_path = os.path.splitext(output_path)[0]
    video_files = glob.glob(f"{base_path}.*")

    if not video_files:
        raise FileNotFoundError(f"비디오 파일을 찾을 수 없습니다: {base_path}")

    return video_files[0]


# Step 2: 음성 추출
def extract_audio(video_path: str, audio_path: str) -> None:
    if os.path.exists(audio_path):
        logging.info(f"오디오 파일이 이미 존재합니다: {audio_path}")
        return

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"비디오 파일을 찾을 수 없습니다: {video_path}")

    try:
        subprocess.run(
            ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise Exception(f"음성 추출 실패: {e}")


# Step 3: 음성 인식 (Whisper 라이브러리 사용)
def transcribe_audio(audio_path: str) -> List[Dict]:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"오디오 파일을 찾을 수 없습니다: {audio_path}")

    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["segments"]


# Step 4: 자막 파일 생성
def create_srt(transcript_segments, srt_path):
    subtitles = []
    for i, segment in enumerate(transcript_segments):
        start = srt.timedelta(seconds=segment["start"])
        end = srt.timedelta(seconds=segment["end"])
        content = segment["text"].strip()
        subtitles.append(
            srt.Subtitle(index=i + 1, start=start, end=end, content=content)
        )

    with open(srt_path, "w", encoding="utf-8") as srt_file:
        srt_file.write(srt.compose(subtitles))


def create_json(srt_path: str, json_path: str) -> None:
    with open(srt_path, "r", encoding="utf-8") as srt_file:
        subtitles = list(srt.parse(srt_file))

    json_data = []
    for subtitle in subtitles:
        json_data.append(
            {
                "index": subtitle.index,
                "start": subtitle.start.total_seconds(),
                "end": subtitle.end.total_seconds(),
                "content": subtitle.content,
            }
        )

    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=2)

    logging.info(f"JSON 파일이 생성되었습니다: {json_path}")


def main() -> None:
    try:
        # 유튜브 비디오 다운로드
        video_file_path = download_video(VIDEO_URL, VIDEO_PATH)
        logging.info(f"다운로드된 비디오 파일 경로: {video_file_path}")

        # 음성 추출
        extract_audio(video_file_path, AUDIO_PATH)

        # 음성 인식
        transcript_segments = transcribe_audio(AUDIO_PATH)

        # 자막 파일 생성
        create_srt(transcript_segments, SRT_PATH)

        # JSON 파일 생성
        JSON_PATH = f"{VIDEO_ID}.json"
        create_json(SRT_PATH, JSON_PATH)

        logging.info(f"자막 파일이 생성되었습니다: {SRT_PATH}")
        logging.info(f"JSON 파일이 생성되었습니다: {JSON_PATH}")
    except Exception as e:
        logging.error(f"오류 발생: {e}", exc_info=True)


if __name__ == "__main__":
    main()
