from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sw_selenium.driver import SwChrome


class NoException:
    """
    Context manager to suppress exceptions
    """

    def __init__(self, driver: SwChrome, include, exclude):
        self.driver = driver
        self.debug = self.driver.debug
        self.include = include
        self.exclude = exclude

    def __enter__(self):
        if self.debug:
            self.driver.debug = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.debug:
            self.driver.debug = True

        # If no exception occurred, return False to indicate normal exit
        if exc_type is None:
            return False

        # If include is specified, suppress only those exceptions
        if self.include and not issubclass(exc_type, self.include):
            return False

        # If exclude is specified, do not suppress those exceptions
        if self.exclude and issubclass(exc_type, self.exclude):
            return False

        # Suppress the exception
        return True


class RetryConfig:
    def __init__(self, driver: SwChrome, timeout=None, freq=None):
        self.driver = driver
        self.orig_timeout = self.driver._timeout
        self.orig_freq = self.driver._freq
        self.timeout = timeout or self.orig_timeout
        self.freq = freq or self.orig_freq

    def __enter__(self):
        self.driver._timeout = self.timeout
        self.driver._freq = self.freq
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver._timeout = self.orig_timeout
        self.driver._freq = self.orig_freq
        return False  # 예외를 억제하지 않음
