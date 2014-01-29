import os, re, urllib2

scrapeUrl = "http://interfacelift.com/wallpaper/downloads/date/widescreen_16:9/1920x1080/"
host = 'http://interfacelift.com'
saveDir = 'scraped'

# how many you want to download, 0 to download all
goal = 0
done = 0
# go to your scrape url, note down how many pages there are. this should not exceed the max.
maxPages = 209

# hi guy from the future, if this script doesn't work, you probably need to update the regex.
tag = re.compile(r"<a href=\"(?P<url>.+)\"><img.+?src=\"/img_NEW/button_download")


if not os.path.exists(saveDir) :
    os.makedirs(saveDir)

# pointless, just makes the output a little nicer.
# formats goal if 0 to read 'about XX' 
goalStr = str(goal)
if goal == 0:
    # round up maxPages*10 to next hundredth
    # shitty convoluted code, i know, but works
    goal = maxPages*10 + 99
    goal = goal - (goal % 100)
    goalStr = 'about %s' % str(goal)

for page in range(1, maxPages+1):
    print 'opening page %s of %s' % (page, maxPages)
    
    url = scrapeUrl + "index" + str(page)

    # interfacelift returns a 403 forbidden unless you include a referer.
    headers = { 'User-agent' : "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
                'Referer': url}
    try:
        req = urllib2.Request(url, None, headers)
        f = urllib2.urlopen(req)

    except IOError, e:
        print "Failed to open", url
        if hasattr(e, 'code'):
            print "Error code:", e.code
        continue

    html = f.read()

    links = tag.finditer(html)

    for i in links:
        if goal == 0 or done < goal :
            print "scraping " + str(done + 1) + " of " + goalStr
            dlurl = host + i.group('url')
            req = urllib2.Request(dlurl, None, headers)
            saveFile = os.path.join(saveDir, str(done)+'.jpg')
            with open(saveFile, 'wb') as f:
                try:
                    res = urllib2.urlopen(req)
                    f.write(res.read())
                except:
                    print 'failed'
                    try:
                        os.remove(saveFile)
                    except: pass

            done += 1
