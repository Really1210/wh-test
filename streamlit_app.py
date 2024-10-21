import streamlit as st
import requests
from math import radians, sin, cos, sqrt, atan2

# 네이버 API 설정
client_id = "buzzqnu77m"
client_secret = "QkOrNDd4v57qIR2WKrE1gNO7WKKYeiXUMtjjfTAN"

def get_coordinates(address):
    url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {"X-NCP-APIGW-API-KEY-ID": client_id, "X-NCP-APIGW-API-KEY": client_secret}
    params = {"query": address}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['addresses']:
            lat = float(data['addresses'][0]['y'])
            lon = float(data['addresses'][0]['x'])
            return lat, lon
    return None

def calculate_distance(coord1, coord2):
    # Haversine 공식 사용
    R = 6371.0  # 지구 반지름 (킬로미터)
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

# Streamlit 앱 UI
st.title("두 지점 사이의 거리 계산기_1138")

start_address = st.text_input("출발 주소 입력")
end_address = st.text_input("도착 주소 입력")

if st.button("거리 계산"):
    start_coord = get_coordinates(start_address)
    end_coord = get_coordinates(end_address)
    
    if not start_coord:
        st.write("출발 주소를 확인해주세요.")
    elif not end_coord:
        st.write("도착 주소를 확인해주세요.")
    else:
        distance = calculate_distance(start_coord, end_coord)
        st.write(f"두 지점 사이의 거리는 {distance:.2f} km 입니다.")
