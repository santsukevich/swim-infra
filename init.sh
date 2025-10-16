#/bin/bash
SECRETNAMES=./secrets/names.txt
SECRETDIR=./secrets

# Set variables from .env file
export $(grep -v '^#' .env | xargs -d '\n')

# Check secrets
# Read the input file line by line using a for loop
IFS=$'\n' # set the Internal Field Separator to newline
for SECRETNAME in $(cat "$SECRETNAMES")
do
   if [ ! -f "$SECRETDIR/$SECRETNAME" ];
   then
      echo "$SECRETNAME file not found"
      exit 1
   fi
done

# Check vars
if [ -z ${APP_DOMAIN+x} ] || [ -z ${APP_DOMAIN} ] ; then
    echo "APP_DOMAIN is not set or empty"
    exit 1
fi

# Create network if it doesn't exist
docker network inspect traefik-public >/dev/null 2>&1 || \
    docker network create --scope=swarm --attachable --driver overlay --subnet 10.0.16.0/20 traefik-public

# Create dir for letsencrypt if it doesn't exist
mkdir -p letsencrypt

# Substitute variables in stack files
docker stack config --compose-file ./traefik-stack.yml >./traefik-stack.prod.yml
docker stack config --compose-file ./portainer-stack.yml >./portainer-stack.prod.yml
docker stack config --compose-file ./minio-stack.yml >./minio-stack.prod.yml
docker stack config --compose-file ./mongo-stack.yml >./mongo-stack.prod.yml
docker stack config --compose-file ./redis-stack.yml >./redis-stack.prod.yml
docker stack config --compose-file ./postgres-stack.yml >./postgres-stack.prod.yml
docker stack config --compose-file ./monitoring-stack.yml >./monitoring-stack.prod.yml
docker stack config --compose-file ./backup-stack.yml >./backup-stack.prod.yml
docker stack config --compose-file ./app-stack.yml >./app-stack.prod.yml

# Deploy stacks
docker stack deploy -c ./traefik-stack.prod.yml traefik-stack
docker stack deploy -c ./portainer-stack.prod.yml portainer-stack
docker stack deploy -c ./minio-stack.prod.yml minio-stack
docker stack deploy -c ./mongo-stack.prod.yml mongo-stack
docker stack deploy -c ./redis-stack.prod.yml redis-stack
docker stack deploy -c ./postgres-stack.prod.yml postgres-stack
docker stack deploy -c ./monitoring-stack.prod.yml monitoring-stack
docker stack deploy -c ./backup-stack.prod.yml backup-stack
docker stack deploy -c ./app-stack.prod.yml app-stack
