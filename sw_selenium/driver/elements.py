from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from ..parser.xpath_parser import generate_xpath

if TYPE_CHECKING:
    from .element import SwElement
    from .finder.findable import AxisStr, ExprStr


class SwElements:
    def __init__(self, elements: list[SwElement]):
        self._elements = elements
        self._index = 0
        self.texts = [element.text for element in self._elements]

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

    def up(self, levels=1):
        return SwElements([element.up(levels) for element in self._elements])

    def find(
        self,
        xpath="",
        *,
        axis: AxisStr = "descendant",
        tag="*",
        id: ExprStr | None = None,
        id_contains: ExprStr | None = None,
        name: ExprStr | None = None,
        class_name: ExprStr | None = None,
        class_name_contains: ExprStr | None = None,
        text: ExprStr | None = None,
        text_contains: ExprStr | None = None,
        **kwargs: ExprStr,
    ):
        xpath = xpath or generate_xpath(**locals())

        return SwElements([element.find(xpath) for element in self._elements])

    def find_or_none(
        self,
        xpath="",
        *,
        axis: AxisStr = "descendant",
        tag="*",
        id: ExprStr | None = None,
        id_contains: ExprStr | None = None,
        name: ExprStr | None = None,
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

    def get_attributes(
        self,
        name: str,
    ):
        return [element.get_attribute(name) for element in self._elements]
