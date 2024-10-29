import streamlit as st
import requests
from xml.etree import ElementTree

# API 키 설정
API_KEY = "aNcRfgfkhHMmk6%2BoALtF4mfxW8RC33Ur9MPkOnJKkjwecj4K7lR8Hdkaw53CtZlSpn0xF7YYe%2BP5lDefgRwksQ%3D%3D"

def get_max_floor(sigunguCd, bjdongCd, bun, ji):
    url = f"http://apis.data.go.kr/1613000/BldRgstService_v2/getBrFlrOulnInfo?serviceKey={API_KEY}&sigunguCd={sigunguCd}&bjdongCd={bjdongCd}&bun={bun}&ji={ji}&_type=xml"
    response = requests.get(url)
    if response.status_code == 200:
        tree = ElementTree.fromstring(response.content)
        items = tree.findall('.//item')
        max_floor = max(
            int(float(item.find('flrNo').text)) 
            for item in items if item.find('flrNo') is not None
        )
        return max_floor
    else:
        return None

st.title("건축물 최고층 층수 조회")
address = st.text_input("주소를 입력하세요 (예: 서울특별시 강남구 개포동 12번지):")

if st.button("조회"):
    if address:
        # 실제 구현에서는 주소 파싱을 통해 sigunguCd, bjdongCd, bun, ji 값을 추출
        sigunguCd = "11680"  # 예시
        bjdongCd = "10300"   # 예시
        bun = "0012"         # 예시
        ji = "0000"          # 예시

        max_floor = get_max_floor(sigunguCd, bjdongCd, bun, ji)
        
        if max_floor is not None:
            st.write(f"최고층 층수: {max_floor}층")
        else:
            st.write("해당 주소에 대한 정보를 찾을 수 없습니다.")
    else:
        st.write("주소를 입력하세요.")
