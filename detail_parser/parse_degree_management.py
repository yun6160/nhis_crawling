def parse_degree_management(soup):
    degree_list = []
    degree_section = None
    for table in soup.find_all('table'):
        caption = table.find('caption')
        if caption and "근무시간외 검진 일정" in caption.text:
            degree_section = table
            break

    if degree_section:
        tbody = degree_section.find('tbody')
        if tbody:
            for tr in tbody.find_all('tr'):
                cols = tr.find_all('td')
                if len(cols) >= 4:
                    degree_list.append({
                        "근무시간 외 검진": cols[0].get_text(strip=True),
                        "내부정도 관리": cols[1].get_text(strip=True),
                        "외부정도 관리": cols[2].get_text(strip=True),
                        "결과통보 우수": cols[3].get_text(strip=True)
                    })
    return degree_list
