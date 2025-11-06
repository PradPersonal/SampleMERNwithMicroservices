import boto3

autoscaling = boto3.client('autoscaling', region_name='ca-central-1')
ec2_client = boto3.client('ec2', region_name='ca-central-1')

def create_launch_template(sg_id):
    # User data script to install a web server and start it (placeholder for your microservice)
    user_data = """#!/bin/bash
    sudo yum update -y
    sudo yum install -y httpd
    sudo systemctl enable httpd
    sudo systemctl start httpd
    echo "<h1>Hello from ASG Instance</h1>" > /var/www/html/index.html
    """
    
    # Use a common AMI, e.g., Amazon Linux 2 AMI ID (check latest for your region)
    ami_id = 'ami-0abac8735a38475db' 
    
    response = ec2_client.create_launch_template(
        LaunchTemplateName='BackendLaunchTemplate',
        LaunchTemplateData={
            'ImageId': ami_id,
            'InstanceType': 't2.micro',
            'SecurityGroupIds': [sg_id],
            'UserData': user_data # This needs to be base64 encoded for actual use in API, but for script demonstration, this is often a simple string.
        }
    )
    print(f"Launch Template created: {response['LaunchTemplate']['LaunchTemplateName']}")
    return response['LaunchTemplate']['LaunchTemplateId']


def create_auto_scaling_group(launch_template_id, public_subnet_ids):
    autoscaling.create_auto_scaling_group(
        AutoScalingGroupName='BackendASG',
        LaunchTemplate={
            'LaunchTemplateId': launch_template_id,
            'Version': '$Latest'
        },
        MinSize=1,
        MaxSize=3,
        DesiredCapacity=1,
        VPCZoneIdentifier=','.join(public_subnet_ids), # ASG needs a comma-separated list of subnet IDs
        Tags=[
            {'Key': 'Name', 'Value': 'BackendASGInstance', 'PropagateAtLaunch': True}
        ]
    )
    print("Auto Scaling Group created: BackendASG")

# Example usage (requires the IDs from the previous script)
# lt_id = create_launch_template(sg.id) # Assuming 'sg' object from previous script
# create_auto_scaling_group(lt_id, [public_subnet.id]) # Assuming 'public_subnet' object from previous script
