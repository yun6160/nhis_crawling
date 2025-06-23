import asyncio
from io import BytesIO
import aiofiles
import json
import math
import time
import datetime
import pandas as pd
import httpx
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CrawlerConfig:
    """크롤러 설정"""
    timeout: int = 30
    max_retries: int = 3
    concurrent_requests: int = 5
    delay_between_requests: float = 0.1
    
class HealthCheckupCrawler:
    """국민건강보험공단 건강검진기관 정보 크롤러"""
    
    SIDO_MAP = {
        '전체' : '',
        '서울특별시': '11', '경기도': '41', '부산광역시': '26', '대구광역시': '27',
        '인천광역시': '28', '광주광역시': '29', '대전광역시': '30', '울산광역시': '31',
        '세종특별자치시': '36', '충청북도': '43', '충청남도': '44', '전라남도': '46',
        '경상북도': '47', '경상남도': '48', '제주특별자치도': '50',
        '강원특별자치도': '51', '전북특별자치도': '52'
    }
    
    TYPE_MAP = {
        '전체':'',
        '일반': '1', '구강': '3', '영유아': '4', '학생': '_STDNT', '암검진 전체': 'cancer_all',
        '위암': '9_1', '대장암': '9_2', '자궁경부암': '9_3', '유방암': '9_4', '간암': '9_5', '폐암': '9_6'
    }
    
    BASE_URL = "https://www.nhis.or.kr/nhis/healthin"
    LIST_ENDPOINT = "/retrieveMdcAdminInq.do"
    DETAIL_ENDPOINT = "/retrieveMdcAdminDtlInq.do"
    
    def __init__(self, config: CrawlerConfig = None):
        self.config = config or CrawlerConfig()
        self.session: Optional[httpx.AsyncClient] = None
        self.stats = {
            'total_requests': 0,
            'failed_requests': 0,
            'detail_requests': 0,
            'detail_failures': 0
        }
        
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        self.session = httpx.AsyncClient(
            timeout=self.config.timeout,
            limits=httpx.Limits(max_connections=self.config.concurrent_requests)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.aclose()
    
    def _build_base_payload(self, sido: str, sido_code: str, page_num: int, page_size: int) -> str:
        sido_name = "" if sido == "전체" else sido
        """기본 페이로드 생성"""
        return (
            f"isMobile=N&pageNum={page_num}&pageFirst={'Y' if page_num == 1 else 'N'}"
            f"&pageSize={page_size}&viewType=&ykiho=&cur_sido_nm=&cur_sigungu_nm=&cur_emd_nm="
            f"&cur_sido=&cur_sigungu=&cur_emd=&search_sido_nm={sido_name}&search_sigungu_nm=&search_emd_nm="
            f"&search_road_nm=&latitude=37.3246580766&longitude=127.9863282634&lat=&lng=&radius=1000&gpsYn=N"
            f"&yoyangforPat=&searchType=examOrg&searchSpcClinicType=01&searchPharmacyDayType=&searchHpType="
            f"&isParam=N&search_year=&search_sido={sido_code}&search_sigungu=&search_emd_gubun=emd"
            f"&search_emd=&search_road=&search_name="
        )
    
    def _add_type_params(self, payload: str, type_code: str) -> str:
        """검진 유형 파라미터 추가"""
        if type_code == "cancer_all":
            return payload + (
                "&chk_examOrgType9_all=Y&searchExamOrgType9_1=Y&searchExamOrgType9_2=Y"
                "&searchExamOrgType9_3=Y&searchExamOrgType9_4=Y&searchExamOrgType9_5=Y&searchExamOrgType9_6=Y"
            )
        return payload + f"&searchExamOrgType{type_code}=Y"
    
    def _build_list_payload(self, sido: str, sido_code: str, type_code: str, page_num: int, page_size: int) -> str:
        """목록 조회용 페이로드 생성"""
        base = self._build_base_payload(sido, sido_code, page_num, page_size)
        return self._add_type_params(base, type_code)
    
    def _build_detail_payload(self, sido: str, sido_code: str, type_code: str, ykiho: str, vlt_year: str) -> str:
        """상세 조회용 페이로드 생성"""
        payload = (
            f"isMobile=N&pageNum=1&pageFirst=Y&pageSize=5&viewType=&ykiho={ykiho}"
            f"&cur_sido_nm=&cur_sigungu_nm=&cur_emd_nm=&cur_sido=&cur_sigungu=&cur_emd="
            f"&search_sido_nm={sido}&search_sigungu_nm=&search_emd_nm=&search_road_nm="
            f"&latitude=37.3246580766&longitude=127.9863282634&lat=0&lng=0&radius=1000&gpsYn=N"
            f"&yoyangforPat=&searchType=examOrg&searchSpcClinicType=&searchPharmacyDayType="
            f"&searchHpType=&isParam=N&search_year={vlt_year}&search_sido={sido_code}"
            f"&search_sigungu=&search_emd_gubun=emd&search_emd=&search_road=&search_name="
        )
        return self._add_type_params(payload, type_code)
    
    def _clean_item_data(self, item: Dict) -> Dict:
        """아이템 데이터 정리"""
        lower_keys = {k.lower(): v for k, v in item.items()}
        return {
            '검진기관_식별코드': lower_keys.get('hpkiho') or lower_keys.get('hp_kiho'),
            '검진기관명': lower_keys.get('hpname') or lower_keys.get('hp_name'),
            '검진기관_전화번호': lower_keys.get('hptelno') or lower_keys.get('hp_telno'),
            '검진기관_주소': lower_keys.get('hpaddr') or lower_keys.get('hp_addr'),
            '검진기관_영업일': lower_keys.get('type_day'),
            '검진기관_우수항목': lower_keys.get('type_hspt'),
            '검진기관_항목': lower_keys.get('type_list'),
            '검진기관_평가연도': lower_keys.get('vlt_yyyy')
        }
    
    async def _make_request_with_retry(self, url: str, payload: str, request_type: str = "list") -> Optional[Dict]:
        """재시도 로직이 포함된 HTTP 요청"""
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.nhis.or.kr',
            'Referer': 'https://www.nhis.or.kr/nhis/healthin/retrieveExmdAdminSearch.do'
        }
        
        self.stats['total_requests'] += 1
        if request_type == "detail":
            self.stats['detail_requests'] += 1
        
        for attempt in range(self.config.max_retries):
            try:
                response = await self.session.post(url, content=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError) as e:
                if attempt == self.config.max_retries - 1:
                    self.stats['failed_requests'] += 1
                    if request_type == "detail":
                        self.stats['detail_failures'] += 1
                    logger.warning(f"요청 실패 ({request_type}): {e}")
                    return None
                await asyncio.sleep(0.5 * (attempt + 1))  # 지수 백오프
        return None
    
    async def _fetch_page_data(self, sido: str, sido_code: str, type_code: str, page_num: int, page_size: int) -> Optional[Dict]:
        """페이지 데이터 조회"""
        payload = self._build_list_payload(sido, sido_code, type_code, page_num, page_size)
        url = self.BASE_URL + self.LIST_ENDPOINT
        return await self._make_request_with_retry(url, payload, "list")
    
    async def _fetch_detail_data(self, sido: str, sido_code: str, type_code: str, ykiho: str, vlt_year: str) -> Optional[Dict]:
        """상세 데이터 조회"""
        payload = self._build_detail_payload(sido, sido_code, type_code, ykiho, vlt_year)
        url = self.BASE_URL + self.DETAIL_ENDPOINT
        
        try:
            response = await self.session.post(url, content=payload, headers={
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://www.nhis.or.kr',
                'Referer': 'https://www.nhis.or.kr/nhis/healthin/retrieveExmdAdminSearch.do'
            })
            response.raise_for_status()
            
            self.stats['detail_requests'] += 1
            
            # JSON 응답 먼저 시도
            try:
                return response.json()
            except json.JSONDecodeError:
                # HTML 파싱 필요한 경우
                from detail_parser.detail_parser import parse_detail_html
                return parse_detail_html(response.text)
                
        except Exception as e:
            self.stats['detail_failures'] += 1
            logger.warning(f"상세 정보 조회 실패 (ykiho: {ykiho}): {e}")
            return None
    
    async def _process_items_with_details(self, items: List[Dict], sido: str, sido_code: str, type_code: str, 
                                        semaphore: asyncio.Semaphore, update_callback: Optional[Callable] = None) -> List[Dict]:
        """상세 정보를 포함한 아이템 처리"""
        detail_start_time = time.time()
        total_items = len(items)
        processed_count = 0
        
        if update_callback:
            update_callback(f"상세 정보 수집 중... (0/{total_items})")
        
        async def fetch_item_detail(item: Dict) -> Dict:
            nonlocal processed_count
            async with semaphore:
                ykiho = item.get('검진기관_식별코드')
                vlt_year = item.get('검진기관_평가연도', '')
                
                if ykiho:
                    detail_data = await self._fetch_detail_data(sido, sido_code, type_code, ykiho, vlt_year)
                    item['상세정보'] = detail_data
                    
                    processed_count += 1
                    
                    # 20% 단위로만 콜백 호출
                    if update_callback and processed_count % max(1, total_items // 5) == 0:
                        progress = (processed_count / total_items) * 100
                        update_callback(f"상세 정보 수집 중... ({processed_count}/{total_items}, {progress:.0f}%)")
                    
                    await asyncio.sleep(self.config.delay_between_requests)
                
                return item
        
        # 세마포어를 사용해 동시 요청 수 제한
        tasks = [fetch_item_detail(item) for item in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        detail_total_time = time.time() - detail_start_time
        success_count = len([r for r in results if not isinstance(r, Exception)])
        
        if update_callback:
            update_callback(f"상세 정보 수집 완료 ({success_count}/{total_items}개)")
        
        return [r for r in results if not isinstance(r, Exception)]
    
    async def crawl(self, sido: str, type_nm: str, update_callback: Optional[Callable] = None) -> str:
        """메인 크롤링 함수"""
        total_start_time = time.time()
        
        if sido not in self.SIDO_MAP:
            raise ValueError(f"지원하지 않는 지역: {sido}")
        if type_nm not in self.TYPE_MAP:
            raise ValueError(f"지원하지 않는 검진 유형: {type_nm}")
        
        sido_code = self.SIDO_MAP[sido]
        type_code = self.TYPE_MAP[type_nm]
        
        # 첫 페이지로 전체 데이터 수 확인
        if update_callback:
            update_callback("전체 데이터 수 확인 중...")
        
        first_data = await self._fetch_page_data(sido, sido_code, type_code, 1, 1320)
        if not first_data:
            raise Exception("첫 페이지 데이터 조회 실패")
        
        total = int(first_data['totalCount'])
        actual_page_size = len(first_data['list'])
        pages = math.ceil(total / actual_page_size)
        
        if update_callback:
            update_callback(f"총 {total}개 기관, {pages}페이지 수집 시작...")
        
        # 모든 페이지 데이터 수집
        all_items = []
        
        for page_num in range(1, pages + 1):
            if page_num == 1:
                page_data = first_data
            else:
                page_data = await self._fetch_page_data(sido, sido_code, type_code, page_num, actual_page_size)
                if not page_data:
                    continue
            
            page_items = [self._clean_item_data(item) for item in page_data['list']]
            all_items.extend(page_items)
            
            # 20% 단위로만 진행률 업데이트
            if update_callback and (page_num % max(1, pages // 5) == 0 or page_num == pages):
                progress = (page_num / pages) * 100
                update_callback(f"페이지 수집 중... ({page_num}/{pages}, {progress:.0f}%)")
        
        # 상세 정보 수집 (비동기)
        semaphore = asyncio.Semaphore(self.config.concurrent_requests)
        processed_items = await self._process_items_with_details(all_items, sido, sido_code, type_code, semaphore, update_callback)
        
        # 예외 발생한 아이템 필터링
        final_items = [item for item in processed_items if not isinstance(item, Exception)]
        
        df = pd.json_normalize(final_items)
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)  # 포인터 초기화

        if update_callback:
            update_callback(f"완료! 총 {len(final_items)}개 기관 정보 수집")
        
        total_time = time.time() - total_start_time
        
        # 간단한 완료 로그
        logger.info(f"크롤링 완료: {len(final_items)}개 기관, {total_time:.1f}초 소요")
        logger.info(f"요청 성공률: {((self.stats['total_requests'] - self.stats['failed_requests']) / self.stats['total_requests'] * 100):.1f}%")
        
        if update_callback:
            update_callback(f"완료! 총 {len(final_items)}개 기관 정보 수집 (소요시간: {total_time:.1f}초)")
        
        return excel_buffer

# 기존 함수와 호환되는 래퍼 함수
async def run_crawler_async(sido: str, type_nm: str, update_callback: Optional[Callable] = None) -> str:
    """비동기 크롤러 실행"""
    config = CrawlerConfig(
        timeout=30,
        max_retries=3,
        concurrent_requests=3,  # 서버 부하를 고려해 적당히 설정
        delay_between_requests=0.1
    )
    
    async with HealthCheckupCrawler(config) as crawler:
        return await crawler.crawl(sido, type_nm, update_callback)

def run_crawler(sido: str, type_nm: str, update_callback: Optional[Callable] = None) -> str:
    """동기 함수로 비동기 크롤러 실행 (기존 코드와 호환)"""
    return asyncio.run(run_crawler_async(sido, type_nm, update_callback))