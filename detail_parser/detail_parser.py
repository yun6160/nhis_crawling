from bs4 import BeautifulSoup
from .parse_basic_info import parse_basic_info
from .parse_checkup_items import parse_checkup_items
from .parse_degree_management import parse_degree_management
from .parse_evaluation_info import parse_evaluation_info
from .parse_major_equipment_section import parse_major_equipment_section 
from .parse_medical_lunch_reception_times import parse_medical_lunch_reception_times
from .parse_parking_info import parse_parking_info
# from .parse_holiday_checkup import parse_holiday_checkup
# from .parse_disability_benefit_section import parse_disability_benefit_section
# from .parse_reservation_status import parse_reservation_status

def parse_detail_html(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')

    basic_info = {}

    # 기본 정보 추출
    basic_info.update(parse_basic_info(soup))
   
    # 검진항목 정보 추출
    basic_info['검진항목'] = parse_checkup_items(soup)

    # 정도관리실시 정보 추출
    basic_info['정도관리실시'] = parse_degree_management(soup)

    # --- 검진기관 평가정보 추출 시작 ---
    basic_info['검진기관 평가정보'] = parse_evaluation_info(soup)

    # --- 예약현황 섹션 파싱 2025.05.26 필요없음 ---
    # basic_info.update(parse_reservation_status(soup))

    # --- 길찾기·주차 섹션 파싱 ---
    basic_info.update(parse_parking_info(soup))

    # --- 진료·점심·접수시간 섹션 파싱 2025.05.26 점심시간만 필요 ---
    basic_info.update(parse_medical_lunch_reception_times(soup))

    # --- 공휴일검진 섹션 파싱 2025.05.26 필요없음 ---
    # basic_info.update(parse_holiday_checkup(soup))

    # --- 주요장비 보유현황 섹션 파싱 ---
    basic_info['주요장비 보유현황'] = parse_major_equipment_section(soup)

    # 장애친화 편익정보 섹션 파싱 추가 2025.05.26 필요없음
    # basic_info['장애친화 편익정보'] = parse_disability_benefit_section(soup)

    return basic_info
