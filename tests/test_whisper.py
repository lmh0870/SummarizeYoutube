import whisper

model = whisper.load_model("base")
result = model.transcribe("audio.mp3")

for segment in result["segments"]:
    start_time = segment["start"]
    end_time = segment["end"]
    text = segment["text"]
    print(f"[{start_time:.2f}s - {end_time:.2f}s] {text}")
