# INFRASTRUCTURE MIGRATION

Infrastructure Documentation and Assessment Phase
First, thoroughly document your existing EKS infrastructure to ensure nothing is missed during migration. Begin by examining and documenting:

Cluster Configuration:
Document your current EKS cluster version, networking configuration (VPC, subnets, security groups), and control plane settings. This includes capturing IAM roles and policies associated with the cluster, authentication mechanisms, and any custom configurations applied through aws-auth ConfigMap.

Node Group Configuration:
Record details about your node groups including instance types, scaling configurations, taints/tolerations, and any custom launch templates or user data scripts. Document node labels and any special node group configurations like GPU instances or ARM-based nodes.

Add-ons and Supporting Services:
Map out all AWS-managed add-ons (like CoreDNS, kube-proxy, VPC CNI) and their versions. Document any self-managed add-ons, including monitoring solutions, logging configurations, and service meshes. Note dependencies between services and their specific configurations.

Storage Configuration:
Document all storage classes, persistent volumes, and any EBS/EFS configurations. Include details about backup solutions, snapshot policies, and any custom storage drivers.

Migration Planning Phase
Now plan your Crossplane and Argo CD implementation:

Crossplane Setup:
Prepare your AWS Provider configuration for Crossplane, ensuring proper IAM permissions. Design your Composite Resource Definitions (XRDs) to match your current infrastructure patterns. Consider breaking down your infrastructure into logical components that can be managed independently.

Argo CD Architecture:
Design your Argo CD project structure and repository organization. Plan your application sets and establish synchronization policies. Define your promotion strategy across environments if applicable.

Migration Execution Phase
Execute the migration in controlled steps:

Initial Setup:
Install and configure Crossplane with AWS Provider in your new environment. Set up Argo CD and configure it to watch your infrastructure repositories. Create initial XRDs and Compositions that match your existing infrastructure.

Parallel Infrastructure:
Build your new infrastructure alongside the existing one, using Crossplane compositions. Implement piece by piece, starting with networking components, then the EKS cluster, followed by node groups. Use GitOps practices through Argo CD to manage the configurations.

Validation Phase
Establish comprehensive testing:

Infrastructure Verification:
Compare the new infrastructure against your documented baseline. Verify networking connectivity, IAM permissions, and security configurations. Ensure all add-ons are properly configured and functioning.

Application Migration Testing:
Deploy test workloads to verify the new environment. Check resource quotas, autoscaling behaviors, and persistent storage functionality. Verify monitoring and logging systems are capturing data correctly.

Performance Baseline:
Conduct load testing to compare performance between old and new infrastructures. Monitor resource utilization patterns and costs. Verify that autoscaling policies work as expected.

Cutover Planning
Prepare for the final migration:

DNS and Load Balancer Strategy:
Plan your DNS cutover strategy. Consider using weighted routing or blue-green deployment patterns. Document rollback procedures in case of issues.

Backup and Recovery:
Ensure all critical data is backed up before cutover. Verify backup restoration procedures in the new environment. Document disaster recovery procedures for the new infrastructure.

Post-Migration Phase
Establish ongoing maintenance procedures:

GitOps Workflows:
Document your GitOps workflows for infrastructure changes. Establish review processes for infrastructure modifications. Create runbooks for common operations tasks.

Monitoring and Alerts:
Update monitoring dashboards to reflect the new infrastructure. Configure alerts for Crossplane and Argo CD specific metrics. Establish SLOs for infrastructure components.

---


# EKS Migration Checklist: Pre and Post Migration Verification

## Core Kubernetes Components

