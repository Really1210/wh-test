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
    return closest_location, closest_lat, closest_lon

# 스트림릿 UI 구성
st.title("출발지와 도착지 간 거리 및 가장 가까운 주소 찾기")

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
                st.write(f"출발지 -> 도착지 거리: {calculate_distance(start_lat, start_lon, end_lat, end_lon):.2f} km")
                
                closest_name, closest_lat, closest_lon = find_closest_location(start_lat, start_lon, df)
                if closest_name:
                    st.write(f"출발지 -> 가장 가까운 장소: {closest_name} ({calculate_distance(start_lat, start_lon, closest_lat, closest_lon):.2f} km)")
                    
                    data = pd.DataFrame({
                        'lat': [start_lat, end_lat, closest_lat],
                        'lon': [start_lon, end_lon, closest_lon],
                        'name': ['출발', '도착', closest_name]
                    })
                    
                    layer = pdk.Layer(
                        'ScatterplotLayer',
                        data,
                        get_position='[lon, lat]',
                        get_color='[200, 30, 0, 160]',
                        get_radius=100,
                        pickable=True
                    )
                    
                    text_layer = pdk.Layer(
                        "TextLayer",
                        data,
                        get_position='[lon, lat]',
                        get_text='name',
                        get_size=16,
                        get_color=[0, 0, 0],
                        get_angle=0,
                        get_alignment_baseline="'bottom'"
                    )

                    view_state = pdk.ViewState(
                        latitude=(start_lat + end_lat) / 2,
                        longitude=(start_lon + end_lon) / 2,
                        zoom=10,
                        pitch=50,
                    )

                    r = pdk.Deck(
                        layers=[layer, text_layer],
                        initial_view_state=view_state,
                        tooltip={"text": "{name}"}
                    )

                    st.pydeck_chart(r)
                else:
                    st.error("가장 가까운 주소를 찾을 수 없습니다.")
            else:
                st.error("출발지 또는 도착지의 좌표를 찾을 수 없습니다.")
