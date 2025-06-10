import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit 앱 제목 설정 및 이모지 추가
st.set_page_config(page_title="과학 실험 데이터 분석기 🔬🧪", layout="centered")
st.title("과학 실험 데이터 분석기 🔬🧪📊")
st.markdown("---")

st.markdown("""
    환영합니다! 👋 이 앱은 여러분의 **과학 실험 데이터**를 시각적으로 분석하는 데 도움을 줄 거예요.
    CSV 파일을 업로드하고, 원하는 변수를 선택해서 멋진 그래프를 만들어 보세요! 🚀
""")

# 1. CSV 파일 업로드
st.header("1. CSV 파일 업로드 📂")
uploaded_file = st.file_uploader("여기에 실험 데이터를 담은 CSV 파일을 업로드해주세요.", type=["csv"])

df = None # 초기화

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("파일 업로드 성공! 🎉 데이터 미리보기를 확인해보세요.")
        st.subheader("데이터 미리보기 (상위 5행) 👀")
        st.dataframe(df.head())

        st.subheader("데이터 컬럼 정보 💡")
        st.write("사용 가능한 컬럼들:")
        st.write(df.columns.tolist())

        # 2. 그래프 그릴 컬럼 선택
        st.header("2. 그래프 그리기 📈")
        st.markdown("어떤 변수들 사이의 관계를 알아보고 싶나요? X축과 Y축에 놓을 컬럼을 선택해주세요.")

        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        if not numeric_cols:
            st.warning("경고: 업로드된 파일에 그래프를 그릴 수 있는 숫자형 데이터 컬럼이 없습니다. 😥")
        else:
            col_x = st.selectbox("X축 (가로축)에 사용할 컬럼을 선택하세요:", options=numeric_cols, key='x_axis')
            col_y = st.selectbox("Y축 (세로축)에 사용할 컬럼을 선택하세요:", options=numeric_cols, key='y_axis')

            if st.button("그래프 그리기! 🎨"):
                if col_x and col_y:
                    st.subheader(f"'{col_x}'와 '{col_y}'의 관계 그래프")

                    # Matplotlib을 이용한 산점도 그리기
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.scatterplot(x=df[col_x], y=df[col_y], ax=ax)
                    ax.set_xlabel(f"{col_x} (단위: 여러분의 상상력)", fontsize=12) # 고등학생 대상 흥미 유발 문구
                    ax.set_ylabel(f"{col_y} (단위: 신비로운 측정치)", fontsize=12) # 고등학생 대상 흥미 유발 문구
                    ax.set_title(f"{col_x} vs {col_y} 산점도 분석 🧐", fontsize=14)
                    ax.grid(True, linestyle='--', alpha=0.7)
                    st.pyplot(fig)
                    st.success("그래프가 성공적으로 그려졌어요! 멋진 발견을 할 수 있기를 바랍니다! ✨")
                    st.markdown("""
                        **그래프 분석 팁:**
                        - 점들이 한 방향으로 모여있나요? (양의 상관관계 또는 음의 상관관계)
                        - 점들이 무작위로 흩어져 있나요? (상관관계가 약하거나 없음)
                        - 혹시 이상한 점(아웃라이어)은 없나요? 😲
                    """)
                else:
                    st.warning("X축과 Y축 컬럼을 모두 선택해주세요. 🧐")

    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다. CSV 파일 형식이 올바른지 확인해주세요: {e} 😞")

st.markdown("---")
st.info("이 앱이 과학 실험 데이터를 이해하는 데 도움이 되었기를 바랍니다! 궁금한 점이 있다면 언제든지 질문하세요! 🧑‍🔬👩‍🔬")
st.markdown("Made with ❤️ by 여러분의 AI 조수")
