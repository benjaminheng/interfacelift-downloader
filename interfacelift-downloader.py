#!/usr/bin/python
import os
import re
import urllib2
import threading
import Queue
import time

HOST = 'http://interfacelift.com'
RES_PATH = '/wallpaper/downloads/date/widescreen_16:9/1920x1080/'
SAVE_DIR = 'wallpapers'
THREADS = 1

IMG_PATH_PATTERN = re.compile(r'<a href=\"(?P<path>.+)\"><img.+?src=\"/img_NEW/button_download')
IMG_FILE_PATTERN = re.compile(r'[^/]*$')

# Downloads the given url and write it to the given directory
def download_file(url, saveDir):
    # interfacelift returns a 403 forbidden unless you include a referer.
    headers = { 'User-agent' : "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
                'Referer': url}
    req = urllib2.Request(url, None, headers)
    filename = IMG_FILE_PATTERN.search(url).group()
    saveFile = os.path.join(saveDir, filename+'.jpg')
    with open(saveFile, 'wb') as f:
        try:
            res = urllib2.urlopen(req)
            f.write(res.read())
            print '[+] Downloaded %s' % filename
        except Exception as e:
            print e
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
    headers = { 'user-agent' : "mozilla/4.0 (compatible; msie 5.5; windows nt)",
                'referer': url}
    try:
        req = urllib2.Request(url, None, headers)
        f = urllib2.urlopen(req)
    except IOError, e:
        print 'failed to open', url
        if hasattr(e, 'code'):
            print 'error code:', e.code
    return f.read()

# Returns the specified number of seconds in H:MM:SS format
def pretty_time(seconds):
    m, s = divmod(round(seconds), 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)

# Create directory if not exist
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

queue = Queue.Queue();
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
print '[*] Download finished! (%d files)' % count
print '[*] Time taken: %s' % pretty_time(time.time() - timeStart)
