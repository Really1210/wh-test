import streamlit as st
import requests

# 네이버 API 정보
CLIENT_ID = 'buzzqnu77m'
CLIENT_SECRET = 'QkOrNDd4v57qIR2WKrE1gNO7WKKYeiXUMtjjfTAN'
NAVER_MAP_CLIENT_ID = 'l1vpx1wn5s'
NAVER_MAP_CLIENT_SECRET = 'uXxTGD601rp8u8WjwesxBHyyLxY50VKa1VAYb8Co'

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

# 스트림릿 UI 구성
st.title("출발지와 도착지 간 거리 계산 및 네이버 지도 표기 1555")

start_address = st.text_input("출발지 주소를 입력하세요")
end_address = st.text_input("도착지 주소를 입력하세요")

if st.button("거리 계산 및 지도 표시"):
    start_lat, start_lon = get_coordinates(start_address)
    end_lat, end_lon = get_coordinates(end_address)
    
    if start_lat and end_lat:
        # 지도 표시용 HTML
        map_html = f"""
        <html>
        <head>
        <script type="text/javascript" src="https://openapi.map.naver.com/openapi/v3/maps.js?ncpClientId={NAVER_MAP_CLIENT_ID}&ncpClientSecret={NAVER_MAP_CLIENT_SECRET}"></script>
        <script>
        function initMap() {{
            var map = new naver.maps.Map('map', {{
                center: new naver.maps.LatLng({start_lat}, {start_lon}),
                zoom: 10
            }});

            var startMarker = new naver.maps.Marker({{
                position: new naver.maps.LatLng({start_lat}, {start_lon}),
                map: map,
                title: '출발지: {start_address}'
            }});

            var endMarker = new naver.maps.Marker({{
                position: new naver.maps.LatLng({end_lat}, {end_lon}),
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
