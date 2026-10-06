import streamlit as st
import pandas as pd
import itertools
import re
import plotly.express as px


# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="급식 규칙 찾기",
    page_icon="🍱",
    layout="wide"
)

st.title("🍱 급식 규칙 찾기")
st.caption("같은 날 함께 나온 메뉴에서 연관규칙을 찾아봅니다.")


# =========================================================
# 데이터 불러오기
# =========================================================

DATA_URL = (
    "https://raw.githubusercontent.com/teacher188-netizen/2026-datascience/refs/heads/main/ara_meals.csv"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    # 중식만 사용
    df = df[df["식사명"] == "중식"].copy()

    # 메뉴를 | 기준으로 분리
    df["메뉴목록"] = df["요리명"].fillna("").apply(
        lambda x: [
            menu.strip()
            for menu in x.split("|")
            if menu.strip()
        ]
    )

    # 괄호와 그 안의 내용 제거
    def clean_menu(menu):
        previous = None

        while previous != menu:
            previous = menu
            menu = re.sub(r"\([^()]*\)", "", menu)

        return menu.strip()

    df["메뉴목록"] = df["메뉴목록"].apply(
        lambda menus: [
            clean_menu(menu)
            for menu in menus
            if clean_menu(menu)
        ]
    )

    # 같은 날 같은 메뉴가 중복 기록되어 있다면 한 번만 인정
    df["메뉴목록"] = df["메뉴목록"].apply(
        lambda menus: sorted(set(menus))
    )

    return df


df = load_data()


# =========================================================
# 연관규칙 계산
# =========================================================

@st.cache_data
def make_rules(df):

    total_days = len(df)

    # 메뉴별 등장 일수
    menu_count = {}

    # 메뉴 쌍별 동시 등장 일수
    pair_count = {}

    for menus in df["메뉴목록"]:

        # 메뉴별 등장 횟수
        for menu in menus:
            menu_count[menu] = menu_count.get(menu, 0) + 1

        # 같은 날 함께 나온 메뉴 쌍
        for a, b in itertools.combinations(menus, 2):

            pair = tuple(sorted([a, b]))

            pair_count[pair] = pair_count.get(pair, 0) + 1

    rules = []

    for (a, b), count in pair_count.items():

        support = count / total_days

        # A → B
        confidence_a_b = count / menu_count[a]
        lift_a_b = confidence_a_b / (
            menu_count[b] / total_days
        )

        rules.append({
            "조건": a,
            "결과": b,
            "동시": count,
            "지지도": support,
            "신뢰도": confidence_a_b,
            "향상도": lift_a_b
        })

        # B → A
        confidence_b_a = count / menu_count[b]
        lift_b_a = confidence_b_a / (
            menu_count[a] / total_days
        )

        rules.append({
            "조건": b,
            "결과": a,
            "동시": count,
            "지지도": support,
            "신뢰도": confidence_b_a,
            "향상도": lift_b_a
        })

    rules_df = pd.DataFrame(rules)

    return rules_df, menu_count, pair_count


rules_df, menu_count, pair_count = make_rules(df)


# =========================================================
# 상단 요약
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("급식 일수", f"{len(df):,}일")

with col2:
    st.metric("메뉴 종류 수", f"{len(menu_count):,}개")

with col3:
    st.metric("함께 나온 메뉴 쌍", f"{len(pair_count):,}쌍")


st.divider()


# =========================================================
# 연관규칙 필터
# =========================================================

st.subheader("🔎 연관규칙 찾기")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    menu_options = ["전체 메뉴"] + sorted(menu_count.keys())

    selected_menu = st.selectbox(
        "메뉴로 좁혀 보기",
        menu_options
    )

with col2:
    sort_option = st.selectbox(
        "정렬 기준",
        ["향상도", "신뢰도", "동시"]
    )

with col3:
    min_cooccurrence = st.slider(
        "최소 동시 일수",
        min_value=1,
        max_value=10,
        value=1,
        step=1
    )


# =========================================================
# 연관규칙 필터 적용
# =========================================================

filtered_rules = rules_df.copy()

# 최소 동시 일수
filtered_rules = filtered_rules[
    filtered_rules["동시"] >= min_cooccurrence
]

# 메뉴 선택
if selected_menu != "전체 메뉴":
    filtered_rules = filtered_rules[
        (filtered_rules["조건"] == selected_menu) |
        (filtered_rules["결과"] == selected_menu)
    ]


# =========================================================
# 정렬
# =========================================================

if sort_option == "향상도":

    filtered_rules = filtered_rules.sort_values(
        ["향상도", "신뢰도", "동시"],
        ascending=[False, False, False]
    )

elif sort_option == "신뢰도":

    filtered_rules = filtered_rules.sort_values(
        ["신뢰도", "향상도", "동시"],
        ascending=[False, False, False]
    )

else:

    filtered_rules = filtered_rules.sort_values(
        ["동시", "향상도", "신뢰도"],
        ascending=[False, False, False]
    )


# =========================================================
# 남은 규칙 수
# =========================================================

st.write(
    f"조건에 맞는 규칙 **{len(filtered_rules):,}개**"
)


# =========================================================
# 연관규칙 표
# =========================================================

st.subheader("📋 급식 연관규칙")

display_df = filtered_rules.copy()

display_df["지지도"] = display_df["지지도"].map(
    lambda x: f"{x:.1%}"
)

display_df["신뢰도"] = display_df["신뢰도"].map(
    lambda x: f"{x:.1%}"
)

display_df["향상도"] = display_df["향상도"].map(
    lambda x: f"{x:.2f}"
)

st.dataframe(
    display_df[
        ["조건", "결과", "동시", "지지도", "신뢰도", "향상도"]
    ],
    use_container_width=True,
    hide_index=True
)


# =========================================================
# 향상도 상위 10개 그래프
# =========================================================

st.subheader("📊 향상도 상위 10개 규칙")

top10 = filtered_rules.head(10).copy()

if len(top10) > 0:

    top10["규칙"] = (
        top10["조건"] + " → " + top10["결과"]
    )

    top10 = top10.sort_values(
        "향상도",
        ascending=True
    )

    fig = px.bar(
        top10,
        x="향상도",
        y="규칙",
        orientation="h",
        text="향상도",
        labels={
            "향상도": "향상도",
            "규칙": "연관규칙"
        }
    )

    fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig.update_layout(
        height=max(400, len(top10) * 50),
        margin=dict(
            l=20,
            r=80,
            t=20,
            b=20
        ),
        yaxis=dict(
            categoryorder="array",
            categoryarray=top10["규칙"].tolist()
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.info(
        "조건에 맞는 연관규칙이 없습니다."
    )


# =========================================================
# 함께 나온 적 없는 짝
# =========================================================

st.divider()

st.subheader("🚫 함께 나온 적 없는 짝")

st.caption(
    "선택한 메뉴와 한 번도 같은 날 나오지 않았으며, "
    "혼자서는 10일 이상 나온 메뉴를 보여줍니다."
)


# 메뉴 선택
selected_no_pair_menu = st.selectbox(
    "비동시 메뉴 찾기",
    sorted(menu_count.keys()),
    key="no_pair_menu"
)


# 선택한 메뉴가 나온 날짜
selected_menu_days = set()

for _, row in df.iterrows():

    if selected_no_pair_menu in row["메뉴목록"]:
        selected_menu_days.add(row["급식일자"])


# 각 메뉴가 나온 날짜를 구함
menu_dates = {}

for _, row in df.iterrows():

    date = row["급식일자"]

    for menu in row["메뉴목록"]:

        if menu not in menu_dates:
            menu_dates[menu] = set()

        menu_dates[menu].add(date)


# 함께 나온 적 없는 메뉴 찾기
no_pair_results = []

selected_dates = selected_menu_days

for menu, dates in menu_dates.items():

    # 자기 자신은 제외
    if menu == selected_no_pair_menu:
        continue

    # 혼자서 10일 이상 나온 메뉴만
    if len(dates) < 10:
        continue

    # 날짜가 하나라도 겹치면 제외
    if selected_dates.intersection(dates):
        continue

    no_pair_results.append({
        "메뉴": menu,
        "나온 날": len(dates)
    })


# 나온 날이 많은 순으로 정렬
no_pair_df = pd.DataFrame(no_pair_results)

if len(no_pair_df) > 0:

    no_pair_df = no_pair_df.sort_values(
        "나온 날",
        ascending=False
    ).reset_index(drop=True)

    st.write(
        f"**{selected_no_pair_menu}**와 함께 나온 적 없는 메뉴 "
        f"**{len(no_pair_df):,}개**"
    )

    st.dataframe(
        no_pair_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "조건에 맞는 메뉴가 없습니다."
    )


# =========================================================
# 지표 설명
# =========================================================

with st.expander("📖 지표가 무엇인가요?"):

    st.markdown("""
**동시**

두 메뉴가 같은 날 함께 나온 횟수입니다.

**지지도**

전체 급식일 중 두 메뉴가 함께 나온 날의 비율입니다.

> 지지도 = 함께 나온 횟수 ÷ 전체 급식일

**신뢰도**

조건 메뉴가 나온 날에 결과 메뉴도 함께 나왔을 확률입니다.

> 신뢰도(A → B) = A와 B가 함께 나온 횟수 ÷ A가 나온 횟수

**향상도**

A가 나온 날 B도 나오는 비율이, B가 평소 나오는 비율보다 얼마나 높은지를 나타냅니다.

- **1보다 큼** → 두 메뉴가 함께 나오는 경향이 있음
- **1에 가까움** → 특별한 관계가 거의 없음
- **1보다 작음** → 함께 나오는 경향이 낮음
""")
