```bash
kubectl describe pod <pod-name> | grep -A10 Events

# List all pods with their namespaces
kubectl get pods -A --no-headers | awk '{print $1, $2}'

# Check events for all pods in all namespaces
for pod in $(kubectl get pods -A --no-headers | awk '{print $1","$2}'); do
    namespace=$(echo $pod | cut -d',' -f1)
    podname=$(echo $pod | cut -d',' -f2)
    echo "=== Events for $namespace/$podname ==="
    kubectl describe pod $podname -n $namespace | grep -A10 Events
    echo ""
done

# Or check only pods in a specific state
for pod in $(kubectl get pods -A --no-headers | grep -i "pending\|error" | awk '{print $1","$2}'); do
    namespace=$(echo $pod | cut -d',' -f1)
    podname=$(echo $pod | cut -d',' -f2)
    echo "=== Events for $namespace/$podname ==="
    kubectl describe pod $podname -n $namespace | grep -A10 Events
    echo ""
done
```


```bash
kubectl get pod <pod-name> -o jsonpath='{.spec.securityContext}'

# Get pod-level security contexts for all pods
kubectl get pods -A -o custom-columns='NAMESPACE:.metadata.namespace,NAME:.metadata.name,SECURITY_CONTEXT:.spec.securityContext'

# Get container-level security contexts
for pod in $(kubectl get pods -A --no-headers | awk '{print $1","$2}'); do
    namespace=$(echo $pod | cut -d',' -f1)
    podname=$(echo $pod | cut -d',' -f2)
    echo "=== Security Context for $namespace/$podname ==="
    echo "Pod Level Security Context:"
    kubectl get pod $podname -n $namespace -o jsonpath='{.spec.securityContext}' | jq '.'
    echo "\nContainer Level Security Contexts:"
    kubectl get pod $podname -n $namespace -o jsonpath='{.spec.containers[*].securityContext}' | jq '.'
    echo "\n"
done

```