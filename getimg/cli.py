import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
import yaml
import os
import argparse
from . import __version__
from .getimg import (
    err_print,
    get_linked_images,
    get_embeded_images,
    get_image,
)


SCRIPT_VERSION = f"v{__version__}"


def main():
    args = parse_arguments()

    url = args.url
    opts = {
        "url": args.url,
        "dir": args.dir,
        "tags": args.tags,
        "isdump": args.dump,
        "no_dl": args.no_dl,
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
        with open(yamlfile, "w") as f:
            f.write(yaml.dump(log))
        err_print(f"\nOutput log to {yamlfile}.")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Download images from web page"
    )
    parser.add_argument(
        "url", metavar="URL", action="store", help="specify page URL"
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=SCRIPT_VERSION,
        help="show version and exit",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-e",
        "--embeded-image",
        dest="embeded",
        action="store_true",
        help="download embeded images(default)",
    )
    group.add_argument(
        "-l",
        "--linked-image",
        dest="linked",
        action="store_true",
        help="download linked images",
    )
    parser.add_argument(
        "-d",
        "--dir",
        dest="dir",
        metavar="DIR",
        action="store",
        help="download into DIR",
    )
    parser.add_argument(
        "-t",
        "--tags",
        dest="tags",
        metavar="TAGS",
        action="store",
        default="",
        help="put tags. use with -s option",
    )
    parser.add_argument(
        "-u",
        "--user-agent",
        dest="user_agent",
        metavar="AGENT",
        action="store",
        help="specify user-agent",
    )
    parser.add_argument(
        "-i",
        "--input-url",
        dest="input_url",
        metavar="URLLIST",
        action="store",
        help="input image url list from file",
    )
    parser.add_argument(
        "-s",
        "--sombrero",
        dest="sombrero",
        action="store_true",
        help="output yaml to post to Sombrero",
    )
    parser.add_argument(
        "-D",
        "--dump",
        dest="dump",
        action="store_true",
        help="dump image url instead download it",
    )
    parser.add_argument(
        "-H",
        "--html-dump",
        dest="html",
        action="store_true",
        help="dump html source",
    )
    parser.add_argument(
        "-n",
        "--no-download",
        dest="no_dl",
        action="store_true",
        help="not download images",
    )
    args = parser.parse_args()
    return args
