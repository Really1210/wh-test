import streamlit as st
import requests
from math import radians, sin, cos, sqrt, atan2
import folium
from streamlit_folium import st_folium

# 네이버 API 정보
CLIENT_ID = 'buzzqnu77m'
CLIENT_SECRET = 'QkOrNDd4v57qIR2WKrE1gNO7WKKYeiXUMtjjfTAN'

# Geocoding API 호출 함수
def get_coordinates(address):
    """
    입력된 주소를 네이버 Geocoding API를 사용하여 위도, 경도로 변환하는 함수.
    """
    url = f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": CLIENT_ID,
        "X-NCP-APIGW-API-KEY": CLIENT_SECRET
    }
    params = {"query": address}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    if data['meta']['totalCount'] > 0:
        lat = data['addresses'][0]['y']
        lon = data['addresses'][0]['x']
        return float(lat), float(lon)
    else:
        return None, None

# 두 좌표 사이의 거리 계산 함수
def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Haversine 공식을 사용하여 두 지점 사이의 거리를 계산하는 함수.
    단위는 km로 반환.
    """
    R = 6371.0  # 지구 반지름 (km)
    
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c

# 스트림릿 UI 구성
st.title("출발지와 도착지 표시 및 거리 계산")

# 사용자로부터 출발지와 도착지 주소 입력 받기
start_address = st.text_input("출발지 주소를 입력하세요")
end_address = st.text_input("도착지 주소를 입력하세요")

# 거리 계산 및 지도 표시 버튼
if st.button("거리 계산 및 지도 표시"):
    start_lat, start_lon = get_coordinates(start_address)
    end_lat, end_lon = get_coordinates(end_address)
    
    if start_lat and end_lat:
        # 입력된 주소의 위도, 경도 출력
        st.write(f"출발지: {start_address} -> 위도: {start_lat}, 경도: {start_lon}")
        st.write(f"도착지: {end_address} -> 위도: {end_lat}, 경도: {end_lon}")
        
        # 거리 계산 결과 출력
        distance = calculate_distance(start_lat, start_lon, end_lat, end_lon)
        st.success(f"출발지와 도착지 사이의 거리는 {distance:.2f} km 입니다.")
        
        # Folium 지도 생성
        map_center = [(start_lat + end_lat) / 2, (start_lon + end_lon) / 2]
        m = folium.Map(location=map_center, zoom_start=13)
        
        # 출발지 마커 추가
        folium.Marker([start_lat, start_lon], popup=f"출발지: {start_address}", icon=folium.Icon(color='green')).add_to(m)
        
        # 도착지 마커 추가
        folium.Marker([end_lat, end_lon], popup=f"도착지: {end_address}", icon=folium.Icon(color='red')).add_to(m)
        
        # 두 지점 사이의 선 그리기
        folium.PolyLine(locations=[[start_lat, start_lon], [end_lat, end_lon]], color='blue', weight=2.5, opacity=1).add_to(m)
        
        # Folium 지도 Streamlit에 표시
        st_folium(m, width=700, height=500)
    else:
        st.error("좌표를 찾을 수 없는 주소가 있습니다. 다시 시도해주세요.")
