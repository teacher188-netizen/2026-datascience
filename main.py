import streamlit as st
import pandas as pd
import plotly.express as px


# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.write("365일간의 일별 박스오피스 데이터를 시간의 흐름에 따라 살펴봅니다.")


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜: YYYYMMDD → 실제 날짜
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d"
    )

    return df


df = load_data()


# ==================================================
# 1. 시간에 따른 일관객 변화
# ==================================================
st.header("1. 시간에 따른 일관객 변화")

st.write(
    "영화를 하나 선택하면 해당 영화의 날짜별 일관객 변화를 확인할 수 있습니다."
)

movie_list = sorted(df["영화명"].dropna().unique())

selected_movie = st.selectbox(
    "영화를 선택하세요",
    movie_list
)

movie_df = (
    df[df["영화명"] == selected_movie]
    .sort_values("날짜")
)


fig = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"「{selected_movie}」의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수"
    }
)

fig.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>관객수: %{y:,}명<extra></extra>"
)

fig.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 수"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.info(
    "💡 이 그래프로 알 수 있는 것: "
    "시간이 흐르면서 이 영화의 하루 관객 수가 어떻게 변화했는지 알 수 있습니다."
)


# ==================================================
# 2. 일관객 합계가 가장 큰 영화 5편의 변화
# ==================================================
st.header("2. 일관객 합계가 가장 큰 영화 5편")

st.write(
    "전체 기간 동안 일관객 합계가 가장 큰 5편을 골라 "
    "날짜별 관객 수 변화를 비교합니다."
)


# 영화별 전체 기간 일관객 합계 계산
top5_movies = (
    df.groupby("영화명")["일관객"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)


# 상위 5편의 날짜별 데이터만 추출
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
# 3. 앞으로 추가할 그래프
# ==================================================
st.header("3. 다음 그래프")

st.write("새로운 그래프를 추가할 공간입니다.")

# 여기에 다음 그래프를 추가하세요.
