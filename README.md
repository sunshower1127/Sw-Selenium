# Sw Selenium

## How to install

1. `git clone https://github.com/sunshower1127/Sw-Selenium.git`
2. `pip install`
3. `import sw_selenium`

## Getting Started

```python
from sw_selenium.driver import SwChrome

web = SwChrome("keep_browser_open")
web.get("https://google.com")

```

## 특징

1. selenium하고 완벽 호환 -> selenium하고 병행해 쓸 수 있음.

# What's the difference with Selenium

- sw_selenium
  - driver
    - SwChrome: 크롬 드라이버 다양한 옵션을 쉽게 줄 수 있음.
      - .find(), .find_or_none(), .find_all(), .find_all_or_none(): 새로 해석한 find_element 함수들
  - debugger
    - debugger: 디버거
  - builder
    - builder: 빌더 (pyinstaller모듈 필요)
  - ui_mananger -> tk 모듈 필요
    - get_input_from_alert(): 알림창 띄워서 값 입력 받기
    - get_button_choice(): 여러개 버튼 띄워서 선택 받기
    - get_data_from_file_or_ui(): file에서 데이터 읽어오기. file이 없으면 ui에서 받아서 file에 저장.
  - parser
    - convert_date_string(): 한글, 영어로된 다양한 날짜, 시간 포맷을 datetime값으로 반환
    - decipher_captcha(): 숫자로된 캡챠 풀어주는 함수 (tesseract 설치필요, opencv, numpy 모듈 필요)
    - generate_xpath(): 인자 받아서 xpath 만들어주는 함수
