# Sw Selenium

## How to install

1. `git clone`
2. `pip install`
3. `import sw-selenium`

## Getting Started

```python
from sw-selenium.driver import SwChrome

web = SwChrome(keep_browser_open=True)
web.get("https://google.com")

```

## 특징

1. selenium하고 완벽 호환 -> selenium하고 병행해 쓸 수 있음.

# What's the difference with Selenium

- sw_selenium
  - driver
    - chrome_driver
    - context
    - element
    - elements
    - finder
      - findable
      - debug_finder
  - debugger
  - builder
  - parser
    - parse_kwargs_to_xpath
    - parse_str_to_datetime
