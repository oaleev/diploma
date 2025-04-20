# AWS Load Balancer Controller on EKS

## Introduction

Hello everyone, today I'll be demonstrating the AWS Load Balancer Controller for Amazon EKS. This controller is a crucial component for managing ingress traffic to the Kubernetes applications running on EKS.

### What is a Kubernetes Controller?

Before diving into the AWS Load Balancer Controller specifically, let's understand what a Kubernetes controller is:

A Kubernetes controller is a non-terminating control loop that watches the shared state of the cluster through the API server and makes changes attempting to move the current state towards the desired state. Controllers follow this pattern:

1. **Observe**: Monitor the state of resources in the Kubernetes cluster
2. **Analyze**: Compare the current state with the desired state
3. **Act**: Take actions to reconcile any differences between current and desired states
4. **Report**: Update status and log information about its actions

Controllers are the "brain" behind Kubernetes' declarative model, continuously working to ensure the actual state of the cluster matches what users have specified. Examples include Deployment controllers, ReplicaSet controllers, and in our case, the AWS Load Balancer Controller.

### What is the AWS Load Balancer Controller?

The AWS Load Balancer Controller is a specialized Kubernetes controller that helps manage Elastic Load Balancers for a Kubernetes cluster. It:

- Replaces the legacy in-tree AWS cloud provider for load balancing
- Manages both Application Load Balancers (ALBs) and Network Load Balancers (NLBs)
- Creates AWS resources in response to Kubernetes Ingress and Service resources
- Handles complex routing configurations and integrates with AWS services

### Why Use the AWS Load Balancer Controller?

There are several key benefits to using this controller:

- **Native AWS Integration**: Direct integration with AWS load balancing services
- **Advanced Features**: Support for AWS-specific functionality like path-based routing, weighted target groups, and SSL/TLS termination
- **Certificate Management**: Automatic discovery and use of certificates from AWS Certificate Manager (ACM)
- **Performance**: Improved performance compared to the legacy cloud provider implementation
- **Kubernetes Native**: Uses standard Kubernetes resources (Ingress, Service) with AWS-specific annotations

## Architecture Overview

Let me explain how the controller works within the EKS ecosystem:

### Controller Deployment Model

The AWS Load Balancer Controller runs as a deployment in your Kubernetes cluster, typically in the `kube-system` namespace. It consists of controller pods that:

- Watch for Kubernetes resources (Ingress, Service)
- Reconcile the desired state in Kubernetes with the actual state in AWS
- Create and manage AWS resources as needed
- Update status of Kubernetes resources based on AWS resource state

### AWS Integration Points

The controller integrates with several AWS services:

- **Elastic Load Balancing**: Creates and manages ALBs and NLBs
- **EC2**: Creates security groups, manages target groups
- **ACM**: Discovers and uses certificates for HTTPS termination
- **WAF**: Optional integration for web application firewall capabilities
- **Shield**: Optional integration for DDoS protection

### Kubernetes Resource Mapping

Here's how Kubernetes resources map to AWS resources:

- **Ingress** → Application Load Balancer (ALB)
- **Service (type: LoadBalancer)** → Network Load Balancer (NLB)
- **Service (with annotations)** → Can create either ALB or NLB
- **IngressClass** → Defines which controller handles which Ingress resources
- **TargetGroupBinding** → Advanced custom target group configurations

## Key Annotations Deep Dive

Annotations are crucial for configuring the AWS Load Balancer Controller behavior. Let's look at some of the most important ones based on the latest version:

### Essential ALB Annotations

```
alb.ingress.kubernetes.io/scheme: [internet-facing | internal]
```
Determines whether the ALB is publicly accessible (internet-facing) or only within your VPC (internal). 
- `internet-facing`: Creates a public ALB with a public DNS name that resolves to public IP addresses
- `internal`: Creates a private ALB that can only be accessed from within your VPC

```
alb.ingress.kubernetes.io/target-type: [instance | ip]
```
Specifies how targets are registered with the ALB:
- `instance`: Registers EC2 instances as targets by node/port
- `ip`: Registers pod IPs directly (works with Fargate and enables better security group control)

```
alb.ingress.kubernetes.io/subnets: subnet-xxxx,subnet-yyyy
```
Explicitly specify which subnets the ALB should be created in. If not specified, the controller auto-discovers subnets.
- For `internet-facing` ALBs: Must specify public subnets with routes to internet gateway
- For `internal` ALBs: Should specify private subnets

```
alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS": 443}]'
```
Specifies which ports the ALB should listen on.

### IngressClass Resource

