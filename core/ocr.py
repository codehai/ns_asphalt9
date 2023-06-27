import os

import pytesseract
from PIL import Image

from core.page_factory import factory
from core.screenshot import screenshot
from core.utils.log import logger


def ocr(name="output", path="./images"):
    image_path = os.path.join(path, f"{name}.jpg")
    im = Image.open(image_path)
    text: str = pytesseract.image_to_string(im, lang="eng", config="--psm 11")
    text = text.replace("\n", " ")
    im.close()
    page = factory.create_page(text)
    logger.info(f"ocr page dict = {page.dict}")
    return page


def ocr_screen():
    """截图并识别"""
    screenshot()
    page = ocr()
    return page


if __name__ == "__main__":
    ocr()
