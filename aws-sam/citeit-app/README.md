## CiteIt on AWS Lambda with AWS SAM
Goals:
  - be able to test and deploy CiteIt on AWS Lambda with Gateway API
  - setup a local development environment using AWS SAM that can run a local version of Lambda and uses Minio as an endpoint / S3 compatable object store.

###Requires

1. Docker
2. AWS CLI
3. AWS SAM CLI 


### Simulating S3 for Local Development
Minio is an open source object storage server that is compatabile with S3 APIs. (Apache2 license) and can be used to simulate S3 for testing purposes.

The commands below are based on the [Minio Docker Quick Start Guide](https://docs.minio.io/docs/minio-docker-quickstart-guide.html)

```
docker pull minio/minio
```

The command below starts the Minio server and creates a */data* directory when the container starts. **All of the data will be lost when the container exits.** This is generally fine for testing purposes.

```
docker run -p 9000:9000 --name minio1 \
  -e "MINIO_ACCESS_KEY=ABCDEFGH123456789" \
  -e "MINIO_SECRET_KEY=alksdfj;2452lkjr;ajtsaljgfslakjfgassgf" \
  minio/minio server /data
```

**In order to have persistent storage**, you need to map a local directory from the host OS and the Minio configuration


```
docker run -p 9000:9000 --name minio1 \
  -e "MINIO_ACCESS_KEY=ABCDEFGH123456789" \
  -e "MINIO_SECRET_KEY=alksdfj;2452lkjr;ajtsaljgfslakjfgassgf" \
  -v /mnt/data:/data \
  -v /mnt/config:/root/.minio \
  minio/minio server /data
```

### Writing Python code that can use either S3 or Minio

The following uses the boto3 library (AWS Python SDK) in order to create a bucket and upload a existing files to the Minio server.

```
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

file_key = 'location/for_file/inS3/some_file.txt'
file_name = 'some_file.txt
s3_resource.Bucket(bucket_name).put_object(Key=file_key, Body=open(file_name, 'rb'))


```


### Simulating CiteIt in Lambda for Local Development
AWS Serverless Application Model (AWS SAM) can be used to develop, test and deploy serverless applications that use Lambda and a Gateway API

[Installing AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)

```
pip install aws-sam-cli
```

Go to the directory for the cite-it SAM app

```
cd aws-sam/citeit-app
```


#### Setting up your code to run with AWS SAM / Lambda

Based off of the [AWS SAM Quickstart](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-quick-start.html)


Make your build folder. This is the directory that gets packaged and loaded into Lambda for running your function. It must include any dependancies as well as your source code.

```
mkdir build
```

Install the python dependancies into the build directory

```
pip install -r requirements.txt -t build/
```

Copy the cite-it src code into the build directory

```
cp -r src/ build/
```

Create your settings.py file

```
cd build
cp settings-default.py settings.py    # Make appropriate changes

```



The template.yaml file for CiteIt includes:

1. A Lambda Function
2. An API Gateway endpoint URL

**TODO:** *Figure out how to secure the API endpoint*

[Related Stackoverflow Q&A](https://stackoverflow.com/questions/39352648/access-aws-api-gateway-with-iam-roles-from-python)

[Related blog post](https://edtheron.me/projects/store-messages-aws-dynamodb-lambda-api-gateway-cognito)


#### Run CiteIt Lambda Function

```
sam local start-api
```

You can then hit the endpoint and trigger CiteIt using the following url:

```
http://127.0.0.1:3000/citeit?url=https://www.citeit.net/
```


#### Remote debugging

```
sam local start-api -d 5858
```

Setting breakpoints in code. Requires having remote_pdb installed

```
import remote_pdb

# Set a breakpoint
remote_pdb.RemotePdb('0.0.0.0', 5858).set_trace()
```

Connect to remote debugging session

```
telnet 127.0.0.1 5858

# or

nc -C 127.0.0.1 5858    # This worked on Mac OSX

# or

socat socat readline tcp:127.0.0.1:5858
```

Breakout into python shell with current variables

```
!import code; code.interact(local=vars())

```

###Other Docker Commands
```
docker ps -a          (system status: uptime)
docker images -a      (list all images)
docker rmi  [image hash example: 12a86fe64bc8]
docker save -o /path/to/output/file [image: 12a86fe64bc8]

docker tag citeit_minio citeit/citeit_minio
docker push citeit/citeit_minio

docker tag 62cc52d59225 citeit/citeit_webservice
docker push citeit/citeit_webservice

```
https://stackoverflow.com/questions/41984399/denied-requested-access-to-the-resource-is-denied-docker