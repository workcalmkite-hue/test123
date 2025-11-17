import streamlit as st
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs

# -----------------------------
# YouTube 영상 ID 추출 함수 (네가 쓰던 거 그대로 재사용)
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
# YouTube 전체 댓글 불러오기
# -----------------------------
def get_all_comments(api_key, video_id, max_pages=5):
    youtube = build('youtube', 'v3', developerKey=api_key)

    comments = []
    page_token = None
    page_count = 0

    while True:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,           # 한 페이지 최대 100개
            order="relevance",        # 관련도 순 (원하면 'time'도 가능)
            pageToken=page_token,
            textFormat="plainText"
        )
        response = request.execute()

        for item in response.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "author": snippet.get("authorDisplayName", "Unknown"),
                "text": snippet.get("textDisplay", ""),
                "likes": snippet.get("likeCount", 0),
                "published_at": snippet.get("publishedAt", "")
            })

        page_count += 1
        page_token = response.get("nextPageToken")

        if not page_token or page_count >= max_pages:
            break

    return comments

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🔍 YouTube 댓글 검색기")
st.write("유튜브 링크와 **검색어**를 입력하면, 해당 단어가 들어간 댓글만 추출해서 보여줍니다.")

# ✅ 기존 베스트 댓글 페이지와 동일하게 secrets 사용!
api_key = st.secrets.get("YT_API_KEY")

youtube_url = st.text_input("YouTube 영상 URL 입력")
keyword = st.text_input("댓글에서 찾을 단어나 문장 입력 (예: 재밌어요, 공감, 욕, 칭찬 등)")

# 몇 페이지까지 불러올지 (1페이지 = 최대 100개 댓글)
max_pages = st.slider(
    "댓글을 얼마나 많이 가져올까요? (페이지 수, 1페이지 = 최대 100개)",
    min_value=1,
    max_value=10,
    value=3,
    step=1
)

if st.button("댓글 검색하기"):
    if not api_key:
        st.error("API 키가 설정되어 있지 않습니다. Streamlit Secrets에 YT_API_KEY를 추가하세요.")
    else:
        video_id = extract_video_id(youtube_url)
        if not video_id:
            st.error("유효한 YouTube URL이 아닙니다.")
        elif not keyword.strip():
            st.warning("검색어를 입력해 주세요.")
        else:
            try:
                with st.spinner("댓글을 불러오는 중입니다..."):
                    comments = get_all_comments(api_key, video_id, max_pages=max_pages)

                if not comments:
                    st.warning("댓글을 찾을 수 없습니다.")
                else:
                    # 🔎 검색어 포함된 댓글만 필터
                    key_lower = keyword.lower()
                    filtered = [
                        c for c in comments
                        if key_lower in c["text"].lower()
                    ]

                    if not filtered:
                        st.info(f"'{keyword}' 가(이) 포함된 댓글이 없습니다.")
                    else:
                        # 좋아요 순으로 정렬
                        filtered.sort(key=lambda x: x["likes"], reverse=True)

                        st.success(f"'{keyword}' 가(이) 들어간 댓글 {len(filtered)}개를 찾았습니다!")

                        for idx, c in enumerate(filtered, 1):
                            st.markdown("---")
                            st.markdown(f"### 댓글 {idx}")
                            st.write(f"**작성자:** {c['author']}")
                            st.write(f"**좋아요:** {c['likes']}")
                            st.write(f"**작성 시각:** {c['published_at']}")
                            st.write(c["text"])

            except Exception as e:
                st.error(f"에러 발생: {e}")
