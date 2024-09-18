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

    # 임시 오디오 파일 경로
    temp_audio_path = audio_path + ".temp.mp3"

    # 오디오 추출
    result = subprocess.run(
        ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", temp_audio_path]
    )
    if result.returncode != 0:
        raise Exception("음성 추출 실패")

    # 오디오 필터링 적용
    result = subprocess.run(
        [
            "ffmpeg",
            "-i",
            temp_audio_path,
            "-af",
            "highpass=f=200, lowpass=f=3000",
            audio_path,
        ]
    )
    if result.returncode != 0:
        raise Exception("오디오 필터링 실패")

    # 임시 파일 삭제
    os.remove(temp_audio_path)

    print(f"오디오 추출 및 필터링 완료: {audio_path}")


# Step 2: 음성 인식 (Whisper 라이브러리 사용)
def transcribe_audio(audio_path, cache_path):
    if os.path.exists(cache_path):
        print(f"캐시된 전사 결과를 불러옵니다: {cache_path}")
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"오디오 파일을 찾을 수 없습니다: {audio_path}")

    print(f"음성 인식 중: {audio_path}")
    model = whisper.load_model("small")

    # 음악 관련 토큰 억제
    options = whisper.DecodingOptions(
        suppress_tokens=[-1, 1, 2, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    )

    result = model.transcribe(audio_path, **options.__dict__)

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


def cut_silent_parts(video_path, srt_path, output_path):
    # 출력 파일이 이미 존재하는지 확인
    if os.path.exists(output_path):
        print(f"무음 구간이 제거된 비디오가 이미 존재합니다: {output_path}")
        return

    # SRT 파일 읽기
    with open(srt_path, "r", encoding="utf-8") as f:
        subtitles = list(srt.parse(f))

    # 임시 파일 생성을 위한 경로
    temp_file = output_path + ".temp"

    # 자막 정보를 바탕으로 컷 리스트 생성
    with open(temp_file, "w", encoding="utf-8") as f:
        for sub in subtitles:
            f.write(f"between(t,{sub.start.total_seconds()},{sub.end.total_seconds()})")
            if sub != subtitles[-1]:
                f.write("+")

    # ffmpeg를 사용하여 무음 구간 제거
    command = [
        "ffmpeg",
        "-i",
        video_path,
        "-vf",
        f"select='{open(temp_file, 'r').read()}',setpts=N/FRAME_RATE/TB",
        "-af",
        f"aselect='{open(temp_file, 'r').read()}',asetpts=N/SR/TB",
        "-y",
        output_path,
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"오류 발생: {result.stderr}")
        raise Exception("무음 구간 제거 실패")

    # 임시 파일 삭제
    os.remove(temp_file)

    print(f"무음 구간이 제거된 비디오가 생성되었습니다: {output_path}")


def process_video(video_path, output_folder, cache_folder):
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = os.path.join(output_folder, f"{base_name}.mp3")
    srt_path = os.path.join(cache_folder, f"{base_name}.srt")
    cache_path = os.path.join(cache_folder, f"{base_name}_transcript.json")
    output_video_path = os.path.join(output_folder, f"{base_name}_no_silence.mp4")

    try:
        extract_audio(video_path, audio_path)
        transcript_segments = transcribe_audio(audio_path, cache_path)
        create_srt(transcript_segments, srt_path)
        cut_silent_parts(video_path, srt_path, output_video_path)
    except Exception as e:
        print(f"오류 발생 ({video_path}): {e}")


def main():
    video_folder = "data/videos"
    output_folder = "data/output"
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
