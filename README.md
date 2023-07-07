# About
This is my python execrise with selenium and paramiko libraries. 
With this execrice, I learned some knowledge that like:

1. Build the docker image of selenium for arm64 architecture.
2. Utilize the selenium library to imitate human behaviors and scraping the infomation that I need from multiple websites.
3. Store the extracted infomation to json files.
4. Upload the json files to sftp by utilizing paramiko library.

# Prerequisite

1. build a selenium image for arm64 environment

   `docker build arm64 -t selenium/arm64`

2. bring up docker

   `docker-compose up -d`

# Add config.py to each project

1. project/evs/config.py
2. project/stations/config.py

```python
sftp = dict(
    hostname       = "",
    username       = "",
    password       = "",
    port           = 22,
    remoteFilePath = "./",
)
```

# Run

1. go into docker container

   `docker exec -it selenium-chrome bash`

3. run the project with different sources like:

   `python /project/evs/scrappy-8891.py`


   
