# KVS-REST-API-EXTREME-EDITION

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

- Think of other edge cases before due
- GET
  - search
    - localhost:8080/keyValue-store/search/target_key
    - true
    - false
  - getValue
    - localhost:8080/keyValue-store/getValue/?item=target_key
    - key exists
    - key doesn't exist
- Put
  - localhost:8080/keyValue-store/<key_name>
  - Body: x-www-form-urlencoded
    - key: val
    - value: intended_value
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

  - docker stop $(docker ps -aq)
  - docker rm $(docker ps -aq)

- Make sure docker network is cleared
  - docker network rm $(docker network ls -aq)

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
python3 hw3_tests.py
after the test:
docker kill $(docker ps -aq)
docker rm$(docker ps -aq)
