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
import re


# --- KDC 대분류 정의 ---
KDC_CATEGORIES = {
    "000": "총류",
    "100": "철학",
    "200": "종교",
    "300": "사회과학",
    "400": "언어",
    "500": "순수과학",
    "600": "기술과학",
    "700": "예술",
    "800": "문학",
    "900": "역사"
}

def get_location_by_call_no(call_no):
    """
    청구기호(call_no)에 따른 인하대학교 정석학술정보관 층별 위치 반환
    """
    call_no_str = str(call_no).strip()
    match = re.search(r'(?:^|[A-Za-z가-힣\s])(\d+(?:\.\d+)?)', call_no_str)
    
    if not match:
        return "정석학술정보관 (위치 정보 없음)"
        
    num = float(match.group(1))
    
    # 000 총류
    if 0 <= num < 100:
        if 1.5 <= num <= 6.69:
            return "2층 자연과학정보실 (컴퓨터)"
        elif 1.3 <= num < 1.5 or 6.69 < num < 90:
            return "3층 인문과학정보실 (인문학)"
        else:
            return "4층 사회과학정보실 (학문일반)"
    # 100 철학 / 200 종교
    elif 100 <= num < 300:
        return "3층 인문과학정보실"
    # 300 사회과학
    elif 300 <= num < 400:
        return "4층 사회과학정보실"
    # 400 언어
    elif 400 <= num < 500:
        return "3층 인문과학정보실"
    # 500 순수과학
    elif 500 <= num < 600:
        return "2층 자연과학정보실"
    # 600 기술과학
    elif 600 <= num < 700:
        if num < 630: # 600~629
            return "2층 자연과학정보실"
        else:
            return "4층 사회과학정보실"
    # 700 예술
    elif 700 <= num < 800:
        return "4층 사회과학정보실"
    # 800 문학
    elif 800 <= num < 900:
        return "3층 인문과학정보실"
    # 900 역사
    elif 900 <= num < 1000:
        if 910 <= num < 920:
            return "4층 사회과학정보실"
        else:
            return "3층 인문과학정보실"
            
    return "정석학술정보관 (위치 정보 없음)"

