"""
Function: Geolocator-lambda
Tasks: 
* Handle the url request from the API to identify,
  validate and assert the input query and additional parameters

* Retrieve the set of attributes and methods associated 
  with each service required in the url request
* Build and execute a new REST request for each associated service
* Retrieve and return the normalized payload form the call
"""
import json
import urllib.request

class URL_object:
    def __init__(self, name, url_base, address, dict_params={}):
        self.name = name
        self.url = url_base
        self.params = dict_params
        self.address = address
    
    """
    def getUrl(self, query_str):
        qry = self.url + "?"+self.address+"="+query_str
        for key in self.params:
            value = self.params[key]
            param_str="&"+key+"="+value
            qry += param_str
        return qry
    """
    
    def get_url(self):
        return self.url
                
    def get_q(self):
        return self.address

def read_services():
    # TODO: save Objects parameters and schema in database
    services = {}
    services["geonames"] = URL_object("geonames","https://geogratis.gc.ca/services/geoname/_PARAM1_/geonames.json","q")
    services["nominatim"] = URL_object("nominatim","https://nominatim.openstreetmap.org/search", "q",{"format":"jsonv2"})
    #services["google"] = URL_object("google","https://maps.googleapis.com/maps/api/geocode/json", "address", {"key":"AIzaSyASQcYTDCw4fRr_GY5WHxIAqeTsDmvAh_8"})
    return services


def catch_unknown_param(entered_params, valid_params):
    unknown_params = ','.join(list(set(entered_params) - set(valid_params)))
    if unknown_params:
        error_message = "paramaters not required: " + unknown_params
        raise Exception(error_message)

def validate_query_string(queryString):
    params_list = {}
    # List of valids must be placed and retrieved from elsewhere
    valid_parms = ['q','keys','lang']
    valid_langs = ['en','fr']
    valid_services = ['geonames','nominatim']

    # Error where there are other keys parameters not required
    parms_keys = queryString.keys()
    catch_unknown_param(parms_keys, valid_parms)

    # Validate 'query'
    if "q" not in parms_keys:
        raise Exception("inexistent parameter 'q'")
    params_list['q'] = queryString["q"]

        
    # Validate parameter for language
    if "lang" not in parms_keys:
        langs = valid_langs
    else:
        langs = queryString.get("lang").split(',')
        catch_unknown_param(langs, valid_langs)
    params_list['langs'] = langs

    # Validate parameter for service
    if "keys" not in parms_keys:
        keys = valid_services
    else:
        keys = queryString.get("keys").split(',')
        catch_unknown_param(keys, valid_services)
    params_list['keys'] = keys
    
    # TODO: Additionally there must be a regex validation for values
    return params_list
    
def lambda_handler(event, context):
    print(event)
    queryString = event.get("params").get("querystring")
    print(queryString)
    params_full_list = validate_query_string(queryString)
    print(params_full_list)

    # TODO: loop for each service / each language
    query = params_full_list["q"]
    keys = params_full_list["keys"]
    langs = params_full_list["langs"]
    print(query)
    print(keys)
    print(langs)
    for service_key in keys:
        print("++++++")
        for lang in langs:
            print("--calling the api for:---")
            print(service_key)
            print(query)
            print(lang)
            # Hardcoding the build of the query for each service
            # TODO: dynamically retrieve the logic for each service
            if service_key == "geonames":
                geonames_api_url = "https://8md538tqs2.execute-api.ca-central-1.amazonaws.com/dev?q=hola&lang=en"
                query_response =urllib.request.urlopen(urllib.request.Request(
                    url=geonames_api_url,
                    method='GET'),
                    timeout=5)
                loads = json.loads(query_response.read())
                print(loads)
    
    return {
        'statusCode': 200,
        'loads ': loads
    }
