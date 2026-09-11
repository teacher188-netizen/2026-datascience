import streamlit as st
import pandas as pd
import plotly.express as px


# ==================================================
# 기본 설정
# ==================================================
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)


# ==================================================
# 제목
# ==================================================
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")

st.markdown(
    """
    1년간 박스오피스 10위권에 든 영화 가운데
    이 기간에 개봉한 **216편의 영화 데이터**를 살펴봅니다.
    """
)


# ==================================================
# 데이터 불러오기
# ==================================================
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/"
    "kobis_movies.csv"
)

df = pd.read_csv(DATA_URL)


# ==================================================
# 데이터 전처리
# ==================================================

# 장르가 여러 개 적혀 있는 경우 첫 번째 장르만 사용
df["genre_first"] = (
    df["genre"]
    .fillna("미상")
    .astype(str)
    .str.split("|")
    .str[0]
    .str.strip()
)

# 빈 값 처리
df["genre_first"] = df["genre_first"].replace("", "미상")


# ==================================================
# 1. 장르별 영화 편수
# ==================================================

st.divider()

st.subheader("📊 그래프 1. 장르별 영화 편수")

genre_count = (
    df["genre_first"]
    .value_counts()
    .reset_index()
)

genre_count.columns = ["장르", "영화 편수"]

total_movies = genre_count["영화 편수"].sum()

fig = px.pie(
    genre_count,
    names="장르",
    values="영화 편수",
    hole=0.5,
    title="장르별 영화 편수"
)

fig.update_traces(
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig.update_layout(
    height=550,
    margin=dict(t=70, b=30, l=30, r=30),
    legend_title="장르"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==================================================
# 그래프로 알 수 있는 것
# ==================================================

st.markdown("---")

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프를 보고 알 수 있는 점을 한 문장으로 써 보세요.",
    placeholder="예: 이 기간에는 ○○ 장르의 영화가 가장 많았다.",
    height=100,
    key="graph1_observation"
)
