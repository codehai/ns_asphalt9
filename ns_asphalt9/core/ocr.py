import os
import re
import json

import pytesseract
from PIL import Image

from .page_factory import factory
from .screenshot import screenshot
from .utils.log import logger


class LogManager:
    log_texts = None
    log_text_index = 0

    @classmethod
    def get_text(cls):
        if not cls.log_texts:
            cls.log_texts = []
            with open("logs/race.log") as file:
                lines = file.readlines()
            for line in lines:
                match = re.search(r"'text':\s*'(.*?)'", line)
                match1 = re.search(r"'text':\s*\"(.*?)\"", line)
                if match:
                    text = match.group(1)
                    cls.log_texts.append(text)
                elif match1:
                    text = match1.group(1)
                    cls.log_texts.append(text)
        text = cls.log_texts[cls.log_text_index]
        cls.log_text_index += 1
        return text


def ocr(name="output", path="./"):
    debug = os.environ.get("A9_DEBUG", 0)
    if debug:
        text = LogManager.get_text()
    else:
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
