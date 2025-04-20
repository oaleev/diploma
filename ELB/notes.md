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
    - Path based routing
    - Host based routing
    - Routing based on the fields of the request(HTTP Headers, HTTP Methods, Query Parameters and Source IP address)
    - Redirecting requests from one URL to another
    - Return a custom HTTP response
    - Registering Lambda functions as targets