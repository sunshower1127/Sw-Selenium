"""builder"""

from __future__ import annotations

import os
import subprocess
import sys
from typing import Callable


class _SwSeleniumBuilder:
    def start(
        self,
        path,
        n=1,
        *,
        never_stop=False,
        on_success: Callable[[list[int]], None] | None = None,
    ):
        """builder.start(__file__)"""

        if os.environ.get("ES_BUILD") == "1":
            return

        os.environ["ES_BUILD"] = "1"

        processes: list = [None] * n
        while True:
            for i in range(n):
                if processes[i] is None or processes[i].poll() is not None:
                    if processes[i] is not None:
                        return_code = processes[i].returncode
                        if return_code != 0:
                            if never_stop:
                                print(
                                    f"Process {i} failed with return code {return_code}. Restarting..."
                                )
                                processes[i] = subprocess.Popen(
                                    [sys.executable, path],
                                    stdin=sys.stdin,
                                    stdout=sys.stdout,
                                    stderr=sys.stderr,
                                )
                            else:
                                print(
                                    f"Process {i} failed with return code {return_code}. Exiting..."
                                )
                        else:
                            if on_success:
                                on_success(
                                    [p.returncode for p in processes if p is not None]
                                )
                            processes[i] = None
                    else:
                        processes[i] = subprocess.Popen(
                            [sys.executable, path],
                            stdin=sys.stdin,
                            stdout=sys.stdout,
                            stderr=sys.stderr,
                        )

            if not never_stop:
                break

            for p in processes:
                if p is not None:
                    p.wait()

    def build(self, file_path: str, dist_path="."):
        """builder.build(__file__)
        Only working in development environment
        """

        # pyinstaller로 패키징된 실행 파일에서 실행되는지 확인
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            print("This is a packaged executable. The build process will not proceed.")
            return

        try:
            # pyinstaller 명령 실행, --distpath 옵션 추가
            subprocess.run(
                [
                    "pyinstaller",
                    "--onefile",
                    "--distpath",
                    dist_path,
                    file_path,
                ],
                check=True,
            )
            print(f"Build completed successfully for {file_path}")
        except subprocess.CalledProcessError as e:
            print(f"Build failed: {e}", file=sys.stderr)


builder = _SwSeleniumBuilder()
