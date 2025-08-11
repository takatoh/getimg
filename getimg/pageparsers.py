import requests
from bs4 import BeautifulSoup
import os
from . import err_print, RE_IMAGE, build_image_url, url_to_filename


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
        soup = BeautifulSoup(res, "lxml")
        if self.html:
            print(soup.prettify())
            exit()
        if self.linked:
            log = self.get_linked_images(soup)
        else:
            log = self.get_embeded_images(soup)
        return log

    def get_linked_images(self, soup):
        images_list = []
        for a in soup("a"):
            if "href" not in a.attrs:
                continue
            image = a["href"]
            try:
                print(image)
                info = self.get_image(image)
                if info:
                    images_list.append(info)
            except IOError:
                err_print("Error: failed to retrieve the image.")
        return images_list

    def get_embeded_images(self, soup):
        images_list = []
        for i in soup("img"):
            image = i["src"]
            try:
                print(image)
                info = self.get_image(image)
                if info:
                    images_list.append(info)
            except IOError:
                err_print("Error: failed to retrieve the image.")
        return images_list

    def get_image(self, image):
        if RE_IMAGE.match(image):
            image = build_image_url(self.url, image)
            print(image)
            if not self.isdump:
                file = url_to_filename(image, self.dir)
                if not self.no_dl:
                    res = requests.get(image)
                    with open(file, "wb") as f:
                        for chunk in res.iter_content(chunk_size=128):
                            f.write(chunk)
                return {
                    "file": str(os.path.basename(file)),
                    "url": str(image),
                    "page_url": self.url,
                    "tags": self.tags,
                }
        return None
