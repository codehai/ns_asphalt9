import datetime
import os
import shutil

from . import consts, pages
from .cache import cache
from .utils.log import logger


class PageFactory:
    last_page = None

    def create_page(self, text: str):
        last_page_name = self.last_page.name if self.last_page else None
        match_pages = []
        page_instances = cache.scan(type="page")
        for page_instance in page_instances:
            weight = page_instance.calc_weight(text)
            if weight > 0:
                if last_page_name == consts.racing:
                    weight += 1
                match_pages.append((page_instance, weight))

        match_pages.sort(key=lambda pages: pages[1], reverse=True)

        if last_page_name in [consts.loading_race, consts.racing] and not match_pages:
            match_pages.append((pages.Racing, 1))

        if (
            not match_pages
            and text
            or len(match_pages) >= 2
            and match_pages[0][1] == match_pages[1][1]
        ):
            logger.info(f"match_pages = {match_pages}")
            # self.capture()

        if match_pages:
            page = match_pages[0][0](text, self.last_page)
        else:
            page = pages.Empty(text, self.last_page)
        methods = [
            method for method in dir(page) if callable(getattr(page, method))
        ]
        for method in methods:
            if method.startswith("parse"):
                func = getattr(page, method)
                func()
        self.last_page = page
        return page

    def capture(self):
        debug = os.environ.get("A9_DEBUG", 0)
        filename = (
            "".join([str(d) for d in datetime.datetime.now().timetuple()]) + ".jpg"
        )
        if not debug:
            shutil.copy("./output.jpg", f"./{filename}")
        return filename


factory = PageFactory()
