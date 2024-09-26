"""
Findable Interface

This module provides the Findable interface, which defines methods for finding
single or multiple elements based on various criteria. It includes support for
XPath generation and logical operators for element selection.

Classes:
    Findable: An interface for finding elements.

Types:
    AxisStr: A type representing the direction in which to search for elements
             relative to the current node.
    ExprStr: A type representing a string expression that supports logical
             operators for element selection.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Literal

from lazy_import import lazy_module
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from sw_selenium.parser import generate_xpath

from ..elements import SwElements

if TYPE_CHECKING:
    import sw_selenium.driver.element as sw_element
    from selenium.webdriver.remote.webelement import WebElement

    from ...driver import SwChrome
else:
    sw_element = lazy_module("sw_selenium.driver.element")

AxisStr = Literal[
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
AxisStr type description

Represents the direction in which to search for elements relative to the current node.

For more information, refer to:
https://www.w3schools.com/xml/xpath_axes.asp
"""

ExprStr = str
"""
ExprStr type description

Represents a string expression that supports logical operators for element selection.

Supported operators:
- `|` and `&` for logical OR and AND, respectively. Example: id="id1 | id2"
- `!` for logical NOT. Example: id="!id1"
- Parentheses `()` for grouping. Example: id="(id1 | id2) & !id3"
- Whitespace is supported. Example: text="hi everyone | hello world"
- Both double and single quotes are supported. Example: text="'(01:00)' | '(02:00)'"
"""


class Findable:
    """
    Interface for finding elements.

    Provides methods to find single or multiple elements based on various criteria.
    """

    if TYPE_CHECKING:
        _driver: SwChrome
        find_element: Callable[[str, str], WebElement]  # Already exists in selenium
        find_elements: Callable[
            [str, str], list[WebElement]
        ]  # Already exists in selenium

    def find(
        self,
        xpath="",
        /,
        *,
        axis: AxisStr = "descendant",
        tag="*",
        id: ExprStr | None = None,
        id_contains: ExprStr | None = None,
        class_name: ExprStr | None = None,
        class_name_contains: ExprStr | None = None,
        text: ExprStr | None = None,
        text_contains: ExprStr | None = None,
        **kwargs: ExprStr,
    ):
        """
        Finds a single element based on the given criteria.

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
        if self._driver.debug:
            print(f"LOG: find: {xpath=}")
        try:
            return sw_element.SwElement(
                self._driver._retry(lambda: self.find_element(By.XPATH, xpath))
            )
        except NoSuchElementException:
            if self._driver.debug:
                self._driver._context_finder.search(xpath)
                return sw_element.SwElement(self.find_element(By.XPATH, xpath))
            else:
                msg = f"\n**Element not found**\n{xpath=}\n"
                raise NoSuchElementException(msg) from None

    def find_or_none(
        self,
        xpath="",
        /,
        *,
        axis: AxisStr = "descendant",
        tag="*",
        id: ExprStr | None = None,
        id_contains: ExprStr | None = None,
        class_name: ExprStr | None = None,
        class_name_contains: ExprStr | None = None,
        text: ExprStr | None = None,
        text_contains: ExprStr | None = None,
        **kwargs: ExprStr,
    ):
        """
        Finds a single element based on the given criteria.

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

        try:
            return sw_element.SwElement(self.find_element(By.XPATH, xpath))
        except NoSuchElementException:
            return None

    def find_all(
        self,
        xpath="",
        /,
        *,
        axis: AxisStr = "descendant",
        tag="*",
        id: ExprStr | None = None,
        id_contains: ExprStr | None = None,
        class_name: ExprStr | None = None,
        class_name_contains: ExprStr | None = None,
        text: ExprStr | None = None,
        text_contains: ExprStr | None = None,
        **kwargs: ExprStr,
    ):
        """
        Finds all elements based on the given criteria.

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

        self.find(xpath)
        return SwElements(
            [sw_element.SwElement(e) for e in self.find_elements(By.XPATH, xpath)]
        )

    def find_all_or_none(
        self,
        xpath="",
        /,
        *,
        axis: AxisStr = "descendant",
        tag="*",
        id: ExprStr | None = None,
        id_contains: ExprStr | None = None,
        class_name: ExprStr | None = None,
        class_name_contains: ExprStr | None = None,
        text: ExprStr | None = None,
        text_contains: ExprStr | None = None,
        **kwargs: ExprStr,
    ):
        """
        Finds all elements based on the given criteria.

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

        return SwElements(
            [sw_element.SwElement(e) for e in self.find_elements(By.XPATH, xpath)]
        )
