import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="실시간 나라장터 입찰 알리미", layout="wide")
st.title("📡 실시간 맞춤형 입찰 리스트")

API_KEY = "61203561a5f6b1757e496997889aa776c9484657a36d4aaea2de18b25192393b" 
# ------------------------------------------

def fetch_g2b_data():
    # 오늘 기준 최근 7일간의 데이터를 가져옵니다.
    end_date = datetime.now().strftime('%Y%m%d%H%M')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d%H%M')
    
    url = 'http://apis.data.go.kr/1230000/BidPublicInfoService05/getBidPblancListInfoPrcsng01'
    params = {
        'serviceKey': API_KEY,
        'numOfRows': '100',
        'pageNo': '1',
        'inqryDiv': '1',
        'inqryBgnDt': start_date,
        'inqryEndDt': end_date,
        'type': 'json'
    }

    try:
        response = requests.get(url, params=params)
        items = response.json()['response']['body']['items']
        df = pd.DataFrame(items)
        
        # 필요한 컬럼만 추출 및 이름 변경
        df = df[['bidNtceNm', 'bdgtAmt', 'ntceSpecNm', 'bidNtceDtlUrl']]
        df.columns = ['공고명', '예산', '자격요건', '링크']
        
        # 예산 숫자 형변환 및 필터링 (1억 이상)
        df['예산'] = pd.to_numeric(df['예산'], errors='coerce').fillna(0)
        df = df[df['예산'] >= 100000000]
        
        # 키워드 필터링 (뉴미디어, 유튜브, SNS, 서포터즈)
        keywords = '뉴미디어|유튜브|SNS|서포터즈'
        df = df[df['공고명'].str.contains(keywords, na=False)]
        
        # 순위 점수 매기기
        df['점수'] = 0
        df.loc[df['자격요건'].str.contains('직접생산', na=False), '점수'] += 20
        df = df.sort_values(by=['점수', '예산'], ascending=False)
        
        return df
    except:
        return pd.DataFrame()

if st.button("새로운 데이터 불러오기"):
    with st.spinner('나라장터에서 최신 공고를 찾는 중...'):
        result = fetch_g2b_data()
        if not result.empty:
            st.write(f"✅ 총 {len(result)}건의 맞춤 공고를 찾았습니다.")
            st.dataframe(result)
        else:
            st.warning("조건에 맞는 새로운 공고가 현재 없습니다.")
