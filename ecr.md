# ECR REPO CREATION AND REPLICATION

```bash
aws ecr put-replication-configuration --region us-west-2 --replication-configuration '{
  "rules": [
    {
      "destinations": [
        {
          "region": "us-east-1",
          "registryId": "<account_number>"
        },
        {
          "region": "us-east-2",
          "registryId": "<account_number>"
        }
      ]
    }
  ]
}'

```


```bash
aws ecr create-repository --repository-name ecrtestapp --region us-west-2
```

```bash
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account_number>.dkr.ecr.us-west-2.amazonaws.com/ecrtestapp
```

```bash
cat > ecr-open-policy.json <<EOF
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Sid": "AllowPushPull",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": [
        "ecr:BatchGetImage",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:CompleteLayerUpload",
        "ecr:DescribeImages",
        "ecr:DescribeRepositories",
        "ecr:InitiateLayerUpload",
        "ecr:PutImage",
        "ecr:UploadLayerPart"
      ]
    }
  ]
}
EOF

aws ecr set-repository-policy \
  --repository-name ecrtestapp \
  --region us-west-2 \
  --policy-text file://ecr-open-policy.json


```


```py
#!/usr/bin/env python3
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Testing for ECR cross region replication"}
```

```txt
fastapi
uvicorn
```

```dockerfile
FROM python:3.12-bullseye

RUN pip install --upgrade pip

RUN adduser worker

USER worker

WORKDIR /home/worker

ENV PATH="/home/worker/.local/bin:${PATH}"

COPY ./requirements.txt /home/worker/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /home/worker/requirements.txt

COPY ./main.py /home/worker/main.py

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
```


```bash
docker build -t ecrtestapp:0.0.1 .

docker run -p 8080:8080 --rm ecrtestapp:0.0.1

aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account_number>.dkr.ecr.us-west-2.amazonaws.com/ecrtestapp

docker tag ecrtestapp:0.0.1 <account_number>.dkr.ecr.us-west-2.amazonaws.com/ecrtestapp:0.0.1

docker images

docker push <account_number>.dkr.ecr.us-west-2.amazonaws.com/ecrtestapp:0.0.1
```


























