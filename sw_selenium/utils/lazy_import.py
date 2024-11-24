from __future__ import annotations

import importlib


class LazyImport:
    def __init__(
        self,
        module_name: str,
        func_names: str | list[str] | None = None,
        pip_name: str | None = None,
    ):
        """Initialize the LazyImport instance.

        Parameters
        ----------
        module_name (str): The name of the module to be lazily imported.
        func_names (str or list of str, optional): The name(s) of the function(s) to be lazily imported. Defaults to None.
        pip_name (str, optional): The name of the pip package to be installed if the module is not found. Defaults to None.
        """
        self.module_name = module_name
        if func_names is None:
            self.func_names = []
        else:
            self.func_names = (
                func_names if isinstance(func_names, list) else [func_names]
            )
        self.pip_name = pip_name
        self.module = None
        self.funcs = {}

    def __getattr__(self, name):
        if self.module is None:
            try:
                self.module = importlib.import_module(self.module_name)
            except ModuleNotFoundError as e:
                if self.pip_name:
                    print(
                        f"Module '{self.module_name}' not found. You can install it using 'pip install {self.pip_name}'"
                    )
                msg = f"Module '{self.module_name}' not found"
                raise ImportError(msg) from e
        return getattr(self.module, name)

    def __call__(self, *args, **kwargs):
        if not self.func_names or len(self.func_names) != 1:
            msg = "Single function name not provided or multiple functions provided"
            raise AttributeError(msg)
        func_name = self.func_names[0]
        if func_name not in self.funcs:
            try:
                self.module = importlib.import_module(self.module_name)
                self.funcs[func_name] = getattr(self.module, func_name)
            except ModuleNotFoundError as e:
                if self.pip_name:
                    print(
                        f"Module '{self.module_name}' not found. You can install it using 'pip install {self.pip_name}'"
                    )
                msg = f"Module '{self.module_name}' not found"
                raise ImportError(msg) from e
            except AttributeError as e:
                msg = f"Function '{func_name}' not found in module '{self.module_name}'"
                raise ImportError(msg) from e
        return self.funcs[func_name](*args, **kwargs)

    def __iter__(self):
        if not self.func_names:
            msg = "Function names not provided"
            raise AttributeError(msg)
        for func_name in self.func_names:
            yield self.__getattr__(func_name)


# 사용 예시
if __name__ == "__main__":
    try:
        sqrt, pow = LazyImport("math", ["sqrt", "pow"])
        print(sqrt(16))  # 4.0 출력
        print(pow(2, 3))  # 8 출력
    except ImportError as e:
        print(e)
