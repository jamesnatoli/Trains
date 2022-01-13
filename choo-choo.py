########### Python 2.7 #############
import sys
import json
import httplib, urllib, base64

headers = {
    # Request headers
    'api_key': '475a849cbcb44f9f8a5f6e73f8532319',
}

requestString = {
    'station_info' : "/Rail.svc/json/jStations?",
    'arrival_info' : '/StationPrediction.svc/json/GetPrediction/all',
}

params = urllib.urlencode({
})

def webConnect( params):
    conn = httplib.HTTPSConnection('api.wmata.com')
    conn.request("GET", requestString[ params], "mystery", headers)
    # conn.request("GET", "/Rail.svc/json/jStations?", "mystery", headers)
    response = conn.getresponse()
    conn.close()
    return response.read()
    
def getStationInfo( printerMode=False):
    json_dict = json.loads( webConnect( 'station_info'))

    # Crack Open the Dictionary
    stations = json_dict['Stations']
    code_dict = {}
    for ele in stations:
        if printerMode:
            print("%50s: \t%s \t%s" % (ele['Name'], ele['Code'], ele['LineCode1']))
        code_dict[ ele['Name']] = ele['Code']

def getArrivals():
    json_dict = json.loads( webConnect( 'arrival_info'))
    print json_dict
    
def main():
    getStationInfo()
    # getArrivals()
    
if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
    # except Exception as e:
    #     print "Error: Info below..."
    #     print e
