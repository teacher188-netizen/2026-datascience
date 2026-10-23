# main.py — 서울의 100년 기온
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="서울의 100년 기온", layout="wide")
st.title("서울의 100년 기온")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    df["날짜"] = pd.to_datetime(df["날짜"])
    df["연도"] = df["날짜"].dt.year
    return df


df = load_data()

st.header("연평균기온의 흐름")
yearly = df.groupby("연도", as_index=False)["평균기온"].mean()
fig = px.line(yearly, x="연도", y="평균기온", markers=True)
st.plotly_chart(fig, width="stretch")

# 일별 평균기온의 분포
st.header("일별 평균기온은 어느 구간에 몰려 있나")
fig2 = px.histogram(df, x="평균기온", nbins=50)
st.plotly_chart(fig2, width="stretch")
