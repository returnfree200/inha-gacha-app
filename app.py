import streamlit as st
import random
import time

# --- 페이지 설정 ---
st.set_page_config(
    page_title="정석가챠 | 인하대 도서 추천",
    page_icon="🎲",
    layout="centered"
)

import requests

# --- API 설정 ---
# TODO: .streamlit/secrets.toml 파일에 OpenAPI 키를 입력하세요.
try:
    API_KEY = st.secrets["API_KEY"]
except (FileNotFoundError, KeyError):
    API_KEY = "YOUR_API_KEY_HERE"

# --- KDC 대분류 정의 ---
KDC_CATEGORIES = {
    "0": "총류",
    "1": "철학",
    "2": "종교",
    "3": "사회과학",
    "4": "자연과학",
    "5": "기술과학",
    "6": "예술",
    "7": "언어",
    "8": "문학",
    "9": "역사"
}

# --- 인하대 맞춤형 로직 ---
def get_location_by_kdc(kdc_code):
    """
    KDC 번호에 따른 인하대학교 정석학술정보관 위치 반환
    """
    kdc_num = int(kdc_code) * 100  # API 호출 시 앞자리만 사용하므로 x100 처리
    
    if 0 <= kdc_num <= 199:
        return "1층 정석라운지 / 헤리티지라운지"
    elif (200 <= kdc_num <= 299) or (700 <= kdc_num <= 999):
        return "2층 인문과학정보실"
    elif 300 <= kdc_num <= 499:
        return "4층 사회과학정보실"
    elif 500 <= kdc_num <= 699:
        return "5층 기술과학정보실"
    else:
        return "위치 정보 없음"

# --- 데이터 가져오기 (OpenAPI 연동 & Fallback) ---
def fetch_books_by_kdc(kdc_code, is_fallback_allowed=True):
    """
    국립중앙도서관 OpenAPI 연동 함수 (에러 발생 시 Mock Data로 자동 우회)
    """
    url = "https://www.nl.go.kr/NL/search/openApi/search.do"
    random_page = random.randint(1, 10)
    
    params = {
        'key': API_KEY,
        'apiType': 'json',
        'kdc': kdc_code,
        'pageSize': 100,
        'pageNum': random_page
    }
    
    try:
        # 응답 지연 시 빠르게 대체 데이터로 넘어가도록 timeout 5초 설정
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("result", {}).get("total", 0) == 0 or not data.get("result", {}).get("item"):
            raise ValueError("검색 결과 없음")
            
        books = data["result"]["item"]
        return books, False  # (데이터, fallback_여부)
        
    except Exception as e:
        if not is_fallback_allowed:
            raise Exception("API 통신 중 오류가 발생했습니다.")
            
        # API 실패 시 빈출되는 Mock Data Fallback
        mock_database = {
            "0": [
                {"titleInfo": "거의 모든 IT의 역사", "authorInfo": "정지훈", "pubYearInfo": "2010", "callNoInfo": "004.09 정78ㄱ", "imageUrl": "https://picsum.photos/seed/it/300/400"},
                {"titleInfo": "도서관의 비밀", "authorInfo": "이정수", "pubYearInfo": "2018", "callNoInfo": "020 이74ㄷ", "imageUrl": "https://picsum.photos/seed/lib/300/400"}
            ],
            "1": [
                {"titleInfo": "철학은 어떻게 삶의 무기가 되는가", "authorInfo": "야마구치 슈", "pubYearInfo": "2019", "callNoInfo": "104 야32ㅊ", "imageUrl": "https://picsum.photos/seed/philo/300/400"}
            ],
            "3": [
                {"titleInfo": "정의란 무엇인가", "authorInfo": "마이클 샌델", "pubYearInfo": "2010", "callNoInfo": "340.2 샌24ㅈ", "imageUrl": "https://picsum.photos/seed/justice/300/400"}
            ],
            "5": [
                {"titleInfo": "클린 코드", "authorInfo": "로버트 C. 마틴", "pubYearInfo": "2013", "callNoInfo": "566.01 마88ㅋ", "imageUrl": "https://picsum.photos/seed/code/300/400"}
            ],
            "8": [
                {"titleInfo": "소년이 온다", "authorInfo": "한강", "pubYearInfo": "2014", "callNoInfo": "813.6 한11ㅅ", "imageUrl": "https://picsum.photos/seed/novel/300/400"}
            ]
        }
        
        fallback_data = mock_database.get(kdc_code, [
            {"titleInfo": f"{KDC_CATEGORIES.get(kdc_code, '도서')} 추천서", "authorInfo": "정석가챠봇", "pubYearInfo": "2024", "callNoInfo": f"{kdc_code}00 가11ㅊ", "imageUrl": f"https://picsum.photos/seed/{kdc_code}f/300/400"}
        ])
        
        return fallback_data, True
        
        # 결과가 없는 경우 None 반환
        if data.get("result", {}).get("total", 0) == 0 or not data.get("result", {}).get("item"):
            return None
            
        books = data["result"]["item"]
        return books
        
    except requests.exceptions.RequestException as e:
        # 통신 에러 등 발생 시 예외 발생
        raise Exception("API 통신 중 오류가 발생했습니다. API 키나 네트워크 상태를 확인해주세요.")
    except ValueError: # json 파싱 에러
        raise Exception("API 키가 올바른지 확인해주세요. (인증 실패 시 JSON 형태가 아닐 수 있습니다.)")


