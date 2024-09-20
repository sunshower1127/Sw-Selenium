"""
catpcha_parser.py

cv2
numpy
pytesseract -> 추가 설치 필요
"""

from __future__ import annotations

import cv2 as cv
import numpy as np
from pytesseract import image_to_string


def decipher_captcha(captcha_img: bytes) -> str:
    """
    주어진 캡챠 이미지를 해석하여 문자열로 반환합니다.

    :param captcha_img: 캡챠 이미지의 바이트 데이터
    :return: 캡챠 이미지에서 추출한 문자열
    """

    image_array = np.frombuffer(captcha_img, dtype=np.uint8)
    image = cv.imdecode(image_array, cv.IMREAD_COLOR)
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    image = cv.adaptiveThreshold(
        image, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 91, 1
    )
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
    image = cv.morphologyEx(image, cv.MORPH_OPEN, kernel, iterations=1)
    cnts, _ = cv.findContours(image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        area = cv.contourArea(c)
        if area < 50:
            cv.drawContours(image, [c], -1, (0, 0, 0), -1)
    kernel2 = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    image = cv.filter2D(image, -1, kernel2)
    result = 255 - image

    return image_to_string(result)