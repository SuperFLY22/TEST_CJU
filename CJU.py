import requests
import streamlit as st
from datetime import datetime

# 🌐 API 정보
API_KEY = 'lfyKqa4L957AUJuYVxMy4fkoXTZxsEESTQgiprYC6Po8hFyBi8IfRrMSqVyP8ft8p8gHbxC3SL40V9C1Vw1zzA=='
url = 'https://api.odcloud.kr/api/FlightStatusListDTL/v1/getFlightStatusListDetail'

# ⏱ 시간 필터링 함수
def time_in_range(time_str, start='0800', end='2000'):
    return start <= time_str <= end

# 🕒 현재 시각을 HHMM 형식으로 가져오기 (예: 1532)
current_time = datetime.now().strftime("%H%M")

# 🎛 Streamlit 사이드바 조건 설정
st.sidebar.title("항공편 필터 설정")
start_time = st.sidebar.text_input("도착시간 시작 (HHMM)", current_time)
end_time = st.sidebar.text_input("도착시간 종료 (HHMM)", "2000")
target_airline = st.sidebar.text_input("항공사 이름 포함", "티웨이항공")
target_arrival = st.sidebar.text_input("도착지 이름 포함", "제주")
page_limit = st.sidebar.slider("조회할 최대 페이지 수", 1, 30, 10)

st.markdown("✈️ 조건에 맞는 항공편 조회")

# 🔍 항공편 데이터 조회
filtered = []

for page in range(1, page_limit + 1):
    params = {
        'page': page,
        'perPage': 100,
        'serviceKey': API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        result = response.json()
        data = result.get('data', [])

        for flight in data:
            airline = flight.get('AIRLINE_KOREAN', '')
            arrival = flight.get('BOARDING_KOR', '')
            etd = flight.get('ETD') or '정보 없음'
            std = flight.get('STD') or '정보 없음'
            flight_no = flight.get('AIR_FLN', '')
            departure = flight.get('ARRIVED_KOR', '')
            gate = flight.get('GATE') or '미지정'

            if (
                target_airline in airline and
                target_arrival in arrival and
                time_in_range(etd, start_time, end_time)
            ):
                filtered.append({
                    '편명': flight_no,
                    '출발지': departure,
                    '도착지': arrival,
                    '예정시간': std,
                    '변경시간': etd,
                    '탑승구': gate
                })
    else:
        st.error(f'{page}페이지 요청 실패. 상태코드: {response.status_code}')

# ✅ 정렬: 변경시간 기준 오름차순
filtered.sort(key=lambda x: x['변경시간'])

# 📊 결과 출력
if not filtered:
    st.warning("조건에 맞는 항공편이 없습니다.")
else:
    st.success(f"조건에 맞는 항공편 {len(filtered)}건이 조회되었습니다.")
    display_data = [
        {
            '편명': f['편명'],
            '출발지': f['출발지'],
            '도착지': f['도착지'],
            '예정시간': f['예정시간'],
            '변경시간': f['변경시간'],
            '탑승구': f['탑승구']
        }
        for f in filtered
    ]
    st.dataframe(display_data)
