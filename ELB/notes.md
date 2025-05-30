# Notes

- If no annotation is given and the type is selected as 'Load Balancer' then the default ELB will be created as 'Classic Load Balancer'
```yaml
spec:
    type: LoadBalancer
```


- If we need to create a 'Network Load balancer' then we need to give and annotation as 'nlb'.

```yaml
annotations:
    service.beta.kuberntes.io/aws-load-balancer-type: nlb
```

- ALB
    - Path based routing.
    - Host based routing.
    - Routing based on the fields of the request(HTTP Headers, HTTP Methods, Query Parameters and Source IP address).
    - Redirecting requests from one URL to another.
    - Return a custom HTTP response.
    - Registering Lambda functions as targets.
    - Load balancer authentication to users.
    - Support for containerized applications(ECS)


- ALB-IC
    - ALB-IC triggers the creatio of the ALB load balancer controller and the necessary supporting AWS resources, wheneven and Ingress resouce is created on the cluster with the `kubernetes.io/ingress.class:alb` annotation.
    - Two traffic modes : Instance and IP

- ALBIC vs AWS Load Balancer Controller
    - ALBIC
        - Only supports AWS Application Load Balancer
        - No support after 1.22
    - AWS LB Controller
        - Supports both AWS Application and Network Load Balancers
        - K8S Ingress Resource - AWS Application Load Balancer
        - K8S Service Resource - AWS Network Load Balancer


- Instance Mode:
    - Register nodes within the cluster as the targets
    - Traffic is reouted to NodePort for the service and then to the pods
    - This is the default traffic mode.
    - Also specify using the annotation: `alb.ingress.kubernetes.io/target-type: instance`

- IP Mode:
    - Register the pods as the targets
    - Traffic reaching the ALB is directly route to pods for the service.
    - Annotation has to be specified as ip : `alb.ingress.kubernetes.io/target-type: ip`


- Process Steps
    - 1. Controller watch for the Ingress events from the API server and if it finds the Ingress resources, it will create the AWS resources.
    - 2. Create the Application Load Balancer for the new Ingress resource.
    - 3. Create the Target Group in AWS for each unique service defined in the manifest.
    - 4. Create the Listeners for the Application Load Balancers
    - 5. Create the rules based on the context.
    - 6. Deleting the Ingress Manifest will delete all the resources created on AWS.


- Resources created and the order of creation
    - K8S
        - ALB controller is installed on kube-system namespace
        - Create a service account
            - IAM role arn will be annotated in the load balancer service account
            - SA is linked to the deployment(pods)
            - This gets the ability to create the AWS resources
        - Deloyment will be created
            - aws load balancer tls certificate
            - aws load balancer webhook cluster IP service
        - Admin or the app team will deploy the Ingress manifest file
        - Ingress resource is created once the Ingress object is created
    - AWS
        - IAM Policy
        - IAM Role
        - AWS ELB(AWS ApELB changesplication Load Balancer Controller)



- Pre-requisite
    - Create IAM Policy and note the ARN
    - Create the role using the policy
    - Create a SA with the role ARN as annotation
    - Install AWS load balancer controller using HELM
    - Create an IngressClass if using multiple Ingress controllers
    - Create an Ingress file to create the resources on AWS