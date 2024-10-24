import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
from math import radians, sin, cos, sqrt, atan2

# 네이버 API 정보
CLIENT_ID = 'buzzqnu77m'
CLIENT_SECRET = 'QkOrNDd4v57qIR2WKrE1gNO7WKKYeiXUMtjjfTAN'

# Geocoding API 호출 함수
def get_coordinates(address):
    url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
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

# 국토교통부 건축물대장정보 API 호출 함수
SERVICE_KEY = 'YaNcRfgfkhHMmk6%2BoALtF4mfxW8RC33Ur9MPkOnJKkjwecj4K7lR8Hdkaw53CtZlSpn0xF7YYe%2BP5lDefgRwksQ%3D%3D'  # 국토교통부 건축물대장 API 서비스키 입력

def get_building_info(address):
    url = f"https://api.data.go.kr/openapi/tn_pubr_public_buldng_rl_buldng_api?serviceKey={SERVICE_KEY}&pageNo=1&numOfRows=10&format=json&sigunguCd=11680&bjdongCd=10300&platGbCd=0&bun=0001&ji=0000&startDate=20000101&endDate=20241231"
    params = {"sigunguCd": "시군구코드", "bjdongCd": "법정동코드", "platGbCd": "0", "bun": "0000", "ji": "0000"}
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'response' in data and data['response']['header']['resultCode'] == "00":
        building_info = data['response']['body']['items'][0]
        return {
            'height': building_info['height'],  # 건물 높이
            'type': building_info['mainPurpsCdNm'],  # 건물 용도
            'floors': building_info['totDongTotArea']  # 층수
        }
    return None

# 두 좌표 사이의 거리 계산 함수
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # 지구 반지름 (km)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# 가장 가까운 주소를 찾는 함수
def find_closest_location(lat1, lon1, df):
    closest_distance = float('inf')
    closest_location = None
    closest_lat = None
    closest_lon = None

    for index, row in df.iterrows():
        lat2, lon2 = get_coordinates(row['주소'])
        if lat2 and lon2:
            distance = calculate_distance(lat1, lon1, lat2, lon2)
            if distance < closest_distance:
                closest_distance = distance
                closest_location = row['명칭']
                closest_lat = lat2
                closest_lon = lon2
    return closest_location, closest_lat, closest_lon, closest_distance

# 스트림릿 UI 구성
st.title("출발지와 도착지 표시 및 건물 정보 표기")

# CSV 파일 업로드
uploaded_file = st.file_uploader("CSV 파일 업로드", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    if len(df) == 0:
        st.error("CSV 파일이 비어 있습니다.")
    else:
        st.write(df)
        start_address = st.text_input("출발지 주소를 입력하세요")
        end_address = st.text_input("도착지 주소를 입력하세요")

        if st.button("거리 계산 및 지도 표시"):
            start_lat, start_lon = get_coordinates(start_address)
            end_lat, end_lon = get_coordinates(end_address)

            if start_lat and end_lat:
                # 출발지 및 도착지 건물 정보 표시
                building_info_start = get_building_info(start_address)
                building_info_end = get_building_info(end_address)

                if building_info_start:
                    st.write(f"출발지 건물 정보: {building_info_start['type']}, {building_info_start['floors']}층, {building_info_start['height']}m")
                if building_info_end:
                    st.write(f"도착지 건물 정보: {building_info_end['type']}, {building_info_end['floors']}층, {building_info_end['height']}m")

                # 출발-도착 거리 계산
                distance_start_end = calculate_distance(start_lat, start_lon, end_lat, end_lon)
                st.write(f"출발지 -> 도착지 거리: {distance_start_end:.2f} km")

                # 지도에 출발지, 도착지, 건물 정보 표시
                data = pd.DataFrame({
                    'lat': [start_lat, end_lat],
                    'lon': [start_lon, end_lon],
                    'name': ['출발', '도착'],
                    'color': [[255, 0, 0], [255, 165, 0]]
                })

                layer = pdk.Layer(
                    'ScatterplotLayer',
                    data,
                    get_position='[lon, lat]',
                    get_color='color',
                    get_radius=50,
                    pickable=True
                )

                view_state = pdk.ViewState(
                    latitude=(start_lat + end_lat) / 2,
                    longitude=(start_lon + end_lon) / 2,
                    zoom=10,
                    pitch=50,
                )

                r = pdk.Deck(
                    layers=[layer],
                    initial_view_state=view_state,
                    tooltip={"text": "{name}"}
                )
                st.pydeck_chart(r)

            else:
                st.error("출발지 또는 도착지의 좌표를 찾을 수 없습니다.")
