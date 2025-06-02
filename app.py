from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import math
import time
from detail_parser.detail_parser import parse_detail_html
import pandas as pd

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

# 사용자에게 선택지
while True:
    print("조회할 지역을 선택하세요:")
    print("1. 서울특별시")
    print("2. 경기도")
    print("3. 부산광역시")
    print("4. 대구광역시")
    print("5. 인천광역시")
    print("6. 광주광역시")
    print("7. 대전광역시")
    print("8. 울산광역시")
    print("9. 세종특별자치시")
    print("10. 충청북도")
    print("11. 충청남도")
    print("12. 전라남도")
    print("13. 경상북도")
    print("14. 경상남도")
    print("15. 제주특별자치도")
    print("16. 강원특별자치도")
    print("17. 전북특별자치도")
    choice = input("번호 입력 : ").strip()
    if choice == '1':
        sido = '서울특별시'
        sidoCode = '11'
        break
    elif choice == '2':
        sido = '경기도'
        sidoCode = '41'
        break
    elif choice == '3':
        sido = '부산광역시'
        sidoCode = '26'
        break
    elif choice == '4':
        sido = '대구광역시'
        sidoCode = '27'
        break
    elif choice == '5':
        sido = '인천광역시'
        sidoCode = '28'
        break
    elif choice == '6':
        sido = '광주광역시'
        sidoCode = '29'
        break
    elif choice == '7':
        sido = '대전광역시'
        sidoCode = '30'
        break
    elif choice == '8':
        sido = '울산광역시'
        sidoCode = '31'
        break
    elif choice == '9':
        sido = '세종특별자치시'
        sidoCode = '36'
        break
    elif choice == '10':
        sido = '충청북도'
        sidoCode = '43'
        break
    elif choice == '11':
        sido = '충청남도'
        sidoCode = '44'
        break
    elif choice == '12':
        sido = '전라남도'
        sidoCode = '46'
        break
    elif choice == '13':
        sido = '경상북도'
        sidoCode = '47'
        break
    elif choice == '14':
        sido = '경상남도'
        sidoCode = '48'
        break
    elif choice == '15':
        sido = '제주특별자치도'
        sidoCode = '50'
        break
    elif choice == '16':
        sido = '강원특별자치도'
        sidoCode = '51'
        break
    elif choice == '17':
        sido = '전북특별자치도'
        sidoCode = '52'
        break
    else:
        print("유효한 숫자만 입력해주세요.")

while True:
    print("검진 유형을 선택하세요:")
    print("1. 일반")    # searchExamOrgType1
    print("2. 구강")    # searchExamOrgType3
    print("3. 영유아")  # searchExamOrgType4
    print("4. 학생")    # searchExamOrgType_STDNT
    print("5. 암검진 전체")
    print("6. 세부 암 검진(선택지를 보여드립니다)")
    choice = input("번호 입력 (1 ~ 6): ").strip()

    if choice == '1':
        type = '1'
        type_nm = '일반'
        break
    elif choice == '2':
        type = '3'
        type_nm = '구강'
        break
    elif choice == '3':
        type = '4'
        type_nm = '영유아'
        break
    elif choice == '4':
        type = '_STDNT'
        type_nm = '학생'
        break
    elif choice == '5':
        type = 'cancer_all'
        type_nm = '암검진 전체'
        break
    elif choice == '6':
        while True:
            print("1. 위암")        # searchExamOrgType9_1
            print("2. 대장암")      # searchExamOrgType9_2
            print("3. 자궁경부암")  # searchExamOrgType9_3
            print("4. 유방암")      # searchExamOrgType9_4
            print("5. 간암")        # searchExamOrgType9_5
            print("6. 폐암")        # searchExamOrgType9_6
            choice = input("번호 입력 (1 ~ 6): ").strip()
            if choice == '1':
                type = '9_1'
                type_nm = '위암'
                break
            elif choice == '2':
                type = '9_2'
                type_nm = '대장암'
                break
            elif choice == '3':
                type = '9_3'
                type_nm = '자궁경부암'
                break
            elif choice == '4':
                type = '9_4'
                type_nm = '유방암'
                break
            elif choice == '5':
                type = '9_5'
                type_nm = '간암'
                break
            elif choice == '6':
                type = '9_6'
                type_nm = '폐암'
                break
            else:
                print("1~6 사이 숫자를 입력해주세요.")
        break
    else:
        print("유효한 숫자만 입력해주세요.")