| Component | Pre-Migration Check | Post-Migration Verification | Notes |
|-----------|-------------------|--------------------------|-------|
| Pods | • List all pods across namespaces (`kubectl get pods -A`)<br>• Record pod counts per namespace<br>• Check pod resource requests/limits<br>• Verify pod scheduling rules (node selectors, affinity)<br>• Document pod disruption budgets | • Compare pod counts with source cluster<br>• Verify all pods are Running/Ready<br>• Confirm resource allocations match<br>• Validate pod placement matches expectations<br>• Check pod startup times and health probes | Use `kubectl describe pod` to capture detailed configuration. Pay special attention to pods with persistent storage or specific node requirements. |
| Deployments | • List all deployments and their replicas<br>• Document deployment strategies<br>• Record HPA configurations<br>• Check deployment labels and annotations<br>• Verify resource quotas | • Verify replica counts match source<br>• Confirm deployment strategies are identical<br>• Validate HPA settings and behavior<br>• Check all labels and annotations<br>• Test scaling operations | Compare deployment manifests using `kubectl get deploy -o yaml` to ensure all specifications match. |
| StatefulSets | • Document StatefulSet configurations<br>• Record volume claims and storage classes<br>• Verify headless service configurations<br>• Check pod management policies | • Confirm ordinal pod creation<br>• Validate persistent volume bindings<br>• Test StatefulSet scaling<br>• Verify pod DNS entries | Pay special attention to volume claim templates and storage configurations. |

## Networking Components

| Component | Pre-Migration Check | Post-Migration Verification | Notes |
|-----------|-------------------|--------------------------|-------|
| Services | • List all services and their types<br>• Record service endpoints<br>• Document external IPs/load balancers<br>• Check service annotations | • Verify service endpoint resolution<br>• Confirm load balancer provisioning<br>• Test service discovery<br>• Validate service mesh integration | Compare service configurations using `kubectl get svc -o wide` across all namespaces. |
| Ingress | • Document ingress configurations<br>• Record TLS certificates<br>• Check ingress controller settings<br>• Verify host rules and path mappings | • Validate all ingress rules<br>• Confirm TLS termination<br>• Test path-based routing<br>• Verify annotations are applied | Use `kubectl get ingress -A -o yaml` to compare configurations. Check certificate expiration dates. |
| Network Policies | • List all network policies<br>• Document pod selector rules<br>• Record ingress/egress rules<br>• Check namespace isolation | • Verify policy enforcement<br>• Test pod-to-pod communication<br>• Validate namespace isolation<br>• Confirm external access rules | Test both allowed and denied traffic patterns to ensure policies are working as expected. |

## Storage and State

| Component | Pre-Migration Check | Post-Migration Verification | Notes |
|-----------|-------------------|--------------------------|-------|
| Persistent Volumes | • List all PVs and their status<br>• Record storage classes<br>• Document retention policies<br>• Check volume permissions | • Verify PV provisioning<br>• Confirm storage class behavior<br>• Test volume expansion<br>• Validate backup solutions | Compare PV configurations and ensure data persistence across cluster migration. |
| ConfigMaps/Secrets | • List all ConfigMaps and Secrets<br>• Document mounting methods<br>• Check for external secret managers<br>• Record update mechanisms | • Verify all configs are present<br>• Confirm secret availability<br>• Test secret rotation<br>• Validate external integrations | Use tools like `sealed-secrets` or external secret managers for secure migration. |

## External Resources and Integrations

| Component | Pre-Migration Check | Post-Migration Verification | Notes |
|-----------|-------------------|--------------------------|-------|
| IAM Roles/Service Accounts | • Document IRSA configurations<br>• List service account annotations<br>• Record role permissions<br>• Check token mounting | • Verify IRSA functionality<br>• Test AWS API access<br>• Confirm permission boundaries<br>• Validate token auto-rotation | Compare using `kubectl get serviceaccount -A -o yaml` and verify AWS IAM role associations. |
| External Services | • List external service dependencies<br>• Document endpoint configurations<br>• Record authentication methods<br>• Check rate limiting settings | • Test external connectivity<br>• Verify authentication works<br>• Validate rate limiting<br>• Confirm service resolution | Include both AWS and non-AWS external service dependencies in verification. |

## Observability and Monitoring

| Component | Pre-Migration Check | Post-Migration Verification | Notes |
|-----------|-------------------|--------------------------|-------|
| Metrics | • Record monitoring configurations<br>• Document custom metrics<br>• Check metric retention policies<br>• List alerting rules | • Verify metrics collection<br>• Confirm dashboard accuracy<br>• Test alert triggering<br>• Validate historical data | Compare metric values between clusters during parallel operation. |
| Logging | • Document log aggregation setup<br>• Record log retention policies<br>• Check log shipping configurations<br>• List log filters and transforms | • Verify log collection<br>• Confirm log formatting<br>• Test log queries<br>• Validate audit logging | Ensure all application and system logs are being collected and shipped correctly. |