# --- 데이터 가져오기 (Inha OpenAPI 연동 & Fallback) ---
def fetch_books_by_kdc(kdc_code, max_retries=10):
    """
    인하대학교 정석학술정보관 API 연동 함수
    트래픽 제한을 위해 최대 max_retries 만큼 페이징(offset)을 늘려가며 요청합니다.
    """
    # 보안을 위해 API URL은 Streamlit Secrets에서 가져옵니다. (.streamlit/secrets.toml)
    try:
        url = st.secrets["LIBRARY_API_URL"]
    except KeyError:
        return None, "api_url_not_found"
    
    # 먼저 해당 카테고리의 총 도서 수(totalCount)를 파악하기 위해 가벼운 예비 요청을 보냅니다.
    total_count = 200  # 예비 요청 실패 시 사용할 기본값
    try:
        probe_params = {
            'ALL': f'cl|a|{str(kdc_code)[:1]}',
            'max': 1,  # 최소한의 데이터만 요청
            'offset': 0,
            'facet': 'true',
            'fuzzy': 'true',
            'isForPyxis3': 'true'
        }
        probe_res = requests.get(url, params=probe_params, timeout=5)
        if probe_res.status_code == 200:
            total_count = probe_res.json().get("data", {}).get("totalCount", 200)
    except Exception:
        pass # 파악 실패 시 무시하고 진행
        
    # 데이터가 너무 적을 때를 대비하고 최대치를 100,000건(안전 한계선)으로 제한합니다.
    max_possible_offset = min(total_count - 200, 100000)
    if max_possible_offset <= 0:
        max_possible_offset = 0
        
    # 한 번에 200권씩 가져오므로 시작점(offset)도 200 단위로 건너뛰어 넓은 범위를 훑습니다
    max_steps = max_possible_offset // 200
    current_offset = random.randint(0, max_steps) * 200
    fallback_reason = "timeout"
    
    for attempt in range(max_retries):
        # pyxis-api 전용 '분류기호(cl)' 검색 적용: 해당 그룹 번호로 시작하는 진짜 도서만 100% 가져옵니다.
        params = {
            'ALL': f'cl|a|{str(kdc_code)[:1]}',
            'max': 200,  # 한 번에 200권 호출하여 확률 극대화
            'offset': current_offset,
            'facet': 'true',
            'fuzzy': 'true',
            'isForPyxis3': 'true'
        }
        
        try:
            # 넉넉한 timeout 설정
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            items = data.get("data", {}).get("list", [])
            
            # API에서 더 이상 가져올 데이터가 없으면 중단
            if not items:
                # 결과가 없으면 offset을 처음(0)으로 되돌려서 재시도
                if current_offset > 0:
                    current_offset = 0
                    continue
                else:
                    fallback_reason = "no_results"
                    break
                
            books = []
            for item in items:
                branch_vols = item.get("branchVolumes", [])
                
                # 정석학술정보관 실물 도서가 아니거나 청구기호 정보가 아예 없는 데이터(전자자료, 외부자료 등)는 무시
                if not branch_vols or not isinstance(branch_vols, list) or len(branch_vols) == 0:
                    continue
                    
                call_no_info = branch_vols[0].get("volume")
                if not call_no_info:
                    continue
                    
                title = item.get("titleStatement") or "제목 없음"
                author = item.get("author") or "저자 미상"
                pub_year = item.get("publication") or "연도 미상"
                image_url = item.get("thumbnailUrl") or ""
                
                books.append({
                    "titleInfo": title,
                    "authorInfo": author,
                    "pubYearInfo": pub_year,
                    "callNoInfo": call_no_info,
                    "imageUrl": image_url
                })
                
            # 분류 기호(KDC) 필터링 완화 (어떤 접두어가 붙어있더라도 첫 번째 등장하는 숫자를 KDC로 판별)
            valid_books = []
            for b in books:
                cnum = b["callNoInfo"].upper().strip()
                match = re.search(r'\d+', cnum)
                if match and match.group(0).startswith(str(kdc_code)[:1]):
                    # 저자 미상 도서는 제외합니다.
                    if b["authorInfo"] == "저자 미상":
                        continue
                        
                    # 한글 서적 위주 노출: 제목이나 저자에 한글이 1글자라도 섞인 도서만 선별합니다
                    if re.search(r'[가-힣]', b["titleInfo"]) or re.search(r'[가-힣]', b["authorInfo"]):
                        valid_books.append(b)
                    
            if valid_books:
                # 조건에 맞는 책을 찾았으면 즉시 반환
                return valid_books, None
            else:
                # 조건에 맞는 책이 없으면 offset을 200(max값)만큼 늘려서 다음 페이지 탐색
                current_offset += 200
                fallback_reason = "no_results"
                
        except Exception as e:
            # 네트워크 통신 오류 시 약간의 대기 후 재시도
            time.sleep(1)
            fallback_reason = "timeout"
            continue
            
    # 찾지 못했을 경우 억지로 샘플 데이터를 만들지 않고 사유만 반환하여 UI에 위임
    return None, fallback_reason


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
                books, reason = fetch_books_by_kdc(selected_kdc)
                
                if not books:
                    # 가상 데이터 대신 재시도 안내 출력
                    if reason == "timeout":
                        st.error("⚠️ 도서관 서버 응답이 지연되고 있습니다. 잠시 후 다시 가챠를 돌려주세요! 🔄")
                    elif reason == "api_url_not_found":
                        st.error("⚠️ API URL이 설정되지 않았습니다. 관리자에게 문의하세요.")
                    else:
                        st.warning("⚠️ 해당 분야의 운명의 책을 찾지 못했습니다. 다시 한 번 가챠를 돌려주세요! 🎲")
                else:

                    result_book = random.choice(books)
                    expected_location = get_location_by_call_no(result_book.get('callNoInfo', ''))
                    
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
                st.info("⚠️ 도서관 서버와의 통신이 원활하지 않습니다.")

if __name__ == "__main__":
    main()
