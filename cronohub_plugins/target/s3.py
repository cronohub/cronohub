import boto3
import os
from cronohub import target_plugin
from typing import List


class TargetPlugin(target_plugin.CronohubTargetPlugin):
    def __init__(self):
        print('initialising S3 target plugin')

    def validate(self):
        print('validating')
        if "CRONOHUB_S3_BUCKETNAME" not in os.environ:
            print('please provide CRONOHUB_S3_BUCKETNAME environment property for archiving.')
            return False
        return True

    def help(self):
        print('help')

    def archive(self, files):
        bucket = os.environ['CRONOHUB_S3_BUCKETNAME']
        s3 = boto3.client('s3')
        for file in files:
            filename = os.path.basename(file[0])
            print('uploading %s to bucket %s' % (filename, bucket))
            s3.upload_file(file, bucket, filename)
            print('uploading complete')
