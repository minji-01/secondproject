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
        df = pd.read_csv(uploaded_file)

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
                # 선택된 Y축 컬럼이 숫자형인지 확인합니다.
                if pd.api.types.is_numeric_dtype(df[y_axis]):
                    st.subheader(f"'{y_axis}' vs '{x_axis}' 그래프")

                    # X축이 날짜/시간 데이터일 경우 파싱을 시도합니다.
                    try:
                        df[x_axis] = pd.to_datetime(df[x_axis])
                        # 날짜가 인덱스로 설정되어야 Plotly가 시간축으로 잘 인식합니다.
                        df.set_index(x_axis, inplace=True)
                        df.sort_index(inplace=True) # 시간 순서로 정렬합니다.
                    except Exception:
                        st.warning(f"X축 컬럼 '{x_axis}'이(가) 날짜/시간 형식이 아닌 것 같습니다. 문자열/숫자로 처리합니다.")
                        # 날짜 파싱 실패 시 인덱스 재설정 및 x_axis 컬럼 유지
                        df = df.reset_index(drop=True)
                        # 이 경우 px.line에서 x=x_axis를 직접 지정해야 합니다.

                    # Plotly Express를 이용한 라인 차트를 그립니다.
                    # X축이 인덱스(날짜)로 설정되었으면 x 인자를 생략할 수 있습니다.
                    if df.index.name == x_axis:
                        fig = px.line(df, y=y_axis, title=f"'{y_axis}'의 변화 추이")
                    else: # X축이 일반 컬럼으로 남아있는 경우 (날짜 파싱 실패 등)
                        fig = px.line(df, x=x_axis, y=y_axis, title=f"'{y_axis}'의 변화 추이")

                    # --- 피크 탐지 및 표시 ---
                    # Y축 데이터에서 NaN (결측치) 값을 제거하고 피크를 탐지합니다.
                    series_for_peaks = df[y_axis].dropna()

                    if not series_for_peaks.empty:
                        # find_peaks 함수를 사용하여 피크를 찾습니다.
                        # prominence: 피크의 상대적인 높이. 값이 높을수록 덜 중요한 피크는 무시됩니다.
                        #             여기서는 데이터의 표준편차를 기준으로 동적으로 설정합니다.
                        try:
                            # 데이터가 충분히 많고 분산되어 있어야 표준편차 계산이 유효합니다.
                            # 데이터가 평탄하거나 너무 적으면 prominence 없이 피크를 찾습니다.
                            if len(series_for_peaks) > 1 and series_for_peaks.std() > 0:
                                peak_prominence = series_for_peaks.std() * 0.5 # 0.5는 조절 가능
                                peaks, _ = find_peaks(series_for_peaks.values, prominence=peak_prominence)
                            else:
                                peaks, _ = find_peaks(series_for_peaks.values) # prominence 없이
                        except Exception:
                            # 표준편차 계산 불가 등 예외 발생 시 prominence 없이 진행합니다.
                            peaks, _ = find_peaks(series_for_peaks.values)

                        if len(peaks) > 0:
                            # 피크의 실제 X축 값(날짜/인덱스)과 Y축 값을 추출합니다.
                            # X축이 날짜/시간 형식일 경우와 아닐 경우를 구분합니다.
                            if isinstance(series_for_peaks.index, pd.DatetimeIndex):
                                peak_x_values = series_for_peaks.index[peaks]
                                # 피크 날짜를 datetime.date 형식으로 변환하여 비교 시 오류 방지
                                peak_x_values_for_display = [ts.strftime('%Y-%m-%d %H:%M:%S') for ts in peak_x_values]
                            else:
                                peak_x_values = series_for_peaks.index.to_numpy()[peaks]
                                peak_x_values_for_display = peak_x_values # 문자열이나 숫자 그대로 표시

                            peak_y_values = series_for_peaks.values[peaks]

                            # Plotly Scatter 트레이스를 사용하여 피크를 마커로 그래프에 추가합니다.
                            fig.add_trace(go.Scatter(
                                x=peak_x_values,
                                y=peak_y_values,
                                mode='markers',
                                marker=dict(symbol='star', size=10, color='red'), # 별 모양, 빨간색 마커
                                name='피크 지점', # 범례에 표시될 이름
                                showlegend=True # 범례에 표시합니다.
                            ))

                            st.write(f"**'{y_axis}' 데이터의 피크 정보:**")
                            # 각 피크의 X값과 Y값을 앱 화면에 출력합니다.
                            for i, (x_val, y_val) in enumerate(zip(peak_x_values_for_display, peak_y_values)):
                                st.write(f"- **피크 {i+1}**: X값: **{x_val}**, Y값: **{y_val:.2f}**")
                        else:
                            st.info("선택된 데이터에서 피크를 찾을 수 없습니다. 'prominence' 값을 조정해보거나, 데이터의 특성을 확인해주세요.")

                    # 그래프 레이아웃을 업데이트하고 표시합니다.
                    fig.update_layout(
                        hovermode="x unified", # 마우스 오버 시 X축에 대한 툴팁을 통합합니다.
                        xaxis_title=x_axis,
                        yaxis_title=y_axis
                    )
                    st.plotly_chart(fig, use_container_width=True)

                else:
                    st.warning(f"선택하신 Y축 컬럼 '{y_axis}'은(는) 숫자형 데이터가 아닙니다. 숫자형 컬럼을 선택해주세요.")
    except pd.errors.EmptyDataError:
        st.error("업로드된 CSV 파일이 비어있습니다. 데이터를 포함한 파일을 업로드해주세요.")
    except pd.errors.ParserError:
        st.error("CSV 파일 형식이 올바르지 않습니다. 파일 내용을 확인해주세요.")
    except Exception as e:
        st.error(f"파일을 읽거나 그래프를 그리는 중 오류가 발생했습니다: {e}")
        st.error("CSV 파일 형식 또는 데이터에 문제가 없는지 확인해주세요.")
