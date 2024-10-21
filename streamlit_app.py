import streamlit as st
import requests
from math import radians, sin, cos, sqrt, atan2

# 네이버 API 설정
client_id = "xbajg8w92p"
client_secret = "MPSE5rkfxFRJT98AgbzRoidsGBu3xjT1h93tKSac"

# 좌표를 받아오는 함수
def get_coordinates(address):
    url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret
    }
    params = {"query": address}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        # Check if 'addresses' key exists and contains data
        if 'addresses' in data and data['addresses']:
            lat = float(data['addresses'][0]['y'])
            lon = float(data['addresses'][0]['x'])
            return lat, lon
        else:
            st.error("No address data found. Please check the input address.")
    else:
        st.error(f"Error with API request. Status code: {response.status_code}")
    
    return None

# 두 좌표 간의 거리를 계산하는 함수 (Haversine 공식 사용)
def calculate_distance(coord1, coord2):
    R = 6371.0  # 지구 반지름 (킬로미터)
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

# 네이버 지도 이미지를 생성하는 함수
def create_naver_map_url(start_coord, end_coord):
    base_url = "https://naveropenapi.apigw.ntruss.com/map-static/v2/raster"
    params = {
        "w": 600,  # 지도 너비
        "h": 400,  # 지도 높이
        "center": f"{(start_coord[1] + end_coord[1]) / 2},{(start_coord[0] + end_coord[0]) / 2}",
        "level": 11,  # 줌 레벨
        "markers": f"type:d|size:mid|pos:{start_coord[1]}%20{start_coord[0]}|icon:https://i.imgur.com/zlMBxw1.png,"
                   f"type:s|pos:{end_coord[1]}%20{end_coord[0]}|icon:https://i.imgur.com/nVtI3wq.png"  # 별 마커
    }
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret
    }
    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code == 200:
        return response.url
    elif response.status_code == 403:
        st.write("API 접근 권한 오류입니다. Client ID와 Secret을 확인하세요.")
    else:
        st.write(f"지도를 불러오는데 실패했습니다. 오류 코드: {response.status_code}")
    return None

# Streamlit 앱 UI
st.title("출발지와 도착지의 거리 및 지도 표시 1514")

start_address = st.text_input("출발 주소 입력")
end_address = st.text_input("도착 주소 입력")

if st.button("계산 및 지도 표시"):
    start_coord = get_coordinates(start_address)
    end_coord = get_coordinates(end_address)
    
    if not start_coord:
        st.write("출발 주소를 확인해주세요.")
    elif not end_coord:
        st.write("도착 주소를 확인해주세요.")
    else:
        # 두 지점의 위도와 경도를 출력
        st.write(f"출발지 위도: {start_coord[0]:.6f}, 경도: {start_coord[1]:.6f}")
        st.write(f"도착지 위도: {end_coord[0]:.6f}, 경도: {end_coord[1]:.6f}")
        
        # 두 지점 간 거리 계산
        distance = calculate_distance(start_coord, end_coord)
        st.write(f"두 지점 사이의 거리는 {distance:.2f} km 입니다.")
        
        # 지도 표시
        map_url = create_naver_map_url(start_coord, end_coord)
        if map_url:
            st.image(map_url, caption="출발: 동그라미, 도착: 별")
