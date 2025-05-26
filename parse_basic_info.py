def parse_basic_info(soup):
    basic_info = {}
    for dt_tag in soup.select('dl dt'):
        label = dt_tag.get_text(strip=True)
        dd_tag = dt_tag.find_next_sibling('dd')
        value = dd_tag.get_text(strip=True) if dd_tag else None

        basic_info[label] = value
    return basic_info
