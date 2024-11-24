from __future__ import annotations

import os
import subprocess
import sys


class _SwSeleniumDebugger:
    QUIT_CODE = 2

    def start(self, path: str):
        """debugger.run(__file__)"""

        if os.environ.get("ES_DEBUG") == "1":
            return

        os.environ["ES_DEBUG"] = "1"
        while True:
            process = subprocess.Popen(
                [sys.executable, path],
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
            process.wait()

            if process.returncode == 1:
                user_input = input("ES Debugger: An error occurred. [R]etry / [Q]uit: ")
                while user_input.lower() not in ["r", "q"]:
                    user_input = input()
                user_input = user_input.lower()
                if user_input == "r":
                    continue

                sys.exit(1)

            elif process.returncode == self.QUIT_CODE:
                print("The ES Debugger has terminated.")
                sys.exit(0)

    def breakpoint(self):
        user_input = input(
            "ES Debugger: Breakpoint reached. [C]ontinue / [R]etry / [Q]uit: "
        )
        while user_input.lower() not in ["c", "r", "q"]:
            user_input = input()
        user_input = user_input.lower()
        if user_input == "c":
            return

        if user_input == "r":
            sys.exit(0)
        elif user_input == "q":
            sys.exit(self.QUIT_CODE)

    def end(self):
        user_input = input("ES Debugger: End of the script. [R]etry / [Q]uit: ")
        while user_input.lower() not in ["r", "q"]:
            user_input = input()
        user_input = user_input.lower()
        if user_input == "r":
            sys.exit(0)
        elif user_input == "q":
            sys.exit(self.QUIT_CODE)


debugger = _SwSeleniumDebugger()
