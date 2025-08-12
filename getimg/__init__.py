import requests
from urllib.parse import urljoin
import re
import sys
import os


__version__ = "0.5.0"


RE_IMAGE = re.compile(r".+\.(jpg|jpeg|png|bmp|gif)", flags=re.IGNORECASE)


def get_linked_images(soup, opts):
    images_list = []
    for a in soup("a"):
        if "href" not in a.attrs:
            continue
        image = a["href"]
        try:
            print(image)
            info = get_image(image, opts)
            if info:
                images_list.append(info)
        except IOError:
            err_print("Error: failed to retrieve the image.")
    return images_list


def get_embeded_images(soup, opts):
    images_list = []
    for i in soup("img"):
        image = i["src"]
        try:
            print(image)
            info = get_image(image, opts)
            if info:
                images_list.append(info)
        except IOError:
            err_print("Error: failed to retrieve the image.")
    return images_list


def get_image(image, opts):
    if RE_IMAGE.match(image):
        image = build_image_url(opts["url"], image)
        print(image)
        if not opts["isdump"]:
            file = url_to_filename(image, opts["dir"])
            if not opts["no_dl"]:
                res = requests.get(image)
                with open(file, "wb") as f:
                    for chunk in res.iter_content(chunk_size=128):
                        f.write(chunk)
            return {
                "file": str(os.path.basename(file)),
                "url": str(image),
                "page_url": opts["url"],
                "tags": opts["tags"],
            }
    return None


def url_to_filename(url, dir):
    filename = url.split("/")[-1]
    filename = re.sub(r"\?.+", "", filename)
    if dir:
        filename = os.path.join(dir, filename)
    return filename


def build_image_url(base, image):
    if re.match(r"\Ahttp", image):
        return image
    else:
        return urljoin(base, image)


def err_print(message):
    print(message, file=sys.stderr)
