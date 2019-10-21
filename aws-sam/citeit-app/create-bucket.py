import boto3

ACCESS_KEY='ABCDEFGH123456789'
SECRET_KEY='alksdfj;2452lkjr;ajtsaljgfslakjfgassgf'

bucket_name = 'read.citeit.net'

# Create the bucket


s3_resource = boto3.resource('s3',
  endpoint_url='http://127.0.0.1:9000',
  config=boto3.session.Config(signature_version='s3v4'),
  aws_access_key_id=ACCESS_KEY,
  aws_secret_access_key=SECRET_KEY
)

s3_resource.create_bucket(Bucket=bucket_name)
s3_resource.Bucket(bucket_name).put_object(Key=file_key, Body=open(file_name, 'rb'))

file_key = 'download.citeit.net/lambda/test'
file_name = 'test_file.txt'
s3_resource.Bucket(bucket_name).put_object(Key=file_key, Body=open(file_name, 'rb'))

