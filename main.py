
import json
from pathlib import Path

import pandas as pd
import streamlit as st


# ==================================================
# 기본 설정
# ==================================================
st.set_page_config(
    page_title="뇌졸중 예측 실습실",
    page_icon="🩺",
    layout="wide"
)

저장파일 = Path("stroke_notes.json")

데이터주소 = (
    "https://raw.githubusercontent.com/"
    "greatsong/modudata/main/data/stroke.csv"
)

출처_기본값 = """출처: 캐글 Stroke Prediction Dataset (게시자 fedesoriano, 2021-01-26 공개)
원본 주소: https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset
라이선스: Data files © Original Authors
게시자가 적은 문구: (Confidential Source) - Use only for educational purposes
이 수업에서는 교육 목적으로만 사용합니다."""


# ==================================================
# 저장된 메모 읽기
# ==================================================
def 적어둔것_읽기():
    try:
        return json.loads(저장파일.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError, OSError):
        return {}


# ==================================================
# 데이터 읽기
# ==================================================
@st.cache_data
def 데이터_읽기():
    return pd.read_csv(데이터주소, encoding="utf-8")


# ==================================================
# 메모 저장
# ==================================================
def 저장하기():
    열설명 = st.session_state.get("열설명_바탕")

    if 열설명 is None:
        return

    # 기본 표에 사용자가 수정한 내용을 반영한다.
    수정내용 = st.session_state.get("열설명표", {})
    편집된_표 = 열설명.copy()

    for 줄, 바뀐것 in 수정내용.get("edited_rows", {}).items():
        줄 = int(줄)

        for 열, 값 in 바뀐것.items():
            편집된_표.loc[줄, 열] = 값

    뜻 = dict(zip(편집된_표["열 이름"], 편집된_표["우리말 뜻"]))

    저장내용 = {
        "우리말 뜻": 뜻,
        "출처": st.session_state.get("출처", 출처_기본값)
    }

    try:
        저장파일.write_text(
            json.dumps(저장내용, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except OSError:
        st.warning("파일에 저장하지 못했습니다. 실행 환경의 파일 쓰기 권한을 확인하세요.")


# ==================================================
# 홈 화면
# ==================================================
def 홈_화면():
    st.title("🩺 뇌졸중 예측 실습실")

    st.write(
        "건강 기록 5,110명분을 읽어 옵니다. "
        "왼쪽 메뉴에서 페이지를 넘기며 데이터를 탐색하고, "
        "모델을 만들고, 채점합니다."
    )

    try:
        df = 데이터_읽기()
    except Exception as 오류:
        st.error("데이터를 읽어오지 못했습니다.")
        st.code(str(오류))
        st.info("인터넷 연결과 CSV 주소를 확인하세요.")
        return

    적어둔것 = 적어둔것_읽기()

    # 데이터 요약
    칸1, 칸2, 칸3, 칸4 = st.columns(4)

    칸1.metric("전체 사람 수", f"{len(df):,}명")
    칸2.metric("열 개수", f"{df.shape[1]}개")

    if "stroke" in df.columns:
        칸3.metric("뇌졸중을 겪은 사람", f"{int(df['stroke'].sum()):,}명")
        칸4.metric("그 비율", f"{df['stroke'].mean() * 100:.2f}%")
    else:
        칸3.metric("뇌졸중 관련 열", "없음")
        칸4.metric("그 비율", "계산 불가")

    # 열 설명
    st.subheader("열마다 무엇이 들어 있는가")

    st.caption(
        "우리말 뜻 칸은 직접 채워 넣으세요. "
        "적은 내용은 실행 환경의 파일에 저장됩니다."
    )

    def 값의_종류(열):
        칸 = df[열].dropna()

        if 칸.empty:
            return "값 없음"

        if pd.api.types.is_numeric_dtype(칸) and 칸.nunique() > 2:
            return f"숫자 {칸.min():g} ~ {칸.max():g}"

        값들 = sorted(칸.astype(str).unique())
        return f"{len(값들)}가지 · " + " · ".join(값들)

    # 표의 바탕은 최초 한 번만 생성
    if "열설명_바탕" not in st.session_state:
        적어둔뜻 = 적어둔것.get("우리말 뜻", {})

        st.session_state["열설명_바탕"] = pd.DataFrame({
            "열 이름": df.columns.tolist(),
            "우리말 뜻": [
                적어둔뜻.get(열, "") for 열 in df.columns
            ],
            "값의 종류": [
                값의_종류(열) for 열 in df.columns
            ],
            "빈 값 개수": [
                int(df[열].isna().sum()) for 열 in df.columns
            ],
        })

    열설명 = st.session_state["열설명_바탕"]

    st.data_editor(
        열설명,
        width="stretch",
        hide_index=True,
        disabled=["열 이름", "값의 종류", "빈 값 개수"],
        num_rows="fixed",
        key="열설명표",
        on_change=저장하기,
    )

    st.caption(
        "우리말 뜻 칸을 수정하면 저장을 시도합니다. "
        "저장 파일은 배포 환경에 따라 초기화될 수 있습니다."
    )

    # 원본 데이터 미리 보기
    st.subheader("앞 다섯 줄 그대로 보기")
    st.dataframe(df.head(5), width="stretch", hide_index=True)

    # 출처
    st.subheader("이 데이터는 어디서 왔는가")

    if "출처" not in st.session_state:
        st.session_state["출처"] = 적어둔것.get(
            "출처", 출처_기본값
        )

    st.text_area(
        "교재를 보고 여기에 적습니다",
        height=170,
        key="출처",
        on_change=저장하기,
    )

    st.caption(
        "데이터 게시자는 원본 데이터의 출처를 명확하게 밝히지 않았으며, "
        "교육 목적으로만 사용하라는 문구를 적었습니다. "
        "이 데이터에서 얻은 결과를 실제 의학적 판단에 사용해서는 안 됩니다."
    )


# ==================================================
# 페이지 이동
# ==================================================
페이지 = st.navigation([
    st.Page(
        홈_화면,
        title="실습실 홈",
        icon="🏠",
        default=True
    ),
    st.Page(
        "pages/1_탐색.py",
        title="1. 데이터 탐색",
        icon="🔎"
    ),
    st.Page(
        "pages/2_분류_모델.py",
        title="2. 분류 모델",
        icon="🧠"
    ),
    st.Page(
        "pages/3_채점표.py",
        title="3. 채점표",
        icon="📋"
    ),
    st.Page(
        "pages/4_전처리.py",
        title="4. 전처리",
        icon="📋"
    ),
    st.Page(
        "pages/5_내가_만든_모델_소개.py",
        title="5_내가_만든_모델_소개",
        icon="📝"
    ),
])

페이지.run()
