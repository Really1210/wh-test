import streamlit as st
import requests
from xml.etree import ElementTree

# API 키 설정
API_KEY = "aNcRfgfkhHMmk6%2BoALtF4mfxW8RC33Ur9MPkOnJKkjwecj4K7lR8Hdkaw53CtZlSpn0xF7YYe%2BP5lDefgRwksQ%3D%3D"

# Streamlit UI 설정
st.title("건축물 층수 조회")
sigunguCd = st.text_input("시군구 코드를 입력하세요:")
bjdongCd = st.text_input("법정동 코드를 입력하세요:")
bun = st.text_input("번을 입력하세요:")
ji = st.text_input("지를 입력하세요:")

if st.button("조회"):
    if sigunguCd and bjdongCd and bun and ji:
        # API 요청 URL 구성
        url = f"http://apis.data.go.kr/1613000/BldRgstService_v2/getBrTitleInfo?serviceKey={API_KEY}&sigunguCd={sigunguCd}&bjdongCd={bjdongCd}&bun={bun}&ji={ji}&_type=xml"
        
        # API 요청 및 응답 처리
        response = requests.get(url)
        
        if response.status_code == 200:
            # XML 파싱
            tree = ElementTree.fromstring(response.content)
            items = tree.findall('.//item')
            
            if items:
                for item in items:
                    # 지상층수 추출
                    grndFlrCnt = item.find('grndFlrCnt').text if item.find('grndFlrCnt') is not None else "정보 없음"
                    
                    # 결과 출력
                    st.write(f"지상층수: {grndFlrCnt}층")
            else:
                st.write("해당 지번에 대한 정보를 찾을 수 없습니다.")
        else:
            st.write("API 요청에 실패했습니다. 다시 시도해주세요.")
    else:
        st.write("모든 필드를 입력하세요.")