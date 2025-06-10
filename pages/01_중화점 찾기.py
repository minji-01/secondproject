import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.signal import find_peaks
import plotly.graph_objects as go

st.set_page_config(layout="wide") # 페이지 전체 너비를 사용합니다.

st.title("CSV 파일 시각화 및 피크 탐지 앱")

# CSV 파일 업로더
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    try:
        # CSV 파일을 pandas DataFrame으로 읽습니다.
        df_original = pd.read_csv(uploaded_file) # 원본 DataFrame을 보존합니다.
        df = df_original.copy() # 작업용 DataFrame 복사본을 만듭니다.

        st.subheader("업로드된 데이터 미리보기")
        st.dataframe(df.head()) # 데이터의 첫 5행을 표 형태로 보여줍니다.

        # DataFrame의 컬럼 목록을 가져옵니다.
        columns = df.columns.tolist()

        if not columns:
            st.warning("업로드된 CSV 파일에 유효한 컬럼이 없습니다.")
        else:
            # 사용자가 X축과 Y축으로 사용할 컬럼을 선택하도록 합니다.
            x_axis = st.selectbox("X축으로 사용할 컬럼을 선택하세요 (날짜/시간 또는 ID):", options=columns)
            y_axis = st.selectbox("Y축으로 사용할 컬럼을 선택하세요 (값, 숫자여야 함):", options=columns)

            if x_axis and y_axis:
                # Y축 컬럼이 숫자형인지 확인합니다.
                if not pd.api.types.is_numeric_dtype(df[y_axis]):
                    st.warning(f"선택하신 Y축 컬럼 '{y_axis}'은(는) 숫자형 데이터가 아닙니다. 숫자형 컬럼을 선택해주세요.")
                    st.stop() # 경고 후 앱 실행을 중단합니다.

                st.subheader(f"'{y_axis}' vs '{x_axis}' 그래프")

                # X축이 날짜/시간 데이터일 경우 파싱을 시도합니다.
                # 새로운 컬럼을 만들어서 원본 X축 컬럼을 보존합니다.
                try:
                    df['_x_axis_parsed'] = pd.to_datetime(df[x_axis])
                    # 날짜/시간 타입으로 변환 성공 시, 정렬합니다.
                    df.sort_values(by='_x_axis_parsed', inplace=True)
                    # 이후 px.line의 x 인자로 '_x_axis_parsed'를 사용합니다.
                    x_axis_for_plot = '_x_axis_parsed'
                except Exception:
                    st.warning(f"X축 컬럼 '{x_axis}'이(가) 날짜/시간 형식이 아닌 것 같습니다. 문자열/숫자로 처리합니다.")
                    x_axis_for_plot = x_axis # 파싱 실패 시 원본 컬럼 사용


                # Plotly Express를 이용한 라인 차트를 그립니다.
                # 항상 x와 y 인자를 명시적으로 지정합니다.
                fig = px.line(df, x=x_axis_for_plot, y=y_axis, title=f"'{y_axis}'의 변화 추이")

                # --- 피크 탐지 및 표시 ---
                # Y축 데이터에서 NaN (결측치) 값을 제거하고 피크를 탐지합니다.
                series_for_peaks = df[y_axis].dropna()

                if not series_for_peaks.empty:
                    # find_peaks 함수를 사용하여 피크를 찾습니다.
                    try:
                        if len(series_for_peaks) > 1 and series_for_peaks.std() > 0:
                            # prominence: 데이터의 표준편차를 기준으로 동적으로 설정합니다.
                            peak_prominence = series_for_peaks.std() * 0.5 # 0.5는 조절 가능한 계수
                            peaks, _ = find_peaks(series_for_peaks.values, prominence=peak_prominence)
                        else:
                            peaks, _ = find_peaks(series_for_peaks.values)
                    except Exception as e:
                        st.warning(f"피크 탐지 중 오류가 발생했습니다 (prominence 계산 문제?): {e}. 기본 설정으로 다시 시도합니다.")
                        peaks, _ = find_peaks(series_for_peaks.values) # prominence 없이

                    if len(peaks) > 0:
                        # 피크의 실제 X축 값과 Y축 값을 추출합니다.
                        # df의 인덱스가 바뀌었을 수 있으므로, df의 현재 인덱스(또는 x_axis_for_plot 컬럼)를 사용합니다.
                        # pandas Series에서 loc를 사용하면 원본 인덱스를 기준으로 데이터를 가져옵니다.
                        peak_x_values = df[x_axis_for_plot].iloc[series_for_peaks.index[peaks].values]
                        peak_y_values = series_for_peaks.values[peaks]

                        # Plotly Scatter 트레이스를 사용하여 피크를 마커로 그래프에 추가합니다.
                        fig.add_trace(go.Scatter(
                            x=peak_x_values,
                            y=peak_y_values,
                            mode='markers',
                            marker=dict(symbol='star', size=10, color='red'),
                            name='피크 지점',
                            showlegend=True
                        ))

                        st.write(f"**'{y_axis}' 데이터의 피크 정보:**")
                        # 각 피크의 X값과 Y값을 앱 화면에 출력합니다.
                        for i, (x_val, y_val) in enumerate(zip(peak_x_values, peak_y_values)):
                            # X값이 날짜/시간 타입이면 포맷팅하여 출력합니다.
                            if isinstance(x_val, pd.Timestamp):
                                st.write(f"- **피크 {i+1}**: X값: **{x_val.strftime('%Y-%m-%d %H:%M:%S')}**, Y값: **{y_val:.2f}**")
                            else:
                                st.write(f"- **피크 {i+1}**: X값: **{x_val}**, Y값: **{y_val:.2f}**")
                    else:
                        st.info("선택된 데이터에서 피크를 찾을 수 없습니다. 'prominence' 값을 조정해보거나, 데이터의 특성을 확인해주세요.")

                # 그래프 레이아웃을 업데이트하고 표시합니다.
                fig.update_layout(
                    hovermode="x unified",
                    xaxis_title=x_axis, # 원래 사용자가 선택한 컬럼 이름으로 표시
                    yaxis_title=y_axis
                )
                st.plotly_chart(fig, use_container_width=True)

    except pd.errors.EmptyDataError:
        st.error("업로드된 CSV 파일이 비어있습니다. 데이터를 포함한 파일을 업로드해주세요.")
    except pd.errors.ParserError:
        st.error("CSV 파일 형식이 올바르지 않습니다. 파일 내용을 확인해주세요.")
    except Exception as e:
        st.error(f"파일을 읽거나 그래프를 그리는 중 예상치 못한 오류가 발생했습니다: {e}")
        st.error("CSV 파일 형식 또는 데이터에 문제가 없는지 확인해주세요.")
