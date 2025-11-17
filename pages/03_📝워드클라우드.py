import streamlit as st
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO

# -----------------------------
# 유튜브 ID 추출 함수
# -----------------------------
def extract_video_id(url):
    try:
        parsed = urlparse(url)
        if parsed.hostname in ["youtu.be"]:
            return parsed.path[1:]
        if parsed.hostname in ["www.youtube.com", "youtube.com"]:
            return parse_qs(parsed.query).get('v', [None])[0]
    except:
        return None

# -----------------------------
# 댓글 불러오기
# -----------------------------
def get_comments(api_key, video_id, max_pages=5):
    youtube = build("youtube", "v3", developerKey=api_key)
    comments = []
    page_token = None

    for _ in range(max_pages):
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=page_token,
            textFormat="plainText"
        )
        response = request.execute()

        for item in response.get("items", []):
            text = item["snippet"]["topLevelComment"]["snippet"].get("textDisplay", "")
            comments.append(text)

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return comments


# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🌈 YouTube 댓글 워드클라우드 생성기")
st.write("많이 등장한 단어일수록 크게 표시되도록 시각화합니다.")

api_key = st.secrets.get("YT_API_KEY")
youtube_url = st.text_input("YouTube 영상 URL 입력")
page_limit = st.slider("댓글 페이지(1페이지=100개) 불러오기", 1, 10, 5)

if st.button("워드클라우드 만들기"):
    if not api_key:
        st.error("API 키가 없습니다. Secrets에 YT_API_KEY를 등록하세요.")
    else:
        video_id = extract_video_id(youtube_url)

        if not video_id:
            st.error("유효한 YouTube 링크가 아닙니다.")
        else:
            comments = get_comments(api_key, video_id, page_limit)

            if not comments:
                st.warning("댓글이 없습니다.")
            else:
                all_text = " ".join(comments)

                # 워드클라우드 생성
                wc = WordCloud(
                    font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 
                    background_color="white",
                    width=800,
                    height=400
                ).generate(all_text)

                fig, ax = plt.subplots(figsize=(10, 6))
                ax.imshow(wc, interpolation="bilinear")
                ax.axis("off")

                st.pyplot(fig)

                # 다운로드 버튼
                img_bytes = BytesIO()
                fig.savefig(img_bytes, format="png")
                img_bytes.seek(0)

                st.download_button(
                    label="📥 워드클라우드 이미지 다운로드",
                    data=img_bytes,
                    file_name="wordcloud.png",
                    mime="image/png"
                )

                st.success("워드클라우드 생성 완료!")
