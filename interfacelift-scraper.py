#!/usr/bin/python
import os
import re
import urllib2
import threading
import Queue
import time

def download_file(url, saveDir):
    # interfacelift returns a 403 forbidden unless you include a referer.
    headers = { 'User-agent' : "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
                'Referer': url}
    req = urllib2.Request(url, None, headers)
    filename = imgFilePattern.search(url).group()
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

def download_worker():
    while True:
        url = queue.get()
        download_file(url, saveDir)
        queue.task_done()

def get_page_path(pageNumber):
    return '%sindex%d.html' % (resPath, pageNumber)

def get_url_from_path(path):
    return '%s/%s' % (host, path)

def get_page_url(pageNumber):
    return get_url_from_path(get_page_path(pageNumber))

def has_next_page(pageContent, currentPage):
    return True if pageContent.find(get_page_path(currentPage+ 1)) > -1 else False

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

def pretty_time(seconds):
    m, s = divmod(round(seconds), 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)

resPath = '/wallpaper/downloads/date/widescreen_16:9/1920x1080/'
host = 'http://interfacelift.com'
saveDir = 'wallpapers'

# hi guy from the future, if this script doesn't work, you probably need to update the regex.
tag = re.compile(r'<a href=\"(?P<path>.+)\"><img.+?src=\"/img_NEW/button_download')
imgFilePattern = re.compile(r'[^/]*$')

# number of threads
numThreads = 4

if not os.path.exists(saveDir):
    os.makedirs(saveDir)

queue = Queue.Queue();
timeStart = time.time()

# Create threads
for i in range(numThreads):
    t = threading.Thread(target=download_worker)
    t.daemon = True
    t.start()

# TODO: add urls to queue
page = 1
count = 0
while True:
    pageContent = open_page(page)
    links = tag.finditer(pageContent)
    for link in links:
        queue.put(get_url_from_path(link.group('path')))
        count += 1

    if has_next_page(pageContent, page):
        page += 1
    else:
        break

queue.join() # block until all urls processed
print '[*] Download finished! (%d files)' % count
print '[*] Time taken: %s' % pretty_time(time.time() - timeStart)
