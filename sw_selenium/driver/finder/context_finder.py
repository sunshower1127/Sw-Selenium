"""
debug_finder

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from selenium.common.exceptions import NoSuchElementException

if TYPE_CHECKING:
    from .. import SwChrome

    window_index = int
    frame_path = str
    context = tuple[window_index, frame_path]


class ContextFinder:
    """
    debug모드에서 element를 찾지 못했을 때, element를 찾을 수 있는 context를 찾아주는 클래스
    window, frame을 찾아주는 기능을 제공
    """

    def __init__(self, driver: SwChrome):
        """
        Args:
            driver (SwChrome): SwChrome 객체
        """
        self.driver = driver
        self.contexts: list[context] = []

    def search(self, xpath: str):
        """
        element를 찾을 수 있는 context를 찾아주는 메서드
        """
        self.xpath = xpath
        self.cur_window_i = self.driver.window_handles.index(
            self.driver.current_window_handle
        )

        self._search()
        self.driver.goto_window(self.cur_window_i)
        self.driver.goto_frame("/")

        if not self.contexts:
            msg = f"Element not found: {xpath}"
            raise NoSuchElementException(msg)

        print(
            f'Context Finder: Element found in the following context\n\t"{self.xpath}"'
        )
        print(self._str_contexts())

        user_input = self._get_user_input(
            "Select the context you want to use [1, 2, ...] / [N]o :"
        )
        if user_input == "n":
            raise NoSuchElementException

        user_input = int(user_input)
        window_i, frame_path = self.contexts[user_input - 1]
        if window_i != self.cur_window_i:
            self.driver.goto_window(window_i)
        self.driver.goto_frame(frame_path)

    def _search(self):
        with self.driver.no_exc(), self.driver.set_retry(1, 0.1):
            idxs = list(range(len(self.driver.window_handles)))
            idxs = idxs[self.cur_window_i :] + idxs[: self.cur_window_i]

            for window_i in idxs:
                self.driver.goto_window(window_i)
                frame_list: list[str] = [""]
                self._dfs(window_i, frame_list)

    def _dfs(self, window_i, frame_list):
        print(f"{window_i=}, {frame_list=}")
        # find element
        try:
            self.driver.find(self.xpath)
            self.contexts.append((window_i, "/".join(frame_list)))
        except NoSuchElementException:
            print("\t Not found")

        # find iframe
        try:
            frame_ids = self.driver.find_all(tag="iframe").attributes("id")
            for frame_id in frame_ids:
                # 이게 None일 수가 있나?
                if frame_id is None:
                    continue
                self.driver.goto_frame(frame_id)
                frame_list.append(frame_id)
                self._dfs(window_i, frame_list)
                self.driver.goto_frame("..")
                frame_list.pop()
        except NoSuchElementException:
            print("\t No frame")

    def _str_contexts(self):
        outputs = []
        for window_i, frame_path in self.contexts:
            if window_i == self.cur_window_i:
                outputs.append(f"Frame: {frame_path}")
            else:
                outputs.append(f"Window: {window_i}, Frame: {frame_path}")

        return "\n".join(f"#{i + 1}\n{output}" for i, output in enumerate(outputs))

    def _get_user_input(self, message):
        user_input = input(message)
        while user_input.lower() not in [
            str(i) for i in range(1, len(self.contexts) + 1)
        ] + ["n"]:
            user_input = input()
        return user_input.lower()
