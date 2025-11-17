import streamlit as st
from urllib.parse import urlparse, parse_qs

# -----------------------------
# YouTube 영상 ID 추출 함수
# -----------------------------
def extract_video_id(url):
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname in ["youtu.be"]:
            return parsed_url.path[1:]
        if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
            return parse_qs(parsed_url.query).get('v', [None])[0]
    except:
        return None

# -----------------------------
# YouTube 썸네일 URL 가져오기
# -----------------------------
def get_video_thumbnail(video_id):
    # 최대 해상도 썸네일 URL
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("📌 YouTube 썸네일 추출기")
st.write("유튜브 링크를 입력하면 영상 썸네일을 보여줍니다.")

youtube_url = st.text_input("YouTube 영상 URL 입력")

if st.button("썸네일 가져오기"):
    video_id = extract_video_id(youtube_url)
    if not video_id:
        st.error("유효한 YouTube URL이 아닙니다.")
    else:
        thumbnail_url = get_video_thumbnail(video_id)
        st.image(thumbnail_url, caption="썸네일", use_column_width=True)
        st.success("썸네일을 가져왔습니다!")

