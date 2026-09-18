# fatsecret.kr 영양성분 조회 프로그램

[fatsecret.kr](https://www.fatsecret.kr) 웹사이트를 **정적 크롤링**하여 식품의 칼로리·영양성분 정보를 조회하고 CSV로 저장하는 미니 프로젝트입니다.

## 동작 방식

브라우저 렌더링이나 JavaScript 실행 없이, `urllib.request`로 페이지의 HTML을 그대로 받아온 뒤 `BeautifulSoup`으로 원하는 데이터만 파싱해내는 **정적(static) 크롤링** 방식입니다.

1. 검색어를 URL 쿼리스트링에 담아 검색 결과 페이지 HTML을 요청
2. `table.searchResult`에서 식품명/브랜드/상세페이지 링크를 추출
3. 선택한 식품의 상세페이지 HTML을 요청
4. `div.factPanel table.generic`에서 영양성분 표를, 서빙크기 표에서 사이즈별 칼로리를 추출
5. 결과를 CSV로 저장 (`pandas`, `utf-8-sig` 인코딩)

## 파일 구성

| 파일 | 설명 |
|---|---|
| `fatsecret_food_data.py` | 크롤링/파싱/저장 로직 (`search_food`, `get_food_detail`, `save_food_data`) |
| `fatsecret_food_ui.py` | `tkinter` 기반 GUI (검색 → 목록 선택 → 상세 조회 → CSV 저장) |
| `requirements.txt` | 의존 패키지 목록 |

## 요구 사항

- Python 3.x
- 외부 패키지: `beautifulsoup4`, `pandas`

```bash
pip install -r requirements.txt
```

> `ModuleNotFoundError: No module named 'bs4'` 가 뜬다면 위 명령으로 `beautifulsoup4`가 설치되어 있는지 먼저 확인하세요.

## 실행 방법

GUI로 실행:

```bash
python fatsecret_food_ui.py
```

데이터 모듈만 단독 실행(콘솔 테스트, `바나나` 검색 예시):

```bash
python fatsecret_food_data.py
```

## 사용 방법 (GUI)

1. 식품명을 입력하고 **검색** 버튼 클릭 → 검색 결과 목록 표시
2. 목록에서 항목을 선택하고 **영양정보 보기** 클릭 → 영양성분/서빙사이즈별 칼로리 표시
3. **저장** 버튼 클릭 → `식품명_조회시각.csv` 형식으로 현재 폴더에 CSV 저장

## 주요 함수

- `_fetch_html(url)`: `User-Agent` 헤더를 실어 페이지를 요청하고 `utf-8`로 디코딩한 HTML 문자열을 반환하는 내부 헬퍼
- `search_food(keyword, count=10)`: 식품명으로 검색해 후보 리스트 반환
- `get_food_detail(food_item)`: 후보 항목 하나의 영양성분 + 서빙사이즈별 칼로리 반환
- `save_food_data(detail, dirpath='.')`: 조회 결과를 CSV로 저장하고 저장 경로 반환

## 참고 / 한계

- fatsecret.kr의 HTML 구조에 의존하는 CSS 선택자 기반 파싱이라, 사이트 구조가 바뀌면 파싱이 깨질 수 있습니다.
- 정적 크롤링이므로 JavaScript로 동적 렌더링되는 콘텐츠는 가져오지 못합니다.
- 학습/개인 용도의 미니 프로젝트이며, 실제 서비스에 사용할 경우 대상 사이트의 이용약관 및 `robots.txt`를 확인해야 합니다.
