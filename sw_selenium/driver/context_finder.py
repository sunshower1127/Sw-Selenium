"""debug_finder

This module provides the ContextFinder class, which helps in finding the context
(window and frame) of an element when it cannot be found in debug mode.

Classes:
    ContextFinder: A class to find the context of an element when it cannot be found in debug mode.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import SwChrome

from selenium.common.exceptions import NoSuchElementException

window_index = int
frame_path = str
context = tuple[window_index, frame_path]


class ContextFinder:
    """ContextFinder class helps in finding the context (window and frame) of an element
    when it cannot be found in debug mode. It provides functionalities to search for
    the element across different windows and frames.

    Attributes:
        driver (SwChrome): The SwChrome driver instance.
        contexts (list[context]): A list of contexts where the element was found.
    """

    def __init__(self, driver: SwChrome):
        """Initializes the ContextFinder with the given SwChrome driver.

        Args:
            driver (SwChrome): The SwChrome driver instance.
        """
        self.driver = driver
        self.contexts: list[context] = []

    def search(self, xpath: str):
        """Searches for the element specified by the given XPath across different contexts
        (windows and frames). If the element is found, it prompts the user to select
        the desired context.

        Args:
            xpath (str): The XPath of the element to search for.

        Raises:
            NoSuchElementException: If the element is not found in any context.
        """
        self.xpath = xpath
        self.current_window_index = self.driver.window_handles.index(
            self.driver.current_window_handle
        )
        self._search_all_contexts()
        self.driver.goto_window(self.current_window_index)
        self.driver.goto_frame("/")

        if not self.contexts:
            msg = f"Element not found: {xpath}"
            raise NoSuchElementException(msg)

        print(
            f'Context Finder: Element found in the following context\n\t"{self.xpath}"'
        )
        print(self._format_contexts())

        user_input = self._get_user_input(
            "Select the context you want to use [1, 2, ...] / [N]o :"
        )
        if user_input == "n":
            raise NoSuchElementException

        print()
        user_input = int(user_input)
        window_index, frame_path = self.contexts[user_input - 1]
        if window_index != self.current_window_index:
            self.driver.goto_window(window_index)
            print(f"self.driver.goto_window({window_index})")

        self.driver.goto_frame(frame_path)
        print(f'self.driver.goto_frame("{frame_path}")')

    def _search_all_contexts(self):
        """Internal method to search for the element across all windows and frames."""
        with self.driver.no_exc(), self.driver.set_retry(1, 0.1):
            indices = list(range(len(self.driver.window_handles)))
            indices = (
                indices[self.current_window_index :]
                + indices[: self.current_window_index]
            )
            print(f"{indices=}")

            for window_index in indices:
                self.driver.goto_window(window_index)
                self.driver.goto_frame("/")
                frame_list: list[str] = [""]  # "/".join 해야해서 빈 문자열 추가
                self._depth_first_search(window_index, frame_list)

    def _depth_first_search(self, window_index, frame_list):
        """Internal method to perform a depth-first search (DFS) for the element
        within the given window and frame list.

        Args:
            window_index (int): The index of the current window.
            frame_list (list[str]): The list of frames to search within.
        """
        print(f"window_index: {window_index}, frame_path: { '/'.join(frame_list) }")
        # find element
        try:
            self.driver.find(self.xpath)
            self.contexts.append((window_index, "/".join(frame_list)))
        except NoSuchElementException:
            print("\t-> The element not found")

        # find iframe
        try:
            frames = self.driver.find_all(tag="iframe")
            frame_headers = []

            for idx, frame in enumerate(frames):
                frame_header = (
                    frame.get_attribute("name") or frame.get_attribute("id") or str(idx)
                )
                frame_headers.append(frame_header)
        except NoSuchElementException:
            print("\t-> No child frame")
            return

        for frame_header in frame_headers:
            self.driver.goto_frame(frame_header)
            frame_list.append(frame_header)
            self._depth_first_search(window_index, frame_list)
            self.driver.goto_frame("..")
            frame_list.pop()

    def _format_contexts(self):
        """Internal method to generate a string representation of the found contexts.

        Returns:
            str: A string representation of the contexts.
        """
        outputs = []
        for window_index, frame_path in self.contexts:
            if window_index == self.current_window_index:
                outputs.append(f"Frame: {frame_path}")
            else:
                outputs.append(f"Window: {window_index}, Frame: {frame_path}")

        return "\n".join(f"#{i + 1}\n{output}" for i, output in enumerate(outputs))

    def _get_user_input(self, message):
        """Internal method to get user input for selecting a context.

        Args:
            message (str): The message to display to the user.

        Returns:
            str: The user's input.
        """
        user_input = input(message)
        valid_inputs = [str(i) for i in range(1, len(self.contexts) + 1)] + ["n"]
        while user_input.lower() not in valid_inputs:
            user_input = input(message)
        return user_input.lower()
