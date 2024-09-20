class Elements:
    def __init__(self, elements: list[Element]):
        self._elements = elements
        self._index = 0
        self.texts = [element.text for element in self._elements]

    def __getitem__(self, index: int):
        return self._elements[index]

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self._elements):
            result = self._elements[self._index]
            self._index += 1
            return result

        raise StopIteration

    def __bool__(self):
        return bool(self._elements)

    def up(self, levels=1):
        return Elements([element.up(levels) for element in self._elements])

    def find(
        self,
        xpath="",
        *,
        axis: axis_str = "descendant",
        tag="*",
        id: expr_str | None = None,
        id_contains: expr_str | None = None,
        name: expr_str | None = None,
        class_name: expr_str | None = None,
        class_name_contains: expr_str | None = None,
        text: expr_str | None = None,
        text_contains: expr_str | None = None,
        **kwargs: expr_str,
    ):
        xpath = xpath or get_xpath(locals())

        return Elements([element.find(xpath) for element in self._elements])

    def find_or_none(
        self,
        xpath="",
        *,
        axis: axis_str = "descendant",
        tag="*",
        id: expr_str | None = None,
        id_contains: expr_str | None = None,
        name: expr_str | None = None,
        class_name: expr_str | None = None,
        class_name_contains: expr_str | None = None,
        text: expr_str | None = None,
        text_contains: expr_str | None = None,
        **kwargs: expr_str,
    ):
        xpath = xpath or get_xpath(locals())

        result: list[Element] = []
        for element in self._elements:
            if (e := element.find_or_none(xpath)) is not None:
                result.append(e)
        return Elements(result)

    def click(self, by: Literal["default", "enter", "js", "mouse"] = "default"):
        match by:
            case "default":
                for element in self._elements:
                    element.click()

            case "enter":
                for element in self._elements:
                    element.send_keys(Keys.ENTER)

            case "js":
                self._elements[0]._driver.execute_script(
                    "arguments.forEach(e => e.click());", *self._elements
                )

            case "mouse":
                actions = ActionChains(self._elements[0]._driver)
                for element in self._elements:
                    actions.click(element)
                actions.perform()

    def send_keys(self, keys: str | list[str]):
        if isinstance(keys, str):
            for element in self._elements:
                element.send_keys(keys)

        else:
            for element, key in zip(self._elements, keys):
                element.send_keys(key)

    def attributes(
        self,
        name: str,
    ):
        return [element.get_attribute(name) for element in self._elements]
