import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.signal import find_peaks # 피크 탐지 라이브러리
import plotly.graph_objects as go # 피크 마커 추가를 위해 필요

st.set_page_config(layout="wide") # 페이지 전체 너비 사용

st.title("CSV 파일 시각화 및 피크 탐지 앱")

# CSV 파일 업로더
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    try:
        # CSV 파일을 pandas DataFrame으로 읽기
        df = pd.read_csv(uploaded_file)

        st.subheader("업로드된 데이터 미리보기")
        st.dataframe(df.head()) # st.write 대신 st.dataframe을 사용하여 표 형태로 보기 좋게 표시

        # 데이터프레임 컬럼 선택 (x, y 축)
        columns = df.columns.tolist()

        if not columns: # 컬럼이 없는 경우
            st.warning("업로드된 CSV 파일에 유효한 컬럼이 없습니다.")
        else:
            x_axis = st.selectbox("X축으로 사용할 컬럼을 선택하세요 (보통 날짜/시간):", options=columns)
            y_axis = st.selectbox("Y축으로 사용할 컬럼을 선택하세요 (값을 나타내는 숫자):", options=columns)

            if x_axis and y_axis:
                # 선택된 Y축 컬럼이 숫자형인지 확인
                if pd.api.types.is_numeric_dtype(df[y_axis]):
                    st.subheader(f"{y_axis} vs {x_axis} 그래프")

                    # X축이 날짜/시간 데이터일 경우 파싱 시도
                    try:
                        df[x_axis] = pd.to_datetime(df[x_axis])
                        df.set_index(x_axis, inplace=True)
                        df.sort_index(inplace=True) # 시간 순서로 정렬
                    except Exception:
                        st.warning("X축 컬럼이 날짜/시간 형식이 아닌 것 같습니다. 문자열/숫자로 처리합니다.")
                        # 날짜 파싱 실패 시 인덱스 재설정 및 x_axis 컬럼 유지
                        df = df.reset_index(drop=True)
                        # 이후 px.line에서 x=x_axis 사용 시 문제가 없을 것임

                    # Plotly Express를 이용한 라인 차트
                    # px.line은 인덱스를 자동으로 x축으로 사용하거나, 컬럼을 x로 지정 가능
                    if df.index.name == x_axis: # Date 컬럼이 인덱스로 설정된 경우
                        fig = px.line(df, y=y_axis, title=f'{y_axis}의 변화')
                    else: # Date 컬럼이 여전히 일반 컬럼인 경우
                        fig = px.line(df, x=x_axis, y=y_axis, title=f'{y_axis}의 변화')

                    # --- 피크 탐지 및 표시 ---
                    # Y축 데이터에 대한 피크 탐지
                    # NaN 값 제거 후 피크 탐지
                    series_for_peaks = df[y_axis].dropna()

                    if not series_for_peaks.empty:
                        # find_peaks 함수 사용
                        # prominence: 피크의 상대적인 높이. 이 값이 높을수록 덜 중요한 피크는 무시됩니다.
                        # width: 피크의 최소 너비.
                        # 이 값들을 조정하여 원하는 피크를 찾도록 합니다.
                        # 예시에서는 prominence를 시리즈 표준편차의 0.5배로 설정 (데이터 변동성에 따라 조절)
                        try:
                            # 데이터가 충분히 있어야 std() 계산 가능
                            peak_prominence = series_for_peaks.std() * 0.5
                            if peak_prominence == 0 or len(series_for_peaks) < 2: # 데이터가 평탄하거나 너무 적으면 오류 방지
                                peaks, _ = find_peaks(series_for_peaks.values) # prominence 없이
                            else:
                                peaks, _ = find_peaks(series_for_peaks.values, prominence=peak_prominence)
                        except Exception: # std() 계산 불가 등 예외 발생 시
                            peaks, _ = find_peaks(series_for_peaks.values) # prominence 없이

                        if len(peaks) > 0:
                            # 피크의 실제 x축 값 (날짜/인덱스)과 y축 값 추출
                            peak_x_values = series_for_peaks.index[peaks] if isinstance(series_for_peaks.index, pd.DatetimeIndex) else series_for_peaks.index.to_numpy()[peaks]
                            peak_y_values = series_for_peaks.values[peaks]

                            # 피크를 마커로 추가 (Plotly Scatter 트레이스 사용)
                            fig.add_trace(go.Scatter(
                                x=peak_x_values,
                                y=peak_y_values,
                                mode='markers',
                                marker=dict(symbol='star', size=10, color='red'), # 별 모양 마커
                                name='피크',
                                showlegend=True
                            ))

                            st.write(f"**'{y_axis}'의 피크:**")
                            for i, (x_val, y_val) in enumerate(zip(peak_x_values, peak_y_values)):
                                if isinstance(x_val, pd.Timestamp):
                                    st.write(f"- 피크 {i+1}: 날짜/시간: **{x_val.strftime('%Y-%m-%d %H:%M')}**, 값: **{y_val:.2f}**")
                                else:
                                    st.write(f"- 피크 {i+1}: X값: **{x_val}**, Y값: **{y_val:.2f}**")
                        else:
                            st.info("선택된 Y축 데이터에서 피크를 찾을 수 없습니다. 'prominence' 값을 조정해보세요.")


                    fig.update_layout(hovermode="x unified", xaxis_title=x_axis, yaxis_title=y_axis)
                    st.plotly_chart(fig, use_container_width=True)

                else:
                    st.warning(f"선택하신 Y축 컬럼 '{y_axis}'은(는) 숫자형 데이터가 아닙니다. 숫자형 컬럼을 선택해주세요.")
    except Exception as e:
        st.error(f"파일을 읽거나 그래프를 그리는 중 오류가 발생했습니다: {e}")
        st.error("CSV 파일 형식을 확인하거나, 데이터에 문제가 없는지 확인해주세요.")
