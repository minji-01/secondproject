import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io # BytesIO를 위해 추가

# 페이지 설정
st.set_page_config(
    page_title="재미있는 과학 실험 데이터 분석! 🧪🔬🧬",
    page_icon="📈"
)

st.title("재미있는 과학 실험 데이터 분석기! 🚀")
st.write("너의 실험 데이터를 시각화하고 숨겨진 패턴을 찾아봐! ✨")

# 파일 업로더
st.header("1. 실험 데이터 CSV 파일 업로드! 📤")
st.write("여기에 너의 실험 결과가 담긴 CSV 파일을 끌어다 놓거나 찾아봐. (예: `my_experiment_results.csv`)")
uploaded_file = st.file_uploader("CSV 파일을 선택하세요", type=["csv"])

df = None # df 초기화

if uploaded_file is not None:
    try:
        # 인코딩 문제 해결을 위해 utf-8, euc-kr 순으로 시도
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        except UnicodeDecodeError:
            uploaded_file.seek(0) # 파일 포인터를 다시 처음으로
            df = pd.read_csv(uploaded_file, encoding='euc-kr')

        st.success("파일 업로드 성공! 🎉 데이터를 확인해볼까? 👇")
        st.dataframe(df)

        st.header("2. 어떤 그래프를 그려볼까? 🤔")
        st.write("네 데이터를 가장 잘 보여줄 그래프 유형을 선택해봐!")

        # 그래프 유형 선택
        chart_type = st.selectbox(
            "그래프 유형 선택",
            ("선 그래프 (Line Chart) 📈", "막대 그래프 (Bar Chart) 📊", "산점도 (Scatter Plot) ⚛️", "히스토그램 (Histogram) 🧪"),
            index=0
        )

        st.header("3. 그래프 설정! 🛠️")
        st.write("그래프에 어떤 데이터를 표시할지 골라보자!")

        # 숫자형 컬럼만 선택 가능하도록 필터링
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        string_columns = df.select_dtypes(include=['object']).columns.tolist() # 문자열 컬럼도 필요할 수 있으므로 추가

        if not numeric_columns:
            st.warning("경고: 그래프를 그릴 수 있는 숫자형 데이터가 없습니다. CSV 파일을 확인해주세요. 🧐")
        else:
            x_axis = st.selectbox("X축 데이터 선택 (주로 시간, 카테고리 등) ➡️", df.columns.tolist())
            y_axis = st.selectbox("Y축 데이터 선택 (측정값) ⬆️", numeric_columns)

            st.header("4. 결과 확인! 🔬")

            fig, ax = plt.subplots(figsize=(10, 6))

            if "선 그래프" in chart_type:
                st.subheader("선 그래프: 시간/순서에 따른 변화 보기 📊")
                sns.lineplot(x=df[x_axis], y=df[y_axis], ax=ax, marker='o')
                ax.set_title(f'{x_axis}에 따른 {y_axis} 변화 (선 그래프) 📈')
                ax.set_xlabel(f'{x_axis} (측정 조건) 📏')
                ax.set_ylabel(f'{y_axis} (측정 결과) 🎯')
                st.pyplot(fig)
                st.write("💡 **팁:** 선 그래프는 시간이나 순서에 따라 데이터가 어떻게 변하는지 볼 때 유용해! 예를 들어, 온도 변화나 반응 속도 변화를 볼 때 최고야! 🌡️⚡")

            elif "막대 그래프" in chart_type:
                st.subheader("막대 그래프: 카테고리별 비교하기 📊")
                # X축이 범주형일 때 막대 그래프가 적합
                if x_axis in string_columns:
                    sns.barplot(x=df[x_axis], y=df[y_axis], ax=ax)
                    ax.set_title(f'{x_axis}별 {y_axis} 비교 (막대 그래프) 📊')
                    ax.set_xlabel(f'{x_axis} (실험 종류) 🧪')
                    ax.set_ylabel(f'{y_axis} (평균값) ⚖️')
                    st.pyplot(fig)
                    st.write("💡 **팁:** 막대 그래프는 서로 다른 카테고리(예: 다른 실험 조건, 다른 시료) 간의 값을 비교할 때 아주 좋아! 어떤 조건에서 결과가 더 좋았는지 한눈에 알 수 있어! 🏆")
                else:
                    st.warning("경고: 막대 그래프는 주로 범주형(문자열) X축 데이터에 적합합니다. 다른 그래프 유형을 선택하거나 X축 데이터를 확인해주세요. 🧐")
                    st.pyplot(fig) # 빈 그래프라도 표시
                    st.write("🚨 **팁:** 현재 선택된 X축은 숫자형 데이터 같아! 막대 그래프는 '학년', '반', '실험 조건' 같은 글자로 된 데이터와 잘 어울려! 📝")


            elif "산점도" in chart_type:
                st.subheader("산점도: 두 변수 사이의 관계 찾기 ⚛️")
                # 산점도는 두 축 모두 숫자형일 때 유용
                if x_axis in numeric_columns and y_axis in numeric_columns:
                    sns.scatterplot(x=df[x_axis], y=df[y_axis], ax=ax)
                    ax.set_title(f'{x_axis}와 {y_axis}의 관계 (산점도) ⚛️')
                    ax.set_xlabel(f'{x_axis} (독립 변수) ➡️')
                    ax.set_ylabel(f'{y_axis} (종속 변수) ⬆️')
                    st.pyplot(fig)
                    st.write("💡 **팁:** 산점도는 두 가지 숫자 데이터 사이에 어떤 관계(선형, 비선형 등)가 있는지 파악할 때 사용해! 예를 들어, '실험 시간'과 '생성물 양' 사이의 관계를 볼 수 있어! 🔗")
                else:
                    st.warning("경고: 산점도는 X축과 Y축 모두 숫자형 데이터에 적합합니다. 데이터를 확인해주세요. 🧐")
                    st.pyplot(fig) # 빈 그래프라도 표시
                    st.write("🚨 **팁:** 산점도는 숫자와 숫자의 관계를 보여줄 때 제일 멋져! 예를 들어 '온도'와 '반응 속도'처럼 말이야! 🌡️💨")


            elif "히스토그램" in chart_type:
                st.subheader("히스토그램: 데이터의 분포 알아보기 🧪")
                sns.histplot(df[y_axis], bins=10, kde=True, ax=ax)
                ax.set_title(f'{y_axis}의 분포 (히스토그램) 🧪')
                ax.set_xlabel(f'{y_axis} (측정값 범위) 📊')
                ax.set_ylabel("빈도 (횟수) 🔢")
                st.pyplot(fig)
                st.write("💡 **팁:** 히스토그램은 네 데이터가 어떤 값들에 가장 많이 모여 있는지, 즉 데이터의 '모양'을 보여줘! 예를 들어, 실험 오차나 측정값의 편차를 확인할 때 유용해! 📉📈")

            st.markdown("---")
            st.markdown("멋진 분석이었어! 더 궁금한 게 있다면 언제든지 물어봐! 😎")
            st.markdown("© 2025 과학 탐구 랩 💡")

    except Exception as e:
        st.error(f"오류 발생! 😱 CSV 파일을 제대로 읽을 수 없어요. 형식을 확인해주세요. 오류 메시지: {e}")
        st.info("💡 **팁:** CSV 파일은 쉼표(,)로 데이터가 구분되어 있고, 첫 번째 줄에 헤더(열 이름)가 있는지 확인해주세요!")

else:
    st.info("아직 CSV 파일이 업로드되지 않았어요. 파일을 업로드하면 멋진 그래프를 볼 수 있어! 👆")
