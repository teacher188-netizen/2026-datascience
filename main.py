```python
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

df["genre_first"] = df["genre_first"].replace("", "미상")

# 총 관객을 숫자로 변환
df["total_audi"] = pd.to_numeric(
    df["total_audi"],
    errors="coerce"
)

# 영화명 결측치 처리
df["movieNm"] = df["movieNm"].fillna("영화명 미상")


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

fig1 = px.pie(
    genre_count,
    names="장르",
    values="영화 편수",
    hole=0.5,
    title="장르별 영화 편수"
)

fig1.update_traces(
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig1.update_layout(
    height=550,
    margin=dict(t=70, b=30, l=30, r=30),
    legend_title="장르"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# ==================================================
# 그래프 1 해석
# ==================================================

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프를 보고 알 수 있는 점을 한 문장으로 써 보세요.",
    placeholder="예: 이 기간에는 ○○ 장르의 영화가 가장 많았다.",
    height=100,
    key="graph1_observation"
)


# ==================================================
# 2. 장르별 영화와 총 관객
# ==================================================

st.divider()

st.subheader("🌳 그래프 2. 장르별 영화와 총 관객")

st.markdown(
    """
    **사각형의 크기가 클수록 총 관객이 많은 영화입니다.**
    장르 안에서 어떤 영화가 많은 관객을 모았는지 살펴보세요.
    """
)

treemap_df = df[
    ["genre_first", "movieNm", "total_audi"]
].dropna(subset=["total_audi"]).copy()

fig2 = px.treemap(
    treemap_df,
    path=["genre_first", "movieNm"],
    values="total_audi",
    title="장르별 영화 총 관객"
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    height=700,
    margin=dict(t=70, b=30, l=20, r=20)
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# ==================================================
# 그래프 2 해석
# ==================================================

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프를 보고 알 수 있는 점을 한 문장으로 써 보세요.",
    placeholder="예: ○○ 장르에서는 △△ 영화의 총 관객이 가장 많았다.",
    height=100,
    key="graph2_observation"
)
```