## Custom Resources and Operators

| Component | Pre-Migration Check | Post-Migration Verification | Notes |
|-----------|-------------------|--------------------------|-------|
| CRDs | • List all Custom Resource Definitions<br>• Document CR instances<br>• Check operator versions<br>• Record conversion webhooks | • Verify CRD installation<br>• Confirm CR migration<br>• Test operator functionality<br>• Validate webhook operations | Use `kubectl get crd -o yaml` to compare CRD specifications between clusters. |
| Operators | • Document operator deployments<br>• Record operator configurations<br>• Check operator dependencies<br>• List managed resources | • Verify operator health<br>• Confirm resource management<br>• Test reconciliation loops<br>• Validate backup/restore | Ensure operator versions and configurations match between clusters. |

## Workload Performance

| Component | Pre-Migration Check | Post-Migration Verification | Notes |
|-----------|-------------------|--------------------------|-------|
| Resource Usage | • Record CPU/Memory utilization<br>• Document throughput metrics<br>• Check resource quotas<br>• List performance bottlenecks | • Compare resource usage patterns<br>• Verify throughput matches<br>• Test under peak load<br>• Validate autoscaling behavior | Use tools like metrics-server and custom monitoring to compare performance profiles. |
| Latency | • Document service latencies<br>• Record API response times<br>• Check network latencies<br>• List performance SLOs | • Compare latency profiles<br>• Verify response times<br>• Test cross-zone latency<br>• Validate SLO compliance | Consider running load tests to verify performance under various conditions. |

## Security and Access Control

| Component | Pre-Migration Check | Post-Migration Verification | Notes |
|-----------|-------------------|--------------------------|-------|
| Pod Security | • Document Pod Security Standards/Policies<br>• List security contexts<br>• Record container privilege settings<br>• Check pod security admission config | • Verify PSS/PSP enforcement<br>• Confirm security contexts<br>• Test privilege escalation blocks<br>• Validate admission control | Compare pod security settings using `kubectl get psp` (if using PSP) or check Pod Security admission settings. |
| RBAC | • List all ClusterRoles/Roles<br>• Document RoleBindings<br>• Record service account permissions<br>• Check aggregated roles | • Verify role permissions<br>• Test access controls<br>• Validate binding associations<br>• Confirm least privilege | Use `kubectl auth can-i` commands to verify permissions across namespaces. |
| Authentication | • Document auth providers<br>• Record webhook configurations<br>• List API server flags<br>• Check token settings | • Verify SSO integration<br>• Test auth flows<br>• Validate token issuance<br>• Confirm MFA enforcement | Include all authentication methods including OIDC, webhook, or certificate-based. |

## AWS Integration Components

| Component | Pre-Migration Check | Post-Migration Verification | Notes |
|-----------|-------------------|--------------------------|-------|
| VPC/Networking | • Document VPC peering<br>• Record Transit Gateway configs<br>• Check PrivateLink endpoints<br>• List security group rules | • Verify VPC connectivity<br>• Test cross-account access<br>• Validate endpoint access<br>• Confirm security groups | Include Direct Connect or VPN configurations if present. |
| Load Balancers | • List ALB/NLB configurations<br>• Document target groups<br>• Record SSL certificates<br>• Check health check settings | • Verify load balancer health<br>• Test SSL termination<br>• Validate sticky sessions<br>• Confirm access logs | Compare load balancer attributes and listener rules. |
| Auto Scaling | • Document node group configs<br>• Record scaling policies<br>• Check warmup periods<br>• List instance refresh settings | • Verify scaling triggers<br>• Test scale out/in<br>• Validate instance refresh<br>• Confirm capacity rebalancing | Include Cluster Autoscaler and Karpenter configurations if used. |

## Add-ons and Supporting Services

