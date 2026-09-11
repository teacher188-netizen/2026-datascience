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
# ==================================================
# 3. 총 관객 분포 히스토그램
# ==================================================

st.divider()

st.subheader("📈 그래프 3. 영화별 총 관객 분포")

st.markdown(
    """
    영화별 **총 관객 수가 어느 구간에 많이 몰려 있는지** 살펴보세요.
    막대가 높을수록 해당 관객 수 구간에 속하는 영화가 많다는 뜻입니다.
    """
)

# 총 관객 데이터가 있는 영화만 사용
hist_df = df.dropna(subset=["total_audi"]).copy()

fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 수 분포",
    labels={
        "total_audi": "총 관객 수",
        "count": "영화 편수"
    }
)

fig3.update_traces(
    hovertemplate=(
        "관객 수 구간: %{x}<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

fig3.update_layout(
    height=550,
    margin=dict(t=70, b=50, l=30, r=30),
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# ==================================================
# 그래프 3 해석
# ==================================================

# 가장 많이 몰려 있는 관객 수 구간
bin_counts = pd.cut(
    hist_df["total_audi"],
    bins=20,
    include_lowest=True
).value_counts()

most_common_bin = bin_counts.idxmax()

# 총 관객이 가장 많은 영화
top_movie = hist_df.loc[
    hist_df["total_audi"].idxmax()
]

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.info(
    f"대부분의 영화는 **{most_common_bin.left:,.0f}명 ~ "
    f"{most_common_bin.right:,.0f}명** 구간에 몰려 있으며, "
    f"총 관객이 가장 많은 영화는 **{top_movie['movieNm']}**로 "
    f"**{top_movie['total_audi']:,.0f}명**의 관객을 기록했습니다."
)

# ==================================================
# 4. 개봉일 스크린수와 총 관객의 관계
# ==================================================

st.divider()

st.subheader("🔵 그래프 4. 개봉일 스크린수와 총 관객의 관계")

st.markdown(
    """
    개봉 첫날 스크린을 많이 확보한 영화가
    총 관객도 많이 모았는지 살펴보세요.
    """
)

# 필요한 데이터 숫자로 변환
scatter_df = df.copy()

scatter_df["first_scrn"] = pd.to_numeric(
    scatter_df["first_scrn"],
    errors="coerce"
)

scatter_df["total_audi"] = pd.to_numeric(
    scatter_df["total_audi"],
    errors="coerce"
)

# 필요한 값이 없는 영화 제외
scatter_df = scatter_df.dropna(
    subset=["first_scrn", "total_audi", "movieNm", "genre_first"]
)

fig4 = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="genre_first",
    hover_name="movieNm",
    title="개봉일 스크린수와 총 관객의 관계",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객 수",
        "genre_first": "장르"
    }
)

fig4.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린수: %{x:,.0f}개<br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig4.update_layout(
    height=650,
    margin=dict(t=70, b=50, l=30, r=30),
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수",
    legend_title="장르"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)


# ==================================================
# 그래프 4 해석
# ==================================================

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프를 보고 알 수 있는 점을 한 문장으로 써 보세요.",
    placeholder="예: 개봉일 스크린수가 많은 영화일수록 총 관객이 많은 경향이 나타난다.",
    height=100,
    key="graph4_observation"
)
