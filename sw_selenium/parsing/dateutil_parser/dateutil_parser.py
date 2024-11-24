import csv
import re
from pathlib import Path
from typing import TYPE_CHECKING

from sw_selenium.utils.lazy_import import LazyImport

if TYPE_CHECKING:
    from dateutil import parser  # type: ignore[import]
else:
    parser = LazyImport("dateutil", "parser", "python-dateutil")


# CSV 파일을 읽어와서 번역 테이블을 딕셔너리로 변환
def _load_translation_table(csv_file: Path) -> dict:
    translation_table = {}
    with csv_file.open(encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            korean = row["korean"]
            english = row["english"]
            translation_table[korean] = english
    return translation_table


def _rearrange_time(text: str) -> str:
    """정규식을 사용하여 "오전 n시"를 "n시 오전"으로 변환하는 함수"""

    # "오전 n시" 패턴을 "n시 오전"으로 변환
    text = re.sub(r"오전 (\d+)시", r"\1시 오전", text)
    # "오후 n시" 패턴을 "n시 오후"로 변환
    text = re.sub(r"오후 (\d+)시", r"\1시 오후", text)
    return text


# 번역 함수 작성
def _translate_korean_to_english(text: str, translation_table: dict) -> str:
    for korean, english in translation_table.items():
        text = text.replace(korean, english)

    return text


# 번역 테이블 로드

# 현재 파일의 디렉토리 경로를 얻습니다.
csv_file_path = Path(__file__).parent / "kr_to_en_table.csv"

# 파일의 절대 경로를 계산합니다.

translation_table = _load_translation_table(csv_file_path.resolve())


def convert_date_string(date_str: str, *, korean_year=False):
    """한국어나 영어로 된 날짜 문자열을 파싱하는 함수"""
    date_str = _rearrange_time(date_str)
    translated_date = _translate_korean_to_english(date_str, translation_table)
    return parser.parse(translated_date, yearfirst=korean_year)


"""
TEST CODE
"""
if __name__ == "__main__":
    date_string = "00/11/27 2:0:0.1"
    date_string = _rearrange_time(date_string)
    translated_date = _translate_korean_to_english(date_string, translation_table)
    print(translated_date)
    parsed_date = parser.parse(translated_date, yearfirst=True)
    print(parsed_date)