| Component | Pre-Migration Check | Post-Migration Verification | Notes |
|-----------|-------------------|--------------------------|-------|
| AWS Add-ons | • List EBS CSI driver config<br>• Document VPC CNI settings<br>• Record CoreDNS configs<br>• Check kube-proxy settings | • Verify CSI functionality<br>• Test CNI networking<br>• Validate DNS resolution<br>• Confirm proxy rules | Include versions and custom configurations of all AWS-managed add-ons. |
| Third-Party Add-ons | • Document cert-manager configs<br>• List external-dns settings<br>• Record service mesh config<br>• Check backup solutions | • Verify certificate issuance<br>• Test DNS management<br>• Validate mesh routing<br>• Confirm backup execution | Include all third-party tools and their configurations. |
| Cluster Add-ons | • List cluster autoscaler settings<br>• Document metrics server config<br>• Record dashboard settings<br>• Check CSI drivers | • Verify autoscaling behavior<br>• Test metrics collection<br>• Validate dashboard access<br>• Confirm volume operations | Include all cluster-level components and their settings. |

## Application-Specific Components

| Component | Pre-Migration Check | Post-Migration Verification | Notes |
|-----------|-------------------|--------------------------|-------|
| Init Containers | • List all init containers<br>• Document startup dependencies<br>• Record volume mounts<br>• Check environment vars | • Verify init completion<br>• Test startup order<br>• Validate volume access<br>• Confirm env injection | Pay special attention to initialization sequence and dependencies. |
| Sidecar Containers | • Document sidecar configs<br>• List shared volumes<br>• Record resource limits<br>• Check lifecycle hooks | • Verify sidecar startup<br>• Test container comms<br>• Validate resource usage<br>• Confirm proper shutdown | Include service mesh proxies and logging sidecars. |
| Cronjobs/Jobs | • List all scheduled jobs<br>• Document job history<br>• Record concurrency rules<br>• Check failure policies | • Verify job scheduling<br>• Test job completion<br>• Validate history limits<br>• Confirm failure handling | Include backup jobs and maintenance tasks. |

## Disaster Recovery Components

| Component | Pre-Migration Check | Post-Migration Verification | Notes |
|-----------|-------------------|--------------------------|-------|
| Backup Configs | • Document backup schedules<br>• List retention policies<br>• Record backup locations<br>• Check exclusion rules | • Verify backup execution<br>• Test backup completion<br>• Validate retention<br>• Confirm data integrity | Include both Kubernetes resource backups and persistent data. |
| DR Procedures | • Document failover process<br>• List recovery objectives<br>• Record manual steps<br>• Check automation scripts | • Verify failover works<br>• Test recovery time<br>• Validate data sync<br>• Confirm procedure docs | Include both regional and zonal failover procedures. |

## Application Layer Components

| Component | Pre-Migration Check | Post-Migration Verification | Notes |
|-----------|-------------------|--------------------------|-------|
| Application Config | • Document env variables<br>• List feature flags<br>• Record app-specific configs<br>• Check config injection methods<br>• Document circuit breaker settings | • Verify all env variables<br>• Test feature flag behavior<br>• Validate config updates<br>• Confirm secrets mounting<br>• Test failure handling | Include application-specific configuration files and dynamic configuration management. |
| Health Checks | • List readiness probe configs<br>• Document liveness probe settings<br>• Record startup probe params<br>• Check failure thresholds<br>• List custom health endpoints | • Verify probe timing<br>• Test failure scenarios<br>• Validate recovery behavior<br>• Confirm health metrics<br>• Check custom endpoint responses | Pay attention to timing settings and failure handling logic. |
| Cache Systems | • Document Redis configurations<br>• List Memcached settings<br>• Record cache policies<br>• Check connection pools<br>• List cache indexes | • Verify cache connectivity<br>• Test cache operations<br>• Validate eviction policies<br>• Confirm persistence<br>• Check cache hit rates | Include both in-memory and distributed cache systems. |
| Message Queues | • List queue configurations<br>• Document topic mappings<br>• Record DLQ settings<br>• Check retention policies<br>• List consumer groups | • Verify message flow<br>• Test DLQ handling<br>• Validate ordering<br>• Confirm throughput<br>• Check consumer lag | Include all messaging systems (Kafka, RabbitMQ, SQS, etc.). |

## Database Components

