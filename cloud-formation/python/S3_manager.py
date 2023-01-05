import boto3

def get_S3bucket():
    return "tutorial-bucket-test1"

def get_S3Services(bucket_name):
    """
    Read and return the list of files in the Bucket
    :param bucket_name
    :return: List of objects in the bucket
    """
    list_obj = []
    try:
        # find list of files from S3 buckets 
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        for obj in bucket.objects.all():
            list_obj.append(obj.key)

        return list(map(lambda key: key.split("_").pop(0) , list_obj))
        #return list_obj
    
    except ClientError as e:
        logging.error(e)
        return False 

def get_s3Model(bucket, service_name):
    """
    Build then call the specific object name for a given service
    :param bucket
    :param service_name
    :return: content of the specific object in bucket
    """
    filename = service_name + "_schema.json"

    return open_file_s3(bucket, filename)

def open_file_s3(bucket, filename):
    """
    return the content of the object
    :param bucket
    :param filename
    :return: body of the file as a string
    """
    try:
        # Load file from S3 buckets 
        s3 = boto3.resource('s3')
        content_object = s3.Object(bucket, filename)
        file_body= content_object.get()['Body'].read().decode('utf-8')

        return str(file_body)

    except ClientError as e:
        logging.error(e)
        return False 
        
