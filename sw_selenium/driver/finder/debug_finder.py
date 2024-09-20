from __future__ import annotations

from collections import namedtuple
from typing import TYPE_CHECKING

from selenium.common.exceptions import NoSuchElementException, TimeoutException

if TYPE_CHECKING:
    from .driver import EnhancedChrome


class DebugFinder:
    def __init__(self, driver: EnhancedChrome):
        self.driver = driver
        self.answers = []
        self.Env = namedtuple("Env", ["timeout", "freq", "win_h"])

    def setup_env(self):
        timeout = self.driver._timeout
        freq = self.driver._freq
        self.driver.set_retry(1, 0.1)
        self.driver.debug = False
        win_h = self.driver.current_window_handle
        self.env = self.Env(timeout, freq, win_h)

    def restore_env(self):
        timeout, freq, win_h = self.env
        self.driver.set_retry(timeout, freq)
        self.driver.debug = True
        self.driver.switch_to.window(win_h)
        self.driver.switch_to.default_content()

    def find(self, xpath: str, N=10):
        self.setup_env()
        answers = []

        for _ in range(N):
            for win_i, win_h in enumerate(self.driver.window_handles):
                frame_path: list[str] = ["default"]
                self.driver.switch_to.window(win_h)
                self._dfs(answers, xpath, win_i, frame_path)

            if answers:
                break

        if not answers:
            raise NoSuchElementException
        print(f"ES Debugger: Element found in the following context\n{xpath=}")
        print(self._get_message(answers))

        if (
            user_input := self._get_user_input(
                "ES Debugger: Select the context you want to use [1, 2, ...] / [N]o :",
                len(answers),
            )
        ) == "n":
            raise NoSuchElementException

        user_input = int(user_input)
        win_i, frame = answers[user_input - 1]
        self.driver.goto_window(win_i)
        self.driver.goto_frame(frame)

        self.restore_env()

    def _dfs(self, answers, xpath, win_i, frame_path):
        print(f"{win_i=}, {frame_path=}")
        # find element
        try:
            self.driver.find(xpath)
            answers.append((win_i, [*frame_path]))
        except TimeoutException:
            print("element 못찾음")

        # find iframe
        try:
            iframe_names = self.driver.find_all(tag="iframe").attributes("name")
            for iframe_name in iframe_names:
                if iframe_name is None:
                    continue
                self.driver.goto_frame(iframe_name)
                frame_path.append(iframe_name)
                self._dfs(answers, xpath, win_i, frame_path)
                self.driver.goto_frame("parent")
                frame_path.pop()
        except:
            print("iframe 못찾음")

    def _get_message(self, answers):
        cur_window_outputs: list[str] = []
        other_window_outputs: list[str] = []
        for window, frame in answers:
            output = ""
            if window != self.driver.window_handles.index(self.env.win_h):
                output += f"driver.goto_window({window})\n"
            output += f'driver.goto_frame("{'", "'.join(frame)}")\n'
            if window == self.driver.window_handles.index(self.env.win_h):
                cur_window_outputs.append(output)
            else:
                other_window_outputs.append(output)

        outputs = cur_window_outputs + other_window_outputs
        return "\n".join(f"#{i + 1}\n{output}" for i, output in enumerate(outputs))

    def _get_user_input(self, message, n):
        user_input = input(message)
        while user_input.lower() not in [str(i) for i in range(1, n + 1)] + ["n"]:
            user_input = input()
        return user_input.lower()
