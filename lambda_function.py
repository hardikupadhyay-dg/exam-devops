# lambda_function.py
import json
import boto3
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("AWS_REGION", "ap-south-1"))
TABLE_NAME = os.environ.get("DDB_TABLE", "AuditEvents")
table = dynamodb.Table(TABLE_NAME)

def extract_username(event):
    detail = event.get("detail", {})
    user_identity = detail.get("userIdentity") or {}
    username = user_identity.get("userName") or user_identity.get("arn") or user_identity.get("principalId") or "Unknown"
    return username

def extract_resource_name(event):
    detail = event.get("detail", {})
    rp = detail.get("requestParameters", {})
    if rp and rp.get("bucketName"):
        return rp.get("bucketName")
    if detail.get("instance-id"):
        return detail.get("instance-id")
    resources = event.get("resources", [])
    if resources:
        arn = resources[0]
        return arn.split("/")[-1] if "/" in arn else arn.split(":")[-1]
    return "Unknown"

def lambda_handler(event, context):
    try:
        event_time = event.get("time") or datetime.utcnow().isoformat()
        source = event.get("source", "Unknown")
        detail = event.get("detail", {})
        event_name = detail.get("eventName") or event.get("detail-type") or "Unknown"
        resource_name = extract_resource_name(event)
        region = event.get("region") or os.environ.get("AWS_REGION", "ap-south-1")
        username = extract_username(event)

        item = {
            "id": str(uuid.uuid4()),
            "event_time": event_time,
            "event_source": source,
            "event_name": event_name,
            "resource_name": resource_name,
            "aws_region": region,
            "username": username
        }

        table.put_item(Item=item)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Stored", "item": item})
        }
    except Exception as e:
        print("Error:", str(e))
        raise
