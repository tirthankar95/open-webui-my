from minio import Minio
from datetime import timedelta

if __name__ == '__main__':
    src_file, dst_file = 'data/dummy.dat', 'dummy.dat'
    bucket_name = 'dummy-bucket'
    client = Minio(
        "172.31.23.155:9000",
        access_key="abot",
        secret_key="hacker1995",
        secure=False
    )
    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)
        print('Bucket created.')
    else:
        print(f'Bucket: {bucket_name} already exists')
    # Upload the file in bucket.
    client.fput_object(bucket_name, dst_file, src_file)
    url = client.presigned_get_object(bucket_name, dst_file, expires=timedelta(hours=1))
    print(f'Artifact url: {url}')
