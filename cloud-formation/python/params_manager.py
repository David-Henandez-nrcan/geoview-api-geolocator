def catch_too_many_values(param_value):
    print(param_value)
    if len(param_value.split(',')) > 1:
        error_message = "Too many values for the parameter: " + param_value
        raise Exception(error_message)

def catch_unknown_value(entered_value, valid_values):
    if entered_value not in valid_values:
        error_message = "paramater invalid: " + entered_value
        raise Exception(error_message)

def catch_unknown_param(entered_params, valid_params):
    unknown_params = ','.join(list(set(entered_params) - set(valid_params)))
    if unknown_params:
        error_message = "paramaters not required: " + unknown_params
        raise Exception(error_message)

def validate_query_string(queryString, valid_services):
    params_list = {}
    # List of valids must be placed and retrieved from elsewhere
    valid_parms = ['q','keys','lang']
    valid_langs = ['en','fr']

    # Error where there are other keys parameters not required
    parms_keys = queryString.keys()
    catch_unknown_param(parms_keys, valid_parms)

    # Validate 'query'
    if "q" not in parms_keys:
        raise Exception("inexistent parameter 'q'")
    params_list['q'] = queryString.get("q")

    # Validate parameter for language
    if "lang" not in parms_keys:
        lang = valid_langs[0]
    else:
        lang = queryString.get("lang")
        catch_too_many_values(lang)
        catch_unknown_value(lang, valid_langs)
    params_list['lang'] = lang
    
    """
    # Original validation accepting both official languages
    # in the same query
    
    # Validate parameter for language
    if "lang" not in parms_keys:
        langs = valid_langs[0]
    else:
        langs = queryString.get("lang").split(',')
        catch_unknown_param(langs, valid_langs)
    params_list['langs'] = langs
    """
    # Validate parameter for service
    if "keys" not in parms_keys:
        keys = valid_services
    else:
        keys = queryString.get("keys").split(',')
        catch_unknown_param(keys, valid_services)
    params_list['keys'] = keys
    
    # TODO: Additionally there must be a regex validation for values
    return params_list
