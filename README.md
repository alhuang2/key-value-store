# KVS-REST-DISTRIBUTED-SYSTEM

### How to run

```
docker-compose up
```

### How to inspect container

```
docker ps
```

copy down the container id

```
docker exec -it container_id sh
```

### API

API requirements
1. Every API requires x-www-form-urlencoded format
2. empty "payload = {}" in data field

- GET
  - /<key>
  - /search/<key>
    - localhost:8080/keyValue-store/search/<key>
    - true
    - false
- Put
  - localhost:8080/keyValue-store/<key_name>
  - Body: x-www-form-urlencoded
    - key: val
    - value: intended_value
    - paylaod = {}
  - key too long/short
  - value too long
  - key valid but already exists
  - key valid and didn't exist
  - key empty
- Delete
  - localhost:8080/keyValue-store/<key_name>
  - key not included in url
  - key doesn't exist
  - key exists

### Environment variables

- Provided in .env file
- https://docs.docker.com/compose/environment-variables/#set-environment-variables-with-docker-compose-run

### How to run testscript (PLEASE BE IN SUDO)

- Make sure containers are cleared by running:

  - docker stop \$(docker ps -aq)
  - docker rm \$(docker ps -aq)

- Make sure docker network is cleared

  - docker network prune

- Run subnetwork

  - sudo docker network create --subnet=10.0.0.0/16 mynet
  - sudo docker network create --subnet=10.0.0.0/16 ap-sharding-system

- Build!

  - docker build -t testing:latest .

- Run testscript
  - python3 <test_script_name>.py

### How to debug server

- docker exec -it a9d9d9cbe074 sh

Running the tests:
docker build -t testing:latest .
python3 test_script.py
after the test:
docker kill $(docker ps -aq)
docker rm$(docker ps -aq)
