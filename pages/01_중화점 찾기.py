import streamlit as st
import pandas as pd
import plotly.express as px # Plotly Express 임포트

# Streamlit 앱 제목 설정 및 이모지 추가
st.set_page_config(page_title="과학 실험 데이터 분석기 🔬🧪", layout="centered")
st.title("온도변화 그래프로 중화점 찾기 📊")
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

            # --- 그래프 종류 선택 추가 ---
            st.subheader("어떤 종류의 그래프로 볼까요? 🤔")
            graph_type = st.radio(
                "그래프 종류 선택:",
                ("산점도 (Scatter Plot) 🟣", "선 그래프 (Line Plot) 〰️")
            )
            # --- 그래프 종류 선택 추가 끝 ---

            if st.button("그래프 그리기! 🎨"):
                if col_x and col_y:
                    st.subheader(f"'{col_x}'와 '{col_y}'의 관계 그래프")

                    if graph_type == "산점도 (Scatter Plot) 🟣":
                        fig = px.scatter(
                            df,
                            x=col_x,
                            y=col_y,
                            title=f"{col_x} vs {col_y} 산점도 분석 🧐",
                            labels={col_x: f"{col_x}", col_y: f"{col_y}"},
                            hover_data=[col_x, col_y]
                        )
                    elif graph_type == "선 그래프 (Line Plot) 〰️":
                        # 선 그래프는 일반적으로 x축이 정렬된 순서대로 연결됩니다.
                        # 필요하다면 df.sort_values(by=col_x, inplace=True)를 사용해 정렬할 수 있습니다.
                        fig = px.line(
                            df,
                            x=col_x,
                            y=col_y,
                            title=f"{col_x}에 따른 {col_y}의 변화 추이 📈", # 제목 변경
                            labels={col_x: f"{col_x} (단위: 시간/횟수)", col_y: f"{col_y} (단위: 측정값)"}, # 레이블 변경
                            hover_data=[col_x, col_y],
                            markers=True # 각 데이터 포인트에 마커 표시
                        )

                    # 그래프 레이아웃 커스터마이징 (선택 사항)
                    fig.update_layout(
                        title_font_size=20,
                        xaxis_title_font_size=14,
                        yaxis_title_font_size=14,
                        height=500
                    )

                    st.plotly_chart(fig, use_container_width=True)
                    st.success("그래프가 성공적으로 그려졌어요! 마우스를 점 위에 올려 정보를 확인해보세요! ✨")
                
                else:
                    st.warning("X축과 Y축 컬럼을 모두 선택해주세요. 🧐")

    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다. CSV 파일 형식이 올바른지 확인해주세요: {e} 😞")

st.markdown("---")
st.info("이 앱이 과학 실험 데이터를 이해하는 데 도움이 되었기를 바랍니다! 궁금한 점이 있다면 언제든지 질문하세요! 🧑‍🔬👩‍🔬")
st.markdown("Made with ❤️ by 곰지T")