| Component | Pre-Migration Check | Post-Migration Verification | Notes |
|-----------|-------------------|--------------------------|-------|
| Relational DBs | • Document connection strings<br>• List DB users/roles<br>• Record backup schedules<br>• Check replication config<br>• List DB parameters<br>• Document table schemas<br>• Check connection pools | • Verify connectivity<br>• Test authentication<br>• Validate replication<br>• Confirm backup execution<br>• Test failover scenarios<br>• Verify data consistency<br>• Monitor connection usage | Include all SQL databases (RDS, Aurora, etc.). |
| NoSQL DBs | • List collection schemas<br>• Document indexes<br>• Record consistency settings<br>• Check sharding config<br>• List access patterns<br>• Document TTL settings | • Verify data access<br>• Test index usage<br>• Validate writes<br>• Confirm throughput<br>• Check latency patterns<br>• Test TTL behavior | Include document, key-value, and graph databases. |
| Search Engines | • Document index mappings<br>• List analyzer configs<br>• Record shard settings<br>• Check replica config<br>• List query templates | • Verify index health<br>• Test search accuracy<br>• Validate updates<br>• Confirm replication<br>• Check query performance | Include Elasticsearch, OpenSearch configurations. |

## Storage Components

| Component | Pre-Migration Check | Post-Migration Verification | Notes |
|-----------|-------------------|--------------------------|-------|
| Object Storage | • List bucket policies<br>• Document lifecycle rules<br>• Record versioning config<br>• Check encryption settings<br>• List CORS rules<br>• Document replication setup | • Verify access patterns<br>• Test lifecycle transitions<br>• Validate object versions<br>• Confirm encryption<br>• Test cross-origin access<br>• Check replication status | Include S3, compatible storage systems. |
| File Systems | • Document mount points<br>• List access patterns<br>• Record capacity settings<br>• Check backup configs<br>• List file permissions<br>• Document throughput limits | • Verify mount success<br>• Test file operations<br>• Validate capacity<br>• Confirm backups<br>• Check access rights<br>• Monitor throughput | Include EFS, NFS, and other shared file systems. |
| Block Storage | • List volume types<br>• Document IOPS settings<br>• Record snapshot schedules<br>• Check encryption config<br>• List volume tags | • Verify volume attachment<br>• Test I/O performance<br>• Validate snapshots<br>• Confirm encryption<br>• Check volume metrics | Include EBS and other block storage solutions. |

## External Endpoints and Integration

| Component | Pre-Migration Check | Post-Migration Verification | Notes |
|-----------|-------------------|--------------------------|-------|
| API Endpoints | • List all external APIs<br>• Document rate limits<br>• Record retry policies<br>• Check timeout settings<br>• List API versions<br>• Document fallback logic | • Verify API access<br>• Test rate limiting<br>• Validate retry behavior<br>• Confirm timeouts<br>• Check version compatibility<br>• Test fallback scenarios | Include both internal and external API dependencies. |
| Authentication | • List auth providers<br>• Document token configs<br>• Record cert locations<br>• Check refresh logic<br>• List allowed origins | • Verify auth flows<br>• Test token refresh<br>• Validate cert chains<br>• Confirm session handling<br>• Check CORS behavior | Include OAuth, OIDC, and custom auth systems. |
| CDN/Edge | • Document CDN configs<br>• List cache rules<br>• Record SSL settings<br>• Check origin configs<br>• List edge functions | • Verify cache behavior<br>• Test cache invalidation<br>• Validate SSL/TLS<br>• Confirm origin health<br>• Check function execution | Include CloudFront and other CDN configurations. |
| Service Discovery | • List service registry<br>• Document DNS records<br>• Record health checks<br>• Check TTL settings<br>• List service mesh routes | • Verify service discovery<br>• Test DNS resolution<br>• Validate health checks<br>• Confirm routing rules<br>• Check mesh config | Include Cloud Map and custom service discovery. |

## Data Migration Components

