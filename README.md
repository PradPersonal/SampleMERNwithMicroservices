# Sample MERN with Microservices



For `helloService`, create `.env` file with the content:
```bash
PORT=3001
```

For `profileService`, create `.env` file with the content:
```bash
PORT=3002
MONGO_URL="specifyYourMongoURLHereWithDatabaseNameInTheEnd"
```

Finally install packages in both the services by running the command `npm install`.

<br/>
For frontend, you have to install and start the frontend server:

```bash
cd frontend
npm install
npm start
```

Note: This will run the frontend in the development server. To run in production, build the application by running the command `npm run build`



## Create repository (if not exists) and authenticate Docker to ECR:

REPO=frontend
aws ecr describe-repositories --repository-names $REPO --region $AWS_REGION >/dev/null 2>&1 || \
  aws ecr create-repository --repository-name $REPO --region $AWS_REGION

aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

## Build, tag, push (repeat per service; adjust Dockerfile path and REPO):
### Frontend
REPO=frontend
docker build -t $REPO -f /workspaces/SampleMERNwithMicroservices/frontend/Dockerfile /workspaces/SampleMERNwithMicroservices/frontend
docker tag $REPO:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO}:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO}:latest

### Hello service
REPO=hello-service
docker build -t $REPO -f /workspaces/SampleMERNwithMicroservices/backend/helloService/Dockerfile /workspaces/SampleMERNwithMicroservices/backend/helloService
docker tag $REPO:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO}:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO}:latest

### Profile service
REPO=profile-service
docker build -t $REPO -f /workspaces/SampleMERNwithMicroservices/backend/profileService/Dockerfile /workspaces/SampleMERNwithMicroservices/backend/profileService
docker tag $REPO:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO}:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO}:latest
