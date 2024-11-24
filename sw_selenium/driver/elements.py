from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from sw_selenium.parsing import generate_xpath

if TYPE_CHECKING:
    from sw_selenium.parsing.xpath_parser import AxisStr, ExprStr

    from .element import SwElement


class SwElements:
    def __init__(self, elements: list[SwElement]):
        self._elements = elements
        self._index = 0

    def __getitem__(self, index: int):
        return self._elements[index]

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self._elements):
            result = self._elements[self._index]
            self._index += 1
            return result

        raise StopIteration

    def __bool__(self):
        return bool(self._elements)

    def __len__(self):
        return len(self._elements)

    @property
    def text(self):
        """text들 모두 반환 -> text가 없으면 빈 문자열 반환"""
        return [element.text for element in self._elements]

    # 이거 프로퍼티로 바꿔야함 element 따라서
    @property
    def up(self):
        return SwElements([element.up for element in self._elements])

    def down(self, index=0):
        return SwElements([element.down[index] for element in self._elements])

    def left(self, index=0):
        return SwElements([element.left[index] for element in self._elements])

    def right(self, index=0):
        return SwElements([element.right[index] for element in self._elements])

    def find(
        self,
        xpath="",
        /,
        *,
        axis: AxisStr = "descendant",
        tag="*",
        id: ExprStr | None = None,  # noqa: A002
        id_contains: ExprStr | None = None,
        name: ExprStr | None = None,
        class_name: ExprStr | None = None,
        class_name_contains: ExprStr | None = None,
        text: ExprStr | None = None,
        text_contains: ExprStr | None = None,
        num: int | None = None,
        **kwargs: ExprStr,
    ):
        xpath = xpath or generate_xpath(**locals())

        return SwElements([element.find(xpath) for element in self._elements])

    def find_or_none(
        self,
        xpath="",
        /,
        *,
        axis: AxisStr = "descendant",
        tag="*",
        id: ExprStr | None = None,  # noqa: A002
        id_contains: ExprStr | None = None,
        class_name: ExprStr | None = None,
        class_name_contains: ExprStr | None = None,
        text: ExprStr | None = None,
        text_contains: ExprStr | None = None,
        **kwargs: ExprStr,
    ):
        xpath = xpath or generate_xpath(**locals())

        result: list[SwElement] = []
        for element in self._elements:
            if (e := element.find_or_none(xpath)) is not None:
                result.append(e)
        return SwElements(result)

    def click(self, by: Literal["enter", "js", "mouse"] = "enter"):
        for element in self._elements:
            element.click(by)

    def send_keys(self, keys: str | list[str]):
        if isinstance(keys, str):
            for element in self._elements:
                element.send_keys(keys)

        else:
            for element, key in zip(self._elements, keys):
                element.send_keys(key)

    def get_attribute(
        self,
        name: str,
    ):
        return [element.get_attribute(name) for element in self._elements]

    def filter(
        self,
        xpath="",
        *,
        tag="*",
        id: ExprStr | None = None,  # noqa: A002
        id_contains: ExprStr | None = None,
        class_name: ExprStr | None = None,
        class_name_contains: ExprStr | None = None,
        text: ExprStr | None = None,
        text_contains: ExprStr | None = None,
        **kwargs: ExprStr,
    ):
        """find(axis="self")와 동일함"""

        xpath = xpath or generate_xpath(**locals(), axis="self")

        result: list[SwElement] = []
        for element in self._elements:
            if (e := element.find_or_none(xpath)) is not None:
                result.append(e)

        return SwElements(result)

    def wait(
        self,
        dur: float | str | tuple[str, str] | None = None,
        *,
        until: str | None = None,
        korean_year=False,
        display=False,
    ):
        """특정 시간 동안 또는 특정 시간까지 대기합니다.

        Args:
            dur (float | str | tuple[str, str], optional): 대기할 시간. 기본값은 None.
                - float: 대기할 시간 (초 단위).
                - str: 대기할 시간을 나타내는 문자열(한국어 지원) -> dateutil.parser 사용
                    - - "1:04:01", "40mins 5secs", "1시간 32.3초"
                - tuple[str, str]: 대기할 시간을 나타내는 문자열의 범위.
                    - - ("2분 43초", "1시간 4분 53초") -> 1시간 2분 10초 대기

            until (str, optional): 실제 대기할 시간을 나타내는 문자열(한국어 지원)
                - "오후 1시 43분 10초", "21일 13:45:10"

            korean_year (bool, optional): 한국식 년도 표기법을 사용할지 여부. 기본값은 False.
                - False: "01/02/03" -> 2003년 1월 2일
                - True: "01/02/03" -> 2001년 2월 3일

        Examples:
            ```python
            # 5초 대기
            web.wait(dur=5)

            # 1시간 4분 1초 대기
            web.wait(dur="1:04:01")

            # 1시간 2분 10초 대기
            web.wait(dur=("2분 43초", "1시간 4분 53초"))

            # 오전 10시 30분까지 대기
            web.wait(until="오전 10시 30분")
            ```

        """

        self._elements[0].driver.wait(
            dur=dur, until=until, korean_year=korean_year, display=display
        )

        return self
