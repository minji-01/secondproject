import streamlit as st
import folium
from streamlit_folium import st_folium

# 관광지 정보 리스트
sydney_attractions = [
    {
        "name": "시드니 오페라 하우스",
        "location": [-33.8568, 151.2153],
        "description": "세계적으로 유명한 공연 예술 센터로, 독특한 조개껍데기 모양의 건축물이 특징입니다. 유네스코 세계유산에 등재되어 있으며, 내부 투어나 공연 관람이 가능합니다."
    },
    {
        "name": "하버 브리지",
        "location": [-33.8523, 151.2108],
        "description": "시드니 하버를 가로지르는 거대한 아치형 철교로, 하버 브리지 클라임을 통해 다리 꼭대기에서 시드니 전경을 감상할 수 있습니다."
    },
    {
        "name": "본다이 비치",
        "location": [-33.8915, 151.2767],
        "description": "세계적인 서핑 명소이자 현지인과 관광객 모두에게 사랑받는 해변입니다. 해안 산책로인 본다이 투 쿠지 워크도 인기입니다."
    },
    {
        "name": "시드니 타워 아이",
        "location": [-33.8705, 151.2088],
        "description": "시드니에서 가장 높은 전망대로, 360도 도시 전망을 감상할 수 있습니다. 스카이워크라는 야외 유리 데크 체험도 가능해요."
    },
    {
        "name": "타롱가 동물원",
        "location": [-33.8430, 151.2413],
        "description": "시드니 하버를 내려다보는 언덕에 위치한 동물원으로, 코알라, 캥거루, 기린 등 다양한 동물을 가까이에서 볼 수 있습니다."
    },
]

# Streamlit 앱 제목
st.title("🇦🇺 시드니 주요 관광지 가이드")
st.markdown("호주의 아름다운 항구 도시 시드니의 주요 관광지를 지도와 함께 소개합니다!")

# Folium 지도 생성
m = folium.Map(location=[-33.8688, 151.2093], zoom_start=12, control_scale=True)

# 관광지 마커 추가
for place in sydney_attractions:
    folium.Marker(
        location=place["location"],
        popup=f"<strong>{place['name']}</strong><br>{place['description']}",
        tooltip=place["name"],
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

# Streamlit에 Folium 지도 출력
st_folium(m, width=700, height=500)

# 관광지 정보 텍스트로도 출력
st.header("📍 관광지 상세 정보")
for place in sydney_attractions:
    with st.expander(place["name"]):
        st.write(place["description"])
