import requests
from bs4 import BeautifulSoup
import os
from . import (
    err_print,
    get_linked_images,
    get_embeded_images,
)


class General:
    def __init__(self, options):
        self.url = options["url"]
        self.tags = options["tags"]
        self.html = options["html"]
        self.linked = options["linked"]
        self.dir = options["dir"]
        self.isdump = options["isdump"]
        self.no_dl = options["no_dl"]

    def parse(self, url):
        try:
            res = requests.get(url)
        except IOError:
            err_print(f"Error: failed to retrieve the page: {url}")
            exit()
        soup = BeautifulSoup(res.content, "lxml")
        if self.html:
            print(soup.prettify())
            exit()
        if self.linked:
            log = self.get_linked_images(soup)
        else:
            log = self.get_embeded_images(soup)
        return log

    def get_linked_images(self, soup):
        opts = self.options_for_getting_images()
        images_list = get_linked_images(soup, opts)
        return images_list

    def get_embeded_images(self, soup):
        opts = self.options_for_getting_images()
        images_list = get_embeded_images(soup, opts)
        return images_list

    def options_for_getting_images(self):
        opts = {
            "url": self.url,
            "tags": self.tags,
            "isdump": self.isdump,
            "dir": self.dir,
            "no_dl": self.no_dl,
        }
        return opts


class EShuuShuu(General):
    URL_BASE = "https://e-shuushuu.net"

    def __init__(self, image_id, options):
        super().__init__(options)
        self.image_id = image_id
        self.url = f"{self.URL_BASE}/images/{self.image_id}"

    def get_linked_images(self, soup):
        opts = self.options_for_getting_images()
        image_list = self.get_images(self, soup, opts)
        return image_list

    def get_embeded_images(self, soup):
        return self.get_linked_images(self, soup)

    def get_images(self, soup, opts):
        image_block = (
            soup.find("div", id="content")
            .find("div", class_="image_thread")
            .find("div", class_="image_block")
        )
        image_path = image_block.find("a", class_="thumb_image")["href"]
        return [
            {
                "file": str(os.path.basename(image_path)),
                "url": image_path,
                "page_url": opts["url"],
                "tags": opts["tags"],
            }
        ]
