"""
Findable Interface

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Literal

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from sw_selenium.parser import generate_xpath

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement

    from ...driver import SwChrome
    from ..element import SwElement
    from ..elements import SwElements

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
"""
axis_str 타입 설명

"""

expr_str = str
"""
expr_str 타입 설명

"""


class Findable:
    """
    Interface for find, find_all

    """

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
        """
        find

        """
        xpath = xpath or generate_xpath(**locals())
        if self._driver.debug:
            print(f"LOG: find: {xpath=}")
        try:
            return SwElement(
                self._driver._retry(lambda: self.find_element(By.XPATH, xpath))
            )
        except NoSuchElementException:
            if self._driver.debug:
                self._driver._context_finder.search(xpath)
                return SwElement(self.find_element(By.XPATH, xpath))
            else:
                msg = f"\n**Element not found**\n{xpath=}\n"
                raise NoSuchElementException(msg) from None

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
        """
        find or none
        """

        xpath = xpath or generate_xpath(**locals())

        try:
            return SwElement(self.find_element(By.XPATH, xpath))
        except NoSuchElementException:
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
        """
        find all
        """

        xpath = xpath or generate_xpath(**locals())

        self.find(xpath)
        return SwElements([SwElement(e) for e in self.find_elements(By.XPATH, xpath)])

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
        """
        find all or none
        """

        xpath = xpath or generate_xpath(**locals())

        return SwElements([SwElement(e) for e in self.find_elements(By.XPATH, xpath)])
