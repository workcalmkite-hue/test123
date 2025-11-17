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
def get_top_comments(api_key, video_id, max_results=50):
youtube = build('youtube', 'v3', developerKey=api_key)


request = youtube.commentThreads().list(
part="snippet",
videoId=video_id,
maxResults=max_results,
order="relevance" # 관련도 높은 순(좋아요 높은 댓글 포함)
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


# 좋아요수 기준 정렬
comments.sort(key=lambda x: x["likes"], reverse=True)
return comments[:3]


# -----------------------------
# Streamlit UI
# -----------------------------
st.title("📌 YouTube 영상 베스트 댓글 추출기")
st.write("유튜브 링크를 입력하면 공감(좋아요) 상위 3개 댓글을 보여줍니다.")


api_key = st.text_input("YouTube API 키 입력", type="password")
youtube_url = st.text_input("YouTube 영상 URL 입력")


if st.button("베스트 댓글 가져오기"):
if not api_key:
st.error("API 키를 입력하세요.")
else:
video_id = extract_video_id(youtube_url)
st.error(f"에러 발생: {e}")
