def parse_parking_info(soup):
    parking_data = {}

    parking_section = soup.find('section', id='Institution-parking')
    if not parking_section:
        return parking_data

    parking_table = parking_section.find('table')
    if not parking_table:
        return parking_data

    cols = [th.get_text(strip=True) for th in parking_table.select('thead tr th')]
    rows_data = []
    for tr in parking_table.select('tbody tr'):
        values = [td.get_text(strip=True) for td in tr.find_all('td')]
        row_dict = {cols[i]: values[i] if i < len(values) else '' for i in range(len(cols))}
        rows_data.append(row_dict)
    parking_data['주차정보'] = rows_data

    return parking_data