Instead of using the `kubernetes.io/ingress.class: alb` annotation, the latest best practice is to use the IngressClass resource:

```yaml
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  name: alb
spec:
  controller: ingress.k8s.aws/alb
```

And then reference it in your Ingress:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
spec:
  ingressClassName: alb
  # ...
```

### Essential NLB Annotations

For NLB services, key annotations include:

```
service.beta.kubernetes.io/aws-load-balancer-type: nlb
```
Specifies that an NLB should be created instead of a classic ELB. In newer versions, this can also be `nlb-ip` for IP-based target type.

```
service.beta.kubernetes.io/aws-load-balancer-internal: "true"
```
Creates an internal NLB (not internet-facing)

```
service.beta.kubernetes.io/aws-load-balancer-scheme: [internet-facing | internal]
```
Similar to ALB scheme, determines the NLB's accessibility:
- `internet-facing`: Creates a public NLB accessible from the internet
- `internal`: Creates a private NLB only accessible within your VPC

```
service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: [instance | ip]
```
Similar to ALB target type:
- `instance`: Registers nodes as targets
- `ip`: Registers pod IPs directly

### Internal vs External Load Balancers

#### Internal Load Balancers
- Deployed within your VPC
- Private DNS names that resolve to private IP addresses
- Not accessible from the public internet
- Used for internal microservices, backend services, and applications that should not be publicly exposed
- Requires appropriate VPC routing and security groups for access from authorized sources
- Best practice for security of sensitive applications

Example for internal ALB:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: internal-alb
  annotations:
    alb.ingress.kubernetes.io/scheme: internal
    alb.ingress.kubernetes.io/target-type: ip
    # Optionally specify private subnets
    alb.ingress.kubernetes.io/subnets: subnet-private1,subnet-private2
spec:
  ingressClassName: alb
  # ...
```

Example for internal NLB:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: internal-nlb
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: nlb
    service.beta.kubernetes.io/aws-load-balancer-internal: "true"
    # Alternative way to specify internal scheme
    service.beta.kubernetes.io/aws-load-balancer-scheme: internal
spec:
  type: LoadBalancer
  # ...
```

#### External (Internet-Facing) Load Balancers
- Public DNS names that resolve to public IP addresses
- Accessible from the public internet
- Used for public-facing applications and services
- Requires public subnets with routes to internet gateway
- Security considerations: Should have proper security groups and WAF if needed

Example for internet-facing ALB:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: external-alb
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    # Optionally specify public subnets
    alb.ingress.kubernetes.io/subnets: subnet-public1,subnet-public2
spec:
  ingressClassName: alb
  # ...
```

Example for internet-facing NLB:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-nlb
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: nlb
    service.beta.kubernetes.io/aws-load-balancer-scheme: internet-facing
spec:
  type: LoadBalancer
  # ...
```

## Demo Setup

Now, let's set up the controller in our EKS cluster using the latest installation methods:

### Prerequisites:

Before installing the controller, we need:

1. An EKS cluster running Kubernetes 1.19+ (1.22+ recommended for latest features)
2. IAM roles for service accounts (IRSA) configured for EKS
3. Appropriate IAM permissions for the controller
4. AWS CLI, kubectl, and Helm installed

### Setting up IAM Permissions

First, we need to create an IAM policy for the controller:

```bash
# Download the IAM policy document from the latest source
curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json

# Create the IAM policy
aws iam create-policy \
    --policy-name AWSLoadBalancerControllerIAMPolicy \
    --policy-document file://iam_policy.json
```

Next, we create an IAM role and service account for the controller using eksctl:

```bash
eksctl create iamserviceaccount \
  --cluster=my-cluster \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --attach-policy-arn=arn:aws:iam::123456789012:policy/AWSLoadBalancerControllerIAMPolicy \
  --approve
```

### Installing with Helm

Now, let's install the controller using Helm:

```bash
# Add the EKS chart repository
helm repo add eks https://aws.github.io/eks-charts
helm repo update

# Install the AWS Load Balancer Controller
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=my-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set region=us-west-2 \
  --set vpcId=vpc-xxxxxxxx
```

### Installing Custom Resource Definitions (CRDs)

The latest versions of the controller require specific CRDs to be installed:

```bash
# Apply the CRDs directly from the controller repository
kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller//crds?ref=master"
```

### Verify Installation

Let's verify the controller is running with the correct version:

```bash
kubectl get deployment -n kube-system aws-load-balancer-controller -o jsonpath="{.spec.template.spec.containers[0].image}" | cut -d ":" -f 2
kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller
```

## Live Demo Scenarios

### Creating the IngressClass Resource

First, let's create the IngressClass resource (new approach in latest Kubernetes versions):

```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  name: alb
spec:
  controller: ingress.k8s.aws/alb
