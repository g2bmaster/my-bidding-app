import streamlit as st
import pandas as pd

st.set_page_config(page_title="공공입찰 맞춤 알리미", layout="wide")

st.title("📊 오늘의 맞춤형 입찰 리스트")
st.info("나라장터(G2B) 1억 이상, 뉴미디어/유튜브/SNS 홍보 공고를 분석합니다.")

# 필터링 및 점수화 로직
def process_data():
    # 샘플 데이터 (추후 API 연동 가능)
    raw_data = [
        {"공고명": "2026 뉴미디어 활용 홍보 캠페인 운영", "예산": 210000000, "자격": "동영상 직접생산, 중소기업 확인서"},
        {"공고명": "유튜브 채널 콘텐츠 제작 및 홍보 사업", "예산": 150000000, "자격": "중소기업 확인서"},
        {"공고명": "공공기관 소셜미디어 서포터즈 모집", "예산": 80000000, "자격": "제한없음"},
    ]
    df = pd.DataFrame(raw_data)
    
    # 순위 계산 알고리즘
    df['점수'] = 0
    df.loc[df['예산'] >= 100000000, '점수'] += 50
    df.loc[df['공고명'].str.contains('뉴미디어|유튜브|SNS|서포터즈'), '점수'] += 30
    df.loc[df['자격'].str.contains('직접생산'), '점수'] += 20
    
    return df.sort_values(by='점수', ascending=False)

df_result = process_data()
st.table(df_result) # 깔끔한 표 형태로 출력

if st.button("내 카톡으로 보고서 전송"):
    st.success("알림 발송 기능이 활성화되었습니다.")
