from __future__ import annotations

from typing import Literal

from pyparsing import (
    Combine,
    OneOrMore,
    QuotedString,
    Suppress,
    White,
    Word,
    ZeroOrMore,
    infix_notation,
    one_of,
    opAssoc,
    pyparsing_unicode,
)

AxisStr = Literal[
    "ancestor",
    "ancestor-or-self",
    "child",
    "descendant",
    "descendant-or-self",
    "following",
    "following-sibling",
    "parent",
    "preceding",
    "preceding-sibling",
    "self",
]
"""AxisStr type description

Represents the direction in which to search for elements relative to the current node.

For more information, refer to:
https://www.w3schools.com/xml/xpath_axes.asp
"""

ExprStr = str
"""ExprStr type description

Represents a string expression that supports logical operators for element selection.

Supported operators:
- `|` and `&` for logical OR and AND, respectively. Example: id="id1 | id2"
- `!` for logical NOT. Example: id="!id1"
- Parentheses `()` for grouping. Example: id="(id1 | id2) & !id3"
- Whitespace is supported. Example: text="hi everyone | hello world"
- Both double and single quotes are supported. Example: text="'(01:00)' | '(02:00)'"
"""


# Define the grammar
_word = Word(pyparsing_unicode.alphanums + "_-.")
_identifier = (
    Combine(OneOrMore(_word + ZeroOrMore(White() + _word)))
    | QuotedString('"')
    | QuotedString("'")
)

# Define the expression using infix_notation
_expr = infix_notation(
    _identifier,
    [("!", 1, opAssoc.RIGHT), (one_of("& |"), 2, opAssoc.LEFT)],
    lpar=Suppress("("),
    rpar=Suppress(")"),
)


def _get_prop_format(prop_name: str):
    prop_name = prop_name.replace("class_name", "class")
    if "text" in prop_name:
        prop_name = prop_name.replace("text", "text()")
    elif "num" in prop_name:
        prop_name = prop_name.replace("num", "position()")
    else:
        prop_name = "@" + prop_name

    idx = prop_name.find("_contains")
    if idx != -1:
        prop_name = prop_name[:idx]
        return "contains(" + prop_name + ", '{}')"

    return prop_name + "='{}'"


def _preprocess_for_not(node: list):
    for i in range(len(node)):
        if isinstance(node[i], list):
            _preprocess_for_not(node[i])
        elif i > 0 and node[i - 1] == "!":
            node[i] = [node[i]]


# Parse the expression
def _parse_expression(expression: str, prop_name: str):
    parsed_expression = _expr.parse_string(expression, parse_all=True).as_list()[0]

    # A -> (A) 로 바꾸기 -> 마지막에 괄호 없애는 과정 통일
    if isinstance(parsed_expression, str):
        parsed_expression = [parsed_expression]

    _preprocess_for_not(parsed_expression)

    prop_format = _get_prop_format(prop_name)
    logical_expression = _convert_to_logical_expression(parsed_expression, prop_format)
    if logical_expression[0] == "(":
        logical_expression = logical_expression[1:-1]
    return logical_expression


def _convert_to_logical_expression(element: str | list, prop_format: str) -> str:
    if isinstance(element, list):
        result = ""
        if element[0] != "!":
            result += "("

        result += "".join(
            _convert_to_logical_expression(sub_element, prop_format)
            for sub_element in element
        )

        if element[0] != "!":
            result += ")"

        return result

    if element == "|":
        return " or "
    if element == "&":
        return " and "
    if element == "!":
        return "not"

    return prop_format.format(element)


def generate_xpath(**kwargs) -> str:
    """Generate an XPath expression from the given keyword arguments."""
    data = kwargs.copy()
    if "kwargs" in data:
        for key, value in data["kwargs"].items():
            data[key] = value
        del data["kwargs"]

    data.pop("self", "")
    data.pop("xpath", "")
    data.pop("delay", "")
    # axis_map = {"": "//", "child": "/"}

    # axis = axis_map.get(data.pop("axis", ""), "") or data.pop("axis", "") + "::"
    axis = data.pop("axis", "//")
    if axis != "//":
        axis += "::"
    header = axis + data.pop("tag", "*")
    body = []
    for key, value in data.items():
        if value is None:
            continue
        body.append(_parse_expression(str(value), key))

    if body:
        return f"{header}[{ ' and '.join(body) }]"
    else:
        return header


"""

오케이.

A B C -> 는 "A B C" 로 입력되게 했구요.
양쪽 띄어쓰기들은 제거 되게 해놨으니깐
굳이 인식되게 하려면 따움표 쓰면 됩니다.
이상.

"""
# Test code
if __name__ == "__main__":
    expression = "A & B  C "
    prop_format = "text"
    result = _parse_expression(expression, prop_format)
    print(result)
