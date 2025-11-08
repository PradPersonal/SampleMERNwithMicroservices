# infra_setup.py
import boto3
import time

ec2 = boto3.client('ec2', region_name='ca-central-1')

# --- Configuration Placeholders (Update these values) ---
VPC_CIDR = '10.0.0.0/16'
PUBLIC_SUBNET_CIDR_A = '10.0.1.0/24'
PUBLIC_SUBNET_CIDR_B = '10.0.2.0/24'
PRIVATE_SUBNET_CIDR_A = '10.0.3.0/24'
PRIVATE_SUBNET_CIDR_B = '10.0.4.0/24'
AZ_A = 'ca-central-1a' # Change region if needed
AZ_B = 'ca-central-1b'
# --------------------------------------------------------

def create_vpc_and_subnets():
    vpcs = ec2.describe_vpcs(Filters=[
        {
            'Name': 'Default',
            'Values': [
                'vpc-07b61209a4160893e',
            ]
        },
    ])
    if not vpcs['Vpcs']:
        print("Creating VPC...")
        vpc = ec2.create_vpc(CidrBlock=VPC_CIDR)
        vpc_id = vpc['Vpc']['VpcId']
        ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': True})
        ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})
        print(f"VPC created: {vpc_id}")
    else:
        vpc_id = vpcs['Vpcs'][0]['VpcId']
        print(f"VPC already exists: {vpc_id}")

    # Create Internet Gateway and attach
    # igw = ec2.describe_internet_gateways(
    #         InternetGatewayIds=['igw-0a10ac32fc2d0aae6']
    #     )
    igw = ec2.create_internet_gateway()
    igw_id = igw['InternetGateway']['InternetGatewayId']
    ec2.attach_internet_gateway(VpcId=vpc_id, InternetGatewayId=igw_id)
    print(f"Internet Gateway created: {igw_id}")

    # Create Subnets
    pub_subnet_a = ec2.create_subnet(VpcId=vpc_id, CidrBlock=PUBLIC_SUBNET_CIDR_A, AvailabilityZone=AZ_A)
    pub_subnet_b = ec2.create_subnet(VpcId=vpc_id, CidrBlock=PUBLIC_SUBNET_CIDR_B, AvailabilityZone=AZ_B)
    pvt_subnet_a = ec2.create_subnet(VpcId=vpc_id, CidrBlock=PRIVATE_SUBNET_CIDR_A, AvailabilityZone=AZ_A)
    pvt_subnet_b = ec2.create_subnet(VpcId=vpc_id, CidrBlock=PRIVATE_SUBNET_CIDR_B, AvailabilityZone=AZ_B)
    
    pub_subnet_ids = [pub_subnet_a['Subnet']['SubnetId'], pub_subnet_b['Subnet']['SubnetId']]
    pvt_subnet_ids = [pvt_subnet_a['Subnet']['SubnetId'], pvt_subnet_b['Subnet']['SubnetId']]
    
    # Enable auto-assign public IP on public subnets
    for subnet_id in pub_subnet_ids:
         ec2.modify_subnet_attribute(SubnetId=subnet_id, MapPublicIpOnLaunch={'Value': True})

    # Create Public Route Table and associate
    pub_rtb = ec2.create_route_table(VpcId=vpc_id)
    pub_rtb_id = pub_rtb['RouteTable']['RouteTableId']
    ec2.create_route(RouteTableId=pub_rtb_id, DestinationCidrBlock='0.0.0.0/0', InternetGatewayId=igw_id)
    for subnet_id in pub_subnet_ids:
        ec2.associate_route_table(SubnetId=subnet_id, RouteTableId=pub_rtb_id)
    
    print("Subnets and route tables created.")
    return vpc_id, pub_subnet_ids, pvt_subnet_ids

def create_security_groups(vpc_id):
    print("Creating Security Groups...")
    # Security group for ALB
    alb_sg = ec2.create_security_group(GroupName='ALBSecurityGroup', Description='Allow HTTP traffic to ALB', VpcId=vpc_id)
    alb_sg_id = alb_sg['GroupId']
    ec2.authorize_security_group_ingress(GroupId=alb_sg_id, IpProtocol='tcp', FromPort=80, ToPort=80, CidrIp='0.0.0.0/0')

    # Security group for backend instances (allow traffic from ALB SG and SSH)
    backend_sg = ec2.create_security_group(GroupName='BackendSecurityGroup', Description='Allow traffic from ALB SG and SSH', VpcId=vpc_id)
    backend_sg_id = backend_sg['GroupId']
    ec2.authorize_security_group_ingress(GroupId=backend_sg_id, IpProtocol='tcp', FromPort=80, ToPort=80, SourceSecurityGroupName='ALBSecurityGroup') # Allow from ALB SG
    ec2.authorize_security_group_ingress(GroupId=backend_sg_id, IpProtocol='tcp', FromPort=22, ToPort=22, CidrIp='0.0.0.0/0')

    # Security group for frontend instances
    frontend_sg = ec2.create_security_group(GroupName='FrontendSecurityGroup', Description='Allow HTTP and SSH to Frontend', VpcId=vpc_id)
    frontend_sg_id = frontend_sg['GroupId']
    ec2.authorize_security_group_ingress(GroupId=frontend_sg_id, IpProtocol='tcp', FromPort=80, ToPort=80, CidrIp='0.0.0.0/0')
    ec2.authorize_security_group_ingress(GroupId=frontend_sg_id, IpProtocol='tcp', FromPort=22, ToPort=22, CidrIp='0.0.0.0/0')

    print(f"Security Groups created.")
    return alb_sg_id, backend_sg_id, frontend_sg_id


if __name__ == "__main__":
    print("Running Infrastructure Setup...")
    # This runs the logic when executed via python3 infra_setup.py
    try:
        vpc_id, pub_subnet_ids, pvt_subnet_ids = create_vpc_and_subnets()
        alb_id, back_id, front_id = create_security_groups(vpc_id)
        print("Infrastructure setup complete successfully.")
    except Exception as e:
        print(f"An error occurred during infrastructure setup: {e}")
        sys.exit(1)
