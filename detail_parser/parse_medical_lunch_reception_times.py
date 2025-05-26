from utils.utils import clean_text

def parse_medical_lunch_reception_times(soup):
    result = {}

    medical_section = soup.find('section', id='Institution-medicalHours')
    if not medical_section:
        return result

    tables = medical_section.find_all('table')
    headers = medical_section.find_all('h3', class_='font bold title md')

    if len(tables) < 3 or len(headers) < 3:
        return result

    # Helper inner function
    def parse_table_with_extra_info(title, table):
        extra = ""
        if '[' in title and ']' in title:
            extra = title.split('[')[-1].rstrip(']')
            title = title.split('[')[0].strip()
        cols = [th.get_text(strip=True) for th in table.select('thead tr th')]
        data = []
        for tr in table.select('tbody tr'):
            values = [clean_text(td.get_text()) for td in tr.find_all('td')]
            # 안내문만 있는 행이면 None 리턴
            if len(values) == 1 and "등록된 데이터가 없습니다" in values[0]:
                return None
            row_dict = {cols[i]: values[i] if i < len(values) else '' for i in range(len(cols))}
            data.append(row_dict)
        return (title, extra, data) if data else None

    # 진료시간
    # med_parsed = parse_table_with_extra_info(headers[0].get_text(strip=True), tables[0])
    # if med_parsed:
    #     med_title, med_extra, med_data = med_parsed
    #     result[med_title] = {"등록일": med_extra, "내용": med_data}
    # 점심시간
    lunch_parsed = parse_table_with_extra_info(headers[1].get_text(strip=True), tables[1])
    if lunch_parsed:
        lunch_title, lunch_extra, lunch_data = lunch_parsed
        result[lunch_title] = {"등록일": lunch_extra, "내용": lunch_data}
    # 접수시간
    # reception_parsed = parse_table_with_extra_info(headers[2].get_text(strip=True), tables[2])
    # if reception_parsed:
    #     reception_title, reception_extra, reception_data = reception_parsed
    #     result[reception_title] = {"등록일": reception_extra, "내용": reception_data}

    return result
