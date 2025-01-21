import boto3
import concurrent.futures
from typing import Dict, List, Tuple

def get_aws_regions() -> List[str]:
    """Get list of all AWS regions."""
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    return regions

def get_clusters_in_region(region: str) -> List[Tuple[str, List[str]]]:
    """
    Get all EKS clusters and their nodegroups in a specific region.
    Returns a list of tuples containing (cluster_name, [nodegroup_names]).
    """
    try:
        eks_client = boto3.client('eks', region_name=region)
        
        # Get all cluster names in the region
        clusters = eks_client.list_clusters()['clusters']
        
        cluster_info = []
        for cluster_name in clusters:
            try:
                # Get nodegroups for each cluster
                nodegroups = eks_client.list_nodegroups(clusterName=cluster_name)['nodegroups']
                cluster_info.append((cluster_name, nodegroups))
            except eks_client.exceptions.ResourceNotFoundException:
                print(f"Cluster {cluster_name} not found in {region}")
            except Exception as e:
                print(f"Error getting nodegroups for cluster {cluster_name} in {region}: {str(e)}")
                
        return cluster_info
    
    except Exception as e:
        print(f"Error scanning region {region}: {str(e)}")
        return []

def scan_all_regions() -> Dict[str, List[Tuple[str, List[str]]]]:
    """
    Scan all AWS regions for EKS clusters and their nodegroups.
    Returns a dictionary with regions as keys and list of (cluster_name, [nodegroup_names]) as values.
    """
    regions = get_aws_regions()
    results = {}
    
    # Use ThreadPoolExecutor for parallel scanning of regions
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_region = {executor.submit(get_clusters_in_region, region): region 
                          for region in regions}
        
        for future in concurrent.futures.as_completed(future_to_region):
            region = future_to_region[future]
            try:
                clusters_info = future.result()
                if clusters_info:  # Only add regions that have clusters
                    results[region] = clusters_info
            except Exception as e:
                print(f"Error processing results for region {region}: {str(e)}")
    
    return results

def main():
    # Configure AWS credentials (make sure these are set up in your environment)
    # boto3.setup_default_session(profile_name='your-profile-name')  # Uncomment if using a specific profile
    
    print("Scanning AWS regions for EKS clusters...")
    results = scan_all_regions()
    
    # Print results in a formatted way
    if not results:
        print("No EKS clusters found in any region.")
        return
    
    print("\nFound EKS clusters in the following regions:")
    for region, clusters in results.items():
        print(f"\nRegion: {region}")
        for cluster_name, nodegroups in clusters:
            print(f"  Cluster: {cluster_name}")
            if nodegroups:
                print("    Nodegroups:")
                for nodegroup in nodegroups:
                    print(f"      - {nodegroup}")
            else:
                print("    No nodegroups found")

if __name__ == "__main__":
    main()
