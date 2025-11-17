import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from openai import OpenAI

# -----------------------------
# 0. 기본 설정
# -----------------------------
st.title("🎬 YouTube 영상 요약 & 학습 도우미")
st.write(
    """
YouTube 영상을 입력하면  
**자막을 분석해서 아래 내용을 자동으로 만들어줘요.**

- ✏️ 핵심 문장
- 📌 3줄 요약
- 🧷 핵심 키워드
- ❓ 이해도 점검 질문
"""
)

yt_api_key = st.secrets.get("YT_API_KEY")
openai_api_key = st.secrets.get("OPENAI_API_KEY")

# -----------------------------
# 1. 유튜브 영상 ID 추출 함수
# -----------------------------
def extract_video_id(url: str):
    try:
        parsed = urlparse(url)
        if parsed.hostname in ["youtu.be"]:
            return parsed.path[1:]
        if parsed.hostname in ["www.youtube.com", "youtube.com"]:
            return parse_qs(parsed.query).get("v", [None])[0]
    except:
        return None

# -----------------------------
# 2. 유튜브 영상 정보 가져오기 (제목 등)
# -----------------------------
def get_video_title(api_key, video_id):
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()
        items = response.get("items", [])
        if not items:
            return None
        return items[0]["snippet"]["title"]
    except HttpError:
        return None

# -----------------------------
# 3. 자막(Transcript) 가져오기
# -----------------------------
def get_video_transcript(video_id: str):
    """
    가능한 경우:
      - 한국어 자막 우선 (ko)
      - 없으면 영어(en)
      - 그것도 없으면 에러
    """
    try:
        # 자막 리스트 확인
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # 한국어 자막 우선
        try:
            transcript = transcript_list.find_transcript(['ko'])
        except NoTranscriptFound:
            # 영어 자막 시도
            transcript = transcript_list.find_transcript(['en'])

        fetched = transcript.fetch()
        # 텍스트만 이어붙이기
        full_text = " ".join([item["text"] for item in fetched])
        return full_text

    except TranscriptsDisabled:
        raise RuntimeError("이 영상은 자막(Transcript)이 비활성화되어 있습니다.")
    except NoTranscriptFound:
        raise RuntimeError("해당 영상에서 사용할 수 있는 자막을 찾을 수 없습니다. (ko/en 없음)")
    except Exception as e:
        raise RuntimeError(f"자막을 가져오는 중 오류가 발생했습니다: {e}")

# -----------------------------
# 4. OpenAI를 사용해서 요약 생성
# -----------------------------
def summarize_with_openai(api_key: str, transcript: str, video_title: str | None = None):
    client = OpenAI(api_key=api_key)

    # 너무 긴 transcript는 잘라서 사용 (토큰 비용 줄이기)
    max_chars = 8000
    if len(transcript) > max_chars:
        transcript = transcript[:max_chars]

    system_prompt = "당신은 한국어로 설명을 잘하는 교사입니다. 중학생에게 설명한다는 느낌으로, 친절하고 명확하게 정리해 주세요."

    user_prompt = f"""
다음은 유튜브 영상의 자막 내용입니다. (필요하면 제목도 참고하세요)

[영상 제목]
{video_title or "제목 정보 없음"}

[자막 내용]
{transcript}

이 내용을 바탕으로 아래 형식으로 한국어로 답변해 주세요.

1. ✏️ 핵심 문장 (가장 중요한 문장 3~5개, 번호 매겨서)
2. 📌 3줄 요약 (딱 3개의 문장으로)
3. 🧷 핵심 키워드 (쉼표로 구분해서 5~10개)
4. ❓ 이해한 내용 점검 질문 (중학생 수준의 확인 질문 5개, 번호 매겨서)

형식 예시는 아래와 같아요:

1. ✏️ 핵심 문장
1) ...
2) ...
3) ...

2. 📌 3줄 요약
- ...
- ...
- ...

3. 🧷 핵심 키워드
키워드: 키워드1, 키워드2, 키워드3, ...

4. ❓ 이해한 내용 점검 질문
1) ...
2) ...
3) ...
4) ...
5) ...
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.5,
    )

    return response.choices[0].message.content

# -----------------------------
# 5. UI 입력 영역
# -----------------------------
youtube_url = st.text_input("🎥 YouTube 영상 URL 입력")
run_button = st.button("📚 영상 요약 분석하기")

# -----------------------------
# 6. 실행 로직
# -----------------------------
if run_button:
    if not yt_api_key:
        st.error("❌ YT_API_KEY가 설정되어 있지 않습니다. Streamlit Secrets에 유튜브 API 키를 넣어주세요.")
        st.stop()

    if not openai_api_key:
        st.error("❌ OPENAI_API_KEY가 설정되어 있지 않습니다. Streamlit Secrets에 OpenAI API 키를 넣어주세요.")
        st.stop()

    video_id = extract_video_id(youtube_url)
    if not video_id:
        st.error("❌ 올바른 유튜브 URL이 아닙니다.")
        st.stop()

    # 1) 영상 제목
    with st.spinner("🎞 영상 정보를 불러오는 중..."):
        video_title = get_video_title(yt_api_key, video_id)

    if video_title:
        st.subheader(f"🎬 영상 제목: {video_title}")
    else:
        st.subheader("🎬 영상 제목 정보를 가져오지 못했습니다.")

    # 2) 자막 가져오기
    try:
        with st.spinner("📝 자막(Transcript)을 가져오는 중..."):
            transcript = get_video_transcript(video_id)
    except RuntimeError as e:
        st.error(str(e))
        st.stop()

    # 자막 일부 미리보기
    with st.expander("🔍 자막 내용 미리보기 (일부)", expanded=False):
        st.write(transcript[:1000] + ("..." if len(transcript) > 1000 else ""))

    # 3) OpenAI 요약
    try:
        with st.spinner("🤖 AI가 요약과 질문을 만들고 있어요..."):
            result = summarize_with_openai(openai_api_key, transcript, video_title)
    except Exception as e:
        st.error(f"요약 생성 중 오류가 발생했습니다: {e}")
        st.stop()

    st.markdown("---")
    st.subheader("📚 영상 요약 결과")
    st.markdown(result)
