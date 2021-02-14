#!/usr/bin/env python
# coding: utf-8

import sys
from urllib.request import urlopen, urlretrieve
from urllib.parse import urlparse, urljoin
import re
import argparse
import os
from bs4 import BeautifulSoup
import yaml


script_version = 'v0.6.0'
re_image = re.compile(".+\.(jpg|jpeg|png|bmp|gif)")


def main():
    parser = argparse.ArgumentParser(description="Download images from web page.")
    parser.add_argument('url', metavar='URL', action='store',
                        help='specify URL')
    parser.add_argument('-v', '--version', action='version', version=script_version,
                        help='show version and exit')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-e', '--embeded-image', dest='embeded', action='store_true',
                       help='download embeded images(default)')
    group.add_argument('-l', '--linked-image', dest='linked', action='store_true',
                       help='download linked images')
    parser.add_argument('-d', '--dir', dest='dir', metavar='DIR', action='store',
                        help='download into DIR')
    parser.add_argument('-t', '--tags', dest='tags', metavar='TAGS', action='store', default='',
                        help='put tags. use with -s option')
    parser.add_argument('-u', '--user-agent', dest='user_agent', metavar='AGENT', action='store',
                        help='specify user-agent')
    parser.add_argument('-i', '--input-url', dest='input_url', metavar='URLLIST', action='store',
                        help='input image url list from file')
    parser.add_argument('-s', '--sombrero', dest='sombrero', action='store_true',
                        help='output yaml to post to Sombrero')
    parser.add_argument('-D', '--dump', dest='dump', action='store_true',
                        help='dump image url instead download it')
    parser.add_argument('-H', '--html-dump', dest='html', action='store_true',
                        help='dump html source')
    parser.add_argument('-n', '--no-download', dest='no_dl', action='store_true',
                        help='not download images')
    args = parser.parse_args()

    url = args.url

    if args.user_agent:
        class Iopener(urllib.FancyURLopener):
            version = args.user_agent
        urllib._urlopener = Iopener()

    if args.dir and not args.dump:
        try:
            os.makedirs(args.dir)
        except OSError:
            err_print("Directory exist: " + args.dir)
            exit()
    err_print("Download images from " + url + "\n")
    if args.input_url:
        log = []
        f = open(args.input_url)
        for image in f:
            image = image.rstrip()
            info = get_image(image)
            log.append(info)
            print(image)
    else:
        try:
            res = urlopen(url).read()
        except IOError:
            err_print("Error: failed to retrieve the page: " + url)
            exit()
        soup = BeautifulSoup(res, "lxml")
        if args.html:
            print(soup.prettify())
            exit()
        if args.linked:
            log = get_linked_images(soup)
        else:
            log = get_embeded_images(soup)

    if not args.dump:
        err_print("\n" + str(len(log)) + " images downloaded.")

    if args.sombrero:
        yamlfile = 'images.yaml'
        if args.dir and not args.dump:
             yamlfile = os.path.join(args.dir, yamlfile)
        f = open(yamlfile, 'w')
        f.write(yaml.dump(log))
        err_print("\nOutput log to " + yamlfile + ".")


def get_linked_images(soup):
    images_list = []
    for a in soup("a"):
        for i in a("img"):
            a2 = i.parent
            if "href" not in a2.attrs:
                continue
            image = a2["href"]
            if re_image.match(image):
                image = build_image_url(args.url, image)
                print(image)
                if not args.dump:
                    try:
                        info = get_image(image)
                        images_list.append(info)
                    except IOError:
                        err_print("Error: failed to retrieve the image.")
    return images_list


def get_embeded_images(soup):
    images_list = []
    for i in soup("img"):
        image = i["src"]
        if re_image.match(image):
            image = build_image_url(args.url, image)
            print(image)
            if not args.dump:
                try:
                    info = get_image(image)
                    images_list.append(info)
                except IOError:
                    err_print("Error: failed to retrieve the image.")
    return images_list


def get_image(image):
    file = url_to_filename(image)
    if not (args.dump or args.no_dl):
        urlretrieve(image, file)
    return {'file' : str(os.path.basename(file)),
            'url' : str(image),
            'page_url' : args.url,
            'tags' : args.tags}


def url_to_filename(url):
    filename = url.split('/')[-1]
    filename = re.sub('\?.+', '', filename)
    if args.dir:
         filename = os.path.join(args.dir, filename)
    return filename


def build_image_url(base, image):
    if re.match("\Ahttp", image):
        return image
    else:
        return urljoin(base, image)


def err_print(message):
    sys.stderr.write(message + "\n")



main()
