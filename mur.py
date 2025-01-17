#!/usr/bin/env python3
# Sorrow446

import os
import re
import sys
import json
import shutil
import zipfile
import argparse
import platform
import tempfile

from requests.models import parse_url

import api
import img2pdf
from tqdm import tqdm
from requests.exceptions import HTTPError
from api.exceptions import IneligibleError

client = api.Client()


def print_title():
    print("""
 _____ _____ _____
|     |  |  | __  |
| | | |  |  |    -|
|_|_|_|_____|__|__|
   """)


def get_os():
    return platform.system() == 'Windows'


def set_con_title():
    if get_os():
        os.system('title MUR R1 (by Sorrow446)')
    else:
        sys.stdout.write('\x1b]2;MUR R1 (by Sorrow446)\x07')


def sanitize(fn):
    if get_os():
        return re.sub(r'[\/:*?"><|]', '_', fn)
    else:
        return re.sub('/', '_', fn)


def parse_args():
    parser = argparse.ArgumentParser(
        description='cradcore.'
    )
    parser.add_argument(
        '-u', '--url',
        help="URL - www.marvel.com/comics/issue/# or read.marvel.com/#/book/. or www.marvel.com/com/ics/series/#",
        nargs='*',
        required=True
    )
    parser.add_argument(
        '-f', '--format',
        help="Export format.",
        choices=['cbz', 'pdf'],
        required=True
    )
    parser.add_argument(
        '-m', '--meta',
        help="Write comic's metadata to JSON file.",
        action='store_true'
    )
    parser.add_argument(
        '--priv',
        help="Marvel developer account private key"
    )
    parser.add_argument(
        '--pub',
        help="Marvel developer account public key"
    )
    return parser.parse_args()


def parse_cookies(cd, out_cookies={}):
    cookies_path = os.path.join(cd, 'cookies.txt')
    if not os.path.exists(cookies_path):
        err("%s does not exist! Please save this file from the cookies.txt chrome/firefox extension before running" % cookies_path, 1, 1)
    with open(cookies_path) as f:
        for line in f:
            if not line.startswith('#') and not line == '\n':
                field = line.strip().split('\t')
                if len(field) != 7:
                    print("Error reading line %s", line)
                    continue
                out_cookies[field[5]] = field[6]
    client.set_cookies(out_cookies)


def exist_check(f):
    return os.path.isfile(f)


def dir_setup(tmp_dir, dl_dir):
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)
    if not os.path.isdir(dl_dir):
        os.makedirs(dl_dir)
    os.makedirs(tmp_dir)


def title_dir_setup(title_dir):
    if not os.path.isdir(title_dir):
        os.makedirs(title_dir)


def check_url(url):
    regexes = [
        r'http[s]://(read).marvel.com/#/(book)/([0-9]+$)',
        r'http[s]://(www).marvel.com/comics/(issue)/([0-9]+)/.+',
        r'http[s]://(www).marvel.com/comics/(series)/([0-9]+)/.+'
    ]
    for regex in regexes:
        match = re.match(regex, url)
        if match:
            return match.group(1), match.group(2), match.group(3)


def download(urls, tmp_dir, cur=0):
    total = len(urls)
    for url in urls:
        cur += 1
        print('Downloading image {} of {}...'.format(cur, total))
        r = client.session.get(url, stream=True)
        r.raise_for_status()
        size = int(r.headers.get('content-length', 0))
        abs = os.path.join(tmp_dir, str(cur).zfill(4)+'.jpg')
        with open(abs, 'wb') as f:
            with tqdm(total=size, unit='B',
                      unit_scale=True, unit_divisor=1024,
                      initial=0, miniters=1) as bar:
                for chunk in r.iter_content(32*1024):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))


def make_pdf(abs, images, title):
    with open(abs, 'wb') as f:
        f.write(img2pdf.convert(images, title=title))


def make_cbz(abs, images):
    with zipfile.ZipFile(abs, 'w', zipfile.ZIP_STORED) as f:
        for i in images:
            f.write(i)


def write_meta(meta_abs, meta):
    with open(meta_abs, 'w') as f:
        json.dump(meta, f, indent=4)


def err(e, cur, tot):
    print(e)
    if cur == tot:
        sys.exit(1)

def parse_keys(cd, private, public):
    if private is not None and public is not None:
        return private, public
    keys_file = os.path.join(cd, "keys.txt")
    if not exist_check(keys_file):
        return None, None
    with open(keys_file, 'r') as f:
        lines = f.read().splitlines()
        if len(lines) != 2:
            err("Invalid keys.txt format. You must have the private key on the first line, and public key on the second line", 1, 1)
        return lines[0], lines[1]

def main():
    if hasattr(sys, 'frozen'):
        cd = os.path.dirname(sys.executable)
    else:
        cd = os.path.dirname(__file__)

    # Create directories
    tmp_dir = os.path.join(tempfile.gettempdir(), 'mur')
    dl_dir = os.path.join(cd, 'downloads')
    dir_setup(tmp_dir, dl_dir)

    # Parse cookies and arguments
    parse_cookies(cd)
    args = parse_args()
    private_key, public_key = parse_keys(cd, args.priv, args.pub)

    # Check if entire series URL was passed in
    urls = []
    for url in args.url:
        _, scope, id = check_url(url)
        # If so, get URLs for individual issues
        if scope == 'series':
            if not client.is_series():
                client.set_series(True)
            if not client.has_keys():
                if private_key is None or public_key is None:
                    err("To download an entire series, you must pass in your public and private Marvel developer keys", 1, 1)
                client.set_keys(private_key, public_key)
            issueIds = client.parse_series(id)
            for issueId in issueIds:
                issueUrl = client.get_issue_url_from_id(issueId)
                urls.append(issueUrl)
        else:
            urls.append(url)
    if client.is_series():
        client.set_series(False)

    tot = len(urls)
    cur = 0
    for url in urls:
        cur += 1
        try:
            print("Comic {} of {}:".format(cur, tot))
            try:
                type, _, id = check_url(url)
            except TypeError:
                err('Invalid URL: '+str(url), cur, tot)
                continue
            if type == "www":
                id = client.get_issue_id(url)
            fmt = args.format
            meta = client.get_comic_meta(id)
            title = meta['title']
            title_s = sanitize(title)
            series_title = sanitize(meta['series_title'])
            print(str(title)+"\n")
            title_dir_setup(os.path.join(dl_dir, series_title))
            series_path = os.path.join(dl_dir, series_title)
            abs = os.path.join(series_path, '{}.{}'.format(title_s, fmt))
            if exist_check(abs):
                err('Comic already exists locally.', cur, tot)
                continue
            try:
                download(client.get_comic(id), tmp_dir)
            except IneligibleError as e:
                print(e)
                sys.exit(1)
            images = [os.path.join(tmp_dir, i.zfill(8))
                      for i in os.listdir(tmp_dir)]
            print('Converting to {}...'.format(fmt.upper()))
            if fmt == 'pdf':
                make_pdf(abs, images, title)
            else:
                make_cbz(abs, images)
            if args.meta:
                print("Writing metadata to JSON file...")
                meta_abs = os.path.join(
                    series_path, '{}_meta.json'.format(title_s))
                write_meta(meta_abs, meta)
            for i in images:
                os.remove(i)
        except HTTPError as e:
            err(e, cur, tot)
        except Exception as e:
            err(e, cur, tot)


if __name__ == '__main__':
    print_title()
    set_con_title()
    main()
