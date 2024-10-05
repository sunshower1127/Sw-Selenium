"""Context Manager

This module provides context managers for handling exceptions and retry configurations.

Classes:
    NoException: A context manager to suppress specified exceptions.
    RetryConfig: A context manager to modify retry configurations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sw_selenium.driver import SwChrome


class NoException:
    """Context manager to suppress specified exceptions.

    Attributes:
        driver (SwChrome): The SwChrome driver instance.
        debug (bool): The original debug state of the driver.
        include_exceptions (tuple[type[BaseException], ...] | None): Exceptions to include for suppression.
        exclude_exceptions (tuple[type[BaseException], ...] | None): Exceptions to exclude from suppression.
    """

    def __init__(
        self,
        driver: SwChrome,
        include_exceptions: tuple[type[BaseException], ...],
        exclude_exceptions: tuple[type[BaseException], ...],
    ):
        """Initializes the NoException context manager.

        Args:
            driver (SwChrome): The SwChrome driver instance.
            include_exceptions (tuple[type[BaseException], ...]): Exceptions to include for suppression.
            exclude_exceptions (tuple[type[BaseException], ...]): Exceptions to exclude from suppression.
        """
        self.driver = driver
        self.debug = self.driver.debug
        self.include_exceptions = include_exceptions
        self.exclude_exceptions = exclude_exceptions

    def __enter__(self):
        """Enters the context manager, disabling debug mode if it was enabled."""
        if self.debug:
            self.driver.debug = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exits the context manager, restoring the original debug state and suppressing specified exceptions.

        Args:
            exc_type (Type[BaseException]): The exception type.
            exc_val (BaseException): The exception instance.
            exc_tb (TracebackType): The traceback object.

        Returns:
            bool: True if the exception should be suppressed, False otherwise.
        """
        if self.debug:
            self.driver.debug = True

        if exc_type is None:
            return False

        if self.include_exceptions and not issubclass(
            exc_type, self.include_exceptions
        ):
            return False

        if self.exclude_exceptions and issubclass(exc_type, self.exclude_exceptions):  # noqa: SIM103
            return False

        return True


class RetryConfig:
    """Context manager to modify retry configurations.

    Attributes:
        driver (SwChrome): The SwChrome driver instance.
        orig_timeout (float): The original timeout value.
        orig_freq (float): The original frequency value.
        retry_timeout (float): The new timeout value.
        retry_frequency (float): The new frequency value.
    """

    def __init__(
        self,
        driver: SwChrome,
        retry_timeout: float | None = None,
        retry_frequency: float | None = None,
    ):
        """Initializes the RetryConfig context manager.

        Args:
            driver (SwChrome): The SwChrome driver instance.
            retry_timeout (float | None): The new timeout value.
            retry_frequency (float | None): The new frequency value.
        """
        self.driver = driver
        self.orig_timeout = self.driver.timeout
        self.orig_freq = self.driver.freq
        self.retry_timeout = retry_timeout or self.orig_timeout
        self.retry_frequency = retry_frequency or self.orig_freq

    def __enter__(self):
        """Enters the context manager, setting the new retry configurations."""
        self.driver.timeout = self.retry_timeout
        self.driver.freq = self.retry_frequency
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exits the context manager, restoring the original retry configurations.

        Args:
            exc_type (Type[BaseException]): The exception type.
            exc_val (BaseException): The exception instance.
            exc_tb (TracebackType): The traceback object.

        Returns:
            bool: False to indicate that exceptions should not be suppressed.
        """
        self.driver.timeout = self.orig_timeout
        self.driver.freq = self.orig_freq
        return False
