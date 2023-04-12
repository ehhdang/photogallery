echo "Starting to deploy docker image.."
DOCKER_IMAGE=acatnamedsummer/photogalleryflaskapp:latest
docker pull $DOCKER_IMAGE
docker rm -f $(docker ps -aq)
docker run --name mariadbtest -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD -e MYSQL_DATABASE=$MYSQL_DATABASE -p 3306:3306  -d mariadb
docker run -d -p 5000:5000 --env-file .env $DOCKER_IMAGE