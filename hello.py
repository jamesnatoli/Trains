########### Python 2.7 #############
import httplib, urllib, base64

headers = {
    # Request headers
    'api_key': '475a849cbcb44f9f8a5f6e73f8532319',
}

params = urllib.urlencode({
    # Request parameters
    'Name': 'Gallery Place',
})

try:
    conn = httplib.HTTPSConnection('api.wmata.com')
    conn.request("GET", "/Rail.svc/json/jStations?", "{body}", headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))
