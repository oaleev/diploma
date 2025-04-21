# AWS Load Balancer Controller - Common FAQs

## General Questions

### Q1: What is the AWS Load Balancer Controller?
**A:** The AWS Load Balancer Controller is a Kubernetes controller that manages Elastic Load Balancers for a Kubernetes cluster. It helps create and configure Application Load Balancers (ALBs) for Kubernetes Ingress resources and Network Load Balancers (NLBs) for Kubernetes Service resources of type LoadBalancer. Previously known as the AWS ALB Ingress Controller, it was rebranded and expanded to handle both ALBs and NLBs.

### Q2: What are the primary benefits of using the AWS Load Balancer Controller?
**A:** The key benefits include:
- Native integration with AWS load balancing services
- Advanced routing features like path-based and host-based routing
- Cost optimization through sharing ALBs across multiple services
- Support for direct pod routing with IP targets
- Integration with other AWS services (ACM, WAF, Shield)
- More configuration options through annotations than the legacy in-tree provider

### Q3: How does the AWS Load Balancer Controller differ from the legacy in-tree AWS cloud provider?
**A:** The legacy in-tree provider is limited to creating Classic Load Balancers or Network Load Balancers with instance targets only. The AWS Load Balancer Controller provides more functionality, including ALBs via Ingress resources, NLBs with IP targets, advanced routing capabilities, and more flexible configuration through annotations. The AWS Load Balancer Controller is actively maintained with new features, while the in-tree provider only receives critical bug fixes.

### Q4: What version of Kubernetes do I need?
**A:** The required Kubernetes version depends on the controller version:
- AWS Load Balancer Controller v2.4.0+ requires Kubernetes 1.19+
- v2.2.0 ~ v2.3.1 requires Kubernetes 1.16-1.21
- v2.0.0 ~ v2.1.3 requires Kubernetes 1.15+

### Q5: Can I use both the AWS Load Balancer Controller and the legacy in-tree provider in the same cluster?
**A:** Yes, you can use both controllers in the same cluster. For services that should be managed by the AWS Load Balancer Controller, add the annotation `service.beta.kubernetes.io/aws-load-balancer-type: "external"` to tell the in-tree controller to ignore these services. In versions 2.5+, the AWS Load Balancer Controller becomes the default controller for LoadBalancer type services unless you disable this behavior.

### Q6: Is the AWS Load Balancer Controller officially supported by AWS?
**A:** Yes, the AWS Load Balancer Controller is officially supported by AWS and receives regular updates and security patches. It is the recommended approach for managing AWS load balancers with Amazon EKS.

## Installation and Configuration

### Q7: How do I install the AWS Load Balancer Controller?
**A:** The recommended way to install the controller is using Helm:
1. Create an IAM policy and role for the controller
2. Create a service account that uses the role
3. Add the EKS Helm repository
4. Install the controller using Helm

Detailed installation instructions are available in the AWS documentation and the controller's GitHub repository.

### Q8: What IAM permissions does the controller need?
**A:** The controller needs permissions to create and manage load balancers, target groups, security groups, and related resources. The official documentation provides a policy document that includes all required permissions. You should follow the principle of least privilege and only grant the necessary permissions.

### Q9: Should I install the controller in every EKS cluster, or can I share a single controller across multiple clusters?
**A:** You should install the controller in each EKS cluster separately. Each controller instance is designed to manage resources for its own cluster. However, with newer versions supporting multi-cluster TargetGroupBinding, you can have load balancers that route traffic to pods in multiple clusters.

### Q10: How do I upgrade the controller?
**A:** To upgrade the controller, first apply the CRDs for the new version, then upgrade the Helm release. For example:
```bash
kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller//crds?ref=master"
helm upgrade aws-load-balancer-controller eks/aws-load-balancer-controller -n kube-system
```

