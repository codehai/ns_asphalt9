import re
from ocr import ocr
from utils.log import logger
import os
from PIL import Image
import pytesseract


def test_ocr():
    text_mapping = [
        "Controllers.*Pairing",  # 1
        "WORLD SERIES.*LIMITED SERIES",  # 3
        "WORLD SERIES",  # 4
        "CAR SELECTION",  # 6
        "CONGRATULATIONS",  # 7
        "DS AUTOMOBILES|TOP SPEED|HANDLING",  # 8
        "SEARCHING",  # 9
        "LOADING RACE",  # 10
        "DIST",  # 11
        "DIST",  # 12
        "YOUR",  # 13
        "YOUR",  # 14
        "YOU'VE BEEN DEMOTED",  # 15
    ]
    for index, num in enumerate([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]):
        logger.info(f"scene {num}")
        name = f"output{num}"
        path = "./scene"
        image_path = os.path.join(path, f"{name}.jpg")
        im = Image.open(image_path)
        # im = im.resize((640, 360), Image.LANCZOS)
        string = pytesseract.image_to_string(
            im,
            lang="eng",
            config="--psm 11 bazaar",
        )
        text = string.replace("\n", " ")
        logger.info(f"ocr text = {text}")
        if text_mapping[index]:
            logger.info(re.findall(text_mapping[index], text))
        im.close()
