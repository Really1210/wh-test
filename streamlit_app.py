import streamlit as st
import requests
from math import radians, sin, cos, sqrt, atan2

# 네이버 API 정보
CLIENT_ID = 'buzzqnu77m'
CLIENT_SECRET = 'QkOrNDd4v57qIR2WKrE1gNO7WKKYeiXUMtjjfTAN'
GOOGLE_MAP_API_KEY = 'AIzaSyBnCSqt1jpfJIJXNevyQHQ-7ZZ2K3ucoVA'

# Geocoding API 호출 함수
def get_coordinates(address):
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

# 두 좌표 사이의 거리 계산 (단위: km)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # 지구 반지름 (km)
    
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c

# 데이터셋의 값을 변경하는 함수 (4번 항목 적용)
def update_dataset_values(database):
    for item in database:
        # 예: 모든 아이템의 특정 컬럼 값 변경
        item['column_to_update'] = 'new_value'
    return database

# 스트림릿 UI 구성
st.title("출발지와 도착지 간 거리 계산 및 구글 지도 표기 1705 ")

start_address = st.text_input("출발지 주소를 입력하세요")
end_address = st.text_input("도착지 주소를 입력하세요")

if st.button("거리 계산 및 지도 표시"):
    start_lat, start_lon = get_coordinates(start_address)
    end_lat, end_lon = get_coordinates(end_address)
    
    if start_lat and end_lat:
        # 위경도 출력
        st.write(f"출발지: {start_address} -> 위도: {start_lat}, 경도: {start_lon}")
        st.write(f"도착지: {end_address} -> 위도: {end_lat}, 경도: {end_lon}")
        
        # 거리 계산
        distance = calculate_distance(start_lat, start_lon, end_lat, end_lon)
        st.success(f"출발지와 도착지 사이의 거리는 {distance:.2f} km 입니다.")
        
        # 구글 지도 표시용 HTML
        map_html = f"""
        <html>
        <head>
        <script src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAP_API_KEY}"></script>
        <script>
        function initMap() {{
            var map = new google.maps.Map(document.getElementById('map'), {{
                zoom: 10,
                center: {{lat: {start_lat}, lng: {start_lon}}}
            }});

            var startMarker = new google.maps.Marker({{
                position: {{lat: {start_lat}, lng: {start_lon}}},
                map: map,
                title: '출발지: {start_address}'
            }});

            var endMarker = new google.maps.Marker({{
                position: {{lat: {end_lat}, lng: {end_lon}}},
                map: map,
                title: '도착지: {end_address}'
            }});
        }}
        </script>
        </head>
        <body onload="initMap()">
        <div id="map" style="width:100%;height:500px;"></div>
        </body>
        </html>
        """
        
        # HTML을 스트림릿에서 표시
        st.components.v1.html(map_html, height=600)
    else:
        st.error("좌표를 찾을 수 없는 주소가 있습니다. 다시 시도해주세요.")

# 데이터셋 값 업데이트 적용 (예시 데이터베이스)
database = [{'id': 1, 'column_to_update': 'old_value'}, {'id': 2, 'column_to_update': 'old_value'}]
updated_database = update_dataset_values(database)
st.write(updated_database)
