from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import math
import time
import detail_parser

# 1️⃣ 드라이버 세팅
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# 2️⃣ 초기 페이지 진입 (세션 확보용)
driver.get("https://www.nhis.or.kr/nhis/healthin/retrieveExmdAdminSearch.do")

# 3️⃣ fetch용 스크립트 생성 함수 (기본 리스트)
def fetch_page_script(page_num, page_size):
    payload = (
        f"isMobile=N"
        f"&pageNum={page_num}"
        f"&pageFirst={'Y' if page_num == 1 else 'N'}"
        f"&pageSize={page_size}"
        f"&viewType=&ykiho=&cur_sido_nm=&cur_sigungu_nm=&cur_emd_nm="
        f"&cur_sido=&cur_sigungu=&cur_emd="
        f"&search_sido_nm=서울특별시&search_sigungu_nm=&search_emd_nm=&search_road_nm="
        f"&latitude=37.3246580766&longitude=127.9863282634&lat=&lng=&radius=1000&gpsYn=N&yoyangforPat="
        f"&searchType=examOrg&searchSpcClinicType=01&searchPharmacyDayType=&searchHpType="
        f"&isParam=N&search_year=&search_sido=11&search_sigungu=&search_emd_gubun=emd"
        f"&search_emd=&search_road=&search_name=&searchExamOrgType1=Y"
    )
    return f"""
    return fetch('https://www.nhis.or.kr/nhis/healthin/retrieveMdcAdminInq.do', {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest'
      }},
      body: '{payload}'
    }}).then(res => res.json());
    """

# 안전하게 상세 데이터 요청 함수 (응답을 텍스트로 받아서 JSON 파싱 시도)
def fetch_detail_script(ykiho):
    payload = (
        f"isMobile=N"
        f"&pageNum=1"
        f"&pageFirst=Y"
        f"&pageSize=5"
        f"&viewType="
        f"&ykiho={ykiho}"
        f"&cur_sido_nm="
        f"&cur_sigungu_nm="
        f"&cur_emd_nm="
        f"&cur_sido="
        f"&cur_sigungu="
        f"&cur_emd="
        f"&search_sido_nm=서울특별시"
        f"&search_sigungu_nm="
        f"&search_emd_nm="
        f"&search_road_nm="
        f"&latitude=37.3246580766"
        f"&longitude=127.9863282634"
        f"&lat=0"
        f"&lng=0"
        f"&radius=1000"
        f"&gpsYn=N"
        f"&yoyangforPat="
        f"&searchType=examOrg"
        f"&searchSpcClinicType="
        f"&searchPharmacyDayType="
        f"&searchHpType="
        f"&isParam=N"
        f"&search_year=2022"
        f"&search_sido=11"
        f"&search_sigungu="
        f"&search_emd_gubun=emd"
        f"&search_emd="
        f"&search_road="
        f"&search_name="
        f"&searchExamOrgType1=Y"
    )
    return f"""
    return fetch('https://www.nhis.or.kr/nhis/healthin/retrieveMdcAdminDtlInq.do', {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://www.nhis.or.kr',
        'Referer': 'https://www.nhis.or.kr/nhis/healthin/retrieveExmdAdminSearch.do'
      }},
      body: '{payload}'
    }})
    .then(res => res.text())
    """

# 중복 키 정리 함수
def clean_duplicate_keys(item):
    lower_keys_item = {k.lower(): v for k, v in item.items()}

    cleaned = {
        'hpkiho': lower_keys_item.get('hpkiho') or lower_keys_item.get('hp_kiho'),
        'hpname': lower_keys_item.get('hpname') or lower_keys_item.get('hp_name'),
        'hptelno': lower_keys_item.get('hptelno') or lower_keys_item.get('hp_telno'),
        'hpaddr': lower_keys_item.get('hpaddr') or lower_keys_item.get('hp_addr'),
        'type_day': lower_keys_item.get('type_day') or lower_keys_item.get('type_day'.upper()),
        'type_hspt': lower_keys_item.get('type_hspt') or lower_keys_item.get('type_hspt'.upper()),
        'type_list': lower_keys_item.get('type_list') or lower_keys_item.get('type_list'.upper())
    }
    return {k: v for k, v in cleaned.items() if v is not None}

# 4️⃣ 1페이지 요청
first_data = driver.execute_script(fetch_page_script(1, page_size=1320))
total = int(first_data['totalCount'])

# 5️⃣ 실제 페이지 크기 계산
actual_page_size = len(first_data['list'])  # 보통 10
pages = math.ceil(total / actual_page_size)

# 6️⃣ 모든 페이지 순회하며 데이터 수집 + 상세 데이터 바로 크롤링
all_items = []
for p in range(1, pages + 1):
    print(f"{p}페이지 크롤링 중... ({p}/{pages})")
    page_data = driver.execute_script(fetch_page_script(p, actual_page_size))
    page_list = page_data['list']

    # 중복 키 정리
    cleaned_page_items = [clean_duplicate_keys(item) for item in page_list]

    # 상세 데이터 추가 크롤링
    for idx, item in enumerate(cleaned_page_items, start=1):
        ykiho = item.get('hpkiho')
        if ykiho:
            print(f"  상세 데이터 크롤링 중... (페이지 {p} 아이템 {idx}/{len(cleaned_page_items)}) ykiho={ykiho}")
            detail_raw = driver.execute_script(fetch_detail_script(ykiho))
            
            try:
                detail_data= json.loads(detail_raw)
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 detail_parser 모듈로 HTML 파싱
                detail_data = detail_parser.parse_detail_html(detail_raw)
            
            item['detail'] = detail_data
            time.sleep(0.3)
            # 테스트용 나중에 지우기
            if idx==3:
                print("3개 처리 완료, 크롤링 종료합니다.")
                break  # 상세 데이터 크롤링 루프 탈출
        else:
            print(f"  ykiho 없음, 상세 데이터 생략 (페이지 {p} 아이템 {idx})")
    # 테스트용 나중에 지우기기
    if p==2:
        break

    all_items.extend(cleaned_page_items)

# 9️⃣ 결과 저장
with open('nhis_all_list_with_detail.json', 'w', encoding='utf-8') as f:
    json.dump(all_items, f, ensure_ascii=False, indent=2)

print(f"총 수집된 항목 수: {len(all_items)} (서버가 알려준 총 건수: {total})")
print("상세 데이터 포함한 리스트를 'nhis_all_list_with_detail.json' 파일에 저장했습니다.")

driver.quit()
