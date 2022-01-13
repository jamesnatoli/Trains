# Natoli, 2021
# Script to get train next arrivals
########### Python 2.7 #############
import sys
import httplib, urllib, base64

headers = {
    # Request headers
    'api_key': '475a849cbcb44f9f8a5f6e73f8532319',
}

params = urllib.urlencode({
})

try:
    conn = httplib.HTTPSConnection('api.wmata.com')
    conn.request("GET", "/StationPrediction.svc/json/GetPrediction/all", "mystery", headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))
