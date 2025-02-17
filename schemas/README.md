# Schemas and Metadata Structure

### Geolocator API Schemas
The Geolocator API has schemas for [input](./api/in-api-schema,json) and [output](./api-out-schema.json).

The __input__ schema identifies the expected parameters to query the API.
    - "q": The query to parse and send to supported API's.
    - "lang": The language on wich to filter the query (fr or en).
    - "keys": The list of supported API key to query. Optional parameter, if missing, all
supported key will be query.Every time we support a new API or services, a new key will be added to this array of accepted values.

The __output__ schemas identifies the parameters we will look for to parse the result.
    - "name": The main return information.
    - "lat": The latitude value.
    - "lng": The longitude value.
    - "bbox": The bbox [minX, minY, maxX, maxY].
    - "province": The province the item belongs to. Optional return value, may be derived from the name parameter or other lookup info.
    - "tag": The tag value of the item. Optional return value. tags may be different from one API to the other, it is a value to help understand what type of item it is.

### Supported API and services Metadata
Each supported APIs and services may have differents input and output signatures. To help the parsing of these signatures, the Geolocator API will rely on JSON metadata file. This metadata file will also holds connection information like urls. The name of this file is the value of the key item (<key>-metadata.json).

The structure of this file is
```
{
    "url": "https://.../_PARAM1_/...?", //API url with optional parameters
    "urlParams": {
        "param1": "lang" // Optional parameter to substitue in urls
    },
    "lookup": {
        "in": { // Input lookup information
            "q": "the_service_value", // Query parameter value to use to call
            "lang": "en" // Language parameter value
        },
        "out": { // Output lookup information
            "name": {
                "field": "items[].name", // Return JSON item to look for
                "lookup": "" // Lookup to apply if needed
            },
            "lat": {
                "field":"items[].latitude",
                "lookup": ""
            },
            "lng": {
                "field": "items[].longitude",
                "lookup": ""
            },
            "bbox": {
                "field": "items[].bbox",
                "lookup": ""
            },
            "province": {
                "field": "items[].province.code",
                "lookup": ""
            },
            "tag": [ // Can contains many field values separated by ;
                     // For optional parameter like "tag", the field value
                     // can be left empty if no items can be use.
                {
                    "field": "items[].location",
                    "lookup": ""
                },
                {
                    "field": "items[].generic.code",
                    "lookup": ""
                    }
                }
            ]
        }
    }
}
```

### Lookup
Lookup can have 2 signatures. One can use a url to retrieve the value, another can use a table.

__URL__
```
 "field": "items[].province.code",
"lookup": {
    "type": "url",
    "url": "https://.../_PARAM1_/../__items[].province.code__...", // Url to call
    "field": "descriptions" // Field to read to get the value
}
```
__Table__
```
 "field": "items[].province.code",
"lookup": {
    "type": "table",
    "items": [
        "code_value": "parsed_value", // e.i. "24": "Quebec"
        ...
    ]
}
```