# NHIS 데이터 수집 스크립트

Selenium과 WebDriver Manager를 사용하여 국민건강보험공단(NHIS) 사이트에서 데이터를 크롤링합니다.

---

## 1. 가상환경 생성 및 활성화 (venv)

### Windows

```bash
cmd 터미널 이용

python -m venv venv
.\venv\Scripts\activate
```

### MAC

```bash
python3 -m venv venv
source venv/bin/activate
```

## 2. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

## 3. 실행 방법

```bash
python app.py
```

```
nhis_crawling/
├── app.py                # Streamlit 앱
├── crawler.py            # 크롤러 비동기 클래스
├── detail_parser/        # HTML fallback 파서
├── utils/                # 유틸리티
```
