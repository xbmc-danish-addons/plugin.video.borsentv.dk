#
#      Copyright (C) 2012 Tommy Winther
#      http://tommy.winther.nu
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#
import os
import sys
import urlparse
import urllib2
import re
import datetime

import buggalo

import xbmcgui
import xbmcaddon
import xbmcplugin

BASE_URL = 'http://borsen.dk/tv/'
MONTHS = ['jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov','dec']

class BorsenTVAddon(object):
    def showCategories(self):
        u = urllib2.urlopen(BASE_URL)
        html = u.read()
        u.close()

        for m in re.finditer('href="/tv/([^"]+)".*?>([^<]+)<', html):
            id = m.group(1)
            title = m.group(2)
            item = xbmcgui.ListItem(title, iconImage = ICON)
            xbmcplugin.addDirectoryItem(HANDLE, PATH + '?category=%s' % id, item, isFolder = True)

        xbmcplugin.endOfDirectory(HANDLE)

    def showCategory(self, path):
        u = urllib2.urlopen(BASE_URL + path)
        html = u.read()
        u.close()

        for m in re.finditer('class="time">(.*?)</span>.*?href="([^"]+)" title="([^"]+)"', html, re.DOTALL):
            dateStr = m.group(1).strip()
            url = m.group(2)
            title = m.group(3)

            date = self._parseDate(dateStr)

            item = xbmcgui.ListItem(title, iconImage = ICON)
            item.setInfo('video', infoLabels = {
                'title' : title,
                'date' : date.strftime('%d.%m.%Y'),
                'aired' : date.strftime('%d-%m-%Y'),
                'studio' : ADDON.getAddonInfo('name'),
                'year' : int(date.strftime('%Y'))
            })

            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(HANDLE, PATH + '?video=%s' % url, item, isFolder = False)

        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.endOfDirectory(HANDLE)

    def playVideo(self, url):
        u = urllib2.urlopen(url)
        html = u.read()
        u.close()

        m = re.search('poster="([^"]+)".*?source src="([^"]+)" type="video/mp4"', html)
        poster = m.group(1)
        videoUrl = m.group(2)

        item = xbmcgui.ListItem(path=videoUrl, thumbnailImage=poster)
        xbmcplugin.setResolvedUrl(HANDLE, True, item)

    def _parseDate(self, input):
        d = datetime.datetime.now()
        m = re.search('(\d{1,2})\. ([a-z]{3})\.', input)
        if m is not None:
            month = MONTHS.index(m.group(2)) + 1
            year = d.year
            if month > d.month:
                year -= 1
            d = datetime.datetime(year = year, month = month, day = int(m.group(1)))

        return d

if __name__ == '__main__':
    ADDON = xbmcaddon.Addon()
    PATH = sys.argv[0]
    HANDLE = int(sys.argv[1])
    PARAMS = urlparse.parse_qs(sys.argv[2][1:])

    ICON = os.path.join(ADDON.getAddonInfo('path'), 'icon.png')

    buggalo.SUBMIT_URL = 'http://tommy.winther.nu/exception/submit.php'
    try:
        btv = BorsenTVAddon()
        if PARAMS.has_key('category'):
            btv.showCategory(PARAMS['category'][0])
        elif PARAMS.has_key('video'):
            btv.playVideo(PARAMS['video'][0])
        else:
            btv.showCategories()
    except Exception:
        buggalo.onExceptionRaised()
