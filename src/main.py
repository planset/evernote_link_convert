#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import clipboard

RE_URL = re.compile('https://www.evernote.com/shard/(.*?)/.*?/(.*?)/(.*?)/')

def url_to_evernote_link(url):
    try:
        m = RE_URL.search(url)
        return 'evernote:///view/{1}/{0}/{2}/{2}/'.format(*m.groups())
    except:
        raise Exception('Error! URL format has been changed. url={}'.format(url))

def main():
    cb = clipboard.Clipboard.get_clipboard()
    url = cb.read()
    evernote_link = url_to_evernote_link(url)
    cb.write(evernote_link)

if __name__ == '__main__':
    main()

