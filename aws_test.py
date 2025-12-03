import boto3
from datetime import datetime

#Make sure to change vehicles and the region accordingly
#This is not recommended as it bypasses security, I only made this to ensure that I could actually send data to AWS.

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
table = dynamodb.Table('Vehicles')

response = table.put_item(
    Item={
        "id": "[Camera Name]",
        "type": f"test#{datetime.now().isoformat()}",
        "timestamp": datetime.now().isoformat(),
        "detections": {"sedan": 1, "bus": 0}
    }
)

print("DynamoDB test write response:", response)
