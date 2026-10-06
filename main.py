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
    "https://raw.githubusercontent.com/teacher188-netizen/"
    "2026-datascience/refs/heads/main/sangok_meals.csv"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    # 중식만 사용
    df = df[df["식사명"] == "중식"].copy()

    # 메뉴를 | 기준으로 분리
    df["메뉴목록"] = df["요리명"].fillna("").apply(
        lambda x: [menu.strip() for menu in x.split("|") if menu.strip()]
    )

    # 괄호와 그 안의 내용 제거
    # 예: 돈까스(소스) → 돈까스
    # 예: 샐러드(요거트(소스)) → 샐러드
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

    # 같은 날 같은 메뉴가 중복으로 기록되어 있다면 한 번만 인정
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

    # 각 메뉴가 나온 날짜 수
    menu_count = {}

    # 메뉴 쌍이 함께 나온 날짜 수
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

        # A → B
        support = count / total_days

        confidence_a_b = count / menu_count[a]
        lift_a_b = confidence_a_b / (menu_count[b] / total_days)

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
        lift_b_a = confidence_b_a / (menu_count[a] / total_days)

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
# 필터
# =========================================================

col1, col2 = st.columns([2, 1])

with col1:
    menu_options = ["전체 메뉴"] + sorted(menu_count.keys())

    selected_menu = st.selectbox(
        "메뉴 선택",
        menu_options
    )

with col2:
    sort_option = st.selectbox(
        "정렬 기준",
        ["향상도", "신뢰도", "동시"]
    )


# =========================================================
# 메뉴 필터
# =========================================================

filtered_rules = rules_df.copy()

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
# 표
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

    # 그래프에서 조건 → 결과 형태로 표시
    top10["규칙"] = (
        top10["조건"] + " → " + top10["결과"]
    )

    # 그래프는 높은 값이 위로 오도록 뒤집기
    top10 = top10.sort_values("향상도", ascending=True)

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
        margin=dict(l=20, r=80, t=20, b=20),
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
    st.info("조건에 맞는 연관규칙이 없습니다.")


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
