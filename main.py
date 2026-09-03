import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="서울 100년 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

# 제목
st.title("🌡️ 서울의 100년 기온 변화")
st.write("서울의 기상 데이터를 이용해 연평균 기온이 어떻게 변해 왔는지 살펴봅니다.")

# 데이터 주소
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜 열을 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    # 평균기온을 숫자로 변환
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    # 결측값 제거
    df = df.dropna(subset=["날짜", "평균기온"])

    return df


# 데이터 불러오기
df = load_data()

# 연도 추출
df["연도"] = df["날짜"].dt.year

# 연평균 기온 계산
annual_temp = (
    df.groupby("연도")["평균기온"]
    .mean()
    .reset_index()
)

annual_temp.columns = ["연도", "연평균기온"]

# 데이터 기간
start_year = annual_temp["연도"].min()
end_year = annual_temp["연도"].max()

st.subheader(f"📈 {start_year}년부터 {end_year}년까지의 연평균 기온")

# 그래프용 데이터
chart_data = annual_temp.set_index("연도")

# Streamlit 기본 라인 차트
st.line_chart(
    chart_data,
    y="연평균기온",
    x_label="연도",
    y_label="연평균 기온 (℃)"
)

# 간단한 설명
st.info(
    "그래프의 가로축은 연도, 세로축은 해당 연도의 평균기온을 나타냅니다. "
    "전체적인 그래프의 흐름을 통해 장기간의 기온 변화를 확인할 수 있습니다."
)

# 데이터 확인
with st.expander("📋 연도별 연평균 기온 데이터 보기"):
    st.dataframe(
        annual_temp,
        use_container_width=True,
        hide_index=True
    )
