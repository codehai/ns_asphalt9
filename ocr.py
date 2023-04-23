import os
from PIL import Image
import pytesseract
from utils.log import logger


def ocr(name="output", path="./images"):
    image_path = os.path.join(path, f"{name}.jpg")
    im = Image.open(image_path)
    string = pytesseract.image_to_string(im, lang="eng", config="--psm 11")
    text = string.replace("\n", " ")
    im.close()
    logger.info(f"ocr text = {text}")
    return text


if __name__ == "__main__":
    name = "test"
    name = "start_zh"
    name = "start"
    # for i in [0, 1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]:
    #    name = f"output{i}"
    #    path = "./images/scene"
    #    ocr(name, path)
    ocr()
