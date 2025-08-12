import requests
from bs4 import BeautifulSoup
import os
from . import err_print, get_linked_images, get_embeded_images, url_to_filename


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

    def parse(self, image_id):
        self.url = f"{self.URL_BASE}/image/{image_id}/"
        print(f"url={self.url}")
        return super().parse(self.url)

    def get_linked_images(self, soup):
        opts = self.options_for_getting_images()
        image_list = self.get_images(soup, opts)
        return image_list

    def get_embeded_images(self, soup):
        return self.get_linked_images(soup)

    def get_images(self, soup, opts):
        image_block = (
            soup.find("div", id="content")
            .find("div", class_="image_thread")
            .find("div", class_="image_block")
        )
        image_path = image_block.find("a", class_="thumb_image")["href"]
        image_url = self.URL_BASE + image_path
        tag_spans = (
            image_block.find("div", class_="meta")
            .find("dd", class_="quicktag")
            .find_all("span")
        )
        tags = [span.find("a").text.replace(" ", "_") for span in tag_spans]
        tags = opts["tags"].split(" ") + tags
        print(image_url)
        if not opts["isdump"]:
            file = url_to_filename(image_url, opts["dir"])
            if not opts["no_dl"]:
                res = requests.get(image_url)
                with open(file, "wb") as f:
                    for chunk in res.iter_content(chunk_size=128):
                        f.write(chunk)
                return [
                    {
                        "file": str(os.path.basename(file)),
                        "url": str(image_url),
                        "page_url": opts["url"],
                        "tags": " ".join(tags),
                    }
                ]
        return None
