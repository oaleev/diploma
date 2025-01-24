# List all PVCs and their status
kubectl get pvc -A -o custom-columns=NAMESPACE:.metadata.namespace,NAME:.metadata.name,STATUS:.status.phase,VOLUME:.spec.volumeName

# Then check corresponding EBS volumes
for pv in $(kubectl get pv -o jsonpath='{.items[?(@.spec.awsElasticBlockStore)].metadata.name}'); do
    echo "=== Checking PV: $pv ==="
    volume_id=$(kubectl get pv $pv -o jsonpath='{.spec.awsElasticBlockStore.volumeID}' | cut -d '/' -f4)
    aws ec2 describe-volumes --volume-ids $volume_id
done