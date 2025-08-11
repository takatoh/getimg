import requests
from bs4 import BeautifulSoup
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
