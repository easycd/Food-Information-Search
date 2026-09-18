from urllib import request, parse, error
from bs4 import BeautifulSoup
import os
import datetime
import pandas as pd

HEADERS = {'User-Agent': 'Mozilla/5.0'}
BASE_URL = 'https://www.fatsecret.kr'
# 원본 경로: '/칼로리-영양소/search' (URL 퍼센트 인코딩된 값)
SEARCH_PATH = '/%EC%B9%BC%EB%A1%9C%EB%A6%AC-%EC%98%81%EC%96%91%EC%86%8C/search'

def _fetch_html(url):
    try:
        req = request.Request(url, headers=HEADERS)
        return request.urlopen(req, timeout=5).read().decode('utf-8')
    except error.URLError as e:
        raise ConnectionError(f'fatsecret.kr 접속에 실패했습니다: {e}')


def search_food(keyword, count=10):
    """fatsecret.kr에서 식품명으로 검색해서 후보 리스트를 반환한다"""
    # parse.quoto(str): 문자열을 받아서 URL에 넣을 수 있도록 퍼센트 인코딩된 문자열로 바꿔서 리턴해주는 함수
    url = f'{BASE_URL}{SEARCH_PATH}?q={parse.quote(keyword)}'
    # 예시) keyword = '바나나'
    # url = 'https://www.fatsecret.kr/칼로리-영양소/search?q=바나나'
    html = _fetch_html(url)
    soup = BeautifulSoup(html, 'html.parser')

    rows = soup.select('table.searchResult tr')
    if not rows:
        raise ValueError(f"'{keyword}'에 대한 검색 결과가 없습니다.")

    results = []
    for row in rows[:count]:
        name_a = row.select_one('a.prominent')
        if name_a is None:
            continue
        brand_a = row.select_one('a.brand')
        results.append({
            'name': name_a.get_text(strip=True),
            'brand': brand_a.get_text(strip=True) if brand_a else None,
            'detail_path': name_a['href'],
        })
    # print(results)

    if not results:
        raise ValueError(f"'{keyword}'에 대한 검색 결과가 없습니다.")
    return results


def get_food_detail(food_item):
    """검색 결과 항목 하나를 받아서 칼로리/영양소 요약 + 서빙사이즈 정보를 반환한다"""
    url = f"{BASE_URL}{food_item['detail_path']}"
    html = _fetch_html(url)
    soup = BeautifulSoup(html, 'html.parser')

    fact_table = soup.select_one('div.factPanel table.generic')
    if fact_table is None:
        raise RuntimeError('상세페이지 구조가 변경되어 영양정보를 찾을 수 없습니다.')

    facts = {}
    for td in fact_table.select('td.fact'):
        title = td.select_one('.factTitle')
        value = td.select_one('.factValue')
        if title and value:
            facts[title.get_text(strip=True)] = value.get_text(strip=True)

    servings = []
    serving_header = soup.find('h4', string=lambda s: s and '서빙크기' in s)
    if serving_header:
        serving_table = serving_header.find_next('table')
        for row in serving_table.select('tr[valign="middle"]'):
            tds = row.select('td')
            if len(tds) < 2:
                continue
            for img in tds[0].select('img'):
                img.decompose()
            servings.append({
                'serving': tds[0].get_text(' ', strip=True),
                'calorie': tds[1].get_text(strip=True),
            })

    return {
        'name': food_item['name'],
        'brand': food_item['brand'],
        'facts': facts,
        'servings': servings,
    }


def save_food_data(detail, dirpath='.'):
    """조회한 영양정보를 CSV로 저장한다 (파일명: 식품명_조회시각.csv), 저장 경로를 반환"""
    row = {'name': detail['name'], 'brand': detail['brand']}
    row.update(detail['facts'])
    row['servings'] = '; '.join(f"{s['serving']}: {s['calorie']}kcal" for s in detail['servings'])
    df = pd.DataFrame([row])

    safe_name = detail['name'].replace(' ', '_').replace('/', '_')
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{safe_name}_{timestamp}.csv'
    filepath = os.path.join(dirpath, filename)

    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    return filepath


if __name__ == '__main__':
    candidates = search_food('바나나')
    for c in candidates[:5]:
        print(c)
    print('------------------')

    detail = get_food_detail(candidates[0])
    print(detail)
    print('------------------')

    path = save_food_data(detail)
    print('saved to', path)
