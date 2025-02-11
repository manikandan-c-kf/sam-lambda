import json
import boto3
import os
from botocore.exceptions import ClientError

session = boto3.session.Session()
secretsmanager = session.client(
    service_name='secretsmanager',
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

def lambda_handler(event, context):
    try:
        print(event)
        valid_environments = ["development", "staging", "production", "dev", "stage", "prod"]
        if 'environment' not in event:
            raise Exception('Required parameter is not available.')
        
        if event['environment'] not in valid_environments:
            raise Exception('Not a valid environment.')
        secrets = {}
        finalEnv = ''
        projectName = event['project']
        
        secretName = f"{event['environment']}/{projectName}/env"
        response = secretsmanager.get_secret_value(
            SecretId=secretName,
        )
        
        print("response --- ", response)

        if 'SecretString' in response:
            secretsData = json.loads(response['SecretString'])
            secrets.update(secretsData)
        
        if len(secrets) > 0:
            buildEnv = []
            for key,value in secrets.items():
                env = key + "=" + str(value)
                buildEnv.append(env)
            finalEnv = "\n".join(buildEnv)
        
        return {
            "status": "success",
            "body": finalEnv
        }
    except Exception as e:
        print(str(e))
        return {
            "status": "failed",
            "body": str(e)
        }