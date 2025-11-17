import streamlit as st

st.set_page_config(
    page_title="방배중 YouTube Learning Tools",
    page_icon="🎬",
)

# -----------------------------
# 상단 타이틀 & 소개
# -----------------------------
st.markdown(
    """
    <div style="text-align:center;">
        <h1>🎬 YouTube 기반 교육 도구 모음</h1>
        <h3>방배중학교 기술교사 <strong>안정연</strong>이 제작한 학습 지원 사이트</h3>
        <p style="color:#666; font-size:17px;">
            유튜브를 활용한 다양한 수업 활동을 더 쉽게!  
            영상 분석 · 댓글 분석 · 썸네일 추출 · 외부 콘텐츠 활용 등  
            교실에서 바로 쓰기 좋은 도구들을 한곳에 모았습니다.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# -----------------------------
# 기능 소개 카드 UI
# -----------------------------

st.subheader("✨ 제공 기능 안내")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div style="text-align:center;">
            <span style="font-size:50px;">💬</span>
            <h4>베스트 댓글 분석기</h4>
            <p style="color:#555;">
                좋아요 순으로 댓글을 추출하여  
                학생 의견 분석이나 토론 수업에 활용 가능
            </p>
        </div>
        """, unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div style="text-align:center;">
            <span style="font-size:50px;">🔍</span>
            <h4>댓글 검색·필터링</h4>
            <p style="color:#555;">
                특정 키워드가 포함된 댓글만 모아  
                정성 분석 · 감정 분석 활동에 활용
            </p>
        </div>
        """, unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div style="text-align:center;">
            <span style="font-size:50px;">🖼️</span>
            <h4>YouTube 썸네일 추출기</h4>
            <p style="color:#555;">
                영상 썸네일 이미지를 즉시 다운받아  
                보고서·과제용 포스터 제작에 활용 가능
            </p>
        </div>
        """, unsafe_allow_html=True
    )

st.markdown("---")

# -----------------------------
# 사용 안내 및 출처 문구
# -----------------------------

st.markdown(
    """
    <div style="text-align:center; margin-top:20px;">
        <h4>📚 방배중학교 기술 수업에서 바로 사용 가능</h4>
        <p style="color:#666; font-size:16px; line-height:1.5;">
            이 사이트는 방배중학교 <strong>안정연 교사</strong>가  
            수업 혁신 및 디지털 기반 학습을 돕기 위해 직접 개발하였습니다.<br>
            학생들이 유튜브를 단순 시청용이 아닌,  
            분석·해석·창작 중심의 도구로 활용하도록 돕는 것을 목표로 합니다.
        </p>
        <p style="font-size:14px; color:#aaa; margin-top:10px;">
            © 2025. Bangbae Middle School · Teacher Ahn Jungyeon. All rights reserved.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
