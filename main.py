import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="실험 데이터 분석기 🔬🧪", layout="centered")
st.title("온도변화 그래프로 중화점 찾기 📊")

st.markdown("""
    <style>
    body {
        background-color: #f4f9ff;
    }
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1581090700227-1e8e5f9f7f86?ixlib=rb-4.0.3&auto=format&fit=crop&w=1470&q=80');
        background-size: cover;
        background-position: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    환영합니다! 👋 이 앱은 여러분의 **화학 실험 데이터**를 시각적으로 분석하는 데 도움을 줄 거예요.  
    무선 센서로 얻은 CSV 파일을 업로드하고, 원하는 변수를 선택해서 멋진 그래프를 만들어 보세요! 🚀  
    특히, **중화점**을 찾는 데 유용합니다. 🧪
""")

st.markdown("---")
st.header("1. CSV 파일 업로드 📂")
uploaded_file = st.file_uploader("여기에 실험 데이터를 담은 CSV 파일을 업로드해주세요.", type=["csv"])

df = None

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("파일 업로드 성공! 🎉 데이터 미리보기를 확인해보세요.")
        st.markdown("👀 데이터 미리보기 (상위 5행)", unsafe_allow_html=True)
        st.dataframe(df.head())

        st.markdown("💡데이터 컬럼 정보", unsafe_allow_html=True)
        st.write("사용 가능한 컬럼들:")
        st.write(df.columns.tolist())

        st.header("2. 그래프 그리기 📈")
        st.markdown("어떤 변수들 사이의 관계를 알아보고 싶나요? X축과 Y축에 놓을 컬럼을 선택해주세요.")

        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        if not numeric_cols:
            st.warning("경고: 업로드된 파일에 그래프를 그릴 수 있는 숫자형 데이터 컬럼이 없습니다. 😥")
        else:
            col_x = st.selectbox("X축 (가로축)을 설정하세요:", options=numeric_cols, key='x_axis')
            col_y = st.selectbox("Y축 (세로축)을 설정하세요:", options=numeric_cols, key='y_axis')

            graph_options = {
                "산점도 (Scatter Plot)": "scatter",
                "선 그래프 (Line Plot)": "line"
            }
            selected_graph = st.radio("그래프 종류 선택:", list(graph_options.keys()))
            graph_type = graph_options[selected_graph]

            if st.button("그래프 그리기! 🎨"):
                if col_x and col_y:
                    st.subheader(f"'{col_x}'와 '{col_y}'의 관계 그래프")

                    max_y = df[col_y].max()
                    max_rows = df[df[col_y] == max_y]
                    max_x_values = max_rows[col_x].tolist()

                    if graph_type == "scatter":
                        fig = px.scatter(
                            df,
                            x=col_x,
                            y=col_y,
                            title=f"{col_x} vs {col_y} 산점도 분석 🧐",
                            labels={col_x: f"{col_x}", col_y: f"{col_y}"},
                            hover_data=[col_x, col_y]
                        )
                    elif graph_type == "line":
                        fig = px.line(
                            df,
                            x=col_x,
                            y=col_y,
                            title=f"{col_x}에 따른 {col_y}의 변화 추이 📈",
                            labels={col_x: f"{col_x}", col_y: f"{col_y}"},
                            hover_data=[col_x, col_y],
                            markers=True
                        )

                    fig.add_scatter(
                        x=max_x_values,
                        y=[max_y] * len(max_x_values),
                        mode='markers+text',
                        marker=dict(color='red', size=12),
                        text=[f"최대 Y: {max_y}"] * len(max_x_values),
                        textposition="top center",
                        name="최대점"
                    )

                    fig.update_layout(
                        title_font_size=20,
                        xaxis_title_font_size=14,
                        yaxis_title_font_size=14,
                        height=500
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    st.success(f"✅ Y값이 최대({max_y})일 때의 X값 목록은 아래 표와 같습니다:")
                    st.dataframe(max_rows[[col_x, col_y]].reset_index(drop=True))
                else:
                    st.warning("X축과 Y축 컬럼을 모두 선택해주세요. 🧐")

    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다. CSV 파일 형식이 올바른지 확인해주세요: {e} 😞")

st.markdown("---")
st.info("이 앱이 화학 실험 데이터를 이해하는 데 도움이 되었기를 바랍니다! 궁금한 점이 있다면 언제든지 질문하세요! 🧑‍🔬👩‍🔬")
st.markdown("Made by 곰지T ❤️")
