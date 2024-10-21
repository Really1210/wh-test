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

def create_naver_map_url(start_coord, end_coord):
    base_url = "https://naveropenapi.apigw.ntruss.com/map-static/v2/raster"
    params = {
        "w": 600,  # 지도 너비
        "h": 400,  # 지도 높이
        "center": f"{(start_coord[1] + end_coord[1]) / 2},{(start_coord[0] + end_coord[0]) / 2}",
        "level": 11,  # 줌 레벨
        "markers": f"type:d|size:mid|pos:{start_coord[1]}%20{start_coord[0]}|icon:https://i.imgur.com/zlMBxw1.png,type:s|pos:{end_coord[1]}%20{end_coord[0]}|icon:https://i.imgur.com/nVtI3wq.png"
    }
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
    }
    response = requests.get(base_url, headers=headers, params=params)
    return response.url

# Streamlit 앱 UI
st.title("출발지와 도착지를 지도에 표시 13:27")

start_address = st.text_input("출발 주소 입력")
end_address = st.text_input("도착 주소 입력")

if st.button("지도 그리기"):
    start_coord = get_coordinates(start_address)
    end_coord = get_coordinates(end_address)
    
    if not start_coord:
        st.write("출발 주소를 확인해주세요.")
    elif not end_coord:
        st.write("도착 주소를 확인해주세요.")
    else:
        map_url = create_naver_map_url(start_coord, end_coord)
        st.image(map_url, caption="출발: 동그라미, 도착: 별")
