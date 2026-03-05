<div align="center">
  <h1>🎲 정석가챠 | 인하대 도서 추천 앱</h1>
  <p><strong>"오늘 당신의 운명은 어떤 서가에 있나요?"</strong></p>
  <p>
    국립중앙도서관 OpenAPI를 활용하여 KDC 대분류 기반으로 무작위 도서를 뽑아주는 <strong>웹 애플리케이션</strong>입니다.<br>
    인하대학교 정석학술정보관 맞춤형 층수 안내 기능을 제공하여, 학생들의 도서관 탐험을 돕습니다!
  </p>
</div>

<br>

## ✨ 핵심 기능

- **🎲 랜덤 도서 가챠**: 사용자가 선택한 KDC 대분류 내에서 랜덤 페이지(1~10)의 100개 도서 중 한 권을 뽑아줍니다.
- **📚 국립중앙도서관 OpenAPI 연동**: 방대한 양의 실제 도서 데이터베이스를 기반으로 결과의 신뢰도를 높였습니다.
- **📍 인하대 맞춤 층수 안내**: KDC 분류 번호를 분석해 인하대학교 정석학술정보관의 예상 위치(1~5층 자료실 등)를 직관적으로 안내합니다.
- **🌙 다크 모드 힙한 UI**: Streamlit의 네이티브 기능을 커스텀하여 힙하고 세련된 다크 모드 카드 디자인을 적용했습니다.

---

## 🚀 실행 방법 (Getting Started)

### 1️⃣ 요구사항 (Prerequisites)
- [Python 3.8+](https://www.python.org/downloads/)
- [Streamlit](https://streamlit.io/) (`pip install streamlit`)
- [Requests](https://pypi.org/project/requests/) (`pip install requests`)

### 2️⃣ 설치 및 실행 (Installation & Run)

```bash
# 1. 레포지토리 클론
git clone https://github.com/사용자아이디/inha-gacha-app.git
cd inha-gacha-app

# 2. 필수 라이브러리 설치
pip install streamlit requests

# 3. 국립중앙도서관 OpenAPI 키 발급 및 설정
```
> **🔑 API 키 설정 가이드**
> - [국립중앙도서관 OpenAPI 센터](https://www.nl.go.kr/NL/search/openApi/search.do)에서 무료로 API 키를 발급받으세요.
> - `app.py` 14번째 줄의 `API_KEY = "YOUR_API_KEY_HERE"` 부분을 발급받은 키로 변경해주세요.

```bash
# 4. 애플리케이션 실행
streamlit run app.py
```

---

## 🛠 기술 스택 (Tech Stack)

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white">
</div>

---

## 🎨 화면 미리보기 (Screenshot)

*(향후 실행된 애플리케이션의 멋진 스크린샷 캡쳐본을 이곳에 추가하시면 좋습니다.)*

---

> **Note**: 본 애플리케이션은 인하대학교 학생들을 위한 비공식 사이드 프로젝트입니다.
