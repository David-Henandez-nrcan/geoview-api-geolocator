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
from params_manager import *
from s3_manager import *
import re

def lambda_handler(event, context):
    # Initilize variables and S3 Service
    items = []
    loads = []
    bucket = get_S3bucket()
    services = get_S3Services(bucket)

    # Read and Validate the parameters
    queryString = event.get("params").get("querystring")
    params_full_list = validate_query_string(queryString, services)
    keys = params_full_list.pop("keys")

    #Initialize the load with the list of services
    loads.append(keys)
    for service in keys:
        # Get the model 
        body = get_s3Model(bucket, service)
        model = json.loads(body)
        # Extract url and parameters from json
        url = model.get("url")
        url_params = model.get("urlParams")
        #Copy the parameters list 
        params_service_list = params_full_list.copy()
        # Paramters to modify the url
        if url_params:
            for url_param in url_params:
                param_match = "_"+url_param.upper()+"_"
                replace_with = params_service_list.pop(url_params.get(url_param))
                url = url.replace(param_match, replace_with)
        lookup_in = model.get("lookup").get("in")

        # The posicion of the '?' affects the logic of this step
        if url[-1] != "?":
            url += "&"
        url += lookup_in.get("q") +"=" + params_service_list.pop("q")
        if len(params_service_list)>0:
            print(params_service_list)
        else:
            print("url is complete")
        # At this point the query must be complete
        query_response =urllib.request.urlopen(urllib.request.Request(
            url=url,
            method='GET'),
            timeout=5)
        response = query_response.read()
        service_load = json.loads(response)
        loads.append(service_load)
        
        ### After this point is where the 'out' part of the model applies
        ###
        ###
        ###
        
    return {
        "services": loads
    }
    