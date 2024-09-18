import openai


# 자막 파일 읽기
with open("subtitles.srt", "r", encoding="utf-8") as file:
    content = file.read()

# OpenAI API를 사용하여 요약
response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant that summarizes Korean text.",
        },
        {
            "role": "user",
            "content": f"""다음 지침에 따라 주어진 스크립트를 분석하고 요약해주세요:

1. 스크립트 구조 파악:
   • 전체적인 구조를 파악하고 주요 부분을 식별하세요.
   • 도입부, 본문, 결론 등의 구조를 확인하세요.

2. 핵심 내용 요약:
   • 스크립트의 주요 내용을 간략히 요약하세요.
   • 중심 주제와 핵심 개념을 중점적으로 다루세요.

3. 단계별 흐름 정리:
   • 스크립트의 진행 순서를 정리하세요.
   • 각 부분의 제목과 주요 내용을 요약하세요.

4. 주요 주제 목록화:
   • 스크립트에서 다루는 핵심 주제나 개념을 나열하세요.
   • 각 주제에 대한 간단한 설명을 포함하세요.

5. 중요 개념 강조:
   • 스크립트에서 강조되는 주요 개념을 부각시키세요.
   • 이 개념들이 전체 내용에서 어떤 역할을 하는지 설명하세요.

6. 종합 요약:
   • 스크립트의 핵심 내용을 간결하게 정리하세요.
   • 결론 부분이 있다면 이를 포함하여 전체 내용을 한 문단으로 요약하세요.

아래 스크립트를 분석해주세요:

{content}""",
        },
    ],
)

# 요약 결과 출력
print(response.choices[0].message["content"])