| Component | Pre-Migration Check | Post-Migration Verification | Notes |
|-----------|-------------------|--------------------------|-------|
| ETL Jobs | • List data pipelines<br>• Document transformation rules<br>• Record schedule configs<br>• Check failure handling<br>• List dependencies | • Verify data flow<br>• Test transformations<br>• Validate schedules<br>• Confirm error handling<br>• Check completeness | Include all data movement and transformation jobs. |
| Data Validation | • Document validation rules<br>• List data quality checks<br>• Record checksum configs<br>• Check reconciliation logic | • Verify data integrity<br>• Test validation rules<br>• Validate checksums<br>• Confirm reconciliation | Include both automated and manual validation processes. |

## Migration Verification Commands

Here are some helpful commands for verification:

```bash
# Compare pod counts between clusters
kubectl get pods -A --no-headers | wc -l

# Check for pods not in Running state
kubectl get pods -A --field-selector status.phase!=Running

# Verify service endpoints
kubectl get endpoints -A

# Compare CRD counts
kubectl get crd -o name | wc -l

# Check for pending PVCs
kubectl get pvc -A --field-selector status.phase=Pending

# Verify node conditions
kubectl get nodes -o custom-columns=NAME:.metadata.name,STATUS:.status.conditions[?(@.type=="Ready")].status

# Compare deployment replica counts
kubectl get deploy -A -o custom-columns=NAMESPACE:.metadata.namespace,NAME:.metadata.name,DESIRED:.spec.replicas,CURRENT:.status.replicas
```

Remember to run these checks against both source and target clusters and compare the results carefully.

# EKS Migration: Component Verification Commands

## Core Kubernetes Components

### Pod Verification
```bash
# Get all pods across namespaces with their status
kubectl get pods -A -o wide

# Check pods not in Running state
kubectl get pods -A --field-selector status.phase!=Running

# View pod resource usage
kubectl top pods -A

# Check pod disruption budgets
kubectl get pdb -A

# View pod scheduling information
kubectl describe pod <pod-name> | grep -A10 Events

# Check pod security contexts
kubectl get pod <pod-name> -o jsonpath='{.spec.securityContext}'
```

### Deployment Verification
```bash
# List all deployments with their status
kubectl get deployments -A -o wide

# Check deployment rollout history
kubectl rollout history deployment/<deployment-name> -n <namespace>

# Verify horizontal pod autoscaling
kubectl get hpa -A

# Check deployment strategies
kubectl get deploy <deployment-name> -o jsonpath='{.spec.strategy}'

# Compare replica counts
kubectl get deploy -A --no-headers | awk '{print $1,$2,$3,$4}'
```

## Storage Components

### Persistent Volume Verification
```bash
# List all PVs and their status
kubectl get pv -o wide

# Check PVC bindings
kubectl get pvc -A

# View storage classes
kubectl get sc

# Check volume attachments
kubectl get volumeattachment -A

# Verify CSI drivers
kubectl get csidrivers
```

### EBS Volume Commands
```bash
# List EBS volumes
aws ec2 describe-volumes --filters Name=tag:kubernetes.io/created-for/pvc/namespace,Values=*

# Check volume snapshots
kubectl get volumesnapshot -A

# Verify EBS CSI driver
kubectl get pods -n kube-system | grep ebs
```

## Networking Components

### Service Verification
```bash
# List all services and their endpoints
kubectl get svc -A -o wide

# Check endpoint connections
kubectl get endpoints -A

# Verify load balancers
aws elb describe-load-balancers

# Check service mesh config (if using App Mesh)
kubectl get virtualnodes -A
kubectl get virtualservices -A
```

### Network Policy Verification
```bash
# List network policies
kubectl get networkpolicies -A

# Check CNI configuration
kubectl describe daemonset aws-node -n kube-system

# Verify DNS resolution
kubectl run tmp-shell --rm -i --tty --image nicolaka/netshoot -- bash
# Then run: dig <service-name>.<namespace>.svc.cluster.local
```

## Security Components

### RBAC Verification
```bash
# List cluster roles
kubectl get clusterroles

# Check role bindings
kubectl get rolebindings -A

# Verify service account permissions
kubectl auth can-i --list --as=system:serviceaccount:<namespace>:<serviceaccount>

# Check pod security policies (if using)
kubectl get psp
```

