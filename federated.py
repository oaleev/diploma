import boto3
from botocore.exceptions import ClientError
import os

def get_current_identity():
    """Get current caller identity to verify credentials"""
    # Create STS client with a default region
    sts = boto3.client('sts', region_name='us-east-1')  # Added default region
    try:
        identity = sts.get_caller_identity()
        print(f"Currently executing as: {identity['Arn']}")
        return identity
    except Exception as e:
        print(f"Error getting identity: {e}")
        raise

def get_all_regions():
    """Get list of all AWS regions"""
    try:
        # Create EC2 client with a default region
        ec2_client = boto3.client('ec2', region_name='us-east-1')  # Added default region
        regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
        return regions
    except ClientError as e:
        print(f"Error getting regions: {e}")
        raise

def get_eks_clusters_and_nodegroups(region):
    """Get EKS clusters and their nodegroups for a specific region"""
    try:
        # Create EKS client for the specified region using the federated credentials
        session = boto3.Session(region_name=region)  # Specify region in session
        eks_client = session.client('eks', region_name=region)
        
        # Get list of cluster names in the region
        clusters = eks_client.list_clusters()['clusters']
        
        if not clusters:
            return None
            
        clusters_info = {}
        for cluster_name in clusters:
            try:
                # Get nodegroups for each cluster
                nodegroups = eks_client.list_nodegroups(clusterName=cluster_name)['nodegroups']
                clusters_info[cluster_name] = nodegroups
            except ClientError as e:
                print(f"Error getting nodegroups for cluster {cluster_name} in region {region}: {e}")
                continue
                
        return clusters_info
        
    except ClientError as e:
        print(f"Error accessing region {region}: {e}")
        return None

def main():
    try:
        # Set default region for the session
        boto3.setup_default_session(region_name='us-east-1')  # Added default region setup
        
        # Verify current identity
        identity = get_current_identity()
        
        # Get all regions
        regions = get_all_regions()
        
        # Dictionary to store results
        all_clusters = {}
        
        # Iterate through each region
        for region in regions:
            print(f"\nSearching region: {region}")
            clusters_info = get_eks_clusters_and_nodegroups(region)
            
            if clusters_info:
                all_clusters[region] = clusters_info
                # Print findings for this region
                for cluster_name, nodegroups in clusters_info.items():
                    print(f"\nCluster: {cluster_name}")
                    print("Nodegroups:")
                    for nodegroup in nodegroups:
                        print(f"  - {nodegroup}")
            else:
                print(f"No EKS clusters found in {region}")
                
    except Exception as e:
        print(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()
