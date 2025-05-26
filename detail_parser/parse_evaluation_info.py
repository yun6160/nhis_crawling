def parse_evaluation_info(soup):
    evaluation_info = {}
    evaluation_section = soup.find('section', id='evaluation')

    if not evaluation_section:
        return evaluation_info

    table = evaluation_section.find('table')
    if not table:
        return evaluation_info

    # thead/tbody 페어 추출 (recursive=False 중요!)
    theads = table.find_all('thead', recursive=False)
    tbodys = table.find_all('tbody', recursive=False)

    # 일반적으로 순서대로 붙음 (thead, tbody, thead, tbody, ...)
    for thead, tbody in zip(theads, tbodys):
        header_rows = thead.find_all('tr')
        if len(header_rows) < 2:
            continue
        eval_title = header_rows[0].find('th').get_text(strip=True)
        col_names = [th.get_text(strip=True) for th in header_rows[1].find_all('th')]

        rows = tbody.find_all('tr')
        data_list = []
        for tr in rows:
            cols = tr.find_all(['td', 'th'])
            row_cells = []
            for td in cols:
                colspan = int(td.get('colspan', 1))
                text = td.get_text(strip=True)
                row_cells.extend([text] + [''] * (colspan - 1))
            while len(row_cells) < len(col_names):
                row_cells.append('')
            row_dict = {col_names[idx]: row_cells[idx] for idx in range(len(col_names))}
            data_list.append(row_dict)
        if data_list:
            evaluation_info[eval_title] = data_list if len(data_list) > 1 else data_list[0]

    return evaluation_info