### Q11: How do I migrate from the ALB Ingress Controller to the AWS Load Balancer Controller?
**A:** The migration involves uninstalling the ALB Ingress Controller first, then installing the AWS Load Balancer Controller. The good news is that your existing Ingress resources and annotations will continue to work with the new controller. The official documentation provides a detailed migration guide.

## Load Balancer Types and Configurations

### Q12: What types of load balancers can I create with the controller?
**A:** The controller can create two types of load balancers:
- Application Load Balancers (ALBs) from Kubernetes Ingress resources
- Network Load Balancers (NLBs) from Kubernetes Service resources of type LoadBalancer

### Q13: When should I use an ALB vs an NLB?
**A:** Use ALBs for HTTP/HTTPS traffic when you need:
- Path-based or host-based routing
- Content-based routing
- SSL/TLS termination
- Authentication integration
- Web application firewall protection

Use NLBs for TCP/UDP traffic when you need:
- Lower latency
- Static IP addresses
- Fixed endpoints for whitelisting
- Preservation of client source IP addresses
- UDP protocol support
- End-to-end encryption

### Q14: How do I create an internal vs external load balancer?
**A:** For internal load balancers (only accessible within your VPC):
- ALB: Use annotation `alb.ingress.kubernetes.io/scheme: internal`
- NLB: Use annotation `service.beta.kubernetes.io/aws-load-balancer-scheme: internal`

For external load balancers (internet-facing):
- ALB: Use annotation `alb.ingress.kubernetes.io/scheme: internet-facing`
- NLB: Use annotation `service.beta.kubernetes.io/aws-load-balancer-scheme: internet-facing`

### Q15: What is the difference between IP and instance target types?
**A:** The target type determines how targets are registered with the load balancer:

**Instance target type**:
- Registers EC2 instances (nodes) as targets
- Traffic goes to the node first, then gets redirected to the pod through kube-proxy
- Works only with EC2 nodes (not Fargate)
- Annotations: `alb.ingress.kubernetes.io/target-type: instance` or `service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: instance`

**IP target type**:
- Registers pod IPs directly as targets
- Traffic goes directly to the pods
- Works with both EC2 and Fargate pods
- Annotations: `alb.ingress.kubernetes.io/target-type: ip` or `service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: ip`

### Q16: Can I use the AWS Load Balancer Controller with Fargate pods?
**A:** Yes, you can use the AWS Load Balancer Controller with Fargate pods, but you must use IP target type, not instance target type. This is because Fargate doesn't provide EC2 instances that can be registered as targets.

### Q17: How do I specify which subnets to use for my load balancers?
**A:** You have two options:
1. **Explicit specification**: Use annotation `alb.ingress.kubernetes.io/subnets` for ALBs or `service.beta.kubernetes.io/aws-load-balancer-subnets` for NLBs to list specific subnet IDs.
2. **Auto-discovery**: Tag your subnets with specific tags, and the controller will find them automatically:
   - For internal load balancers: Tag with `kubernetes.io/role/internal-elb: 1`
   - For external load balancers: Tag with `kubernetes.io/role/elb: 1`
   - Always include the cluster tag: `kubernetes.io/cluster/CLUSTER_NAME: owned` or `shared`

### Q18: How do I configure HTTPS for my load balancer?
**A:** For HTTPS configuration with an ALB, use these annotations:
```yaml
alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:region:account-id:certificate/certificate-id
alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS": 443}]'
alb.ingress.kubernetes.io/ssl-redirect: '443'
```

For NLBs, use:
```yaml
service.beta.kubernetes.io/aws-load-balancer-ssl-cert: arn:aws:acm:region:account-id:certificate/certificate-id
service.beta.kubernetes.io/aws-load-balancer-ssl-ports: "443"
```

