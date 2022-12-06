"""
Function: Geonames-lambda
Tasks: 
* Handle the url request from the API to execute the query to 
  geonames service passing q and lang parameters:

  ** This a temporary solution. the final Lambda must read the logic dynamically 
 """

import json
import urllib.request

def lambda_handler(event, context):
    service_geonames = "https://geogratis.gc.ca/services/geoname/_PARAM1_/geonames.json"
    lang = event.get("lang")
    q = event.get("q")
    url = service_geonames.replace("_PARAM1_",lang)
    print(url)
    url += "?q=" + q
    print(url)
    
    query_response =urllib.request.urlopen(urllib.request.Request(
        url=url,
        method='GET'),
        timeout=5)
        
    loads = json.loads(query_response.read())
    items=loads.get("items")
    # TODO implement
    return {
        'statusCode': 200,
        'loads': loads
    }
