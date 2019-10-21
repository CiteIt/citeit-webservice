import settings
import boto

print("Starting ..")

s3_resource = boto3.resource('s3', endpoint_url=settings.AMAZON_S3_ENDPOINT,
	config=boto3.session.Config(signature_version='s3v4'),
	aws_access_key_id=settings.AMAZON_ACCESS_KEY,
	aws_secret_access_key=settings.AMAZON_SECRET_KEY,
	region_name=settings.AMAZON_REGION_NAME
)
print("Resource")

file_key = 'test.json'
s3_resource.Bucket(settings.AMAZON_S3_BUCKET).put_object(
	Key=file_key,
	Body=open(json_full_filepath,  'rb'),
	ContentType="application/json"
)

print("Saved: json")
