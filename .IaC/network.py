import boto3
from botocore.exceptions import ClientError

ec2 = boto3.resource('ec2', region_name='ca-central-1')
ec2_client = boto3.client('ec2', region_name='ca-central-1')

# --- VPC Creation ---
def create_vpc():
    vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
    vpc.create_tags(Tags=[{"Key": "Name", "Value": "Microservices_VPC"}])
    vpc.wait_until_available()
    print(f"VPC created: {vpc.id}")
    return vpc

# --- Subnet Creation ---
def create_subnets(vpc):
    # Create public subnet
    public_subnet = vpc.create_subnet(CidrBlock='10.0.1.0/24', AvailabilityZone='us-east-1a')
    public_subnet.create_tags(Tags=[{"Key": "Name", "Value": "Public_Subnet"}])
    # Create private subnet
    private_subnet = vpc.create_subnet(CidrBlock='10.0.2.0/24', AvailabilityZone='us-east-1b')
    private_subnet.create_tags(Tags=[{"Key": "Name", "Value": "Private_Subnet"}])
    print(f"Subnets created: {public_subnet.id}, {private_subnet.id}")
    return public_subnet, private_subnet

# --- Internet Gateway (IGW) and Routing ---
def setup_gateway_routing(vpc, public_subnet):
    igw = ec2.create_internet_gateway()
    vpc.attach_internet_gateway(InternetGatewayId=igw.id)
    igw.create_tags(Tags=[{"Key": "Name", "Value": "Microservices_IGW"}])
    print(f"Internet Gateway created and attached: {igw.id}")

    route_table = vpc.create_route_table()
    route = route_table.create_route(DestinationCidrBlock='0.0.0.0/0', InternetGatewayId=igw.id)
    route_table.associate_with_subnet(SubnetId=public_subnet.id)
    print(f"Route table created and associated with public subnet: {route_table.id}")

# --- Security Group Creation ---
def create_security_group(vpc):
    sg = ec2.create_security_group(
        GroupName='BackendSG',
        Description='Security Group for backend ASG instances',
        VpcId=vpc.id
    )
    sg.create_tags(Tags=[{"Key": "Name", "Value": "BackendSG"}])
    
    # Define ingress rules (e.g., allow HTTP/HTTPS traffic)
    sg.authorize_ingress(
        IpPermissions=[
            {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', 'FromPort': 443, 'ToPort': 443, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ]
    )
    print(f"Security Group created: {sg.id}")
    return sg

# Combine the calls in a main function
if __name__ == "__main__":
    vpc = create_vpc()
    public_subnet, private_subnet = create_subnets(vpc)
    setup_gateway_routing(vpc, public_subnet)
    sg = create_security_group(vpc)