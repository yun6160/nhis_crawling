def parse_evaluation_info(soup):
    evaluation_info = {}
    evaluation_section = soup.find('section', id='evaluation')
    if evaluation_section:
        table = evaluation_section.find('table')
        if table:
            children = [child for child in table.children if child.name in ['thead', 'tbody']]
            i = 0
            while i < len(children):
                if children[i].name == 'thead':
                    thead = children[i]
                    header_rows = thead.find_all('tr')
                    if len(header_rows) < 2:
                        i += 1
                        continue
                    
                    eval_title_th = header_rows[0].find('th')
                    eval_title = eval_title_th.get_text(strip=True) if eval_title_th else "주기명 없음"

                    col_names = [th.get_text(strip=True) for th in header_rows[1].find_all('th')]

                    if i+1 < len(children) and children[i+1].name == 'tbody':
                        tbody = children[i+1]
                        rows = tbody.find_all('tr')
                        data_list = []
                        for tr in rows:
                            cols = tr.find_all(['td', 'th'])
                            row_cells = []
                            for td in cols:
                                colspan = int(td.get('colspan', 1))
                                text = td.get_text(strip=True)
                                row_cells.extend([text] + ['']*(colspan-1))
                            while len(row_cells) < len(col_names):
                                row_cells.append('')
                            row_dict = {col_names[idx]: row_cells[idx] for idx in range(len(col_names))}
                            data_list.append(row_dict)

                        if len(data_list) == 1:
                            evaluation_info[eval_title] = data_list[0]
                        else:
                            evaluation_info[eval_title] = data_list
                        i += 2
                    else:
                        i += 1
                else:
                    i += 1
    return evaluation_info
