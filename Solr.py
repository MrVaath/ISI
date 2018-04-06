#!/usr/bin/python2
# -*- coding: utf-8 -*-

import urllib2
import json

topKek = 0

server = '150.254.78.133'
core = 'isi'

url = 'http://%s:8983/solr/%s/update/json/docs?commit=true' % (server, core)

def test(start, stop):
    global topKek
    try:
        for i in range(start, stop):
            data = json.dumps(d[i])
            req = urllib2.Request(url, data)
            req.add_header('Content-type', 'application/json')
            response = urllib2.urlopen(req)
            the_page = response.read()
            print('Post: ' + str(i))
            print(the_page)
    except:
        topKek = topKek + 1
        print('Nie udało się :< ' + str(topKek))
        test(i+1, stop)
    return;

with open('data.json') as json_data:
    d = json.load(json_data)
    test(0, len(d))
