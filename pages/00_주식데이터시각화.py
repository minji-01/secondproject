import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide") # 페이지 전체 너비 사용

st.title("글로벌 시총 상위 기업 주가 변동 시각화")

# 추천하는 시가총액 상위 기업 티커 심볼 리스트
# 주의: Saudi Aramco (2222.SR)는 yfinance에서 데이터가 불안정할 수 있습니다.
# Berkshire Hathaway는 BRK-B가 더 일반적입니다.
top_companies_tickers = {
    "Microsoft": "MSFT",
    "Nvidia": "NVDA",
    "Apple": "AAPL",
    "Amazon": "AMZN",
    "Alphabet (Google)": "GOOGL",
    "Meta Platforms": "META",
    "Broadcom": "AVGO",
    "Berkshire Hathaway": "BRK-B",
    "TSMC": "TSM",
    # "Saudi Aramco": "2222.SR" # yfinance 데이터가 불안정할 수 있어 주석 처리
}

# 사용자에게 보여줄 이름 리스트
company_names = list(top_companies_tickers.keys())

# 데이터 가져올 기간 설정 (최근 3년)
end_date = pd.to_datetime('today')
start_date = end_date - pd.DateOffset(years=3)

@st.cache_data # 데이터 캐싱으로 앱 성능 최적화
def get_stock_data(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end)
        return data
    except Exception as e:
        st.warning(f"티커 {ticker}의 데이터를 가져오는 데 실패했습니다: {e}")
        return pd.DataFrame() # 빈 데이터프레임 반환

# 모든 기업의 데이터를 저장할 딕셔너리
all_data = {}
for name, ticker in top_companies_tickers.items():
    data = get_stock_data(ticker, start_date, end_date)
    if not data.empty:
        all_data[name] = data

if not all_data:
    st.error("데이터를 가져올 수 있는 기업이 없습니다. 티커 심볼을 확인해주세요.")
else:
    st.subheader(f"최근 3년간 주가 변동 ({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})")

    # 선택 박스를 통해 원하는 기업 선택
    selected_companies = st.multiselect(
        "시각화할 기업을 선택하세요 (여러 개 선택 가능):",
        options=company_names,
        default=list(top_companies_tickers.keys()) # 기본으로 모두 선택
    )

    if not selected_companies:
        st.info("시각화할 기업을 선택해주세요.")
    else:
        # 각 기업의 종가(Close)를 정규화하여 비교
        normalized_data = pd.DataFrame()
        for company in selected_companies:
            if company in all_data:
                # 첫날 가격으로 정규화 (백분율 변화를 보기 위함)
                first_close = all_data[company]['Close'].iloc[0]
                normalized_data[company] = (all_data[company]['Close'] / first_close - 1) * 100

        if not normalized_data.empty:
            st.write("### 정규화된 종가 변동률 (기준일 대비)")
            fig_normalized = px.line(
                normalized_data,
                title="기준일 대비 종가 변화율 (%)",
                labels={'value': '변화율 (%)', 'index': '날짜'},
            )
            fig_normalized.update_layout(hovermode="x unified") # x축에 대한 툴팁 통합
            st.plotly_chart(fig_normalized, use_container_width=True)

        # 개별 기업의 캔들스틱 차트 표시
        st.subheader("개별 기업 상세 차트")
        for company in selected_companies:
            if company in all_data:
                st.write(f"#### {company} ({top_companies_tickers[company]})")
                stock_df = all_data[company]

                fig_candlestick = go.Figure(data=[go.Candlestick(
                    x=stock_df.index,
                    open=stock_df['Open'],
                    high=stock_df['High'],
                    low=stock_df['Low'],
                    close=stock_df['Close'],
                    name='Candlestick'
                )])

                # 이동 평균선 추가 (선택 사항)
                if len(stock_df) > 50: # 데이터가 충분할 때만
                    stock_df['MA20'] = stock_df['Close'].rolling(window=20).mean()
                    stock_df['MA50'] = stock_df['Close'].rolling(window=50).mean()
                    fig_candlestick.add_trace(go.Scatter(x=stock_df.index, y=stock_df['MA20'], mode='lines', name='MA20', line=dict(color='blue', width=1)))
                    fig_candlestick.add_trace(go.Scatter(x=stock_df.index, y=stock_df['MA50'], mode='lines', name='MA50', line=dict(color='green', width=1)))

                fig_candlestick.update_layout(
                    title=f'{company} 캔들스틱 차트',
                    xaxis_rangeslider_visible=False,
                    xaxis_title="날짜",
                    yaxis_title="가격",
                    hovermode="x unified"
                )
                st.plotly_chart(fig_candlestick, use_container_width=True)

                # 거래량 차트
                fig_volume = px.bar(stock_df, x=stock_df.index, y='Volume', title=f'{company} 거래량', labels={'Volume': '거래량'})
                fig_volume.update_layout(xaxis_title="날짜", yaxis_title="거래량")
                st.plotly_chart(fig_volume, use_container_width=True)
