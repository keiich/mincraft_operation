import boto3
import time
import requests

def lambda_handler(event, context):
    path = event.get("rawPath", "")
    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    if method == "HEAD" or path.endswith("favicon.ico"):
        return {
            "statusCode": 204,
            "body": ""  # 何もしない
        }
    # EC2インスタンスID
    instance_id = 'XXXXXXXXXXXXXXXXX'

    # EC2インスタンスを起動するためのパラメータ
    ec2 = boto3.client('ec2')

    # まず現在の状態を確認
    instance = ec2.describe_instances(InstanceIds=[instance_id])
    state = instance['Reservations'][0]['Instances'][0]['State']['Name']
    webhook_url = 'https://discord.com/api/webhooks/XXXXXXXXXXXXXXXXXXXX'

    if state == 'running':
        # すでに起動している場合
        public_ip = instance['Reservations'][0]['Instances'][0].get('PublicIpAddress', '未割り当て')
        data = {
            'content': f'インスタンスはすでに起動中です。\rサーバーアドレス：{public_ip}'
        }
        requests.post(webhook_url, json=data)
        return public_ip

    else:
        response = ec2.start_instances(InstanceIds=[instance_id])

        # EC2インスタンスが起動するのを待つ
        instance_running = False
        while not instance_running:
            instance = ec2.describe_instances(InstanceIds=[instance_id])
            state = instance['Reservations'][0]['Instances'][0]['State']['Name']
            if state == 'running':
                instance_running = True
            else:
                time.sleep(5)

        # EC2インスタンスのパブリックIPアドレスを取得する
        instance = ec2.describe_instances(InstanceIds=[instance_id])
        public_ip = instance['Reservations'][0]['Instances'][0]['PublicIpAddress']
    
        #DiscordにWebhookを送信
        data = {
            'content': f'インスタンスは起動しました\rサーバーアドレス：{public_ip}'
        }
        requests.post(webhook_url, json=data)
    
        return public_ip
