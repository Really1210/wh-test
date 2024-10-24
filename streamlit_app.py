import streamlit as st
import requests
from xml.etree import ElementTree

# API 키 설정
API_KEY = "aNcRfgfkhHMmk6%2BoALtF4mfxW8RC33Ur9MPkOnJKkjwecj4K7lR8Hdkaw53CtZlSpn0xF7YYe%2BP5lDefgRwksQ%3D%3D"

# Streamlit UI 설정
st.title("건축물 정보 조회")
address = st.text_input("주소를 입력하세요:")

if st.button("조회"):
    if address:
        # API 요청 URL 구성
        url = f"http://apis.data.go.kr/1613000/BldRgstService_v2/getBrTitleInfo?serviceKey={API_KEY}&brTitleNm={address}"
        
        # API 요청 및 응답 처리
        response = requests.get(url)
        
        if response.status_code == 200:
            # XML 파싱
            tree = ElementTree.fromstring(response.content)
            items = tree.findall('.//item')
            
            if items:
                for item in items:
                    # 건물 높이와 층수 추출
                    height = item.find('height').text if item.find('height') is not None else "정보 없음"
                    floors = item.find('totFloor').text if item.find('totFloor') is not None else "정보 없음"
                    
                    # 결과 출력
                    st.write(f"건물 높이: {height}m")
                    st.write(f"총 층수: {floors}층")
            else:
                st.write("해당 주소에 대한 정보를 찾을 수 없습니다.")
        else:
            st.write("API 요청에 실패했습니다. 다시 시도해주세요.")
    else:
        st.write("주소를 입력하세요.")
    