def parse_major_equipment_section(soup):
    equipment_info = {}

    section = soup.find('section', id='PossessionEquipment')
    if not section:
        print("PossessionEquipment 섹션을 찾을 수 없습니다.")
        return equipment_info

    section_divs = section.select('div.section.row-gap-24')

    for div in section_divs:
        header = div.find('h3')
        table = div.find('table')
        if not header or not table:
            continue

        title = header.get_text(strip=True)

        # 암 검사장비 테이블
        if "암 검사장비" in title:
            cols = ["구분", "장비명", "대수"]
            rows = table.select('tbody tr')

            rowspan_map = {}
            rows_data = []
            current_category = None

            for i, tr in enumerate(rows):
                cells = tr.find_all(['th', 'td'])
                values = []
                col_idx = 0

                while col_idx < len(cols):
                    if (i, col_idx) in rowspan_map:
                        values.append(rowspan_map[(i, col_idx)])
                        col_idx += 1
                        continue

                    if not cells:
                        values.append('')
                        col_idx += 1
                        continue

                    cell = cells.pop(0)
                    cell_text = cell.get_text(strip=True)

                    # 첫번째 컬럼 <th>이면서 값이 있을 때 current_category 갱신
                    if col_idx == 0 and cell.name == 'th' and cell_text:
                        current_category = cell_text

                    # 병합 셀 처리 (rowspan)
                    if cell.has_attr('rowspan'):
                        span = int(cell['rowspan'])
                        for r in range(1, span):
                            rowspan_map[(i + r, col_idx)] = cell_text

                    # 첫번째 컬럼이 빈 값이면 현재 카테고리 유지
                    if col_idx == 0 and not cell_text:
                        cell_text = current_category

                    values.append(cell_text)
                    col_idx += 1

                # 부족한 컬럼 빈칸 처리
                while len(values) < len(cols):
                    values.append('')

                row_dict = {cols[i]: values[i] for i in range(len(cols))}
                rows_data.append(row_dict)

            equipment_info[title] = rows_data

        # 골밀도 측정기 테이블
        elif "골밀도 측정기" in title:
            cols = ["장비명", "대수"]
            rows = table.select('tbody tr')

            rows_data = []
            for tr in rows:
                cells = tr.find_all(['th', 'td'])
                # 장비명은 th, 대수는 td
                if len(cells) == 2:
                    equipment_name = cells[0].get_text(strip=True)
                    quantity = cells[1].get_text(strip=True)
                    rows_data.append({
                        cols[0]: equipment_name,
                        cols[1]: quantity
                    })

            equipment_info[title] = rows_data

        else:
            # 그 외 테이블(예상하지 못한 경우)
            cols = [th.get_text(strip=True) for th in table.select('thead tr th')]
            if not cols:
                first_row = table.find('tr')
                if first_row:
                    cols = [cell.get_text(strip=True) for cell in first_row.find_all(['th', 'td'])]

            rows = table.select('tbody tr')
            if not rows:
                rows = table.select('tr')

            rows_data = []
            for tr in rows:
                values = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                while len(values) < len(cols):
                    values.append('')
                row_dict = {cols[i]: values[i] for i in range(len(cols))}
                rows_data.append(row_dict)

            equipment_info[title] = rows_data

    return equipment_info
