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


- Instance Mode:
    - Register nodes within the cluster as the targets
    - Traffic is reouted to NodePort for the service and then to the pods
    - This is the default traffic mode.
    - Also specify using the annotation: `alb.ingress.kubernetes.io/target-type: instance`

- IP Mode:
    - Register the pods as the targets
    - Traffic reaching the ALB is directly route to pods for the service.
    - Annotation has to be specified as ip : `alb.ingress.kubernetes.io/target-type: ip`