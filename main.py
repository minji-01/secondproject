import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import date

# 관광지 정보 리스트
sydney_attractions = [
    {
        "name": "시드니 오페라 하우스",
        "location": [-33.8568, 151.2153],
        "description": """
세계적으로 유명한 공연 예술 센터로,
독특한 조개껍데기 모양의 건축물이 특징입니다.
유네스코 세계유산에 등재되어 있으며,
내부 투어나 공연 관람이 가능합니다.
"""
    },
    {
        "name": "하버 브리지",
        "location": [-33.8523, 151.2108],
        "description": """
시드니 하버를 가로지르는 거대한 아치형 철교입니다.
하버 브리지 클라임을 통해 다리 꼭대기에서
시드니 전경을 감상할 수 있습니다.
"""
    },
    {
        "name": "본다이 비치",
        "location": [-33.8915, 151.2767],
        "description": """
세계적인 서핑 명소이자 인기 있는 해변입니다.
해안 산책로인 본다이 투 쿠지 워크도 추천됩니다.
"""
    },
    {
        "name": "시드니 타워 아이",
        "location": [-33.8705, 151.2088],
        "description": """
시드니에서 가장 높은 전망대로,
360도 도시 전망을 감상할 수 있습니다.
스카이워크 야외 유리 데크 체험도 제공됩니다.
"""
    },
    {
        "name": "타롱가 동물원",
        "location": [-33.8430, 151.2413],
        "description": """
시드니 하버를 내려다보는 언덕에 위치한 동물원입니다.
코알라, 캥거루, 기린 등 다양한 동물을 가까이서 볼 수 있습니다.
"""
    },
]

# Streamlit 앱 제목
st.title("\U0001F1E6\U0001F1FA 나의 시드니 여행 가이드 ")
st.markdown("호주의 아름다운 항구 도시 시드니의 주요 관광지를 소개합니다!")

# Folium 지도 생성
m = folium.Map(location=[-33.8688, 151.2093], zoom_start=12, control_scale=True)

# 관광지 마커 추가
for place in sydney_attractions:
    html_popup = f"""
    <h4>{place['name']}</h4>
    <p style='white-space: pre-wrap;'>{place['description'].strip()}</p>
    """
    folium.Marker(
        location=place["location"],
        popup=folium.Popup(html_popup, max_width=300, min_width=200),
        tooltip=place["name"],
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

# Streamlit에 Folium 지도 출력
st_folium(m, width=700, height=500)

# 관광지 정보 텍스트로도 출력
st.header("\U0001F4CD 관광지 상세 정보")
for place in sydney_attractions:
    with st.expander(place["name"]):
        st.write(place["description"])

# 여행 코스 추천
st.header("\U0001F5FA 추천 여행 코스")
selected_days = st.slider("여행 일수 선택", min_value=1, max_value=5, value=3)

itinerary = {
    1: ["시드니 오페라 하우스", "하버 브리지"],
    2: ["본다이 비치", "시드니 타워 아이"],
    3: ["타롱가 동물원", "하버 브리지"],
    4: ["본다이 비치", "타롱가 동물원"],
    5: ["시드니 오페라 하우스", "시드니 타워 아이"]
}

for day in range(1, selected_days + 1):
    st.subheader(f"Day {day}")
    for place_name in itinerary.get(day, []):
        place = next(p for p in sydney_attractions if p["name"] == place_name)
        st.markdown(f"**{place['name']}**: {place['description'].strip().splitlines()[0]}")

# 간단한 일정표 생성기
st.header("\U0001F4C5 나의 일정 만들기")
st.markdown("원하는 날짜와 관광지를 선택해보세요!")

travel_date = st.date_input("여행 시작일", date.today())
schedule = {}

for i in range(selected_days):
    day = travel_date.strftime("%Y-%m-%d")
    selected_place = st.selectbox(f"Day {i+1} 일정 선택", [p["name"] for p in sydney_attractions], key=f"day_{i}")
    schedule[day] = selected_place
    travel_date = travel_date.replace(day=travel_date.day + 1)

st.subheader("📆 나의 여행 일정표")
for day, place in schedule.items():
    st.write(f"{day}: {place}")
