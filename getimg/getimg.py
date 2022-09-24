import urllib
from urllib.request import urlopen, urlretrieve
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import yaml
import re
import sys
import os
import argparse
from . import __version__


script_version = f"v{__version__}"
re_image = re.compile(".+\.(jpg|jpeg|png|bmp|gif)")


def main():
    args = parse_arguments()

    url = args.url
    opts = {
        "url" : args.url,
        "dir" : args.dir,
        "tags" : args.tags,
        "isdump" : args.dump,
        "no_dl" : args.no_dl
    }

    if args.user_agent:
        class Iopener(urllib.FancyURLopener):
            version = args.user_agent
        urllib._urlopener = Iopener()

    if args.dir and not args.dump:
        try:
            os.makedirs(args.dir)
        except OSError:
            err_print(f"Directory exist: {args.dir}")
            exit()

    err_print(f"Download images from {url}\n")

    if args.input_url:
        log = []
        with open(args.input_url) as f:
            for image in f:
                image = image.rstrip()
                info = get_image(image, opts)
                log.append(info)
                print(image)
    else:
        try:
            res = urlopen(url).read()
        except IOError:
            err_print(f"Error: failed to retrieve the page: {url}")
            exit()
        soup = BeautifulSoup(res, "lxml")
        if args.html:
            print(soup.prettify())
            exit()
        if args.linked:
            log = get_linked_images(soup, opts)
        else:
            log = get_embeded_images(soup, opts)

    if not args.dump:
        err_print(f"\n{str(len(log))} images downloaded.")

    if args.sombrero:
        yamlfile = "images.yaml"
        if args.dir and not args.dump:
             yamlfile = os.path.join(args.dir, yamlfile)
        f = open(yamlfile, "w")
        f.write(yaml.dump(log))
        err_print(f"\nOutput log to {yamlfile}.")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Download images from web page")
    parser.add_argument("url",
        metavar="URL",
        action="store",
        help="specify page URL")
    parser.add_argument("-v", "--version",
        action="version",
        version=script_version,
        help="show version and exit")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-e", "--embeded-image",
        dest="embeded",
        action="store_true",
        help="download embeded images(default)")
    group.add_argument("-l", "--linked-image",
        dest="linked",
        action="store_true",
        help="download linked images")
    parser.add_argument("-d", "--dir",
        dest="dir",
        metavar="DIR",
        action="store",
        help="download into DIR")
    parser.add_argument("-t", "--tags",
        dest="tags",
        metavar="TAGS",
        action="store",
        default="",
        help="put tags. use with -s option")
    parser.add_argument("-u", "--user-agent",
        dest="user_agent",
        metavar="AGENT",
        action="store",
        help="specify user-agent")
    parser.add_argument("-i", "--input-url",
        dest="input_url",
        metavar="URLLIST",
        action="store",
        help="input image url list from file")
    parser.add_argument("-s", "--sombrero",
        dest="sombrero",
        action="store_true",
        help="output yaml to post to Sombrero")
    parser.add_argument("-D", "--dump",
        dest="dump",
        action="store_true",
        help="dump image url instead download it")
    parser.add_argument("-H", "--html-dump",
        dest="html",
        action="store_true",
        help="dump html source")
    parser.add_argument("-n", "--no-download",
        dest="no_dl",
        action="store_true",
        help="not download images")
    args = parser.parse_args()
    return args


def get_linked_images(soup, opts):
    images_list = []
    for a in soup("a"):
        for i in a("img"):
            a2 = i.parent
            if "href" not in a2.attrs:
                continue
            image = a2["href"]
            if re_image.match(image):
                image = build_image_url(opts["url"], image)
                print(image)
                if not opts["isdump"]:
                    try:
                        info = get_image(image, opts)
                        images_list.append(info)
                    except IOError:
                        err_print("Error: failed to retrieve the image.")
    return images_list


def get_embeded_images(soup, opts):
    images_list = []
    for i in soup("img"):
        image = i["src"]
        if re_image.match(image):
            image = build_image_url(opts["url"], image)
            print(image)
            if not opts["isdump"]:
                try:
                    info = get_image(image, opts)
                    images_list.append(info)
                except IOError:
                    err_print("Error: failed to retrieve the image.")
    return images_list


def get_image(image, opts):
    file = url_to_filename(image, opts["dir"])
    if not (opts["isdump"] or opts["no_dl"]):
        urlretrieve(image, file)
    return {
        "file" : str(os.path.basename(file)),
        "url" : str(image),
        "page_url" : opts["url"],
        "tags" : opts["tags"]
    }


def url_to_filename(url, dir):
    filename = url.split("/")[-1]
    filename = re.sub("\?.+", "", filename)
    if dir:
         filename = os.path.join(dir, filename)
    return filename


def build_image_url(base, image):
    if re.match("\Ahttp", image):
        return image
    else:
        return urljoin(base, image)


def err_print(message):
    sys.stderr.write(message + "\n")
