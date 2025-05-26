from utils.utils import clean_text


def parse_reservation_status(soup):
    reservation_data = {}

    reservation_section = soup.find('section', id='reservationStatus')
    if not reservation_section:
        return reservation_data

    # 영유아검진 예약 안내
    baby_checkup_table = None
    baby_checkup_header = reservation_section.find('h3', string=lambda s: s and "영유아검진 예약 안내" in s)
    if baby_checkup_header:
        baby_checkup_table = baby_checkup_header.find_next('table')

    baby_checkup_data = []
    if baby_checkup_table:
        cols = [th.get_text(strip=True) for th in baby_checkup_table.select('thead tr th')]
        for tr in baby_checkup_table.select('tbody tr'):
            values = [clean_text(td.get_text()) for td in tr.find_all('td')]
            row_dict = {cols[i]: values[i] if i < len(values) else '' for i in range(len(cols))}
            baby_checkup_data.append(row_dict)
    reservation_data['영유아검진 예약 안내'] = baby_checkup_data

    # 검진 가능시간
    checkup_time_table = None
    checkup_time_header = reservation_section.find('h3', string=lambda s: s and "검진 가능시간" in s)
    if checkup_time_header:
        checkup_time_table = checkup_time_header.find_next('table')

    checkup_time_data = []
    if checkup_time_table:
        cols = [th.get_text(strip=True) for th in checkup_time_table.select('thead tr th')]
        for tr in checkup_time_table.select('tbody tr'):
            values = [clean_text(td.get_text()) for td in tr.find_all('td')]
            row_dict = {cols[i]: values[i] if i < len(values) else '' for i in range(len(cols))}
            checkup_time_data.append(row_dict)
    reservation_data['검진 가능시간'] = checkup_time_data

    return reservation_data
