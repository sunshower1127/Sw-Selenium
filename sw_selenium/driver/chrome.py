from __future__ import annotations

import os
import threading
import time
from datetime import datetime
from typing import TYPE_CHECKING, Callable, Literal

import urllib3
from selenium.common.exceptions import (
    NoSuchElementException,
    NoSuchWindowException,
    WebDriverException,
)
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By

from sw_selenium.parsing import convert_date_string, generate_xpath
from sw_selenium.utils import LazyImport

from .context_finder import ContextFinder
from .context_manager import NoException, RetryConfig
from .element import SwElement
from .elements import SwElements

if TYPE_CHECKING:
    import keyboard  # type: ignore[import]

    from sw_selenium.parsing.xpath_parser import ExprStr
else:
    keyboard = LazyImport("keyboard")


# 이게 대체 뭔지 모르겠음
# Warning이 뜨니깐...
urllib3.disable_warnings()

SwOption = Literal[
    "keep_browser_open",
    "mute_audio",
    "maximize",
    "headless",
    "disable_popup",
    "prevent_sleep",
    "disable_info_bar",
]

ChromeOptionArg = str
"""ChromeOptions().add_argument() 메서드의 인자 타입
예)
"--mute-audio"
"""

ChromeExperimentalOption = str
"""ChromeOptions().add_experimental_option(key, value) 메서드의 인자 타입
"""


