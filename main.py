import streamlit as st
import folium
from streamlit_folium import folium_static

# 웹 앱 제목
st.title("시드니 주요 관광지 가이드")

# 지도 생성
m = folium.Map(location=[-33.8688, 151.2093], zoom_start=12)

# 관광지 마커 추가
for _, row in places.iterrows():
    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        popup=row["name"],
        icon=folium.Icon(color="blue")
    ).add_to(m)

# 지도 표시
folium_static(m)

# 관광지 설명
st.write("""
### 시드니의 대표 관광지
- **오페라 하우스**: 시드니의 랜드마크로, 독특한 조개껍질 모양의 건축물이 특징입니다.
- **하버 브리지**: 시드니 항구를 가로지르는 거대한 다리로, 브리지 클라이밍 체험이 가능합니다.
- **본다이 비치**: 세계적으로 유명한 해변으로, 서핑과 해변 산책을 즐길 수 있습니다.
- **달링 하버**: 다양한 레스토랑과 쇼핑몰이 있는 활기찬 지역입니다.
- **블루 마운틴**: 웅장한 자연 경관을 감상할 수 있는 국립공원으로, 하이킹과 전망대 방문이 가능합니다.
""")
