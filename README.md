# Inspiration providers
https://blog.antosubash.com/posts/part-2-setup-docker-swarm-with-traefik-and-portainer
https://www.portainer.io/blog/monitoring-a-swarm-cluster-with-prometheus-and-grafana
https://geek-cookbook.funkypenguin.co.nz/recipes/minio/
https://github.com/stefanprodan/swarmprom/
https://github.com/persunde/swarmprom-improved/
https://github.com/skl256/grafana_stack_for_docker/tree/main

# Regards
Many thanks to @stefanprodan and @persunde for `swarmprom` and `swarmprom-improved`. This project is for sure built on the basis of their work.

# Project's limits
This example runs on Docker Swarm without any persistent storage.
You MUST rework it a lot if you are using Ceph or GlusterFS. At least you can get rid of my excessive usage of `config`s.
Redis, Postgres, Mongo replicas are manually assigned to cluster nodes. Each replica has it's own service in corresponding `*-stack.yml` file. This is not cool.

# Prereqs
1. Up and ready to go Docker Swarm cluster
2. Docker Swarm Nodes labeled as:
```
$ docker node update --label-add "type=app"
$ docker node update --label-add "type=backup"
$ docker node update --label-add "type=minio"
$ docker node update --label-add "mongo.replica=1"
$ docker node update --label-add "mongo.replica=2"
$ docker node update --label-add "mongo.replica=3"
$ docker node update --label-add "redis.replica=1"
$ docker node update --label-add "redis.replica=2"
$ docker node update --label-add "redis.replica=3"
$ docker node update --label-add "postgres.replica=1"
$ docker node update --label-add "postgres.replica=2"
$ docker node update --label-add "postgres.replica=3"
```
3. Correct .env file, check `/.env.example`
4. Correct secrets, check `/secrets/README.md`
5. Carefully proofread and adjusted `*-stack.yml` files

# Operational notes
All stacks use an external overlay network `traefik-public` created by `init.sh` script. Stacks can't be brought up without this network.
Traefik, Portainer, Monitoring, Minio, Redis, Mongo, and Backup stacks are updated via `git pull` and `init.sh`. You should do this in your CI/CD pipeline.
> After each deployment, verify that changes were applied correctly.

# Stacks
## Traefik
`traefik-stack.yml`
1. Traefik is deployed on the Swarm Manager node
2. Entrypoints `web` (80) and `websecure` (443) are configured
3. HTTP -> HTTPS redirect is configured
4. Basic Auth

## Portainer
`portainer-stack.yml`
1. Portainer Server is deployed on the Swarm Manager
2. Portainer Agent is deployed on all nodes
3. Routing via Traefik

## Monitoring
`monitoring-stack.yml`
1. Grafana is deployed on the node with label `type==backup`
2. Prometheus is deployed on the node with label `type==backup`
3. cadvisor is deployed on all nodes
4. node-exporter is deployed on all nodes
5. dockerd-exporter is deployed on all nodes
6. promtail is deployed on all nodes
7. alertmanager is deployed on the node with label `type==backup`
8. Loki is deployed on the node with label `type==backup`
9. pushgateway is deployed on the node with label `type==backup`
10. Routing for Grafana, Prometheus, Alertmanager via Traefik
11. Basic Auth for Prometheus and Alertmanager
12. Data for Grafana, Prometheus, Alertmanager, and Loki are stored on the machine with label `type==backup` at `/home/monitoring/`
I used bind-mount to get around my test setup limitations. Adjust at your needs.

## App
`app-stack.yml`
1. All services are deployed on nodes with label `type==app`
2. Example app connects to storages, performs ping-like check and returns status message, check `/app`
3. Routing via Traefik

## Minio
1. Replicas are deployed on nodes with label `type==minio`
2. Nodes are prepped; disks for Minio are partitioned and added to `fstab`
3. Routing for Minio and Minio-Console via Traefik
4. Don't forget to check the volumes section for Minio; all used disks must be mounted into the container

## Redis
1. Replicas are created as separate services and deployed on nodes with label `redis.replica == X`, where X is the replica number
2. Redis Sentinel is used for HA; Sentinel replicas are created as separate services and deployed the same way as Redis replicas
3. For clients that don't support Redis Sentinel, a workaround based on HAProxy is deployed to poll Redis Sentinel replicas

## Mongo
1. Replicas are created as separate services and deployed on nodes with label `mongo.replica == X`, where X is the replica number

## Postgres
1. Replicas are created as separate services and deployed on nodes with label `postgres.replica == X`, where X is the replica number

## Backup
1. The `crazymax/swarm-cronjob` image is used as the scheduler and is deployed on the Swarm Manager
2. Backups of Redis and Mongo are saved on the machine with label `type==backup` at `/home/backup/`
I used bind-mount to get around my test setup limitations. Adjust at your needs.