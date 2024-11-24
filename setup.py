"""setup.py for pip"""

from setuptools import find_packages, setup

setup(
    name="sw_selenium",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "selenium",
        "pyparsing",
    ],
    description="A custom Selenium driver package",
    author="Sunwoo Kim",
    author_email="seng001127@soongsil.ac.kr",
    url="https://github.com/sunshower1127/Sw-Selenium",  # 프로젝트 URL
)
