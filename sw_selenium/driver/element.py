from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select

from sw_selenium.parsing import generate_xpath

from .elements import SwElements

if TYPE_CHECKING:
    from sw_selenium.parsing.xpath_parser import AxisStr, ExprStr

    from .chrome import SwChrome


class SwElement(WebElement):
    """SwElement"""

    def __init__(self, element: WebElement, xpath: str):
        super().__init__(element.parent, element.id)
        self.driver: SwChrome = super().parent
        self.xpath = xpath

    @property
    def up(self):
        return self.find("..")

    @property
    def down(self):
        return self.find_all_or_none("./*")

    @property
    def left(self):
        return self.find_all_or_none(axis="preceding-sibling")

    @property
    def right(self):
        return self.find_all_or_none(axis="following-sibling")

    def move_mouse(self, offset_x=0, offset_y=0):
        ActionChains(self._parent).move_to_element_with_offset(
            self, offset_x, offset_y
        ).perform()
        return self

    def click(self, by: Literal["enter", "js", "mouse"] = "enter"):
        """기존 python_selenium이 지원하는 click 메서드는 가끔 클릭 안되는 에러가 있으니
        에러가 안나는 방향의 클릭들을 지원함.
        경험적으로 send_keys(Keys.ENTER)가 가장 안전함.
        """
        if by == "enter":
            func = lambda: self.send_keys(Keys.ENTER)
        elif by == "js":
            func = lambda: self.driver.execute_script("arguments[0].click();", self)
        elif by == "mouse":
            func = lambda: ActionChains(self._parent).click(self).perform()

        self.driver.retry(func)

    def select(
        self,
        by: Literal["index", "value", "text"] = "index",
        value: str | int = 0,
    ):
        select = Select(self)
        if by == "index":
            select.select_by_index(int(value))
        elif by == "value":
            select.select_by_value(str(value))
        elif by == "text":
            select.select_by_visible_text(str(value))

    def find(  # noqa: D417
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
        """Finds a single element based on the given criteria.

        Raises:
            NoSuchElementException: If the element is not found.

        Args:
            xpath (str): The XPath of the element to find.

            axis (AxisStr): The axis direction for the search.
            tag (str): The tag name of the element.
            `prop` (ExprStr, optional): The property of the element.(`class` is renamed to `class_name`)
            `prop`_contains (ExprStr, optional): The substring of the property.
            **kwargs (ExprStr): Additional criteria.

        Returns:
            SwElement: The found element.

        Examples:
            ```python
            element = web.find(tag="input", id="username")
            element = web.find(text="Sign In | Sign Up")
            element = web.find(class_name_contains="btn & !primary")
            element = web.find(axis="child")
            element = web.find("//*[contains(@class, 'btn')]")
            # Xpath copied by brower inspector
            ```
        """

        xpath = xpath or generate_xpath(**locals())
        full_xpath = f"{self.xpath}/{xpath}"
        if self.driver.debug:
            print(f"LOG: find: {xpath=}")
        try:
            return SwElement(
                self.driver.retry(lambda: self.find_element(By.XPATH, xpath)),
                full_xpath,
            )
        except NoSuchElementException:
            if self.driver.debug:
                self.driver.context_finder.search(full_xpath)
                return SwElement(self.find_element(By.XPATH, full_xpath), full_xpath)
            else:
                msg = f"\n**Element not found**\n{full_xpath=}\n"
                raise NoSuchElementException(msg) from None

    def find_or_none(  # noqa: D417
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
        """Finds a single element based on the given criteria.

        Difference from `find` method:
        - Does not raise `NoSuchElementException` if the element is not found. Returns `None` instead.

        Args:
            xpath (str): The XPath of the element to find.

            axis (AxisStr): The axis direction for the search.
            tag (str): The tag name of the element.
            `prop` (ExprStr, optional): The property of the element.(**`class` is renamed to `class_name`**)
            `prop`_contains (ExprStr, optional): The substring of the property.
            **kwargs (ExprStr): Additional criteria.

        Returns:
            SwElement: The found element.

        Examples:
            ```python
            element = web.find(tag="input", id="username")
            element = web.find(text="Sign In | Sign Up")
            element = web.find(class_name_contains="btn & !primary")
            element = web.find(axis="child")
            element = web.find("//*[contains(@class, 'btn')]")
            # Xpath copied by brower inspector
            ```
        """

        xpath = xpath or generate_xpath(**locals())
        full_xpath = f"{self.xpath}/{xpath}"

        try:
            return SwElement(self.find_element(By.XPATH, xpath), full_xpath)
        except NoSuchElementException:
            return None

    def find_all(  # noqa: D417
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
        """Finds all elements based on the given criteria.

        Args:
            xpath (str): The XPath of the elements to find.

            axis (AxisStr): The axis direction for the search.
            tag (str): The tag name of the element.
            `prop` (ExprStr, optional): The property of the element.(**`class` is renamed to `class_name`**)
            `prop`_contains (ExprStr, optional): The substring of the property.
            **kwargs (ExprStr): Additional criteria.

        Returns:
            SwElements: The found elements.

        Raises:
            NoSuchElementException: If no elements are found.
        """

        xpath = xpath or generate_xpath(**locals())
        full_xpath = f"{self.xpath}/{xpath}"
        self.find(xpath)
        return SwElements(
            [SwElement(e, full_xpath) for e in self.find_elements(By.XPATH, xpath)]
        )

    def find_all_or_none(  # noqa: D417
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
        """Finds all elements based on the given criteria.
        Difference from `find_all` method:
        - Does not raise `NoSuchElementException` if no elements are found. Returns `None` instead.

        Args:
            xpath (str): The XPath of the elements to find.

            axis (AxisStr): The axis direction for the search.
            tag (str): The tag name of the element.
            `prop` (ExprStr, optional): The property of the element.(**`class` is renamed to `class_name`**)
            `prop`_contains (ExprStr, optional): The substring of the property.
            **kwargs (ExprStr): Additional criteria.

        Returns:
        SwElements | None: The found elements or None if no elements are found.
        """

        xpath = xpath or generate_xpath(**locals())
        full_xpath = f"{self.xpath}/{xpath}"
        return SwElements(
            [SwElement(e, full_xpath) for e in self.find_elements(By.XPATH, xpath)]
        )