EOF
```

### Scenario 1: Deploy an Application with Internal ALB

Let's deploy a sample application and configure an internal Application Load Balancer for it.

First, create a deployment and service:

```bash
# Create a namespace for our demo
kubectl create namespace demo

# Deploy the sample application
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  namespace: demo
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  namespace: demo
spec:
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
  selector:
    app: nginx
EOF
```

Now, let's create an Ingress resource to trigger the creation of an internal ALB:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-internal-ingress
  namespace: demo
  annotations:
    alb.ingress.kubernetes.io/scheme: internal
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/group.name: internal-apps
    alb.ingress.kubernetes.io/healthcheck-protocol: HTTP
    alb.ingress.kubernetes.io/healthcheck-path: /
    alb.ingress.kubernetes.io/tags: Environment=demo,Team=platform
spec:
  ingressClassName: alb
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-service
            port:
              number: 80
EOF
```

Note: The `group.name` annotation is a feature in recent versions that allows multiple Ingress resources to share the same ALB.

### Scenario 2: Deploy an Application with External ALB

Now, let's create an internet-facing ALB for public access:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-external-ingress
  namespace: demo
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/group.name: external-apps
    alb.ingress.kubernetes.io/healthcheck-protocol: HTTP
    alb.ingress.kubernetes.io/healthcheck-path: /
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS": 443}]'
    alb.ingress.kubernetes.io/ssl-redirect: '443'
    alb.ingress.kubernetes.io/tags: Environment=demo,Team=platform,Public=true
spec:
  ingressClassName: alb
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-service
            port:
              number: 80
EOF
```

### Scenario 3: NLB for TCP Services (Internal and External)

Let's create internal and external Network Load Balancers for TCP traffic using the latest annotations:

Internal NLB with IP targets (newer recommended approach):
```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: nginx-internal-nlb
  namespace: demo
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb-ip"
    service.beta.kubernetes.io/aws-load-balancer-scheme: "internal"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-protocol: "http"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-path: "/"
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
  selector:
    app: nginx
EOF
```

External NLB with IP targets:
```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: nginx-external-nlb
  namespace: demo
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb-ip"
    service.beta.kubernetes.io/aws-load-balancer-scheme: "internet-facing"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-protocol: "http"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-path: "/"
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
  selector:
    app: nginx
EOF
```

## Latest Features in AWS Load Balancer Controller

### ALB Sharing with Group Name Annotation

```
alb.ingress.kubernetes.io/group.name: shared-alb
```
This allows multiple Ingress resources to share the same ALB, reducing costs and simplifying management.

### Enhanced Shield Advanced Integration

```
alb.ingress.kubernetes.io/shield-advanced-protection: "true"
```
Enable AWS Shield Advanced protection for your ALB.

### Cross-Zone Load Balancing

```
service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
```
Enable cross-zone load balancing for NLB (newer annotation).

### IP-Based Target Groups for NLB

Use the `nlb-ip` load balancer type instead of just `nlb`:
```
service.beta.kubernetes.io/aws-load-balancer-type: "nlb-ip"
```

### Load Balancer Tags

```
alb.ingress.kubernetes.io/tags: Environment=production,Team=dev
```
Apply tags to the created AWS resources for better organization.

### AWS WAF v2 Integration

```
alb.ingress.kubernetes.io/wafv2-acl-arn: arn:aws:wafv2:region:account-id:global/webacl/my-web-acl/1234567890123456
```
Associate a WAFv2 web ACL with your ALB.

## TargetGroupBinding for Direct Control

The TargetGroupBinding custom resource allows you to use existing target groups with your Kubernetes Services:

```yaml
apiVersion: elbv2.k8s.aws/v1beta1
kind: TargetGroupBinding
metadata:
  name: my-tgb
  namespace: demo
spec:
  serviceRef:
    name: nginx-service
    port: 80
  targetGroupARN: arn:aws:elasticloadbalancing:region:account-id:targetgroup/my-tg/1234567890123456
  networking:
    ingress:
    - from:
      - securityGroup:
          groupID: sg-0123456789
      ports:
      - protocol: TCP
        port: 80