print(f"선택한 지역과 검진: {sido}, {type_nm} (파라미터: {type})")


# 3️⃣ fetch용 스크립트 생성 함수 (기본 리스트)
def fetch_page_script(page_num, page_size, search_sido_nm=sido, search_sido_cd=sidoCode, type=type ):
    base_payload = (
        f"isMobile=N"
        f"&pageNum={page_num}"
        f"&pageFirst={'Y' if page_num == 1 else 'N'}"
        f"&pageSize={page_size}"
        f"&viewType="
        f"&ykiho="
        f"&cur_sido_nm="
        f"&cur_sigungu_nm="
        f"&cur_emd_nm="
        f"&cur_sido="
        f"&cur_sigungu="
        f"&cur_emd="
        f"&search_sido_nm={search_sido_nm}"
        f"&search_sigungu_nm="
        f"&search_emd_nm="
        f"&search_road_nm="
        f"&latitude=37.3246580766&longitude=127.9863282634&lat=&lng=&radius=1000&gpsYn=N"
        f"&yoyangforPat="
        f"&searchType=examOrg"
        f"&searchSpcClinicType=01"
        f"&searchPharmacyDayType="
        f"&searchHpType="
        f"&isParam=N"
        f"&search_year="
        f"&search_sido={search_sido_cd}"
        f"&search_sigungu="
        f"&search_emd_gubun=emd"
        f"&search_emd="
        f"&search_road="
        f"&search_name="
    )

    if type == "cancer_all":
            # 암검진 전체 파라미터 추가
        cancer_params = (
            "&chk_examOrgType9_all=Y"
            "&searchExamOrgType9_1=Y"
            "&searchExamOrgType9_2=Y"
            "&searchExamOrgType9_3=Y"
            "&searchExamOrgType9_4=Y"
            "&searchExamOrgType9_5=Y"
            "&searchExamOrgType9_6=Y"
        )
        payload = base_payload + cancer_params
    else:
        # 기본 검사 유형 파라미터
        payload = base_payload + f"&searchExamOrgType{type}=Y"

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
def fetch_detail_script(ykiho, vlt_year, search_sido_nm=sido, search_sido_cd=sidoCode, type=type):
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
        f"&search_sido_nm={search_sido_nm}"
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
        f"&search_year={vlt_year}"
        f"&search_sido={search_sido_cd}"
        f"&search_sigungu="
        f"&search_emd_gubun=emd"
        f"&search_emd="
        f"&search_road="
        f"&search_name="
    )
    if type == 'cancer_all':
        cancer_params = (
            "&chk_examOrgType9_all=Y"
            "&searchExamOrgType9_1=Y"
            "&searchExamOrgType9_2=Y"
            "&searchExamOrgType9_3=Y"
            "&searchExamOrgType9_4=Y"
            "&searchExamOrgType9_5=Y"
            "&searchExamOrgType9_6=Y"
        )
        payload += cancer_params
    else:
        payload += f"&searchExamOrgType{type}=Y"

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
        '검진기관_식별코드': lower_keys_item.get('hpkiho') or lower_keys_item.get('hp_kiho'),
        '검진기관명': lower_keys_item.get('hpname') or lower_keys_item.get('hp_name'),
        '검진기관_전화번호': lower_keys_item.get('hptelno') or lower_keys_item.get('hp_telno'),
        '검진기관_주소': lower_keys_item.get('hpaddr') or lower_keys_item.get('hp_addr'),
        '검진기관_영업일': lower_keys_item.get('type_day') or lower_keys_item.get('type_day'.upper()),
        '검진기관_우수항목': lower_keys_item.get('type_hspt') or lower_keys_item.get('type_hspt'.upper()),
        '검진기관_항목': lower_keys_item.get('type_list') or lower_keys_item.get('type_list'.upper()),
        '검진기관_평가연도' : lower_keys_item.get('vlt_yyyy') or lower_keys_item.get('vlt_yyyy'.upper())
    }
    return {k: v for k, v in cleaned.items() if v is not None}