class SwChrome(Chrome):
    def __init__(
        self,
        *args: SwOption | ChromeOptionArg,
        timeout=5.0,
        freq=0.5,
        **kwargs: ChromeExperimentalOption,
    ):
        """SwChrome 클래스의 초기화 메서드.

        Args:
            timeout (float, optional): WebDriver의 기본 타임아웃 시간 (초 단위). 기본값은 5.0.
            freq (float, optional): WebDriver의 폴링 빈도 (초 단위). 기본값은 0.5.
            keep_browser_open (bool, optional): 코드 실행 후 브라우저 창을 계속 열어둘지 여부. 기본값은 True.
            audio (bool, optional): 브라우저의 오디오를 음소거할지 여부. 기본값은 False.
            maximize (bool, optional): 브라우저 창을 최대화할지 여부. 기본값은 True.
            headless (bool, optional): 브라우저를 헤드리스 모드로 실행할지 여부. 기본값은 False.
            popup (bool, optional): 팝업 차단을 비활성화할지 여부. 기본값은 True.
            prevent_sleep (bool, optional): 컴퓨터가 대기 모드에 빠지지 않도록 할지 여부. 기본값은 False.
            info_bar (bool, optional): 브라우저의 정보 표시줄을 비활성화할지 여부. 기본값은 True.

        Examples:
            ```python
            from enhanced_selenium import SwChrome

            web = SwChrome()
            web.get("https://www.google.com")
            ```

        """

        self.debug = os.environ.get("ES_DEBUG") == "1"
        options = ChromeOptions()

        prevent_sleep = False
        keep_browser_open = False

        option_map = {
            "mute_audio": "--mute-audio",
            "maximize": "--start-maximized",
            "headless": "--headless",
            "disable_popup": "--disable-popup-blocking",
            "disable_info_bar": "--disable-infobars",
        }

        for option in args:
            if option == "prevent_sleep":
                prevent_sleep = True
            elif option == "keep_browser_open":
                keep_browser_open = True
            else:
                options.add_argument(option_map.get(option) or option)

        if keep_browser_open:
            options.add_experimental_option("detach", value=True)

        for key, value in kwargs.items():
            options.add_experimental_option(key, value)

        super().__init__(options=options)

        if prevent_sleep:
            self._caffeinate()

        # selenium의 implicitly_wait와 explicit_wait는 빠르게 동작하지 않음.
        # 따라서, try-except-pass로 구현된 _repeat 메서드를 사용하여 대체함.
        self.implicitly_wait(0)
        self.context_finder = ContextFinder(self)
        self.timeout = timeout
        self.freq = freq

    def __del__(self):
        if self.debug:
            self.quit()

    def no_exc(
        self,
        include: tuple[type[BaseException], ...] = (WebDriverException,),
        exclude: tuple[type[BaseException], ...] = (),
    ):
        """코드 실행 중 발생하는 모든 예외를 무시합니다.
        도중에 예외가 발생하면 with 구문을 빠져나옵니다.

        Args:
            include (tuple[type[BaseException], ...]): 무시할 예외의 리스트. 기본값은 (WebDriverException, ).
            exclude (tuple[type[BaseException], ...]): 무시하지 않을 예외의 리스트. 기본값은 ().

        Returns:
            NoException: 예외 무시 객체. -> with 구문으로 사용

        Examples:
            ```python
            with web.no_exc():
                web.goto_alert().accep()

            with web.no_exc():
                web.find(tag="a")
            ```

        """
        return NoException(self, include, exclude)

    def set_retry(self, timeout: float | None = None, freq: float | None = None):
        """요소를 찾기 위한 재시도 설정을 구성합니다.

        Args:
            timeout (float, optional): 요소를 찾기 위한 최대 대기 시간 (초 단위). 기본값은 None. -> 기존의 쓰던 값
            freq (float, optional): 요소를 찾기 위한 재시도 빈도 (초 단위). 기본값은 None. -> 기존의 쓰던 값

        Returns:
            RetryConfig: 재시도 설정 객체. -> with 구문으로 사용 가능

        Examples:
            ```python
            web.set_retry(timeout=5.0, freq=0.5)
            web.find(tag="a")

            # with 구문으로 특정 블록에서만 재시도 설정을 사용할 수 있습니다.
            with web.set_retry(timeout=5.0):
                web.find(tag="a")
            ```

        """
        return RetryConfig(self, timeout, freq)

    def find(  # noqa: D417
        self,
        xpath="",
        /,
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
        """Finds a single element based on the given criteria.

        Raises:
            NoSuchElementException: If the element is not found.

        Args:
            xpath (str): The XPath of the element to find.

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
        if self.debug:
            print(f"LOG: find: {xpath=}")
        try:
            return SwElement(
                self.retry(lambda: self.find_element(By.XPATH, xpath)), xpath
            )
        except NoSuchElementException:
            if self.debug:
                self.context_finder.search(xpath)
                return SwElement(self.find_element(By.XPATH, xpath), xpath)
            else:
                msg = f"\n**Element not found**\n{xpath=}\n"
                raise NoSuchElementException(msg) from None

    def find_or_none(  # noqa: D417
        self,
        xpath="",
        /,
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
        """Finds a single element based on the given criteria.

        Difference from `find` method:
        - Does not raise `NoSuchElementException` if the element is not found. Returns `None` instead.

        Args:
            xpath (str): The XPath of the element to find.

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
            return SwElement(self.find_element(By.XPATH, xpath), xpath)
        except NoSuchElementException:
            return None

    def find_all(  # noqa: D417
        self,
        xpath="",
        /,
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
        """Finds all elements based on the given criteria.

        Args:
            xpath (str): The XPath of the elements to find.

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
            [SwElement(e, xpath) for e in self.find_elements(By.XPATH, xpath)]
        )

    def find_all_or_none(  # noqa: D417
        self,
        xpath="",
        /,
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
        """Finds all elements based on the given criteria.
        Difference from `find_all` method:
        - Does not raise `NoSuchElementException` if no elements are found. Returns `None` instead.

        Args:
            xpath (str): The XPath of the elements to find.

            tag (str): The tag name of the element.
            `prop` (ExprStr, optional): The property of the element.(**`class` is renamed to `class_name`**)
            `prop`_contains (ExprStr, optional): The substring of the property.
            **kwargs (ExprStr): Additional criteria.

        Returns:
        SwElements | None: The found elements or None if no elements are found.
        """

        xpath = xpath or generate_xpath(**locals())

        return SwElements(
            [SwElement(e, xpath) for e in self.find_elements(By.XPATH, xpath)]
        )

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

        if isinstance(dur, str):
            # convert_date_string 함수로 받은 datetime 값
            converted_datetime = convert_date_string(dur, korean_year=korean_year)

            # 현재 날짜와 시간
            now = datetime.now()

            # 날짜 부분을 제거하고 시간 부분만 추출
            time_difference = datetime.combine(
                now.date(), converted_datetime.time()
            ) - datetime.combine(now.date(), now.time())

            # 시간 부분을 초로 변환
            dur = time_difference.total_seconds()
        elif isinstance(dur, tuple):
            dur = abs(
                (
                    convert_date_string(dur[1], korean_year=korean_year)
                    - convert_date_string(dur[0], korean_year=korean_year)
                ).total_seconds()
            )

        if until:
            dur = (
                convert_date_string(until, korean_year=korean_year) - datetime.now()
            ).total_seconds()

        if display:
            print("Waiting for", dur, "seconds")

            def print_remaining_time(remaining_time):
                while remaining_time > 0:
                    print(f"\t{remaining_time} seconds left", end="\r")
                    time.sleep(1)
                    remaining_time -= 1

            threading.Thread(
                target=print_remaining_time, args=[dur], daemon=True
            ).start()

        if dur:
            time.sleep(dur)

    def add_hotkey(self, key: str, callback: Callable):
        """특정 키보드 입력에 대한 핫키를 추가합니다. -> keyboard 모듈 사용

        Args:
            key (str): 키보드의 키를 나타내는 문자열.
                - "ctrl+shift+a", "f1", "esc"
            callback (Callable): 키가 눌렸을 때 실행될 콜백 함수.

        Examples:
            ```python
            web.add_hotkey("ctrl+shift+a", lambda: print("Hotkey pressed!"))
            web.add_hotkey("f1", some_function)
            ```

        """
        keyboard.add_hotkey(key, callback)

    def remove_hotkey(self, key: str):
        """특정 키보드 입력에 대한 핫키를 제거합니다. -> keyboard 모듈 사용

        Args:
            key (str): 키보드의 키를 나타내는 문자열.
                - "ctrl+shift+a", "f1", "esc"

        Examples:
            ```python
            web.remove_hotkey("ctrl+shift+a")
            web.remove_hotkey("f1")
            ```

        """
        keyboard.remove_hotkey(key)

    def wait_hotkey(self, key: str):
        """특정 키보드 입력을 대기합니다. -> keyboard 모듈 사용

        Args:
            key (str): 키보드의 키를 나타내는 문자열.
                - "ctrl+shift+a", "f1", "esc"

        Examples:
            ```python
            web.add_hotkey("1", lambda: print("1 pressed"))
            web.add_hoykey("2", lambda: print("2 pressed"))

            web.wait_hotkey("ctrl+shift+a")

            web.remove_hotkey("1")
            web.remove_hotkey("2")

            web.find(tag="a")
            ```

        """
        keyboard.wait(key)

    def close_all(self):
        """모든 창을 닫습니다."""
        for window_handle in self.window_handles:
            try:
                self.switch_to.window(window_handle)
                self.close()
            except NoSuchWindowException:
                pass

    def goto_frame(self, path="/"):
        """주어진 경로를 따라 프레임으로 전환합니다.

        Args:
            path (str, optional): 전환할 프레임의 경로. 기본값은 "/".
                - 절대 경로: "/frame1_id/frame2_id"
                - 상대 경로: "./frame1_id/frame2_id" 또는 "frame1_id/frame2_id"
                - 부모 프레임으로 이동: ".."
                - 인덱스, id, name 모두 사용 가능

        Examples:
            ```python
            # 절대 경로를 사용하여 프레임으로 전환
            web.goto_frame("/frame1_id/frame2_id")

            # 상대 경로를 사용하여 프레임으로 전환
            web.goto_frame("./frame1_id/frame2_id")

            # 부모 프레임으로 전환
            web.goto_frame("..")

            # 인덱스를 사용하여 프레임으로 전환
            web.goto_frame("0")
            ```

        """

        split_path = path.split("/")

        if split_path[0] == "":
            self.switch_to.default_content()
            split_path = split_path[1:]

        elif split_path[0] == ".":
            split_path = split_path[1:]

        for node in split_path:
            if node == "":
                continue
            if node == "..":
                self.switch_to.parent_frame()
            elif node.isdigit():
                self.switch_to.frame(int(node))
            else:
                self.retry(lambda node=node: self.switch_to.frame(node))

    def goto_window(self, i=0):
        """주어진 인덱스의 윈도우로 전환합니다.

        Args:
            i (int, optional): 전환할 윈도우의 인덱스. 기본값은 0.
                - 음수 값도 허용됩니다. 예를 들어, -1은 마지막 윈도우를 나타냅니다.

        Examples:
            ```python
            # 첫 번째 윈도우로 전환
            web.goto_window(0)

            # 마지막 윈도우로 전환
            web.goto_window(-1)
            ```

        """

        self.retry(lambda: self.switch_to.window(self.window_handles[i]))

    def goto_alert(self):
        """현재 활성화된 경고(alert)로 전환합니다.

        Returns:
            Alert: 현재 활성화된 경고 객체.

        Examples:
            ```python
            # 만약 알림이 뜨면 "예"를 누르는 코드
            with web.no_exc:
                web.goto_alert().accept()  # 경고 수락
            ```
        """
        return self.retry(lambda: self.switch_to.alert)

    # def goto_focused_element(self):
    #     """현재 포커스된 요소로 전환합니다.

    #     Returns:
    #         Element: 현재 포커스된 요소 객체.

    #     Examples:
    #         ```python
    #         # 현재 포커스된 요소로 전환
    #         focused_element = web.goto_focused_element()
    #         focused_element.click()  # 포커스된 요소 클릭
    #         ```
    #     """
    #     return self.retry(lambda: SwElement(self.switch_to.active_element))

    def retry(self, func: Callable):
        """func을 실행하고, 예외가 발생하면 timeout 시간 동안 freq 간격으로 재시도합니다.

        실패시 마지막 시도의 에러를 반환.
        """
        end_time = time.time() + self.timeout
        while time.time() < end_time:
            try:
                return func()
            except WebDriverException:
                pass
            time.sleep(self.freq)

        return func()

    def _caffeinate(self): ...
