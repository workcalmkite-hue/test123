import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from urllib.parse import urlparse, parse_qs
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO

# -----------------------------
# 🔎 디버그용: 지금 이 앱에서 읽히는 secrets 키들 확인
# -----------------------------
st.sidebar.write("🔐 Secrets keys:", list(st.secrets.keys()))


# -----------------------------
# 1. 유튜브 영상 ID 추출 함수
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

# ✅ 다른 페이지와 '완전히 똑같이' API 키 불러오기
api_key = st.secrets.get("YT_API_KEY")
st.write("🔎 DEBUG - api_key is None? →", api_key is None)

youtube_url = st.text_input("🎥 YouTube 영상 URL 입력")
max_pages = st.slider("가져올 댓글 페이지 수 (1페이지=100개)", 1, 10, 5)

# -----------------------------
# 버튼 클릭 시 실행
# -----------------------------
if st.button("워드클라우드 만들기"):
    if not api_key:
        st.error("❌ API 키가 없습니다. 이 앱의 Secrets에 YT_API_KEY를 다시 확인해 주세요.")
        st.stop()

    video_id = extract_video_id(youtube_url)
    if not video_id:
        st.error("❌ 올바른 유튜브 링크가 아닙니다.")
        st.stop()

    try:
        with st.spinner("댓글을 불러오는 중입니다..."):
            comments = get_all_comments(api_key, video_id, max_pages)

    except RuntimeError as e:
        st.error(str(e))
        st.stop()

    except Exception as e:
        st.error(f"알 수 없는 오류 발생: {e}")
        st.stop()

    if not comments:
        st.warning("댓글이 하나도 없어요!")
        st.stop()

    all_text = " ".join(comments)

    # Streamlit Cloud에서 한글 지원되는 폰트 (Noto)
    font_path = "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"

    wc = WordCloud(
        font_path=font_path,
        width=800,
        height=400,
        background_color="white",
    ).generate(all_text)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

    img_bytes = BytesIO()
    fig.savefig(img_bytes, format="png")
    img_bytes.seek(0)

    st.download_button(
        label="📥 워드클라우드 이미지 다운로드",
        data=img_bytes,
        file_name="wordcloud.png",
        mime="image/png",
    )

    st.success("워드클라우드 생성 완료!")
