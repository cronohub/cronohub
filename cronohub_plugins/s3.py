import boto3
import os
import time

def archive(file: str):
    if "CRONOHUB_S3_BUCKETNAME" not in os.environ:
        print('please provide CRONOHUB_S3_BUCKETNAME environment property for archiving.')
        return

    timestr = time.strftime("%Y%m%d-%H%M%S")
    bucket = os.environ['CRONOHUB_S3_BUCKETNAME']
    s3 = boto3.client('s3')
    filename = "{}_{}".format(os.path.basename(file), timestr)
    print('uploading %s to bucket %s' % (filename, bucket))
    s3.upload_file(file, bucket, filename)
    print('uploading complete')
