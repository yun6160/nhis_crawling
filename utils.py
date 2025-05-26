import re
from bs4 import Tag

def clean_text(text: str) -> str:
    """텍스트 앞뒤 공백, 개행, 탭 제거 및 연속 공백 1칸으로 정리"""
    if not text:
        return ''
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_text_from_cell(cell: Tag) -> str:
    """셀에서 텍스트 추출 및 클린징"""
    return clean_text(cell.get_text())

def parse_table_rows_with_rowspan(table) -> list[dict]:
    """
    rowspan이 포함된 테이블에서 올바르게 데이터를 추출하기 위한 유틸 함수
    - colspan은 무시하고 rowspan만 처리
    - 각 행은 딕셔너리로 반환됨 (컬럼명과 매핑해서 사용)
    """
    cols = [clean_text(th.get_text()) for th in table.select('thead tr th')]
    if not cols:
        # thead 없으면 첫 tr에서 컬럼명 추출
        first_row = table.find('tr')
        if first_row:
            cols = [clean_text(cell.get_text()) for cell in first_row.find_all(['th', 'td'])]

    tbody = table.find('tbody')
    rows = tbody.find_all('tr') if tbody else table.find_all('tr')[1:]  # 첫 행 제외

    rowspan_map = {}
    result = []

    for row_idx, tr in enumerate(rows):
        cells = tr.find_all(['td', 'th'])
        values = []
        col_idx = 0

        while col_idx < len(cols):
            if (row_idx, col_idx) in rowspan_map:
                values.append(rowspan_map[(row_idx, col_idx)])
                col_idx += 1
                continue

            if not cells:
                values.append('')
                col_idx += 1
                continue

            cell = cells.pop(0)
            cell_text = extract_text_from_cell(cell)
            values.append(cell_text)

            if cell.has_attr('rowspan'):
                span = int(cell['rowspan'])
                for i in range(1, span):
                    rowspan_map[(row_idx + i, col_idx)] = cell_text

            col_idx += 1

        # 컬럼수 맞게 빈칸 채우기
        while len(values) < len(cols):
            values.append('')

        row_dict = {cols[i]: values[i] for i in range(len(cols))}
        result.append(row_dict)

    return result
