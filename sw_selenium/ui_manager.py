from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable, Literal, TypeVar

from sw_selenium.utils.lazy_import import LazyImport

if TYPE_CHECKING:
    import tkinter as tk
    from tkinter import simpledialog
else:
    tk = LazyImport("tkinter", pip_name="tk")
    simpledialog = LazyImport("tkinter.simpledialog")

T = TypeVar("T", str, int, float)


def get_input_from_alert(
    body: str,
    data_type: type[T] = str,
    validate_func: Callable[[T], bool] | None = None,
) -> T:
    """Displays an alert dialog with a title and body,
    and returns the user's input cast to the specified type.

    :param body: The body message of the alert dialog.
    :param return_type: The type to which the user's input should be cast.
    :param validate_func: A function to validate the user's input.
    :return: The user's input cast to the specified type.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    while True:
        if data_type is str:
            user_input = simpledialog.askstring("", body)
        elif data_type is int:
            user_input = simpledialog.askinteger("", body)
        elif data_type is float:
            user_input = simpledialog.askfloat("", body)
        else:
            msg = "Unsupported return type. Please use str, int, or float."
            raise ValueError(msg)

        if user_input is None:
            msg = "User cancelled the input dialog."
            root.destroy()
            raise ValueError(msg)

        if validate_func is None or validate_func(data_type(user_input)):
            break  # Exit loop if input is valid

    root.destroy()  # Destroy the root window after getting input
    return data_type(user_input)


def get_button_choice(button_texts: list[str]) -> int:
    """Displays a dialog with buttons and returns the index of the clicked button.

    :param button_texts: A list of texts for the buttons.
    :return: The index of the clicked button.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    choice = tk.IntVar()

    def on_button_click(index: int):
        choice.set(index)
        dialog.destroy()

    dialog = tk.Toplevel(root)
    dialog.title("Choose an option")

    for index, text in enumerate(button_texts):
        button = tk.Button(
            dialog, text=text, command=lambda idx=index: on_button_click(idx)
        )
        button.pack(pady=5)

    dialog.wait_window(dialog)
    root.destroy()
    return choice.get()


def get_data_from_file_or_ui(
    file_path: str,
    prompt_message: str,
    length: int | Literal["INF"],
    data_type: type[T] = str,
    encoding: Literal["utf-8", "euc-kr", "ascii"] = "utf-8",
) -> list[T]:
    """주어진 파일에서 줄바꿈으로 구분된 문자열들을 읽어 리스트로 반환합니다.

    파일이 없거나 읽기 중 에러가 발생하면,
    사용자에게 문자열을 입력받아 파일에 저장하고 리스트로 반환합니다.

    Args:
        file_path (str): 읽을 파일의 경로.
        prompt_message (str): 사용자에게 입력을 요청할 때 표시할 메시지.
        length (int | Literal["INF"]): 입력받을 문자열의 개수. "INF"인 경우 무한히 입력받습니다.
        data_type (type[T], optional): 문자열을 변환할 타입. 기본값은 str.
        encoding (Literal["utf-8", "euc-kr", "ascii"], optional): 파일의 인코딩. 기본값은 "utf-8".

    Returns:
        list[T]: 파일에서 읽은 문자열들의 리스트.

    Examples:
        ```python
        # 파일에서 금지할 제목 리스트를 읽어오기
        ban_list = get_data_from_file_or_ui(
            "ban_list.txt",
            "Enter a title which you want to ban. If done, Cancel", "INF"
        )

        # 파일에서 아이디, 패스워드를 읽어오기
        id, pw = get_data_from_file_or_ui("id_pw.txt", "Enter your ID and password", 2)

        ```
    """
    try:
        with Path(file_path).open(encoding=encoding) as file:
            return list(map(data_type, file.read().splitlines()))
    except (OSError, FileNotFoundError):
        # 파일이 없거나 읽기 중 에러가 발생한 경우
        if length == "INF":
            data = []
            while True:
                try:
                    user_input = get_input_from_alert(
                        prompt_message,
                        data_type=data_type,
                    )
                except ValueError:
                    break

                data.append(user_input)
        else:
            data = [
                get_input_from_alert(prompt_message, data_type=data_type)
                for _ in range(length)
            ]

        with Path(file_path).open("w", encoding=encoding) as file:
            file.write("\n".join(map(str, data)))

        return data


"""
TEST CODE
"""
if __name__ == "__main__":
    # Example usage:
    def validate_positive(value: int) -> bool:
        return value > 0

    user_input_str = get_input_from_alert("Please enter your input:", str)
    print(f"User input as str: {user_input_str}")

    user_input_int = get_input_from_alert(
        "Please enter a positive number:", int, validate_positive
    )
    print(f"User input as int: {user_input_int}")

    button_texts = ["Option 1", "Option 2", "Option 3"]
    button_choice = get_button_choice(button_texts)
    print(f"User selected button index: {button_choice}")
