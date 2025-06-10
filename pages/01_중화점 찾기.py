import streamlit as st
import pandas as pd
import plotly.express as px # Plotly Express 임포트

# Streamlit 앱 제목 설정 및 이모지 추가
st.set_page_config(page_title="온도변화를 이용하여 중화점 찾기🔬🧪", layout="centered")
st.title("온도변화를 이용하여 중화점 찾기 🔬🧪📊")
st.markdown("---")

st.markdown("""
    PASCO 무선 센서를 이용하여 얻은 데이터를 이용하여 그래프를 만들어볼게요.
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

                    # Plotly Express를 이용한 산점도 그리기 (툴팁 자동 포함)
                    # hover_name 또는 hover_data를 사용하여 툴팁에 추가 정보를 표시할 수 있습니다.
                    fig = px.scatter(
                        df,
                        x=col_x,
                        y=col_y,
                        title=f"{col_x} vs {col_y} 산점도 분석 🧐",
                        labels={col_x: f"{col_x} (단위: 여러분의 상상력)", col_y: f"{col_y} (단위: 신비로운 측정치)"},
                        hover_data=[col_x, col_y] # 마우스를 올렸을 때 보여줄 데이터 지정
                    )

                    # 그래프 레이아웃 커스터마이징 (선택 사항)
                    fig.update_layout(
                        title_font_size=20,
                        xaxis_title_font_size=14,
                        yaxis_title_font_size=14,
                        height=500 # 그래프 높이 설정
                    )

                    st.plotly_chart(fig, use_container_width=True) # Streamlit에 Plotly 그래프 표시
                    st.success("그래프가 성공적으로 그려졌어요! 마우스를 점 위에 올려 정보를 확인해보세요! ✨")
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
st.markdown("Made with ❤️ by 곰지T")
