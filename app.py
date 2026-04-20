import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="맞춤형 입찰 알리미", layout="wide")
st.title("📡 실시간 맞춤형 입찰 공고 리스트")

# --- 설정 (발급받은 인증키를 여기에 입력하세요) ---
API_KEY = "61203561a5f6b1757e496997889aa776c9484657a36d4aaea2de18b25192393b" 
# ------------------------------------------

def fetch_g2b_data():
    # 1. 날짜 설정 (오늘부터 30일 전까지)
    end_date = datetime.now().strftime('%Y%m%d%H%M')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d%H%M')
    
    url = 'http://apis.data.go.kr/1230000/BidPublicInfoService05/getBidPblancListInfoPrcsng01'
    
    # 2. 검색 키워드 설정
    keywords = [
        "뉴미디어", "유튜브", "sns", "온라인홍보", "농촌", "여행", "친환경"
        "문화", "관광", "서포터즈", "외국인", "글로벌", "홍보", "캠페인"
    ]
    keyword_query = "|".join(keywords) # 키워드들을 '또는(OR)' 조건으로 묶음

    params = {
        'serviceKey': API_KEY,
        'numOfRows': '300', # 넉넉하게 300건 조회
        'pageNo': '1',
        'inqryDiv': '1', # 공고게시일 기준
        'inqryBgnDt': start_date,
        'inqryEndDt': end_date,
        'type': 'json'
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'response' in data and 'body' in data['response'] and 'items' in data['response']['body']:
            items = data['response']['body']['items']
            df = pd.DataFrame(items)
            
            # 필요한 컬럼만 추출
            # bidNtceNm: 공고명, bdgtAmt: 배정예산, ntceSpecNm: 입찰자격, bidNtceDtlUrl: 상세페이지URL
            df = df[['bidNtceNm', 'bdgtAmt', 'ntceSpecNm', 'bidNtceDtlUrl', 'bidNtceDt']]
            df.columns = ['공고명', '예산', '자격요건', '상세링크', '게시일시']
            
            # 3. 예산 필터링 (1억 원 이상)
            df['예산'] = pd.to_numeric(df['예산'], errors='coerce').fillna(0)
            df = df[df['예산'] >= 100000000]
            
            # 4. 확장된 키워드 필터링 (공고명에 키워드가 포함된 경우)
            df = df[df['공고명'].str.contains(keyword_query, case=False, na=False)]
            
            # 최신순 정렬
            df = df.sort_values(by='게시일시', ascending=False)
            
            return df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"데이터 연결 중 오류 발생: {e}")
        return pd.DataFrame()

# 앱 화면 구성
st.markdown(f"### 🔍 검색 조건: 1억 이상 / 30일 이내 게시 / {len(['뉴미디어', '유튜브', 'sns', '온라인홍보', '농촌', '문화', '관광', '서포터즈', '외국인', '글로벌', '홍보', '캠페인'])}개 핵심 키워드")

if st.button("최신 공고 데이터 가져오기"):
    with st.spinner('나라장터 서버에서 실시간 데이터를 분석 중입니다...'):
        result = fetch_g2b_data()
        
        if not result.empty:
            st.success(f"조건에 맞는 공고 {len(result)}건을 찾았습니다.")
            # 상세링크를 클릭 가능하게 표시
            st.write("※ 상세링크 주소를 복사하여 브라우저에 붙여넣으시면 공고문을 보실 수 있습니다.")
            st.dataframe(result, use_container_width=True)
        else:
            st.warning("지난 7일간 해당 키워드와 예산 조건에 맞는 새로운 공고가 없습니다.")
