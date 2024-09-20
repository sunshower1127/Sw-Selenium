from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Literal

from enhanced_selenium._utils.xpath_parser import get_xpath
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select

if TYPE_CHECKING:
    from .driver import SwChrome

axis_str = Literal[
    "ancestor",
    "ancestor-or-self",
    "child",
    "descendant",
    "descendant-or-self",
    "following",
    "following-sibling",
    "parent",
    "preceding",
    "preceding-sibling",
]


expr_str = str


# Interface for find, find_all
class Findable:
    # From other classes
    _driver: SwChrome
    find_element: Callable[[str, str], WebElement]
    find_elements: Callable[[str, str], list[WebElement]]

    def find(
        self,
        xpath="",
        /,
        *,
        axis: axis_str = "descendant",
        tag="*",
        id: expr_str | None = None,
        id_contains: expr_str | None = None,
        name: expr_str | None = None,
        class_name: expr_str | None = None,
        class_name_contains: expr_str | None = None,
        text: expr_str | None = None,
        text_contains: expr_str | None = None,
        **kwargs: expr_str,
    ):
        xpath = xpath or get_xpath(locals())
        print(f"LOG: find: {xpath=}")
        try:
            return Element(
                self._driver._retry(lambda: self.find_element(By.XPATH, xpath))
            )
        except TimeoutException as e:
            if self._driver.debug:
                self._driver._debugfinder.find(xpath)
                return Element(
                    self._driver._retry(lambda: self.find_element(By.XPATH, xpath))
                )
            msg = f"\n**Element not found**\n{xpath=}\n"
            raise TimeoutException(msg) from None

    def find_or_none(
        self,
        xpath="",
        /,
        *,
        axis: axis_str = "descendant",
        tag="*",
        id: expr_str | None = None,
        id_contains: expr_str | None = None,
        name: expr_str | None = None,
        class_name: expr_str | None = None,
        class_name_contains: expr_str | None = None,
        text: expr_str | None = None,
        text_contains: expr_str | None = None,
        **kwargs: expr_str,
    ):
        xpath = xpath or get_xpath(locals())

        try:
            return Element(self.find_element(By.XPATH, xpath))
        except (TimeoutException, NoSuchElementException):
            return None

    def find_all(
        self,
        xpath="",
        /,
        *,
        axis: axis_str = "descendant",
        tag="*",
        id: expr_str | None = None,
        id_contains: expr_str | None = None,
        name: expr_str | None = None,
        class_name: expr_str | None = None,
        class_name_contains: expr_str | None = None,
        text: expr_str | None = None,
        text_contains: expr_str | None = None,
        **kwargs: expr_str,
    ):
        xpath = xpath or get_xpath(locals())

        self.find(xpath)
        return Elements([Element(e) for e in self.find_elements(By.XPATH, xpath)])

    def find_all_or_none(
        self,
        xpath="",
        /,
        *,
        axis: axis_str = "descendant",
        tag="*",
        id: expr_str | None = None,
        id_contains: expr_str | None = None,
        name: expr_str | None = None,
        class_name: expr_str | None = None,
        class_name_contains: expr_str | None = None,
        text: expr_str | None = None,
        text_contains: expr_str | None = None,
        **kwargs: expr_str,
    ):
        xpath = xpath or get_xpath(locals())

        return Elements([Element(e) for e in self.find_elements(By.XPATH, xpath)])
