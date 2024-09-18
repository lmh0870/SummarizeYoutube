import os
import subprocess
import whisper
import srt
import json
from tqdm import tqdm


# Step 1: 음성 추출
def extract_audio(video_path, audio_path):
    if os.path.exists(audio_path):
        print(f"오디오 파일이 이미 존재합니다: {audio_path}")
        return
    result = subprocess.run(
        ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path]
    )
    if result.returncode != 0:
        raise Exception("음성 추출 실패")


# Step 2: 음성 인식 (Whisper 라이브러리 사용)
def transcribe_audio(audio_path, cache_path):
    if os.path.exists(cache_path):
        print(f"캐시된 전사 결과를 불러옵니다: {cache_path}")
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"오디오 파일을 찾을 수 없습니다: {audio_path}")

    print(f"음성 인식 중: {audio_path}")
    model = whisper.load_model("large")
    result = model.transcribe(audio_path)

    # 캐시에 결과 저장
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(result["segments"], f, ensure_ascii=False, indent=2)

    return result["segments"]


# Step 3: 자막 파일 생성
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

    print(f"자막 파일이 생성되었습니다: {srt_path}")


def process_video(video_path, output_folder, cache_folder):
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = os.path.join(output_folder, f"{base_name}.mp3")
    srt_path = os.path.join(
        cache_folder, f"{base_name}.srt"
    )  # srt 파일 경로를 cache_folder로 변경
    cache_path = os.path.join(cache_folder, f"{base_name}_transcript.json")

    try:
        extract_audio(video_path, audio_path)
        transcript_segments = transcribe_audio(audio_path, cache_path)
        create_srt(transcript_segments, srt_path)
    except Exception as e:
        print(f"오류 발생 ({video_path}): {e}")


def main():
    video_folder = "data/videos"
    output_folder = "data/mp3"
    cache_folder = "data/cache"

    for folder in [output_folder, cache_folder]:
        os.makedirs(folder, exist_ok=True)

    video_extensions = (".mp4", ".avi", ".mov", ".webm")
    video_files = [
        f for f in os.listdir(video_folder) if f.lower().endswith(video_extensions)
    ]

    for video_file in tqdm(video_files, desc="비디오 처리 중"):
        video_path = os.path.join(video_folder, video_file)
        process_video(video_path, output_folder, cache_folder)


if __name__ == "__main__":
    main()
