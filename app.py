from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import math

# 1️⃣ 드라이버 세팅
options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# 2️⃣ 초기 페이지 진입 (세션 확보용)
driver.get("https://www.nhis.or.kr/nhis/healthin/retrieveExmdAdminSearch.do")

# 3️⃣ fetch용 스크립트 생성 함수
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
    }})
    .then(res => res.json());
    """

# 중복 키 정리 함수
def clean_duplicate_keys(item):
    # 모든 키를 소문자로 통일
    lower_keys_item = {k.lower(): v for k, v in item.items()}

    cleaned = {
        'hpkiho': lower_keys_item.get('hpkiho') or lower_keys_item.get('hp_kiho'),
        'hpname': lower_keys_item.get('hpname') or lower_keys_item.get('hp_name'),
        'hptelno': lower_keys_item.get('hptelno') or lower_keys_item.get('hp_telno'),
        'hpaddr': lower_keys_item.get('hpaddr') or lower_keys_item.get('hp_addr'),
        # 필요하면 다른 필드 추가 가능
        'type_day': lower_keys_item.get('type_day') or lower_keys_item.get('type_day'.upper()),
        'type_hspt': lower_keys_item.get('type_hspt') or lower_keys_item.get('type_hspt'.upper()),
        'type_list': lower_keys_item.get('type_list') or lower_keys_item.get('type_list'.upper())
    }
    # None 값은 제거
    return {k: v for k, v in cleaned.items() if v is not None}

# 4️⃣ 1페이지 요청
first_data = driver.execute_script(fetch_page_script(1, page_size=1320))
total = int(first_data['totalCount'])

# 5️⃣ 실제 페이지 크기 계산
actual_page_size = len(first_data['list'])  # 보통 10
pages = math.ceil(total / actual_page_size)

# 6️⃣ 모든 페이지 순회하며 데이터 수집
all_items = first_data['list']
for p in range(2, pages + 1):
    print(f"{p}페이지 크롤링 중... ({p}/{pages})")  # 진행상황 출력
    page_data = driver.execute_script(fetch_page_script(p, actual_page_size))
    all_items.extend(page_data['list'])

# 7️⃣ 중복 키 정리 적용
cleaned_items = [clean_duplicate_keys(item) for item in all_items]

# 8️⃣ 결과 저장
with open('nhis_all_list.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_items, f, ensure_ascii=False, indent=2)

print(f"총 수집된 항목 수: {len(all_items)} (서버가 알려준 총 건수: {total})")
print(f"중복 키 정리 후 항목 수: {len(cleaned_items)}")
print("정리된 리스트를 'nhis_all_list_cleaned.json' 파일에 저장했습니다.")

driver.quit()