### Authentication Verification
```bash
# Check authentication config
kubectl config view

# List service accounts
kubectl get serviceaccounts -A

# Verify IRSA configuration
kubectl describe serviceaccount <name> -n <namespace>
aws iam get-role --role-name <role-name>
```

## AWS Integration

### VPC and Networking
```bash
# Get VPC info
aws ec2 describe-vpcs --filters Name=tag:kubernetes.io/cluster/<cluster-name>,Values=owned

# Check security groups
aws ec2 describe-security-groups --filters Name=tag:kubernetes.io/cluster/<cluster-name>,Values=owned

# Verify subnet configuration
aws ec2 describe-subnets --filters Name=tag:kubernetes.io/cluster/<cluster-name>,Values=owned
```

### Load Balancer Verification
```bash
# Check AWS Load Balancers
aws elbv2 describe-load-balancers

# Verify target groups
aws elbv2 describe-target-groups

# Check listener configurations
aws elbv2 describe-listeners --load-balancer-arn <lb-arn>
```

## Database Connectivity

### RDS Verification
```bash
# Test database connectivity from pod
kubectl run mysql-client --image=mysql:5.7 -i --rm --restart=Never -- mysql -h <rds-endpoint> -u <username> -p<password>

# Check RDS status
aws rds describe-db-instances --db-instance-identifier <instance-id>
```

### DynamoDB Verification
```bash
# Test DynamoDB access
aws dynamodb list-tables
aws dynamodb describe-table --table-name <table-name>
```

## Application Monitoring

### Metrics Verification
```bash
# Check metrics server
kubectl top nodes
kubectl top pods -A

# Verify Prometheus (if installed)
kubectl get pods -n prometheus
kubectl port-forward svc/prometheus-server 8080:80 -n prometheus
```

### Logging Verification
```bash
# Check CloudWatch logs
aws logs describe-log-groups

# Verify Fluentd/Fluent Bit
kubectl get pods -n logging
kubectl logs -n logging <fluentd-pod-name>
```

## Add-ons and Supporting Services

### AWS Add-on Verification
```bash
# Check AWS add-ons
aws eks describe-addon --cluster-name <cluster-name> --addon-name vpc-cni
aws eks describe-addon --cluster-name <cluster-name> --addon-name coredns
aws eks describe-addon --cluster-name <cluster-name> --addon-name kube-proxy

# Verify add-on versions
kubectl describe daemonset aws-node -n kube-system
kubectl describe deployment coredns -n kube-system
```

### External DNS Verification
```bash
# Check External DNS pods
kubectl get pods -n external-dns
kubectl logs -n external-dns <external-dns-pod>

# Verify Route53 records
aws route53 list-resource-record-sets --hosted-zone-id <zone-id>
```

## Backup and Recovery

### Velero Backup Verification
```bash
# List backups
velero backup get

# Check backup details
velero backup describe <backup-name>

# Verify backup locations
velero backup-location get

# Check restore status
velero restore get
```

## Performance Testing

### Load Testing Commands
```bash
# Install hey for HTTP load testing
kubectl run load-test --image=rakyll/hey --rm -i --tty -- /hey -z 30s -q 20 -c 50 http://<service-url>

# Check resource utilization
kubectl top pods --containers=true
kubectl top nodes

# Get HPA metrics
kubectl get hpa -A -w
```

## Useful Diagnostic Commands

### Cluster Health
```bash
# Check cluster health
aws eks describe-cluster --name <cluster-name>

# Verify node status
kubectl get nodes -o custom-columns=NAME:.metadata.name,STATUS:.status.conditions[?(@.type=="Ready")].status

# Check system components
kubectl get componentstatuses
```

### Resource Quota Verification
```bash
# Check resource quotas
kubectl get resourcequota -A

# Verify limit ranges
kubectl get limitrange -A

# Check pod resource requests/limits
kubectl get pods -A -o json | jq '.items[] | select(has("spec")) | .spec.containers[] | select(has("resources")) | .resources'
```

Remember to:
1. Replace placeholders (like <cluster-name>, <namespace>, etc.) with actual values
2. Run these commands against both source and target clusters to compare
3. Store the output for comparison and documentation
4. Use tools like `diff` to compare outputs between clusters
5. Consider scripting these checks for automation