### Q19: How can I customize the health check parameters for load balancers?
**A:** For ALBs, use these annotations:
```yaml
alb.ingress.kubernetes.io/healthcheck-protocol: HTTP
alb.ingress.kubernetes.io/healthcheck-path: /health
alb.ingress.kubernetes.io/healthcheck-interval-seconds: '15'
alb.ingress.kubernetes.io/healthcheck-timeout-seconds: '5'
alb.ingress.kubernetes.io/success-codes: '200'
alb.ingress.kubernetes.io/healthy-threshold-count: '2'
alb.ingress.kubernetes.io/unhealthy-threshold-count: '2'
```

For NLBs, use:
```yaml
service.beta.kubernetes.io/aws-load-balancer-healthcheck-protocol: "http"
service.beta.kubernetes.io/aws-load-balancer-healthcheck-path: "/health"
service.beta.kubernetes.io/aws-load-balancer-healthcheck-port: "8080"
service.beta.kubernetes.io/aws-load-balancer-healthcheck-interval: "10"
service.beta.kubernetes.io/aws-load-balancer-healthcheck-timeout: "5"
service.beta.kubernetes.io/aws-load-balancer-healthcheck-healthy-threshold: "2"
service.beta.kubernetes.io/aws-load-balancer-healthcheck-unhealthy-threshold: "2"
```

## Advanced Features and Use Cases

### Q20: What is an IngressGroup and how does it work?
**A:** IngressGroups allow you to share a single ALB across multiple Ingress resources, which helps reduce costs and simplify management. To add an Ingress to a group, use this annotation:
```yaml
alb.ingress.kubernetes.io/group.name: shared-alb
```

All Ingresses with the same `group.name` will share the same ALB. You can control rule priority with:
```yaml
alb.ingress.kubernetes.io/group.order: '10'
```
Lower values have higher priority.

### Q21: Can I implement canary deployments or blue/green deployments with the controller?
**A:** Yes, you can implement canary deployments using weighted target groups with this annotation:
```yaml
alb.ingress.kubernetes.io/actions.weighted-routing: |
  {
    "Type":"forward",
    "ForwardConfig":{
      "TargetGroups":[
        {
          "ServiceName":"stable-service",
          "ServicePort":"80",
          "Weight":80
        },
        {
          "ServiceName":"canary-service",
          "ServicePort":"80",
          "Weight":20
        }
      ]
    }
  }
```
This sends 80% of traffic to the stable service and 20% to the canary service.

### Q22: How can I implement authentication for my ALB?
**A:** The AWS Load Balancer Controller supports integration with Amazon Cognito for authentication:
```yaml
alb.ingress.kubernetes.io/auth-type: cognito
alb.ingress.kubernetes.io/auth-idp-cognito: '{"UserPoolArn":"arn:aws:cognito-idp:region:account:userpool/user-pool-id","UserPoolClientId":"client-id","UserPoolDomain":"domain-prefix"}'
alb.ingress.kubernetes.io/auth-on-unauthenticated-request: authenticate
```

It also supports OIDC providers:
```yaml
alb.ingress.kubernetes.io/auth-type: oidc
alb.ingress.kubernetes.io/auth-idp-oidc: '{"Issuer":"https://example.com","AuthorizationEndpoint":"https://example.com/auth","TokenEndpoint":"https://example.com/token","UserInfoEndpoint":"https://example.com/userinfo","SecretName":"oidc-secret"}'
```

### Q23: How can I implement WAF and Shield protection with my ALBs?
**A:** To enable AWS WAF, use this annotation:
```yaml
alb.ingress.kubernetes.io/wafv2-acl-arn: arn:aws:wafv2:region:account-id:global/webacl/my-web-acl/1234567890123456
```

For AWS Shield Advanced protection:
```yaml
alb.ingress.kubernetes.io/shield-advanced-protection: "true"
```

### Q24: How can I enable cross-zone load balancing?
**A:** For NLBs, use the annotation:
```yaml
service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
```

For ALBs, cross-zone load balancing is enabled by default.

