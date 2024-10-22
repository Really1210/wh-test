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

# 동적 지도 크기 설정 함수
def calculate_zoom_level(distance):
    if distance < 1:
        return 14  # 작은 거리일 때 높은 줌 레벨
    elif distance < 5:
        return 12
    elif distance < 20:
        return 10
    else:
        return 8  # 큰 거리일 때 낮은 줌 레벨

# Streamlit UI 구성
st.title("거리 계산 앱")

# 1. 개별 거리 계산 아이콘 버튼
if st.button("1. 개별 거리 계산"):
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
                    # 출발-도착 거리 계산
                    distance_start_end = calculate_distance(start_lat, start_lon, end_lat, end_lon)
                    st.write(f"출발지 -> 도착지 거리: {distance_start_end:.2f} km")
                    
                    # 출발지에서 가장 가까운 주소 찾기
                    closest_name, closest_lat, closest_lon = find_closest_location(start_lat, start_lon, df)
                    
                    if closest_name:
                        distance_start_closest = calculate_distance(start_lat, start_lon, closest_lat, closest_lon)
                        st.write(f"출발지 -> 가장 가까운 장소: {closest_name} ({distance_start_closest:.2f} km)")
                        
                        # 지도 줌 레벨 계산
                        max_distance = max(distance_start_end, distance_start_closest)
                        zoom_level = calculate_zoom_level(max_distance)

                        # 출발지, 도착지, 가장 가까운 주소 데이터를 포함하는 DataFrame 생성
                        data = pd.DataFrame({
                            'lat': [start_lat, end_lat, closest_lat],
                            'lon': [start_lon, end_lon, closest_lon],
                            'name': ['출발', '도착', closest_name],
                            'color': [[255, 0, 0], [255, 165, 0], [0, 0, 255]]  # 빨간색, 주황색(도착), 파란색
                        })
                        
                        # pydeck Layer 설정
                        layer = pdk.Layer(
                            'ScatterplotLayer',
                            data,
                            get_position='[lon, lat]',
                            get_color='color',
                            get_radius=50,  # 원 크기 조정 (단위: 미터)
                            pickable=True
                        )
                        
                        # 텍스트 라벨 레이어 추가
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

                        # pydeck Deck 생성
                        view_state = pdk.ViewState(
                            latitude=(start_lat + end_lat) / 2,
                            longitude=(start_lon + end_lon) / 2,
                            zoom=zoom_level,
                            pitch=50,
                        )

                        r = pdk.Deck(
                            layers=[layer, text_layer],
                            initial_view_state=view_state,
                            tooltip={"text": "{name}"}
                        )

                        # pydeck 맵 표시
                        st.pydeck_chart(r)
                        
                        # 범례 추가
                        st.markdown("""
                        <style>
                            .legend {
                                position: absolute;
                                bottom: 20px;
                                left: 20px;
                                background-color: white;
                                padding: 10px;
                                border-radius: 5px;
                                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.3);
                            }
                        </style>
                        <div class="legend">
                            <b>범례</b><br>
                            <span style="color: red;">● 출발</span><br>
                            <span style="color: orange;">● 도착</span><br>
                            <span style="color: blue;">● 가까운 주소</span>
                        </div>
                        """, unsafe_allow_html=True)

                    else:
                        st.error("가장 가까운 주소를 찾을 수 없습니다.")
                else:
                    st.error("출발지 또는 도착지의 좌표를 찾을 수 없습니다.")
