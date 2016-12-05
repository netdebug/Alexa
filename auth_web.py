#! /usr/bin/env python

import json
import os
import urllib

import cherrypy
import requests

from creds import *


class Start(object):
    def index(self):
        scope = "alexa_all"
        sd = json.dumps({
            "alexa:all": {
                "productID": ProductID,
                "productInstanceAttributes": {
                    "deviceSerialNumber": "001"
                }
            }
        })
        url = "https://www.amazon.com/ap/oa"
        callback = cherrypy.url() + "authresponse"
        payload = {"client_id": Client_ID, "scope": "alexa:all", "scope_data": sd, "response_type": "code",
                   "redirect_uri": callback}
        req = requests.Request('GET', url, params=payload)
        p = req.prepare()
        raise cherrypy.HTTPRedirect(p.url)

    def authresponse(self, var=None, **params):
        code = urllib.quote(cherrypy.request.params['code'])
        callback = cherrypy.url()
        payload = {"client_id": Client_ID, "client_secret": Client_Secret, "code": code,
                   "grant_type": "authorization_code", "redirect_uri": callback}
        url = "https://api.amazon.com/auth/o2/token"
        r = requests.post(url, data=payload)
        resp = r.json()
        line = '\nrefresh_token = "{}"'.format(resp['refresh_token'])
        with open("creds.py", 'a') as f:
            f.write(line)
        return "Success!, refresh token has been added to your creds file, you may now run <code>python alexa.py</code> <br>{}".format(
            resp['refresh_token'])

    index.exposed = True
    authresponse.exposed = True


cherrypy.config.update({'server.socket_host': '0.0.0.0',})
cherrypy.config.update({'server.socket_port': int(os.environ.get('PORT', '3000')),})
print('Open http://localhost:3000 to login in amazon alexa service')
cherrypy.quickstart(Start())