### Q25: What is the TargetGroupBinding resource and when should I use it?
**A:** The TargetGroupBinding resource allows you to use existing target groups with your Kubernetes Services:
```yaml
apiVersion: elbv2.k8s.aws/v1beta1
kind: TargetGroupBinding
metadata:
  name: my-tgb
  namespace: default
spec:
  serviceRef:
    name: my-service
    port: 80
  targetGroupARN: arn:aws:elasticloadbalancing:region:account-id:targetgroup/my-tg/1234567890123456
```

Use this when you need fine-grained control over target groups or want to integrate with existing load balancers created outside of Kubernetes.

## Troubleshooting

### Q26: Why isn't my load balancer being created?
**A:** There are several common reasons:
1. IAM permissions: The controller needs appropriate permissions to create and manage AWS resources
2. Subnet tags: Subnets must be properly tagged for auto-discovery
3. Security group issues: Security groups might be preventing the controller from creating resources
4. Annotation syntax errors: Check your annotations for any syntax errors
5. Controller logs: Check the controller logs for error messages

Start by checking the controller logs:
```bash
kubectl logs -n kube-system deployment/aws-load-balancer-controller
```

### Q27: Why are my pods not receiving traffic from the load balancer?
**A:** Common causes include:
1. Health check failures: Check if your health checks are correctly configured
2. Security group issues: Ensure security groups allow traffic from the load balancer to the targets
3. Pod readiness: Make sure your pods are passing readiness probes
4. Network configuration: Verify network policies or other network plugins aren't blocking traffic

You can check the target group health in the AWS console or with the AWS CLI:
```bash
aws elbv2 describe-target-health --target-group-arn your-target-group-arn
```

### Q28: What happens if the controller crashes or is unavailable?
**A:** If the controller becomes unavailable, existing AWS resources (load balancers, target groups, etc.) will continue to function normally. However, any changes to Kubernetes resources (new Ingress/Service resources, pod scaling, etc.) won't be reflected in the AWS resources until the controller is available again. This is why it's recommended to deploy the controller with multiple replicas for high availability.

### Q29: How can I debug issues with the controller?
**A:** Use these methods to debug controller issues:
1. Check controller logs:
   ```bash
   kubectl logs -n kube-system deployment/aws-load-balancer-controller
   ```
2. Enable debug logging:
   ```bash
   helm upgrade aws-load-balancer-controller eks/aws-load-balancer-controller -n kube-system --set logLevel=debug
   ```
3. Check events for your Ingress or Service:
   ```bash
   kubectl describe ingress my-ingress
   kubectl describe service my-service
   ```
4. Look at the status of TargetGroupBindings:
   ```bash
   kubectl get targetgroupbindings -A
   ```
5. Check AWS resources in the console or with AWS CLI to see what's been created.

### Q30: How do I adjust the timeout settings on my load balancer?
**A:** For ALBs, use this annotation:
```yaml
alb.ingress.kubernetes.io/load-balancer-attributes: idle_timeout.timeout_seconds=60
```

For NLBs with TCP, use:
```yaml
service.beta.kubernetes.io/aws-load-balancer-target-group-attributes: tcp.idle_timeout.seconds=350
```

## Performance and Scaling

### Q31: Are there any limits to how many Ingress resources can share an ALB using IngressGroups?
**A:** There's no specific limit on the number of Ingress resources that can share an ALB. However, there are AWS service limits to consider:
- ALBs have a limit of 100 rules per load balancer
- Each rule can have up to 5 conditions
- There's a limit of 1000 target groups per region

If you hit these limits, you may need to create additional IngressGroups.

### Q32: What's the performance impact of using IP vs Instance target types?
**A:** 
- **Instance target type**: Traffic goes to the node first, then gets redirected to the pod through kube-proxy. This adds a network hop but can be more efficient for many pods on the same node (fewer target group entries).
- **IP target type**: Traffic goes directly to the pod IP. This reduces latency by eliminating the extra hop, but requires more target group entries (one per pod).

For most applications, the performance difference is minimal.

