import json
import urllib.request
import urllib.parse
from params_manager import *
from s3_manager import *
from model_manager import *


IN_API = 'in-api'
OUT_API = 'out-api'

def get_schema_from_bucket(bucket, file_path):
    """
    Get the schema specified by the path from the AWS s3 bucket

    Params:
      bucket: The Id of the bucket
      file_path: Full path of the object inside the bucket
    Returns:
      The schema on json format
    """
    body = read_file(bucket, file_path)
    return json.loads(body)

def get_from_field(field, item):
    """
    Get the data value asociated with an specific field from a data item

    Params:
      field: The field name
      item: the data record
    Returns:
        The field value from the record if the field exists in the data item.
    """
    if field is None or field not in item:
        return None
    return item.get(field)

def get_url_from_field(schema, data):
    """
    Get the url asociated with an specific field based on the schema provided

    Params:
      schema: The schema with the path to get access to the url
      data: the data structure where the url can be found
    Returns: the field value asociated with
    """
    field = schema.get("field")
    url = schema.get("lookup").get("url")
    # Modify the url with the href at the bottom of the fields
    fields_list = field.split(".")
    href = data.get(fields_list[0]). \
                get(fields_list[1]). \
                get(fields_list[2]). \
                get(fields_list[3])
    return url.replace("_URL_", href)

def get_from_url(schema, data):
    """
    Get the data value asociated with an specific field from a REST response

    Params:
      schema: The schema defintion to access to the url
      data: the data structure where the url can be found
    Returns: from a valid REST response, extracts the value from the asociated
             attribute.
    """
    field = schema.get("lookup").get("field")
    url = get_url_from_field(schema, data)
    #return url
    query_response =urllib.request.urlopen(urllib.request.Request(
        url=url,
        method='GET'),
        timeout=5)
    response = query_response.read()
    load = json.loads(response)
    return get_from_field(field, load)

def replace_url_with_params(url, params, params_list):
    """
    Replace and returns the parameters embedded in the url with a valid set
    of values

    Params:
      url: The url to be affected
      params: The list of parameters to be replace in the url
      params_list: The list of query parameters where to search for the
                   replacent to params
    Returns: The url whit the original parameters are replaced with the
             asociated values.
    """
    for param in params:
        param_match = "_"+param.upper()+"_"
        replace_with = params_list.pop(params.get(param))
        url = url.replace(param_match, replace_with)
    return url

def lambda_handler(event, context):
    """
    Task: Main function. When called, performs specific actions in order to
          extract, adapt, and return REST data from several specific services.
    Those actions are:
    - Initialize. Defines variables and services, reads schemas and validates
                  parameters
    - Query assembling. Based on the schema for each required service, a valid
                        url is assembled before calling the REST service
    - Service output. the response is adapted to the expected structure
    - Validation. The resulting data is validated against an output schema to
                  be 'metadata' conformed before be handed to the front-end
    Params:
      event: Contiens the query parameters
      context: Not required for this function

    Returns: Standarized, validated data from REST services related to
             geolocation to be handed to the front-end
    """
    # Initilize variables and S3 service
    loads = []
    bucket = get_s3_bucket()

    # Schemas
    schema_paths = get_schemas_paths(bucket)
    apis_dict = schema_paths['apis']
    services_dict = schema_paths['services']
    # Metadata extracted from api-input-schema
    in_api_schema = get_schema_from_bucket(bucket, apis_dict[IN_API])
    # Metadata extracted from api-output-schema
    out_api_schema = get_schema_from_bucket(bucket, apis_dict[OUT_API])
    output_schema = out_api_schema.get("definitions").get("output")
    # 0. Read and Validate the parameters
    params_full_list = validate_querystring_against_schema(event,in_api_schema)

    keys = params_full_list.pop("keys")
    #Initialize the load with the list of services
    for service in keys:
        # Get the model
        filename = services_dict.get(service)
        body = read_file(bucket, filename)
        model = json.loads(body)

        # 1. Extract url and parameters from json
        url = model.get("url")
        url_params = model.get("urlParams")
        #1.1. Copy the parameters list
        params_service_list = params_full_list.copy()
        # 2. Parameters to modify the url
        if url_params:
            url = replace_url_with_params(url, url_params, params_service_list)

        # 3. lookup in parameters to replace with
        lookup_in = model.get("lookup").get("in")
        qry_params_list = []
        if lookup_in:
            for in_param in lookup_in:
                qry_params_list.append(lookup_in.get(in_param) \
                                       + "=" + \
                                       params_service_list.pop(in_param))

        # 4. static parameters
        static_params = model.get("staticParams")
        if static_params:
            for param in static_params:
                qry_params_list.append(param)

        # 5. Add qry parameters (steps 3, 4) to url
        if qry_params_list:
            url += "&".join(qry_params_list)
        # At this point the query must be complete
        query_response =urllib.request.urlopen(urllib.request.Request(
            url=url,
            method='GET'),
            timeout=5)
        response = query_response.read()
        service_load = json.loads(response)

        # At this point is where the 'out' part of each model applies
        output = []
        outer_field_layer = ""
        lookup_out = model.get("lookup").get("out")
        field_name_pattern = lookup_out.get("name").get("field")
        if "[]." in field_name_pattern:
            outer_field_layer = field_name_pattern.split("[].")[0]
            inner_field_layer = service_load.get(outer_field_layer)
            str_to_remove = outer_field_layer + "[]."
            lookup_out_str = str(lookup_out)
            clean_lookup_out_str = lookup_out_str.replace(str_to_remove, ""). \
                                                  replace("'", '"')
            lookup_out = json.loads(clean_lookup_out_str)
        else:
            inner_field_layer = service_load
        for data_item in inner_field_layer:
            # Start each record with 'key:service' to match the out-api-schema
            output_item = {"key": service}
            for key in lookup_out:
                val = lookup_out.get(key)
                if isinstance(val,dict):
                    field = val.get("field")
                    lookup = val.get("lookup")
                    if not lookup:
                        output_item.update(
                            {key: get_from_field(field, data_item)}
                        )
                    else:
                        if lookup.get("type") == "url":
                            output_item.update(
                                {key: get_from_url(val, data_item)}
                            )
                elif isinstance(val,list):
                    list_for_field = []
                    for item_schema in val:
                        field = item_schema.get("field")
                        lookup = item_schema.get("lookup")
                        if not lookup:
                            list_for_field.append(
                                get_from_field(field, data_item)
                            )
                        else:
                            if lookup.get("type") == "url":
                                field_url = get_from_url(item_schema, data_item)
                                list_for_field.append(field_url)
                    output_item.update({key : list_for_field})
                else:
                    print("Dont know!")
            output.append(output_item)

        # From this point is where the generic 'out-api-schema applies
        schema_items = output_schema.get("items").get("properties")
        schema_required = output_schema.get("items").get("required")
        for output_item in output:
            for key in schema_items:
                value = output_item.get(key)
                # Validate required parameters
                if (key in schema_required) and (value is None):
                    value = "Attribute required not found in item"
                    output_item[key] = value
                else:
                    # Validate value against schema
                    key_definition = schema_items.get(key)
                    val, schema_error = validate_against_schema(value, \
                                                                key_definition)
                    if schema_error:
                        output_item[key] = f"{value} - {schema_error}"
                    else:
                        output_item[key] = val
            # The item is added to the loads
            loads.append(output_item)

    return loads
