#!/usr/bin/env python3
# helper for interacting with imgur api
# Now only download images and images from album
# I'll add new features once needed...


import requests
from argparse import ArgumentParser
from os import mkdir

SECRET_FILE="./.imgur_secrets"
BASE_URL = "https://api.imgur.com/3/"


def get_args():
    p = ArgumentParser(description="Python helper for interacting with imgur api")

    p.add_argument("--no-verify", help="Do not verify ssl certificate", action="store_true", default=False)
    p.add_argument("-i", "--image", help="Download an image")
    p.add_argument("-a", "--album", help="Download an album")
    p.add_argument("-o", "--output", help="Output directory for downloaded content", default=".")

    return p.parse_args()


def get_secrets():
    CLIENT_ID = CLIENT_SECRET = ""
    with open(SECRET_FILE, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.replace("\n","")

        if line.startswith("CLIENT_ID"):
            CLIENT_ID = line.split("=")[1]
        elif line.startswith("CLIENT_SECRET"):
            CLIENT_SECRET = line.split("=")[1]

    return (CLIENT_ID, CLIENT_SECRET)


class Pymgur(object):
    def __init__(self, secrets, no_verify):
        self.cid, self.csec = secrets
        self.verify = not no_verify
        self.s = requests.Session()

        if not self.verify:
            requests.packages.urllib3.disable_warnings()
            print("[!] Warning: SSL cert check is disabled.")


    def get(self, endpoint, fmt=None):
        return self.raw_get(f"{BASE_URL}{endpoint}", {'Authorization': f'Client-ID {self.cid}'}, fmt)

    def raw_get(self, url, headers=None, fmt=None):
        data = self.s.get(url, headers=headers, verify=self.verify)
        if fmt == 'json':
            return data.json()
        else:
            return data.content


def get_ext(imgtype):
    ext = ""
    if imgtype == 'image/jpeg':
        ext = "jpg"
    elif imgtype == 'image/png':
        ext = "png"
    return ext


def main():
    args = get_args()
    pymgur = Pymgur(get_secrets(), args.no_verify)
    if args.image:
        print(f"[*] Downloading image {args.image}...")
        imgdata = pymgur.get(f"image/{args.image}", fmt='json')['data']
        img = pymgur.raw_get(imgdata["link"])
        ext = get_ext(imgdata['type'])

        with open(f"{args.output}/{imgdata['id']}.{ext}", "wb") as f:
            f.write(img)

        print(f"[+] Image saved @ {args.output}/{imgdata['id']}.{ext}")
        return

    if args.album:
        print("[*] Retrieving album images...")
        albumdata = pymgur.get(f"album/{args.album}/images", fmt='json')['data']
        print(f"[+] Data acquired, total images: {len(albumdata)}")
        print(f"[*] Downloaded images will go to {args.output}/{args.album} ...")

        try:
            mkdir(f"{args.output}/{args.album}")
        except FileExistsError:
            pass

        for imgdata in albumdata:
            img = pymgur.raw_get(imgdata["link"])
            ext = get_ext(imgdata['type'])
            print(f"[*] Downloading image {imgdata['id']} to {args.output}/{args.album}/{imgdata['id']}.{ext} ...")

            with open(f"{args.output}/{args.album}/{imgdata['id']}.{ext}", "wb") as f:
                f.write(img)

        print("[+] All images from album retrived!")
        return


if __name__=='__main__':
    main()