### Q33: How does the controller handle pod scaling events?
**A:** The controller watches for pod events and updates the target groups accordingly. For instance target type, it only needs to ensure that the node is registered as a target. For IP target type, it needs to register or deregister each pod IP when pods are created or deleted.

In newer versions of the controller, there's a deferral queue for TargetGroupBindings that change rarely, which improves performance during leadership failover by prioritizing target groups with membership changes.

### Q34: How can I optimize my load balancer for high traffic?
**A:** To optimize for high traffic:
1. Use appropriate instance types for your EKS nodes
2. Configure horizontal pod autoscaling (HPA) for your applications
3. Consider using cross-zone load balancing to distribute traffic evenly
4. Optimize health check settings to quickly remove unhealthy targets
5. For NLBs, consider using the UDP protocol for non-HTTP traffic to reduce overhead
6. Implement proper connection draining settings
7. Monitor and adjust based on CloudWatch metrics

## Latest Features and Integration

### Q35: What new features are available in the latest versions of the controller?
**A:** Recent features include:
- AWS VPC IPAM Support for ALBs ("Bring Your Own IP" capability)
- IPv6-only support for ALBs
- Enhanced performance with a deferral queue for TargetGroupBindings
- Multi-cluster TargetGroupBinding support
- Configurable TCP idle timeout for NLBs
- HTTP header modification capabilities
- Support for SageMaker HyperPod clusters
- UDP support over IPv6 via Dualstack NLBs

### Q36: How does the AWS Load Balancer Controller work with other Kubernetes networking options like service meshes?
**A:** The AWS Load Balancer Controller can work alongside service meshes like Istio, Linkerd, or AWS App Mesh. In a typical architecture:
- The AWS Load Balancer Controller manages the external-facing load balancers (ALBs/NLBs)
- The service mesh handles internal service-to-service communication

This gives you the best of both worlds: AWS-native integration for external traffic and advanced service mesh capabilities for internal traffic.

### Q37: Can I use the controller in a multi-cluster or hybrid environment?
**A:** Yes, the controller works well in multi-cluster and hybrid environments:
- For multi-cluster setups, the Multi-Cluster TargetGroupBinding feature allows a single load balancer to route traffic to pods across different clusters.
- For hybrid environments (mixing EC2 and Fargate), you can use IP target type to directly route traffic to pods regardless of where they're running.
- For clusters spanning multiple VPCs, you need to ensure proper connectivity between VPCs (using VPC peering, Transit Gateway, etc.).

### Q38: How do I automate the controller deployment in a CI/CD pipeline?
**A:** To automate deployment in CI/CD:
1. Use infrastructure as code tools (Terraform, CloudFormation, etc.) to create the IAM roles and policies
2. Use Helm in your pipeline to install/upgrade the controller
3. Store the configuration values in a Git repository or parameter store
4. Include tests to verify the controller is operational after deployment
5. Consider using GitOps tools like ArgoCD or Flux for Kubernetes resource management

### Q39: Does the AWS Load Balancer Controller support EKS Auto Mode?
**A:** Yes, with Amazon EKS Auto Mode, the AWS Load Balancer Controller capabilities are included by default - no separate installation is needed. EKS Auto Mode includes integrated pod networking and load balancing capabilities out of the box.

### Q40: What changes do I need to make when migrating from LoadBalancer Services managed by the in-tree provider to the AWS Load Balancer Controller?
**A:** When migrating from the in-tree provider to the AWS Load Balancer Controller:
1. Add the annotation `service.beta.kubernetes.io/aws-load-balancer-type: "external"` to your Service resources
2. If you want to use IP target type, add `service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: "ip"`
3. Recreate your services (deleting and recreating is safer than modifying existing ones)
4. Update any annotations to use the AWS Load Balancer Controller format
5. Consider setting up IngressGroups if you have multiple services that could share an ALB

Remember that attempting to replace existing Network Load Balancers created with the AWS cloud provider load balancer controller can result in multiple Network Load Balancers, which might cause application downtime.
