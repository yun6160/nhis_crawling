def parse_basic_info(soup):
    basic_info = {}
    for dt_tag in soup.select('dl dt'):
        label = dt_tag.get_text(strip=True)
        dd_tag = dt_tag.find_next_sibling('dd')
        value = dd_tag.get_text(strip=True) if dd_tag else None

        if "의사수" in label:
            basic_info['의사수'] = value
        elif "전문과목별" in label:
            basic_info['전문과목별(전문의수)'] = value
        elif "진료과목" in label:
            basic_info['진료과목'] = value
        elif "종별" in label:
            basic_info['종별'] = value
    return basic_info