```

## Advanced Routing Configurations

### Path-Based Routing

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path-based-routing
  namespace: demo
  annotations:
    alb.ingress.kubernetes.io/target-type: ip
spec:
  ingressClassName: alb
  rules:
  - http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
      - path: /admin
        pathType: Prefix
        backend:
          service:
            name: admin-service
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

### Host-Based Routing

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: host-based-routing
  namespace: demo
  annotations:
    alb.ingress.kubernetes.io/target-type: ip
spec:
  ingressClassName: alb
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
  - host: www.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

### Weighted Target Groups (Canary Deployments)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: canary-ingress
  namespace: demo
  annotations:
    alb.ingress.kubernetes.io/actions.weighted-routing: '{"Type":"forward","ForwardConfig":{"TargetGroups":[{"ServiceName":"nginx-service","ServicePort":"80","Weight":80},{"ServiceName":"nginx-canary","ServicePort":"80","Weight":20}]}}'
spec:
  ingressClassName: alb
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: weighted-routing
            port:
              name: use-annotation
```

### SSL/TLS Termination with ACM

For HTTPS, we can configure SSL/TLS termination using ACM certificates:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: secure-ingress
  namespace: demo
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:region:account-id:certificate/certificate-id
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS":443}]'
    alb.ingress.kubernetes.io/ssl-redirect: '443'
spec:
  ingressClassName: alb
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-service
            port:
              number: 80
```

## Security Best Practices

### Implement Security Groups

```
alb.ingress.kubernetes.io/security-groups: sg-xxxx,sg-yyyy
```
Apply specific security groups to your ALB for access control.

### Enable Access Logs

```
alb.ingress.kubernetes.io/load-balancer-attributes: access_logs.s3.enabled=true,access_logs.s3.bucket=my-elb-logs,access_logs.s3.prefix=alb-logs
```
Enable access logging to S3 for auditing and monitoring.

### Remove Plaintext HTTP Access

```
alb.ingress.kubernetes.io/ssl-redirect: '443'
alb.ingress.kubernetes.io/actions.ssl-redirect: '{"Type": "redirect", "RedirectConfig": {"Protocol": "HTTPS", "Port": "443", "StatusCode": "HTTP_301"}}'
```
Force HTTPS by redirecting HTTP requests.

### Use Authentication

```
alb.ingress.kubernetes.io/auth-type: cognito
alb.ingress.kubernetes.io/auth-idp-cognito: '{"UserPoolArn":"arn:aws:cognito-idp:us-west-2:123456789012:userpool/us-west-2_aaaaaaaaa","UserPoolClientId":"1example23456789","UserPoolDomain":"test-domain"}'
```
Implement authentication using Amazon Cognito.

## Troubleshooting Tips

When facing issues, use these commands for investigation:

1. Check controller logs:
   ```bash
   kubectl logs -n kube-system deployment/aws-load-balancer-controller
   ```

2. Check controller event records:
   ```bash
   kubectl get events -n kube-system --field-selector involvedObject.name=aws-load-balancer-controller
   ```

3. Examine Ingress/Service events:
   ```bash
   kubectl describe ingress -n demo nginx-external-ingress
   ```

4. Verify IAM permissions:
   ```bash
   aws iam simulate-principal-policy --policy-source-arn $(aws iam get-role --role-name eksctl-my-cluster-addon-iamserviceaccount-kube-sys-Role1-XXXX --query "Role.Arn" --output text) --action-names elasticloadbalancing:*
   ```

5. Check subnet configurations:
   ```bash
   aws ec2 describe-subnets --filters "Name=tag:kubernetes.io/cluster/my-cluster,Values=owned" --query "Subnets[*].{ID:SubnetId,AZ:AvailabilityZone,Public:MapPublicIpOnLaunch}"
   ```

6. Check security groups:
   ```bash
   kubectl get targetgroupbindings -A -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.networking.ingress[*].from[*].securityGroup.groupID}{"\n"}{end}'
   ```

## Summary and Q&A

In this demo, we've covered:

- What a Kubernetes controller is and how it operates
- The purpose and architecture of the AWS Load Balancer Controller
- Installation and configuration of the latest controller version
- Using IngressClass resources (the modern approach)
- Key annotations for configuring ALBs and NLBs
- Differences between internal and external facing load balancers
- Advanced features like group.name for sharing ALBs
- Security best practices
- Troubleshooting techniques

### Resources for Further Learning:

- [AWS Load Balancer Controller GitHub Repository](https://github.com/kubernetes-sigs/aws-load-balancer-controller)
- [Official Documentation](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/)
- [EKS Workshop](https://www.eksworkshop.com/)
- [AWS EKS Best Practices Guide](https://aws.github.io/aws-eks-best-practices/)
- [Complete Annotations Reference](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/guide/ingress/annotations/)
