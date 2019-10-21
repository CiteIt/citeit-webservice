import settings
import boto3

print("Starting ..")
file_key = 'test.json'
remote_path = 'quote/test.json'


s3 = boto3.resource('s3')
s3.meta.client.upload_file(
	file_key, 
	settings.AMAZON_S3_BUCKET, 
	remote_path, 
	ExtraArgs={'ContentType':"application/json", 'ACL': "public-read"}
)


"""
s3_resource = boto3.resource('s3', endpoint_url=settings.AMAZON_S3_ENDPOINT,
	config=boto3.session.Config(signature_version='s3v4'),
	aws_access_key_id=settings.AMAZON_ACCESS_KEY,
	aws_secret_access_key=settings.AMAZON_SECRET_KEY,
	region_name=settings.AMAZON_REGION_NAME
)
print("Resource")

s3_resource.Bucket(settings.AMAZON_S3_BUCKET).put_object(
	Key=file_key,
	Body=open(json_full_filepath,  'rb'),
	ContentType="application/json"
)
"""

print("Saved: json")
