import streamlit as st
import pandas as pd
import plotly.express as px

st.title("온도변화를 이용한 중화점 찾기")

# CSV 파일 업로더
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    try:
        # CSV 파일을 pandas DataFrame으로 읽기
        df = pd.read_csv(uploaded_file)

        st.subheader("업로드된 데이터 미리보기")
        st.write(df.head())

        # 데이터프레임 컬럼 선택 (x, y 축)
        columns = df.columns.tolist()
        x_axis = st.selectbox("X축으로 사용할 정보를 선택하세요:", options=columns)
        y_axis = st.selectbox("Y축으로 사용할 정보를 선택하세요:", options=columns)

        if x_axis and y_axis:
            st.subheader(f"{y_axis} vs {x_axis} 그래프")

            # Plotly Express를 이용한 라인 차트
            fig = px.line(df, x=x_axis, y=y_axis, title=f'{y_axis}와 {x_axis}의 관계')
            st.plotly_chart(fig, use_container_width=True)

            # (선택 사항) Scatter Plot
            st.subheader("산점도")
            fig_scatter = px.scatter(df, x=x_axis, y=y_axis, title=f'{y_axis}와 {x_axis}의 산점도')
            st.plotly_chart(fig_scatter, use_container_width=True)

    except Exception as e:
        st.error(f"파일을 읽거나 그래프를 그리는 중 오류가 발생했습니다: {e}")
        st.error("CSV 파일 형식을 확인해주세요.")
