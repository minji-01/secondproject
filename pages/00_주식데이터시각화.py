import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go # Plotly를 더 세밀하게 제어할 때

st.title("주식 데이터 시각화 앱")

# 사용자로부터 티커 입력 받기
ticker_symbol = st.text_input("주식 티커를 입력하세요 (예: AAPL, GOOGL, 005930.KS):", "AAPL")

if ticker_symbol:
    try:
        # yfinance로 주식 데이터 가져오기
        stock_data = yf.download(ticker_symbol, start="2023-01-01", end=pd.to_datetime('today'))

        if not stock_data.empty:
            st.subheader(f"{ticker_symbol} 주식 데이터")
            st.write(stock_data.tail()) # 최근 5개 데이터 표시

            # 캔들스틱 차트 그리기 (Plotly)
            fig = go.Figure(data=[go.Candlestick(
                x=stock_data.index,
                open=stock_data['Open'],
                high=stock_data['High'],
                low=stock_data['Low'],
                close=stock_data['Close']
            )])
            fig.update_layout(title=f'{ticker_symbol} 캔들스틱 차트', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

            # 종가 라인 차트 그리기 (Plotly Express)
            # import plotly.express as px
            # fig_line = px.line(stock_data, x=stock_data.index, y='Close', title=f'{ticker_symbol} 종가')
            # st.plotly_chart(fig_line, use_container_width=True)

        else:
            st.warning("선택하신 티커에 대한 데이터를 찾을 수 없습니다.")

    except Exception as e:
        st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
