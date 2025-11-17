import streamlit as st
import requests
from urllib.parse import urlparse, parse_qs

st.set_page_config(page_title="유튜브 댓글 검색", page_icon="🔍")

# ✅ YouTube API 키 (secrets에 맞게 이름만 수정해서 사용!)
API_KEY = st.secrets["YOUTUBE_API_KEY"]  # 예: st.secrets["youtube"]["api_key"] 로 써도 됨


# ---------------------------
# 유튜브 링크에서 videoId 뽑는 함수
# ---------------------------
def extract_video_id(url_or_id: str) -> str:
    """유튜브 전체 링크 / shorts 링크 / live 링크 / 그냥 videoId 모두 처리"""
    text = url_or_id.strip()

    # 그냥 ID만 넣은 경우도 허용 (길이 11짜리 등)
    if "youtube.com" not in text and "youtu.be" not in text:
        return text

    parsed = urlparse(text)

    # youtu.be/VIDEO_ID
    if parsed.hostname in ("youtu.be", "www.youtu.be"):
        return parsed.path.lstrip("/")

    # youtube.com/watch?v=VIDEO_ID
    if parsed.hostname and "youtube.com" in parsed.hostname:
        # /watch?v=VIDEO_ID
        if parsed.path == "/watch":
            qs = parse_qs(parsed.query)
            return qs.get("v", [""])[0]

        # /shorts/VIDEO_ID
        if parsed.path.startswith("/shorts/"):
            return parsed.path.split("/")[2]

        # /live/VIDEO_ID
        if parsed.path.startswith("/live/"):
            return parsed.path.split("/")[2]

    return ""


# ---------------------------
# 댓글 받아오는 함수
# ---------------------------
@st.cache_data(show_spinner=False)
def fetch_all_comments(video_id: str, max_pages: int = 10):
    """해당 video_id의 상위 댓글들을 여러 페이지에 걸쳐 가져오기"""
    comments = []
    url = "https://www.googleapis.com/youtube/v3/commentThreads"

    params = {
        "key": API_KEY,
        "part": "snippet",
        "videoId": video_id,
        "maxResults": 100,
        "order": "relevance",      # 필요에 따라 'time' 으로 바꿔도 됨
        "textFormat": "plainText",
    }

    page_count = 0

    while True:
        resp = requests.get(url, params=params)
        data = resp.json()

        # 에러 처리
        if "error" in data:
            raise RuntimeError(data["error"]["message"])

        for item in data.get("items", []):
            top = item["snippet"]["topLevelComment"]["snippet"]
            comments.append(
                {
                    "author": top.get("authorDisplayName", ""),
                    "text": top.get("textDisplay", ""),
                    "likeCount": top.get("likeCount", 0),
                    "publishedAt": top.get("publishedAt", ""),
                }
            )

        page_count += 1
        if "nextPageToken" not in data or page_count >= max_pages:
            break

        params["pageToken"] = data["nextPageToken"]

    return comments


# ---------------------------
# Streamlit UI
# ---------------------------
st.title("🔍 유튜브 댓글 검색 페이지")

st.markdown(
    """
유튜브 링크와 **검색어**를 입력하면  
그 검색어가 들어간 댓글만 골라서 보여줄게!
"""
)

col1, col2 = st.columns(2)
with col1:
    video_input = st.text_input(
        "🎥 유튜브 링크 또는 영상 ID",
        placeholder="예: https://www.youtube.com/watch?v=XXXXXXXXXXX",
    )
with col2:
    keyword = st.text_input(
        "🔎 검색할 단어나 문장",
        placeholder="예: 재밌어요, 공감, 너무 좋다",
    )

limit = st.slider(
    "가져올 최대 댓글 페이지 수 (1페이지 = 최대 100개 댓글)",
    min_value=1,
    max_value=20,
    value=5,
    help="너무 많이 가져오면 느려질 수 있어요!",
)

if st.button("댓글 검색하기"):
    if not video_input.strip():
        st.warning("먼저 유튜브 링크(또는 영상 ID)를 입력해 주세요.")
    elif not keyword.strip():
        st.warning("검색어를 입력해 주세요.")
    else:
        video_id = extract_video_id(video_input)

        if not video_id:
            st.error("영상 ID를 찾을 수 없어요. 링크를 다시 확인해 주세요.")
        else:
            with st.spinner("유튜브에서 댓글을 가져오는 중입니다... ⏳"):
                try:
                    comments = fetch_all_comments(video_id, max_pages=limit)
                except Exception as e:
                    st.error(f"댓글을 가져오는 중 오류가 발생했어요: {e}")
                    comments = []

            if not comments:
                st.info("가져온 댓글이 없어요.")
            else:
                # 🔎 검색어 필터링 (대소문자 무시)
                key = keyword.lower()
                filtered = [
                    c for c in comments
                    if key in c["text"].lower()
                ]

                if not filtered:
                    st.info(f"'{keyword}' 가(이) 들어간 댓글을 찾지 못했어요.")
                else:
                    # 좋아요 많은 순으로 정렬
                    filtered.sort(key=lambda x: x["likeCount"], reverse=True)

                    st.success(
                        f"✅ '{keyword}' 가(이) 포함된 댓글 {len(filtered)}개를 찾았어요!"
                    )

                    # 상단 요약
                    top_like = filtered[0]["likeCount"]
                    st.write(f"- 가장 좋아요가 많은 댓글의 좋아요 수: **{top_like}개**")

                    # 댓글 리스트 출력
                    for c in filtered:
                        st.markdown("---")
                        st.markdown(f"**작성자**: {c['author']}")
                        st.markdown(
                            f"👍 좋아요: **{c['likeCount']}개**  |  ⏰ {c['publishedAt']}"
                        )
                        st.write(c["text"])
