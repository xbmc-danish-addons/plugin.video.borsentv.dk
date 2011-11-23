import os
import sys
import urlparse
import urllib2
import re

from elementtree import ElementTree
#from xml.etree import ElementTree

import xbmcgui
import xbmcaddon
import xbmcplugin

CATEGORIES = {
    30100 : 'QWxsZQ==',
    30101 : 'SW52ZXN0b3I=',
    30102 : 'IFByaXZhdPhrb25vbWk=',
    30103 : '2Gtvbm9taQ==',
    30104 : 'UG9saXRpaw==',
    30105 : 'SVQ=',
    30106 : 'S2FycmllcmU=',
    30107 : 'd2Vla2VuZA==',
    30108 : 'QWxsZQ=='
}

VIDEO_URL = 'http://borsentv.dk/services/frontend/borsentv/mFrontendT2_latestClips.php?perpage=5&showdate=1&tab1=%s=&maxItems=50&activatedTab1=1'
#RTMP_URL = 'rtmp://stream.borsentv.dk/arkiv/borsen_tv/mp4:%s.mp4'
RTMP_URL = 'rtmp://stream.borsentv.dk/arkiv'
RTMP_PATH = 'borsen_tv/mp4:%s.mp4'

class BorsenTVAddon(object):
    def showCategories(self):
        for id, slug in CATEGORIES.items():
            item = xbmcgui.ListItem(ADDON.getLocalizedString(id), iconImage = ICON)
            xbmcplugin.addDirectoryItem(HANDLE, PATH + '?category=%s' % slug, item, isFolder = True)

        xbmcplugin.endOfDirectory(HANDLE)

    def showCategory(self, slug):
        u = urllib2.urlopen(VIDEO_URL % slug)
        xml = u.read()
        u.close()

        dom = ElementTree.fromstring(xml)
        for video in dom.find('videos/tab'):
            image = video.findtext('sthumb').replace('_125.jpg', '.jpg')

            item = xbmcgui.ListItem(video.findtext('title'), iconImage = image, thumbnailImage = image)
            item.setInfo('video', infoLabels = {
                'title' : video.findtext('title'),
                'plot' : video.findtext('description').replace('<br />', '')
            })

            # Parse video id from file_url
            m = re.search('([0-9]+)$', video.findtext('file_url'))
            url = RTMP_PATH % m.group(1)
            item.setProperty('PlayPath', url)
            item.setProperty('tcUrl', RTMP_URL)
            xbmcplugin.addDirectoryItem(HANDLE, RTMP_URL, item)

        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.endOfDirectory(HANDLE)

if __name__ == '__main__':
    ADDON = xbmcaddon.Addon(id = 'plugin.video.borsentv.dk')
    PATH = sys.argv[0]
    HANDLE = int(sys.argv[1])
    PARAMS = urlparse.parse_qs(sys.argv[2][1:])

    ICON = os.path.join(ADDON.getAddonInfo('path'), 'icon.png')

    btv = BorsenTVAddon()
    if PARAMS.has_key('category'):
        btv.showCategory(PARAMS['category'][0])
    else:
        btv.showCategories()


