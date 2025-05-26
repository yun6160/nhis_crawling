def parse_disability_benefit_section(soup):
    
    section = soup.find('section', id='disabilityBenefits')
    if not section:
        print("disabilityBenefits 섹션을 찾을 수 없습니다.")
        return {}

    table = section.find('table')
    if not table:
        print("장애친화 편익정보 테이블을 찾을 수 없습니다.")
        return {}

    # 원래 컬럼명 가져오기 (thead 없으면 첫 tr 기준)
    cols = [th.get_text(strip=True) for th in table.select('thead tr th')]
    if not cols:
        first_row = table.find('tr')
        if first_row:
            cols = [cell.get_text(strip=True) for cell in first_row.find_all(['th', 'td'])]

    # 새 컬럼명으로 강제 지정
    cols = ["구분", "항목명", "설치 및 구비여부", "검진장비 보유 수 및 기타"]

    rows = table.select('tbody tr')
    if not rows:
        rows = table.find_all('tr')[1:]  # 첫 행은 컬럼명일 가능성 있어 제외

    data_list = []
    rowspan_map = {}  # (row_idx, col_idx) -> text 저장

    for row_idx, tr in enumerate(rows):
        cells = tr.find_all(['th', 'td'])
        values = []
        col_idx = 0
        cell_idx = 0

        while col_idx < len(cols):
            if (row_idx, col_idx) in rowspan_map:
                values.append(rowspan_map[(row_idx, col_idx)])
                col_idx += 1
                continue

            if cell_idx >= len(cells):
                values.append('')
                col_idx += 1
                continue

            cell = cells[cell_idx]
            cell_text = cell.get_text(strip=True)
            cell_idx += 1

            if cell.has_attr('rowspan'):
                span = int(cell['rowspan'])
                for i in range(span):
                    rowspan_map[(row_idx + i, col_idx)] = cell_text

            values.append(cell_text)
            col_idx += 1

        row_dict = {cols[i]: values[i] for i in range(len(cols))}
        data_list.append(row_dict)

    return data_list
