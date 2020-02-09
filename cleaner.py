#!/usr/bin/env python

from argparse import ArgumentParser
from http.client import HTTPSConnection
import multiprocessing
import os
import re
import sys
import subprocess as P
from urllib.parse import urlparse
from typing import List, Optional

def parse_args(args):
    argparser = ArgumentParser(description='clean plugins')
    argparser.add_argument('-c', '--openmwcfg', help='Path to the openmw.cfg file')
    argparser.add_argument('-u', '--mod-list-url', required=True, help='Where the list of mods can be found (hint: https://modding-openmw.com/lists/<your_version>/)')
    argparser.add_argument('-t', '--tes3cmd', default='tes3cmd', help='Location of tes3cmd')
    parsed = argparser.parse_args(args)
    if not os.path.isfile(parsed.openmwcfg):
        sys.stderr.write('{} does not exist\n'.format(parsed.openmwcfg))
        sys.exit(1)
    return parsed

def find_mods(openmwcfg):
    mods = {} # esp name -> esp path
    with open(openmwcfg, 'rt') as f:
        for line in f.readlines():
            clean_line = line.strip()
            if clean_line == '' or clean_line.startswith('#') or '=' not in clean_line: continue
            pieces = [piece.strip() for piece in clean_line.split('=')]
            if pieces[0] == 'data':
                if pieces[1][0] == '"' and pieces[1][-1] == '"':
                    data_dir = pieces[1][1:-1] # remove the quote around
                else:
                    data_dir = pieces[1]
                for basedir, dirnames, filenames in os.walk(data_dir):
                    for filename in filenames:
                        if filename.lower().endswith('esp'):
                            if filename not in mods: mods[filename] = set()
                            mods[filename].add(os.path.join(basedir, filename)) 
    return mods

clean_regex = re.compile('<a href="/tips/cleaning-with-tes3cmd/">([yYnN][^<]+)</a>')
esp_regex = re.compile('[^>]+\\.esp')

def first_or_none(xs):
    return None if len(xs) < 1 else xs[0]

def getbody_or_die(host, url) -> str:
    conn = HTTPSConnection(host=host)
    try:
        print('GET {} {}'.format(host, url))
        conn.request('GET', url=url)
        r = conn.getresponse()
        if r.getcode() < 200 or r.getcode() >= 300:
            sys.stderr.write('Error while sending a request to {}. code: {} reason: {}'.format(url, r.getcode(), r.reason))
            sys.exit(5)
        return r.read().decode()
    finally:
        print('GET DONE {} {}'.format(host, url))
        conn.close()

def get_dirty_esps(host, path) -> List[str]:
    body = getbody_or_die(host, path)
    yes_no_none = first_or_none(clean_regex.findall(body))
    if yes_no_none == None or yes_no_none.lower() == 'no':
        return []
    return esp_regex.findall(body)

def download_dirty_mods(mod_list_url):
    dirty_mods = set()
    host = mod_list_url.netloc
    body = getbody_or_die(host, mod_list_url.path)
    mod_paths = [path[1:] for path in re.compile('"/mods/[^"]+').findall(body)]
    mod_list_url.netloc
    pool = multiprocessing.Pool()
    espss = pool.starmap(get_dirty_esps, ((host, path) for path in mod_paths))
    for esps in espss:
        for esp in esps:
            dirty_mods.add(esp)
    return dirty_mods

def clean(tes3cmd, esp_path):
    r = P.run([tes3cmd, 'clean', esp_path], encoding='UTF-8', stdout=P.PIPE, stderr=P.PIPE)
    for line in r.stdout.split('\n'):
        if line.strip() != '':
            print(line)
    if r.returncode == 0:
        print('CLEANING DONE {}'.format(esp_path))
    else:
        print('CLEANING ERROR {} {}'.format(r.returncode, esp_path))
        for line in r.stderr.split('\n'):
            if line.strip() != '':
                sys.stderr.write('{}\n'.format(line))

def main():
    args = parse_args(sys.argv[1:])
    mods = find_mods(args.openmwcfg)
    mod_list_url = urlparse(args.mod_list_url)
    dirty_mods_in_list = download_dirty_mods(mod_list_url)
    for esp_filename in mods.keys():
        if esp_filename in dirty_mods_in_list:
            for esp_paths in mods[esp_filename]:
                clean(args.tes3cmd, esp_paths)

if __name__=='__main__':
    main()