def validate_against_schema(value, definition):
    """
    Task: Validate a piece of data with its asociated section in the schema

    Params:
      value: The data value to be evaluated
      params: The section of the schema with the definition of the field

    Returns: The return value for the piece of data either original or altered
             and an error string where None or empty means no error.
    """
    if value is not None:
        data_type = definition.get("type")
        if data_type == "string":
            if not isinstance(value, str):
                return value, "Invalide string value"
        elif data_type == "number":
            try:
                val = float(value)
            except:
                return value, "Invalide number value"
            minimum = definition.get("minimum")
            maximum = definition.get("maximum")
            if (val < minimum) or (val > maximum):
                return val, "value number out of range"
            return val, ""
        elif data_type == "array":
            if not isinstance(value,list):
                value = value.split(",")
            min_items = definition.get("minItems")
            items = definition.get("items")
            try:
                m_items = int(min_items)
            except:
                m_items = 0
            # Match each item in the data list against the list in schema
            if isinstance(items, list):
                for i in range(m_items):
                    val, error = validate_against_schema(value[i], items[i])
                    if error != "":
                        value[i] = f"{value[i]} - {error}"
                    else:
                        value[i] = val
            else:
                # Match the data list against the type of list in
                for i in range(len(value)):
                    val, error = validate_against_schema(value[i], items)
                    if error != "":
                        value[i] = f"{value[i]} - {error}"
                    else:
                        value[i] = val

        else:
            error = "data-type not recognized"

    return value, ""
