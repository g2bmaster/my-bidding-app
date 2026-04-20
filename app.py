import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="나라장터 수동검색기", layout="wide")
st.title("🔍 나라장터 실시간 수동 검색 (크롤링)")

def crawl_g2b():
    # 나라장터 검색 URL (뉴미디어, 유튜브, SNS, 서포터즈 통합 검색)
    # 실제 구현 시에는 검색 파라미터를 복잡하게 조합해야 하므로, 핵심 로직만 구현합니다.
    url = "https://www.g2b.go.kr:8101/ep/tbid/tbidList.do"
    
    # 검색 조건 설정 (최근 7일, 홍보 관련 키워드 등)
    params = {
        'searchCnt': '30',
        'bidNm': '홍보 유튜브 SNS', # 검색어
        'bidType': '1', # 물품/서비스 등
        'fromBidDt': '2026/04/13', # 시작일 (자동 계산 로직 필요)
        'toBidDt': '2026/04/20',   # 종료일
        'budget': '100000000'      # 1억 이상
    }

    try:
        response = requests.get(url, params=params)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 나라장터 테이블의 공고 목록 추출
        table = soup.find('table', {'class': 'table_list'})
        rows = table.find_all('tr')[1:] # 헤더 제외
        
        data = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 1:
                title = cols[3].text.strip()
                price = cols[7].text.strip().replace(',', '') # 예산
                link = "https://www.g2b.go.kr" + cols[3].find('a')['href']
                
                data.append({"공고명": title, "예산": price, "링크": link})
        
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"데이터를 가져오는데 실패했습니다: {e}")
        return pd.DataFrame()

if st.button("지금 바로 나라장터 검색하기"):
    with st.spinner('사이트에서 직접 검색 결과를 가져오는 중...'):
        df = crawl_g2b()
        if not df.empty:
            # 점수 매기기 로직 추가
            df['예산'] = pd.to_numeric(df['예산'], errors='coerce')
            df = df.sort_values(by='예산', ascending=False)
            st.write(f"✅ 검색된 공고 {len(df)}건")
            st.dataframe(df)
        else:
            st.info("검색 조건에 맞는 공고가 없습니다.")
