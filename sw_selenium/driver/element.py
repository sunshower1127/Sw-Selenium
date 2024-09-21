"""
element
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select

from .finder.findable import Findable

if TYPE_CHECKING:
    from .chrome import SwChrome


class SwElement(WebElement, Findable):
    """
    SwElement
    """

    def __init__(self, element: WebElement):
        super().__init__(element.parent, element.id)
        self._driver: SwChrome = super().parent

    def up(self, levels=1):
        xpath = "/".join([".."] * levels)
        return SwElement(
            self._driver._retry(lambda: self.find_element(By.XPATH, xpath))
        )

    def move_mouse(self, offset_x=0, offset_y=0):
        ActionChains(self._parent).move_to_element_with_offset(
            self, offset_x, offset_y
        ).perform()
        return self

    def click(self, by: Literal["enter", "js", "mouse"] = "enter"):
        """
        기존 python_selenium이 지원하는 click 메서드는 가끔 클릭 안되는 에러가 있으니
        에러가 안나는 방향의 클릭들을 지원함.
        default = js
        """
        match by:
            case "enter":
                func = lambda: self.send_keys(Keys.ENTER)
            case "js":
                func = lambda: self._driver.execute_script(
                    "arguments[0].click();", self
                )
            case "mouse":
                func = lambda: ActionChains(self._parent).click(self).perform()

        self._driver._retry(func)

    def select(
        self,
        by: Literal["index", "value", "text"] = "index",
        value: str | int = 0,
    ):
        select = Select(self)
        match by:
            case "index":
                select.select_by_index(int(value))
            case "value":
                select.select_by_value(str(value))
            case "text":
                select.select_by_visible_text(str(value))
