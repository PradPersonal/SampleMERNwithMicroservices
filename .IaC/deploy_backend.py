# deploy_backend.py
import boto3
import time

ec2 = boto3.client('ec2', region_name='ca-central-1')
as_client = boto3.client('autoscaling', region_name='ca-central-1')
elb_client = boto3.client('elbv2', region_name='ca-central-1')
route53 = boto3.client('route53', region_name='ca-central-1')

# --- Configuration Placeholders (Update these values) ---
AMI_ID = 'ami-0abcdef1234567890' # Replace with valid AMI ID (e.g., Amazon Linux 2)
INSTANCE_TYPE = 't2.micro'
KEY_NAME = 'your-key-pair-name' # Replace with your EC2 key pair name
DOMAIN_NAME = 'example.com.' # Replace with your domain name (trailing dot is important)
# User data script for EC2 instances (installs docker and runs container)
USER_DATA_SCRIPT_BACKEND = """#!/bin/bash
yum update -y
amazon-linux-extras install docker -y
service docker start
usermod -a -G docker ec2-user
docker run -d -p 80:80 your-dockerhub-user/backend-image:latest
"""
# --------------------------------------------------------

def create_backend_asg(backend_sg_id, pvt_subnet_ids, ec2_instance_profile_arn):
    print("Creating Backend Launch Template and ASG...")

    launch_template = ec2.create_launch_template(
        LaunchTemplateName='BackendLaunchTemplate',
        LaunchTemplateData={
            'ImageId': AMI_ID,
            'InstanceType': INSTANCE_TYPE,
            'KeyName': KEY_NAME,
            'SecurityGroupIds': [backend_sg_id],
            'UserData': USER_DATA_SCRIPT_BACKEND, 
            'IamInstanceProfile': {'Arn': ec2_instance_profile_arn}, 
        }
    )
    lt_id = launch_template['LaunchTemplate']['LaunchTemplateId']

    as_client.create_auto_scaling_group(
        AutoScalingGroupName='BackendASG',
        LaunchTemplate={'LaunchTemplateId': lt_id, 'Version': '$Latest'},
        MinSize=1, MaxSize=3, DesiredCapacity=1,
        VPCZoneIdentifier=','.join(pvt_subnet_ids), # Use private subnets
        Tags=[{'Key': 'Name', 'Value': 'BackendInstance', 'PropagateAtLaunch': True}]
    )
    print("Backend ASG created.")
    return 'BackendASG'

def setup_load_balancer_and_dns(vpc_id, pub_subnet_ids, alb_sg_id, asg_name):
    print("Setting up ALB and DNS...")

    target_group = elb_client.create_target_group(
        Name='BackendTG', Protocol='HTTP', Port=80, VpcId=vpc_id, HealthCheckPath='/health'
    )
    tg_arn = target_group['TargetGroups'][0]['TargetGroupArn']

    as_client.attach_load_balancer_target_groups(AutoScalingGroupName=asg_name, TargetGroupARNs=[tg_arn])

    alb = elb_client.create_load_balancer(
        Name='BackendALB', Subnets=pub_subnet_ids, SecurityGroups=[alb_sg_id], Scheme='internet-facing'
    )
    alb_arn = alb['LoadBalancers'][0]['LoadBalancerArn']
    alb_dns_name = alb['LoadBalancers'][0]['DNSName']
    alb_zone_id = alb['LoadBalancers'][0]['CanonicalHostedZoneId']

    # Wait for ALB to be active (use a proper waiter in prod)
    print("Waiting for ALB to become active...")
    time.sleep(60) 

    elb_client.create_listener(
        LoadBalancerArn=alb_arn, Protocol='HTTP', Port=80,
        DefaultActions=[{'TargetGroupArn': tg_arn, 'Type': 'forward'}]
    )
    print("ALB Listener created.")

    # Configure Route 53 (Requires a pre-existing Hosted Zone)
    try:
        zones = route53.list_hosted_zones_by_name(DNSName=DOMAIN_NAME)
        hosted_zone_id = next(zone['Id'] for zone in zones['HostedZones'] if zone['Name'] == DOMAIN_NAME)
        
        route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={'Changes': [{'Action': 'UPSERT', 'ResourceRecordSet': {
                'Name': f'api.{DOMAIN_NAME}',
                'Type': 'A',
                'AliasTarget': {'HostedZoneId': alb_zone_id, 'DNSName': alb_dns_name, 'EvaluateTargetHealth': True}
            }}]}
        )
        print(f"DNS record api.{DOMAIN_NAME} created/upserted.")
    except StopIteration:
        print(f"Hosted zone {DOMAIN_NAME} not found. Manual DNS setup required.")
    except Exception as e:
        print(f"Could not configure Route 53: {e}")
    
    return alb_dns_name

if __name__ == "__main__":
    # This script typically runs after infra_setup, so variables would be passed in the main orchestrator
    print("Run this script via the main orchestrator script.")
