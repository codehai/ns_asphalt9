import datetime
import os
import shutil

import pytesseract
from PIL import Image

from core import consts, pages
from core.cache import cache
from core.screenshot import screenshot
from core.utils.log import logger


class PageFactory:
    last_page: pages.Page = None

    def create_page(self, text: str):
        last_page_name = self.last_page.name if self.last_page else None
        match_pages = []
        pages_dict = cache.scan(type="page")
        for page_key in pages:
            page: pages.Page = pages_dict.get(page_key)
            weight = page.calc_weight(text)
            if weight > 0:
                if last_page_name == consts.racing:
                    weight += 1
                match_pages.append((page, weight))

        match_pages.sort(key=lambda pages: pages[1], reverse=True)

        if last_page_name in [consts.loading_race, consts.racing] and not match_pages:
            match_pages.append((self.last_page, 1))

        if (
            not match_pages
            and text
            or len(match_pages) >= 2
            and match_pages[0][1] == match_pages[1][1]
        ):
            logger.info(f"match_pages = {match_pages}")
            self.capture()

        if match_pages:
            page = match_pages[0][0]
            methods = [
                method for method in dir(page) if callable(getattr(page, method))
            ]
            for method in methods:
                if method.startswith("parse"):
                    func = getattr(page, method)
                    func()
            return page

        empty = pages.Empty()
        return empty

    def capture(self):
        filename = (
            "".join([str(d) for d in datetime.datetime.now().timetuple()]) + ".jpg"
        )
        shutil.copy("./images/output.jpg", f"./images/not_match_images/{filename}")
        return filename


factory = PageFactory()


def ocr(name="output", path="./images"):
    image_path = os.path.join(path, f"{name}.jpg")
    im = Image.open(image_path)
    text: str = pytesseract.image_to_string(im, lang="eng", config="--psm 11")
    text = text.replace("\n", " ")
    im.close()
    page: pages.Page = factory.create_page(text)
    logger.info(f"ocr page dict = {page.dict}")
    return page


def ocr_screen():
    """截图并识别"""
    screenshot()
    page = ocr()
    return page


if __name__ == "__main__":
    ocr()
