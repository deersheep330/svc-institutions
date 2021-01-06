# Institutions Service

#### run without docker
```
python main.py
```

#### start a docker service
```
docker-compose build --no-cache
docker-compose push
docker stack deploy -c docker-compose.yml institutions
```

##### fast test docker-compose
```

```