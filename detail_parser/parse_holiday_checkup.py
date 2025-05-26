from utils.utils import clean_text


def parse_holiday_checkup(soup):
    result = {}

    holiday_section = soup.find('section', id='holiday-Checkup')
    if not holiday_section:
        return result

    # 주중 공휴일 검진
    weekday_header = holiday_section.find('h3', string=lambda s: s and "주중 공휴일 검진" in s)
    weekday_table = None
    if weekday_header:
        weekday_table = weekday_header.find_next('table')

    weekday_data = []
    if weekday_table:
        cols = [clean_text(th.get_text()) for th in weekday_table.select('thead tr th')]
        for tr in weekday_table.select('tbody tr'):
            values = [clean_text(cell.get_text()) for cell in tr.find_all(['th', 'td'])]
            while len(values) < len(cols):
                values.append('')
            row_dict = {cols[i]: values[i] for i in range(len(cols))}
            weekday_data.append(row_dict)
    result['주중 공휴일 검진'] = weekday_data

    # 일요일 검진 상세 내역
    sunday_header = holiday_section.find('h3', string=lambda s: s and "일요일 검진 상세 내역" in s)
    sunday_table = None
    if sunday_header:
        sunday_table = sunday_header.find_next('table')

    sunday_data = []
    if sunday_table:
        header_rows = sunday_table.select('thead tr')
        col_names = []

        first_header_cells = header_rows[0].find_all(['th', 'td'])
        second_header_cells = header_rows[1].find_all(['th', 'td'])

        col_names.append(first_header_cells[0].get_text(strip=True))
        for th in second_header_cells:
            col_names.append(th.get_text(strip=True))

        for tr in sunday_table.select('tbody tr'):
            th_cell = tr.find('th')
            row_label = th_cell.get_text(strip=True) if th_cell else ""
            td_cells = tr.find_all('td')
            values = [td.get_text(strip=True) for td in td_cells]

            while len(values) < len(col_names) -1:
                values.append('')

            row_dict = {col_names[0]: row_label}
            for i in range(1, len(col_names)):
                row_dict[col_names[i]] = values[i-1]

            sunday_data.append(row_dict)
    result['일요일 검진 상세 내역'] = sunday_data

    return result
