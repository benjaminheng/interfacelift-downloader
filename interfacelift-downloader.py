#!/usr/bin/python

from __future__ import print_function
# Imports for Python 3 and 2 respectively
try:
    from urllib.request import urlopen, Request
    import queue
except ImportError:
    from urllib2 import urlopen, Request
    import Queue as queue

import os
import sys
import re
import threading
import time
import argparse

HOST = 'http://interfacelift.com'
RES_PATHS = {
        '3840x2400': '/wallpaper/downloads/date/wide_16:10/3840x2400/',
        '3360x2100': '/wallpaper/downloads/date/wide_16:10/3360x2100/',
        '2880x1800': '/wallpaper/downloads/date/wide_16:10/2880x1800/',
        '2560x1600': '/wallpaper/downloads/date/wide_16:10/2560x1600/',
        '2560x1600': '/wallpaper/downloads/date/wide_16:10/1920x1200/',
        '1680x1050': '/wallpaper/downloads/date/wide_16:10/1680x1050/',
        '1440x900': '/wallpaper/downloads/date/wide_16:10/1440x900/',
        '1280x800': '/wallpaper/downloads/date/wide_16:10/1280x800/',
        '5120x2880': '/wallpaper/downloads/date/wide_16:9/5120x2880/',
        '3840x2160': '/wallpaper/downloads/date/wide_16:9/3840x2160/',
        '2880x1620': '/wallpaper/downloads/date/wide_16:9/2880x1620/',
        '2560x1440': '/wallpaper/downloads/date/wide_16:9/2560x1440/',
        '1920x1080': '/wallpaper/downloads/date/wide_16:9/1920x1080/',
        '1600x900': '/wallpaper/downloads/date/wide_16:9/1600x900/',
        '1280x720': '/wallpaper/downloads/date/wide_16:9/1280x720/',
        '2560x1080': '/wallpaper/downloads/date/wide_21:9/2560x1080/',

        '2560x1024': '/wallpaper/downloads/date/2_screens/2560x1024/',
        '2880x900': '/wallpaper/downloads/date/2_screens/2880x900/',
        '3200x1200': '/wallpaper/downloads/date/2_screens/3200x1200/',
        '3360x1050': '/wallpaper/downloads/date/2_screens/3360x1050/',
        '3840x1200': '/wallpaper/downloads/date/2_screens/3840x1200/',
        '5120x1600': '/wallpaper/downloads/date/2_screens/5120x1600/',

        '3840x960': '/wallpaper/downloads/date/3_screens/3840x960/',
        '3840x1024': '/wallpaper/downloads/date/3_screens/3840x1024/',
        '4320x900': '/wallpaper/downloads/date/3_screens/4320x900/',
        '4096x1024': '/wallpaper/downloads/date/3_screens/4096x1024/',
        '4800x1200': '/wallpaper/downloads/date/3_screens/4800x1200/',
        '5040x1050': '/wallpaper/downloads/date/3_screens/5040x1050/'
        }

IMG_PATH_PATTERN = re.compile(r'<a href=\"(?P<path>.+)\"><img.+?src=\"/img_NEW/button_download')
IMG_FILE_PATTERN = re.compile(r'[^/]*$')

# Downloads the given url and write it to the given directory
def download_file(url, saveDir):
    # interfacelift returns a 403 forbidden unless you include a referer.
    headers = { 'User-Agent' : "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
                'Referer': url}
    req = Request(url, None, headers)
    filename = IMG_FILE_PATTERN.search(url).group()
    saveFile = os.path.join(saveDir, filename)
    with open(saveFile, 'wb') as f:
        try:
            res = urlopen(req)
            f.write(res.read())
            print('[+] Downloaded %s' % filename)
        except Exception as e:
            print(e)
            try: os.remove(saveFile)
            except: pass

# Thread worker. Constantly takes URLs from the queue
def download_worker():
    while True:
        url = queue.get()
        download_file(url, SAVE_DIR)
        queue.task_done()

# Returns the path of the specified page number
def get_page_path(pageNumber):
    return '%sindex%d.html' % (RES_PATH, pageNumber)

# Returns the full URL of the specified path
def get_url_from_path(path):
    return '%s/%s' % (HOST, path)

# Returns the full URL of the specified page number
def get_page_url(pageNumber):
    return get_url_from_path(get_page_path(pageNumber))

# Returns True if next page exists, else False
def has_next_page(pageContent, currentPage):
    return True if pageContent.find(get_page_path(currentPage+ 1)) > -1 else False

# Opens the specified page and returns the page's HTML content
def open_page(pageNumber):
    url = get_page_url(pageNumber)
    # interfacelift returns a 403 forbidden unless you include a referer.
    headers = { 'User-Agent' : "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
                'Referer': url}
    try:
        req = Request(url, None, headers)
        f = urlopen(req)
    except IOError as e:
        print('Failed to open', url)
        if hasattr(e, 'code'):
            print('Error code:', e.code)
    return f.read().decode(errors='ignore')

# Returns the specified number of seconds in H:MM:SS format
def pretty_time(seconds):
    m, s = divmod(round(seconds), 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)

# Validates the supplied arguments
def validate_args(parser, args):
    if args.list:
        print('Available resolutions:')
        for key in RES_PATHS:
            print('%s' % key)
        sys.exit(0)
    if args.resolution not in list(RES_PATHS.keys()):
        print('Invalid specified resolution (%s)' % args.resolution)
        print('List available resolutions: %s --list' % os.path.basename(__file__))
        sys.exit(1)

# Prints the starting variables for the script
def print_starting_vars():
    print('Selected resolution: %s' % args.resolution)
    print('Destination directory: %s' % SAVE_DIR)
    print('Threads: %s' % THREADS)
    
# Parse arguments
parser = argparse.ArgumentParser(description='Download wallpapers from interfacelift.com')
parser.add_argument('resolution', nargs='?', help='the resolution to download (default: 1920x1080)', default='1920x1080')
parser.add_argument('-d', '--dest', help='the directory to download to (default: ./wallpapers)', default='wallpapers')
parser.add_argument('-t', '--threads', help='the number of threads to use (default: 4)', default=4, type=int)
parser.add_argument('--list', help='list available resolutions', action='store_true')
args = parser.parse_args()
validate_args(parser, args)

# Initialize and print starting variables 
RES_PATH = RES_PATHS[args.resolution]
SAVE_DIR = args.dest
THREADS = args.threads
print_starting_vars()

# Create directory if not exist
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

queue = queue.Queue();
timeStart = time.time()

# Create threads
for i in range(THREADS):
    t = threading.Thread(target=download_worker)
    t.daemon = True
    t.start()

# Add image URLs to queue
page = 1
count = 0
while True:
    pageContent = open_page(page)
    links = IMG_PATH_PATTERN.finditer(pageContent)
    for link in links:
        queue.put(get_url_from_path(link.group('path')))
        count += 1

    # break if no next page
    if has_next_page(pageContent, page):
        page += 1
    else:
        break

queue.join() # block until all urls processed
print('[*] Download finished! (%d files)' % count)
print('[*] Time taken: %s' % pretty_time(time.time() - timeStart))
