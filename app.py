import streamlit as st
from crawler import run_crawler
import datetime
import os

st.set_page_config(page_title="건강검진기관 크롤러", layout="centered")
st.title("🩺 국민건강보험공단 건강검진기관 정보 수집기")

sido = st.selectbox("📍 지역을 선택하세요", [
    "서울특별시", "경기도", "부산광역시", "대구광역시", "인천광역시", "광주광역시",
    "대전광역시", "울산광역시", "세종특별자치시", "충청북도", "충청남도",
    "전라남도", "경상북도", "경상남도", "제주특별자치도", "강원특별자치도", "전북특별자치도"
])

type_nm = st.selectbox("🩻 검진 유형을 선택하세요", [
    "일반", "구강", "영유아", "학생", "암검진 전체",
    "위암", "대장암", "자궁경부암", "유방암", "간암", "폐암"
])

if st.button("🚀 데이터 수집 시작"):
    with st.spinner("크롤링 중입니다. 잠시만 기다려주세요..."):
        progress_placeholder = st.empty()  # 진행률 표시용 공간 확보

        def update_progress(message):
            progress_placeholder.text(message)

        try:
            filename = run_crawler(sido, type_nm, update_callback=update_progress)
            st.success("✅ 크롤링이 완료되었습니다!")
            now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            display_name = f"{now_str}_{sido}_{type_nm}_검진기관목록.xlsx"

            # 다운로드 버튼을 깔끔하게 카드를 이용해 배치
            with st.container():
                st.markdown("---")
                st.subheader("📂 엑셀 파일 다운로드")
                with open(filename, "rb") as f:
                    st.download_button(
                        label="⬇️ 다운로드 하기",
                        data=f,
                        file_name=display_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")
