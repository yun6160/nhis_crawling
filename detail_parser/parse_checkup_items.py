def parse_checkup_items(soup):
    checkup_items = {}
    checkup_section = soup.find('h3', string=lambda s: s and "검진항목" in s)
    if checkup_section:
        ul_tag = checkup_section.find_next('ul')
        if ul_tag:
            for li in ul_tag.find_all('li'):
                item_name_tag = li.find('em')
                status_tag = li.find('span')
                item_name = item_name_tag.get_text(strip=True) if item_name_tag else None
                status = status_tag.get_text(strip=True) if status_tag else None
                if item_name:
                    checkup_items[item_name] = status
    return checkup_items
