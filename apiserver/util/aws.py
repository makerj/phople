from boto.s3.connection import S3Connection
from boto.s3.key import Key
from django.conf import settings

BUCKET = None


def init():
    global BUCKET
    bucketname = getattr(settings, 'S3_FILE_BUCKET_NAME', 'file.phople.us')
    BUCKET = S3Connection().get_bucket(bucketname)


def s3_set_bucket(name):
    global BUCKET
    BUCKET = S3Connection().get_bucket(name)


def s3_put(key_name, stream, size=None):
    k = Key(BUCKET)
    k.key = key_name
    k.set_contents_from_file(stream, size=size)


def s3_delete(key):
    key.delete()


def s3_get(key_name, expire_sec=300):
    k = Key(BUCKET, key_name)
    return k.generate_url(expires_in=expire_sec)
