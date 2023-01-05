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

    # 0. Read and Validate the parameters
    queryString = event.get("params").get("querystring")
    params_full_list = validate_query_string(queryString, services)
    print("params_full_list: {}".format(params_full_list))
    keys = params_full_list.pop("keys")

    #Initialize the load with the list of services
    #loads.append(keys)
    for service in keys:
        # Get the model
        body = get_s3Model(bucket, service)
        model = json.loads(body)
        # 1. Extract url and parameters from json
        url = model.get("url")
        print("url before: {}".format(url))
        url_params = model.get("urlParams")
        #Copy the parameters list 
        params_service_list = params_full_list.copy()
        # 2. Paramters to modify the url
        if url_params:
            for url_param in url_params:
                print(url_params)
                param_match = "_"+url_param.upper()+"_"
                replace_with = params_service_list.pop(url_params.get(url_param))
                url = url.replace(param_match, replace_with)
        print("url after: {}".format(url))
        
        # replace input-key parameters 
        lookup_in = model.get("lookup").get("in")
        print("lookup in: {}".format(lookup_in))
        qry_params_list = []
        # 3. lookup in parameters
        if lookup_in:
            for in_param in lookup_in:
                qry_params_list.append(lookup_in.get(in_param) +"=" + params_service_list.pop(in_param))
        print("qry_params_list after lookup in: {}".format(qry_params_list))

        # 4. static parameters
        static_params = model.get("staticParams")
        if static_params:
            for param in static_params:
                qry_params_list.append(param)
        print("qry_params_list after static parameters: {}".format(qry_params_list))
        # 3-4 Add qry parameters to url    
        if qry_params_list:
            url += "&".join(qry_params_list)
        print("url after qry parameters: {}".format(url))
            
        # At this point the query must be complete
        query_response =urllib.request.urlopen(urllib.request.Request(
            url=url,
            method='GET'),
            timeout=5)
        response = query_response.read()
        service_load = json.loads(response)

        ### After this point is where the 'out' part of the model applies
        ###
        ###
        ###
        
        loads.append(service_load)

    return {
        "services": loads
    }
    