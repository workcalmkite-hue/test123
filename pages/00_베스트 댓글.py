import streamlit as st
from googleapiclient.discovery import build
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
# YouTube 댓글 불러오기
# -----------------------------
def get_top_comments(api_key, video_id, max_results=50, top_n=3):
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=max_results,
        order="relevance"  # 관련도 높은 순
    )

    response = request.execute()

    comments = []
    for item in response.get("items", []):
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        comments.append({
            "author": snippet.get("authorDisplayName", "Unknown"),
            "text": snippet.get("textDisplay", ""),
            "likes": snippet.get("likeCount", 0)
        })

    comments.sort(key=lambda x: x["likes"], reverse=True)
    return comments[:top_n]

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("📌 YouTube 영상 베스트 댓글 추출기")
st.write("유튜브 링크를 입력하면 공감(좋아요) 상위 댓글을 보여줍니다.")

# Streamlit Secrets에서 API 키 가져오기
api_key = st.secrets.get("YT_API_KEY")

youtube_url = st.text_input("YouTube 영상 URL 입력")
top_n = st.number_input("몇 개의 댓글을 볼까요?", min_value=1, max_value=50, value=3, step=1)

if st.button("댓글 가져오기"):
    if not api_key:
        st.error("API 키가 설정되어 있지 않습니다. Streamlit Secrets에 YT_API_KEY를 추가하세요.")
    else:
        video_id = extract_video_id(youtube_url)
        if not video_id:
            st.error("유효한 YouTube URL이 아닙니다.")
        else:
            try:
                top_comments = get_top_comments(api_key, video_id, top_n=top_n)
                if not top_comments:
                    st.warning("댓글을 찾을 수 없습니다.")
                else:
                    st.subheader(f"👍 베스트 댓글 Top {top_n}")
                    for idx, c in enumerate(top_comments, 1):
                        st.markdown(f"### 댓글 {idx}")
                        st.write(f"**작성자:** {c['author']}")
                        st.write(f"**좋아요:** {c['likes']}")
                        st.write(c['text'])
                        st.markdown("---")
            except Exception as e:
                st.error(f"에러 발생: {e}")