# 4️⃣ 1페이지 요청
first_data = driver.execute_script(fetch_page_script(1, page_size=1320))
total = int(first_data['totalCount'])

# 5️⃣ 실제 페이지 크기 계산
actual_page_size = len(first_data['list'])  # 보통 10
pages = math.ceil(total / actual_page_size)

# 시작 시간 기록
start_time = time.time()

# 6️⃣ 모든 페이지 순회하며 데이터 수집 + 상세 데이터 바로 크롤링
all_items = []
for p in range(1, pages + 1):
    print(f"{p}페이지 크롤링 중... ({p}/{pages})")
    page_data = driver.execute_script(fetch_page_script(p, actual_page_size, sido, sidoCode, type))
    page_list = page_data['list']

    # 중복 키 정리
    cleaned_page_items = [clean_duplicate_keys(item) for item in page_list]

    # 상세 데이터 추가 크롤링
    for idx, item in enumerate(cleaned_page_items, start=1):
        ykiho = item.get('검진기관_식별코드')
        vlt_year = item.get('검진기관_평가연도')
        name = item.get('검진기관명')
        # print({name},vlt_year)
        if ykiho:
            # print(f"  상세 데이터 크롤링 중... (페이지 {p} 아이템 {idx}/{len(cleaned_page_items)}) ykiho={ykiho}")
            detail_raw = driver.execute_script(fetch_detail_script(ykiho, vlt_year, sido, sidoCode, type))
            
            try:
                detail_data= json.loads(detail_raw)
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 detail_parser 모듈로 HTML 파싱
                detail_data = parse_detail_html(detail_raw)
            
            item['상세정보'] = detail_data
            time.sleep(0.3)
        else:
            print(f" 식별코드 없음, 상세 데이터 생략 (페이지 {p} 아이템 {idx})")
    # 테스트용 나중에 지우기
    # if p==5:
    #     break

    all_items.extend(cleaned_page_items)

    # ETA 계산
    elapsed = time.time() - start_time
    avg_time_per_page = elapsed / p
    remaining_pages = pages - p
    eta_minutes = (avg_time_per_page * remaining_pages) / 60
    print(f"  경과 시간: {elapsed/60:.2f}분, 예상 남은 시간: {eta_minutes:.2f}분")

# 9️⃣ 결과 저장
with open('nhis_all_list_with_detail.json', 'w', encoding='utf-8') as f:
    json.dump(all_items, f, ensure_ascii=False, indent=2)

# JSON 다시 읽기 (선택 사항, 방금 저장한 파일을 읽어서 DataFrame으로 변환)
with open('nhis_all_list_with_detail.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# JSON 데이터를 pandas DataFrame으로 변환 (복잡한 중첩 데이터도 안전하게 처리)
df = pd.json_normalize(data)

# 3️⃣ 엑셀로 저장
df.to_excel(f'nhis_all_list_with_detail_{sido}_{type_nm}.xlsx', index=False)

print(f"총 수집된 항목 수: {len(all_items)} (서버가 알려준 총 건수: {total})")
print("상세 데이터 포함한 리스트를 'nhis_all_list_with_detail.xlsx' 파일에 저장했습니다.")

driver.quit()
