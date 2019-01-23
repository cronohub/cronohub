import boto3
import os

def archive(file: str):
    if "CRONOHUB_S3_BUCKETNAME" not in os.environ:
        print('please provide CRONOHUB_S3_BUCKETNAME environment property for archiving.')
        return

    bucket = os.environ['CRONOHUB_S3_BUCKETNAME']
    s3 = boto3.client('s3')
    filename = os.path.basename(file)
    print('uploading %s to bucket %s' % (filename, bucket))
    s3.upload_file(file, bucket, filename)
    print('uploading complete')
