import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from urllib.parse import urlparse, parse_qs
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
import os
import re

# -----------------------------
# 1. 유튜브 영상 ID 추출
# -----------------------------
def extract_video_id(url):
    try:
        parsed = urlparse(url)
        if parsed.hostname in ["youtu.be"]:
            return parsed.path[1:]
        if parsed.hostname in ["www.youtube.com", "youtube.com"]:
            return parse_qs(parsed.query).get("v", [None])[0]
    except:
        return None

# -----------------------------
# 2. 댓글 불러오기
# -----------------------------
def get_all_comments(api_key, video_id, max_pages=5):
    youtube = build("youtube", "v3", developerKey=api_key)

    comments = []
    page_token = None

    for _ in range(max_pages):
        try:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                textFormat="plainText",
                pageToken=page_token,
            )
            response = request.execute()

        except HttpError as e:
            if e.resp.status == 403:
                raise RuntimeError("이 영상은 댓글이 비활성화되어 있습니다.")
            raise

        for item in response.get("items", []):
            c = item["snippet"]["topLevelComment"]["snippet"]
            comments.append(c.get("textDisplay", ""))

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return comments


# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🌈 YouTube 댓글 워드클라우드 생성기")
st.write("많이 등장하는 단어일수록 크게 보이는 시각화를 제공합니다!")

api_key = st.secrets.get("YT_API_KEY")

youtube_url = st.text_input("🎥 YouTube 영상 URL 입력")
max_pages = st.slider("불러올 댓글 페이지 수 (1페이지=100개)", 1, 10, 5)

# 🔤 불용어(금지단어) 입력 UI
user_stopwords = st.text_input("🛑 제외하고 싶은 단어(쉼표로 구분)", "ㅋㅋㅋㅋ, ㅋㅋ, 진짜, 그냥, 영상, 사람, 그거")

# 기본 불용어 목록
default_stopwords = {
    "영상", "진짜", "그냥", "ㅋㅋㅋㅋ", "ㅋㅋㅋ", "ㅋㅋ", 
    "그거", "이거", "님", "아니", "근데", "그리고"
}

# -----------------------------
# 버튼 클릭 시 실행
# -----------------------------
if st.button("워드클라우드 만들기"):
    if not api_key:
        st.error("❌ API 키가 없습니다.")
        st.stop()

    video_id = extract_video_id(youtube_url)
    if not video_id:
        st.error("❌ 올바른 유튜브 링크가 아닙니다.")
        st.stop()

    try:
        comments = get_all_comments(api_key, video_id, max_pages)
    except Exception as e:
        st.error(f"에러 발생: {e}")
        st.stop()

    if not comments:
        st.warning("댓글이 없습니다.")
        st.stop()

    # -----------------------------
    # 3. 텍스트 전처리 + 불용어 제거
    # -----------------------------
    text = " ".join(comments)

    # 정규식으로 특수문자/이모지 제거
    text = re.sub(r"[^가-힣A-Za-z0-9\s]", " ", text)

    # 사용자 입력 불용어 정리
    custom_words = set(w.strip() for w in user_stopwords.split(",") if w.strip())

    # 전체 불용어 조합
    stopwords = default_stopwords.union(custom_words)

    # 불용어 제거 수행
    for sw in stopwords:
        text = text.replace(sw, " ")

    # -----------------------------
    # 4. 폰트 설정 → MaruBuri (안되면 기본폰트로)
    # -----------------------------
    font_path = "fonts/MaruBuri-Regular.ttf"
    wc_kwargs = dict(width=800, height=400, background_color="white")

    try:
        wc = WordCloud(font_path=font_path, **wc_kwargs).generate(text)
    except:
        st.warning("⚠️ MaruBuri 폰트를 사용할 수 없어 기본폰트로 생성합니다.")
        wc = WordCloud(**wc_kwargs).generate(text)

    # -----------------------------
    # 5. 워드클라우드 표시
    # -----------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

    # 이미지 다운로드
    img_bytes = BytesIO()
    fig.savefig(img_bytes, format="png")
    img_bytes.seek(0)

    st.download_button(
        label="📥 워드클라우드 이미지 다운로드",
        data=img_bytes,
        file_name="wordcloud.png",
        mime="image/png",
    )
    st.success("완료! 워드클라우드 생성됨 😊")
