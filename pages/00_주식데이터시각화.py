import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide") # 페이지 전체 너비 사용

st.title("글로벌 시총 상위 기업 주가 변동 시각화")

# 추천하는 시가총액 상위 기업 티커 심볼 리스트
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
        # 중요: 인덱스를 'Date'라는 이름의 컬럼으로 변환
        data.reset_index(inplace=True)
        data.rename(columns={'Date': 'Date'}, inplace=True) # 컬럼 이름을 'Date'로 명확히 지정 (선택 사항이지만 일관성 유지)
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
                # `get_stock_data`에서 이미 Date 컬럼이 있으므로, 그걸 사용
                # 정규화 시에는 'Close' 컬럼만 필요하므로, Date 컬럼을 다시 인덱스로 설정하거나, Date 컬럼 기준으로 Merge
                # 여기서는 Long Format으로 변환하는 것이 더 견고함 (이전 답변에서 제시했던 2번째 해결책)
                temp_df = all_data[company].set_index('Date') # 임시로 Date를 인덱스로 설정
                first_close = temp_df['Close'].iloc[0]
                normalized_data[company] = (temp_df['Close'] / first_close - 1) * 100
        
        # 다시 `normalized_data`를 `px.line`이 선호하는 Long Format으로 변환
        if not normalized_data.empty:
            normalized_data_long = normalized_data.reset_index().melt(
                id_vars='index',
                var_name='Company',
                value_name='Normalized Change (%)'
            )
            normalized_data_long = normalized_data_long.rename(columns={'index': 'Date'}) # 'index' 컬럼명을 'Date'로 변경

            st.write("### 정규화된 종가 변동률 (기준일 대비)")
            fig_normalized = px.line(
                normalized_data_long,
                x='Date',
                y='Normalized Change (%)',
                color='Company',
                title="기준일 대비 종가 변화율 (%)",
                labels={'Date': '날짜', 'Normalized Change (%)': '변화율 (%)'},
                hover_name='Company'
            )
            fig_normalized.update_layout(hovermode="x unified")
            st.plotly_chart(fig_normalized, use_container_width=True)

        # 개별 기업의 캔들스틱 차트 표시
        st.subheader("개별 기업 상세 차트")
        for company in selected_companies:
            if company in all_data:
                st.write(f"#### {company} ({top_companies_tickers[company]})")
                stock_df = all_data[company].copy() # 원본 데이터프레임 변경 방지를 위해 .copy() 사용

                # 캔들스틱 차트는 Date 컬럼을 x축으로 사용
                fig_candlestick = go.Figure(data=[go.Candlestick(
                    x=stock_df['Date'], # 이제 'Date' 컬럼 사용
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
                    fig_candlestick.add_trace(go.Scatter(x=stock_df['Date'], y=stock_df['MA20'], mode='lines', name='MA20', line=dict(color='blue', width=1)))
                    fig_candlestick.add_trace(go.Scatter(x=stock_df['Date'], y=stock_df['MA50'], mode='lines', name='MA50', line=dict(color='green', width=1)))

                fig_candlestick.update_layout(
                    title=f'{company} 캔들스틱 차트',
                    xaxis_rangeslider_visible=False,
                    xaxis_title="날짜",
                    yaxis_title="가격",
                    hovermode="x unified"
                )
                st.plotly_chart(fig_candlestick, use_container_width=True)

                # 거래량 차트
                # x='Date' 컬럼을 명시적으로 사용
                fig_volume = px.bar(stock_df, x='Date', y='Volume', title=f'{company} 거래량', labels={'Volume': '거래량'})
                fig_volume.update_layout(xaxis_title="날짜", yaxis_title="거래량")
                st.plotly_chart(fig_volume, use_container_width=True)
