import streamlit as st
from crawler import run_crawler
from datetime import timezone, datetime, timedelta


st.set_page_config(page_title="건강검진기관 크롤러", layout="centered")
st.subheader("🩺 국민건강보험공단 건강검진기관 정보 수집기")

st.markdown(
    """
    <div style="text-align: right;">
        <a href="https://www.nhis.or.kr/nhis/healthin/retrieveExmdAdminSearch.do" target="_blank" style="
            display: inline-block;
            background-color: #ffffff;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            <img src="https://i.namu.wiki/i/_xiPzrb68F58E0Moys2DlWQxzeZj6izoj6Jl1xB3kIttTJWUUU8s8zY-m7B0-BrEA6e3YbxEroJK-JplUgUE9LgFXTiLi7AqdOksm2HuVn_k2mY78QX71fZ4eWXP8Xdywg5tRaDIGtviAw2dixQnNQ.svg" 
                alt="검진기관 찾기" 
                style="height: 40px;">
        </a>
    </div>
    """,
    unsafe_allow_html=True
)


sido = st.selectbox("📍 지역을 선택하세요", ["전체"
,    "서울특별시", "경기도", "부산광역시", "대구광역시", "인천광역시", "광주광역시",
    "대전광역시", "울산광역시", "세종특별자치시", "충청북도", "충청남도",
    "전라남도", "경상북도", "경상남도", "제주특별자치도", "강원특별자치도", "전북특별자치도"
])

type_nm = st.selectbox("🩻 검진 유형을 선택하세요", ["전체",
    "일반", "구강", "영유아", "학생", "암검진 전체",
     "　위암", "　대장암", "　자궁경부암", 
    "　유방암", "　간암", "　폐암"
])

# 검색 버튼을 가운데 정렬
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    search_button = st.button("🚀 데이터 수집 시작", use_container_width=True)

if search_button:
    with st.spinner("크롤링 중입니다. 잠시만 기다려주세요..."):
        progress_placeholder = st.empty()  # 진행률 표시용 공간 확보

        def update_progress(message):
            progress_placeholder.text(message)

        try:
            excel_data = run_crawler(sido.strip(), type_nm.strip(), update_callback=update_progress)
            
            # 진행률 메시지 지우기
            progress_placeholder.empty()
            
            # 크롤링 결과 검증
            if excel_data is None:
                st.error("❌ 크롤링 중 문제가 발생했습니다. 데이터를 가져올 수 없습니다.")
                st.info("💡 다른 지역이나 검진 유형을 선택해서 다시 시도해보세요.")
            else:
                st.success("✅ 크롤링이 완료되었습니다!")
                
                # 한국 시간대로 현재 시간 가져오기
                kst = timezone(timedelta(hours=9))
                now = datetime.now(kst)
                now_str = now.strftime("%Y%m%d_%H%M")
                display_name = f"{now_str}_{sido.strip()}_{type_nm.strip()}_검진기관목록.xlsx"

                # 다운로드 버튼을 가운데 정렬
                st.markdown("---")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    # BytesIO 객체인 경우 getvalue()로 bytes 데이터 추출
                    try:
                        download_data = excel_data.getvalue() if hasattr(excel_data, 'getvalue') else excel_data
                        st.download_button(
                            label="📂 다운로드",
                            data=download_data,
                            file_name=display_name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    except Exception as download_error:
                        st.error(f"❌ 다운로드 데이터 준비 중 오류: {download_error}")
                        
        except Exception as e:
            progress_placeholder.empty()  # 오류 발생 시에도 진행률 메시지 지우기
            st.error(f"❌ 오류 발생: {e}")
            st.info("💡 잠시 후 다시 시도해보세요.")