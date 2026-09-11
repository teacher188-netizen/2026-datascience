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


# --------------------------------------------------
# 1. 시간에 따른 일관객 변화
# --------------------------------------------------
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


# --------------------------------------------------
# 2. 앞으로 추가할 그래프
# --------------------------------------------------
st.header("2. 다음 그래프")

st.write("앞으로 시간 데이터를 활용한 새로운 그래프가 추가될 예정입니다.")

# 여기에 다음 그래프를 추가하세요.


# --------------------------------------------------
# 3. 앞으로 추가할 그래프
# --------------------------------------------------
st.header("3. 다음 그래프")

st.write("새로운 그래프를 추가할 공간입니다.")

# 여기에 다음 그래프를 추가하세요.
