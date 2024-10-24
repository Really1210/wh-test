import streamlit as st
import requests
from xml.etree import ElementTree

# API 키 설정
API_KEY = "aNcRfgfkhHMmk6%2BoALtF4mfxW8RC33Ur9MPkOnJKkjwecj4K7lR8Hdkaw53CtZlSpn0xF7YYe%2BP5lDefgRwksQ%3D%3D"

# Streamlit UI 설정
st.title("건축물 최고층 층수 조회")
address = st.text_input("주소를 입력하세요 (예: 서울특별시 강남구 개포동 12번지):")

if st.button("조회"):
    if address:
        # 주소에서 시군구 코드, 법정동 코드, 번, 지 추출 (여기서는 예시로 고정된 값을 사용)
        # 실제 구현에서는 주소를 파싱하여 적절한 코드를 추출해야 함
        sigunguCd = "11680"  # 예시 시군구 코드
        bjdongCd = "10300"   # 예시 법정동 코드
        bun = "0012"         # 예시 번
        ji = "0000"          # 예시 지

        # API 요청 URL 구성
        url = f"http://apis.data.go.kr/1613000/BldRgstService_v2/getBrFlrOulnInfo?serviceKey={API_KEY}&sigunguCd={sigunguCd}&bjdongCd={bjdongCd}&bun={bun}&ji={ji}&_type=xml"
        
        # API 요청 및 응답 처리
        response = requests.get(url)
        
        if response.status_code == 200:
            # XML 파싱
            tree = ElementTree.fromstring(response.content)
            items = tree.findall('.//item')
            
            if items:
                max_floor = 0
                for item in items:
                    flrNo = int(item.find('flrNo').text) if item.find('flrNo') is not None else 0
                    if flrNo > max_floor:
                        max_floor = flrNo
                
                # 결과 출력
                st.write(f"최고층 층수: {max_floor}층")
            else:
                st.write("해당 주소에 대한 정보를 찾을 수 없습니다.")
        else:
            st.write("API 요청에 실패했습니다. 다시 시도해주세요.")
    else:
        st.write("주소를 입력하세요.")