# --- 메인 UI ---
def main():
    # 헤더 섹션
    st.markdown("<h1 style='text-align: center; font-size: 3.5rem; margin-bottom: 0px;'>🎲 정석가챠</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888888; font-size: 1.1rem; margin-bottom: 30px;'>오늘 당신의 운명은 어떤 서가에 있나요?</p>", unsafe_allow_html=True)
    
    # 폼 영역: 카테고리 선택 및 버튼
    with st.container():
        selected_kdc = st.selectbox(
            "탐험하고 싶은 분야를 선택하세요 (대분류)",
            options=list(KDC_CATEGORIES.keys()),
            format_func=lambda x: f"{x} - {KDC_CATEGORIES[x]}"
        )
        
        st.write("") # 약간의 여백
        
        # 가챠 버튼 (primary 타입을 적용하여 눈에 띄게)
        is_clicked = st.button("✨ 가챠 돌리기", type="primary", use_container_width=True)
    
    # 결과 영역
    if is_clicked:
        with st.spinner('운명의 책을 고르는 중...'):
            time.sleep(1.2)  # 로딩 연출
            
            try:
                books, is_fallback = fetch_books_by_kdc(selected_kdc)
                
                if not books:
                    st.warning("앗, 운명의 책을 찾지 못했습니다! 검색 조건에 맞는 도서가 없거나 API 응답에 문제가 있을 수 있습니다. 다시 시도해주세요!")
                else:
                    if is_fallback:
                        st.warning("⚠️ **연결 지연 안내**: 현재 국립중앙도서관 서버 응답이 매우 지연되어, **오프라인 샘플 데이터**로 운명의 책을 선별했습니다!")

                    result_book = random.choice(books)
                    expected_location = get_location_by_kdc(selected_kdc)
                    
                    st.balloons()
                    st.write("") # 여백
                    
                    # Streamlit 네이티브 컨테이너
                    with st.container(border=True):
                        col1, col2 = st.columns([1, 2])
                        
                        # 표지 이미지가 비어있는 경우(API 특성) 기본 텍스트 이미지로 대체
                        cover_url = result_book.get("imageUrl")
                        if not cover_url or cover_url.strip() == "":
                            # 임시 표지 (분류코드별 색상 다름)
                            cover_url = f"https://via.placeholder.com/300x400/222222/FFFFFF?text={KDC_CATEGORIES.get(selected_kdc, 'Book')}"
                            
                        with col1:
                            st.image(cover_url, use_container_width=True)
                            
                        with col2:
                            st.markdown(f"#### 📍 {expected_location}")
                            st.subheader(result_book.get('titleInfo', '제목 없음'))
                            
                            author = result_book.get('authorInfo', '저자 미상').replace('지은이:', '').strip()
                            pub_year = result_book.get('pubYearInfo', '연도 미상')
                            st.caption(f"**저자** : {author} &nbsp;|&nbsp; **발행** : {pub_year}년")
                            
                            st.markdown("**청구기호**")
                            call_no = result_book.get('callNoInfo', '청구기호 정보 없음')
                            st.code(call_no, language="plaintext")
                            
                            st.info("청구기호를 메모해서 해당 층으로 찾아가보세요!", icon="💡")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")
                st.info("⚠️ 상단의 API_KEY 변수에 정상적인 국립중앙도서관 OpenAPI 키가 입력되었는지 확인해주세요.")

if __name__ == "__main__":
    main()
