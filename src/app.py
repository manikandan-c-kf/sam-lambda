import json
import boto3
import os

ssm = boto3.client("ssm", region_name=os.getenv("AWS_REGION", "us-east-1"))

def get_parameters_by_path(path, with_decryption=True):
    """Fetches all parameters under a given path from AWS SSM Parameter Store"""
    parameters = {}
    next_token = None

    try:
        while True:
            if next_token:
                response = ssm.get_parameters_by_path(Path=path, WithDecryption=with_decryption, Recursive=True, NextToken=next_token)
            else:
                response = ssm.get_parameters_by_path(Path=path, WithDecryption=with_decryption, Recursive=True)

            for param in response.get("Parameters", []):
                param_name = param["Name"].split("/")[-1]
                parameters[param_name] = param["Value"]

            next_token = response.get("NextToken")
            if not next_token:
                break

    except Exception as e:
        print(f"Error fetching parameters: {e}")

    return parameters

def lambda_handler(event, context):
    environment = event.get("environment", "development")

    # Fetch all parameters under /config/
    env_vars = get_parameters_by_path("/config/")

    # Add ENVIRONMENT variable separately
    env_vars["ENVIRONMENT"] = environment

    return {
        "statusCode": 200,
        "body": json.dumps(env_vars),
    }