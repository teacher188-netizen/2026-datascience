import streamlit as st
import pandas as pd
import plotly.express as px


# ==================================================
# 기본 설정
# ==================================================
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


# ==================================================
# 데이터 불러오기
# ==================================================
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜를 진짜 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d"
    )

    return df


df = load_data()


# ==================================================
# 1. 영화별 날짜에 따른 일관객 변화
# ==================================================
st.header("1. 영화별 날짜에 따른 일관객 변화")

movie_list = sorted(df["영화명"].dropna().unique())

selected_movie = st.selectbox(
    "영화를 선택하세요.",
    movie_list
)

movie_df = (
    df[df["영화명"] == selected_movie]
    .sort_values("날짜")
)

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"{selected_movie}의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수"
    }
)

fig1.update_traces(
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}<br>"
        "관객수: %{y:,}명"
        "<extra></extra>"
    )
)

fig1.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 수"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.info(
    "💡 이 그래프로 알 수 있는 것: "
    "선택한 영화의 날짜별 관객 수가 어떻게 변했는지 확인할 수 있습니다."
)


# ==================================================
# 2. 일관객 합계가 가장 큰 영화 5편
# ==================================================
st.header("2. 일관객 합계가 가장 큰 영화 5편")

st.write(
    "전체 기간 동안 일관객 합계가 가장 큰 5편을 골라 "
    "날짜별 관객 수 변화를 비교합니다."
)

top5_movies = (
    df.groupby("영화명")["일관객"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

top5_df = (
    df[df["영화명"].isin(top5_movies)]
    .sort_values(["날짜", "영화명"])
)

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계 상위 5편의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
        "영화명": "영화"
    }
)

fig2.update_traces(
    hovertemplate=(
        "영화: %{fullData.name}<br>"
        "날짜: %{x|%Y-%m-%d}<br>"
        "관객수: %{y:,}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 수",
    legend_title="영화"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.info(
    "💡 이 그래프로 알 수 있는 것: "
    "기간 동안 가장 많은 관객을 모은 영화 5편의 흥행 추이를 날짜별로 비교할 수 있습니다."
)


# ==================================================
# 3. 날짜별 전체 10위권 일관객 합계
# ==================================================
st.header("3. 날짜별 10위권 일관객 합계")

st.write(
    "매일 박스오피스 10위권 영화의 일관객을 모두 합산하여 "
    "전체적인 영화 관람 규모의 변화를 확인합니다."
)

daily_total = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)

# 일관객 합계가 가장 큰 3일
top3_days = (
    daily_total
    .nlargest(3, "일관객")
    .sort_values("날짜")
)

fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="날짜별 10위권 일관객 합계",
    labels={
        "날짜": "날짜",
        "일관객": "10위권 일관객 합계"
    }
)

fig3.update_traces(
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}<br>"
        "10위권 일관객 합계: %{y:,}명"
        "<extra></extra>"
    )
)

fig3.add_scatter(
    x=top3_days["날짜"],
    y=top3_days["일관객"],
    mode="markers+text",
    text=[
        date.strftime("%Y-%m-%d")
        for date in top3_days["날짜"]
    ],
    textposition="top center",
    marker=dict(
        size=10,
        color="red"
    ),
    name="관객 수 TOP 3",
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}<br>"
        "10위권 일관객 합계: %{y:,}명"
        "<extra></extra>"
    )
)

fig3.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="10위권 일관객 합계",
    showlegend=False
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.info(
    "💡 이 그래프로 알 수 있는 것: "
    "날짜별 전체적인 영화 관람 규모와 관객이 가장 많이 몰린 날을 확인할 수 있습니다."
)


# ==================================================
# 4. 영화별 누적 일관객 TOP 10
# ==================================================
st.header("4. 영화별 누적 일관객 TOP 10")

st.write(
    "이 기간 동안 일관객을 모두 더해 관객 수가 가장 많은 "
    "영화 10편을 비교합니다."
)

# 영화별 일관객 합계 + 10위권 등장 일수 계산
movie_summary = (
    df.groupby("영화명")
    .agg(
        일관객합계=("일관객", "sum"),
        등장일수=("날짜", "nunique")
    )
    .reset_index()
)

# 일관객 합계가 많은 순으로 TOP 10
top10_movies = (
    movie_summary
    .sort_values("일관객합계", ascending=False)
    .head(10)
    .sort_values("일관객합계", ascending=True)
)

fig4 = px.bar(
    top10_movies,
    x="일관객합계",
    y="영화명",
    orientation="h",
    title="영화별 일관객 합계 TOP 10",
    labels={
        "일관객합계": "일관객 합계",
        "영화명": "영화"
    }
)

fig4.update_traces(
    hovertemplate=(
        "영화: %{y}<br>"
        "일관객 합계: %{x:,}명<br>"
        "10위권 등장일수: %{customdata}일"
        "<extra></extra>"
    ),
    customdata=top10_movies["등장일수"]
)

fig4.update_layout(
    xaxis_title="일관객 합계",
    yaxis_title="영화",
    yaxis=dict(
        categoryorder="total ascending"
    )
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.info(
    "💡 이 그래프로 알 수 있는 것: "
    "기간 동안 가장 많은 관객을 모은 영화와 그 영화가 10위권에 등장한 날수를 비교할 수 있습니다."
)


# ==================================================
# 앞으로 추가할 그래프
# ==================================================
st.header("5. 다음 그래프")

st.write("앞으로 새로운 그래프를 이곳에 계속 추가할 수 있습니다.")
