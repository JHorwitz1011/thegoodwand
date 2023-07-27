# The Good Wand #

This repository contains all software necessary for implementing the good wand on a Raspberry Pi 0W 2 running Raspberry Pi OS Lite

### Services ###

![system architecture](images/system_architecture.png)

Services connect the technology behind the wand together via MQTT. [Click here for a detailed description of all services, and the MQTT API.](services/README.md)

### Templates ###

Templates provide a Python API that abstracts away the MQTT interface.

### Spells ###

Spells utilize the services to create games. [Click here for a detailed description of all spells](spells/README.md)

### Setup ###

Shell scripts are provided to install dependencies of the project. [Click here for more setup details](setup/README.md)

1. Clone repo
2. cd to setup folder
3. run ./install_all.sh (DO NOT RUN AS SUDO)
4. Monitor for errors

### Contribution guidelines ###

* No pushing directly to master. All changes are to be done on a feature branch and merged in with a PR.


### random other stuff ###

git clone https://x-token-auth:ATCTT3xFfGN0_hPNa5cD3xyTp8eeLd-tIBV5AQhfUNYwk8lHSuL9FN_WlCAQ3yKDfZURT0dOypsdJzHqpRl99A77V6DVTsvLEAUg7a43dwW25FfryWnvSdME6vQDg827UzSqXKFfP9Kvttm6NLqH-wLZLOk_cE4VV5skRE-erkvolAiWpIDNQ5A=F09C70EA@bitbucket.org/fishwandproto/thegoodwand.git

Authorization: Bearer ATCTT3xFfGN0_hPNa5cD3xyTp8eeLd-tIBV5AQhfUNYwk8lHSuL9FN_WlCAQ3yKDfZURT0dOypsdJzHqpRl99A77V6DVTsvLEAUg7a43dwW25FfryWnvSdME6vQDg827UzSqXKFfP9Kvttm6NLqH-wLZLOk_cE4VV5skRE-erkvolAiWpIDNQ5A=F09C70EA

ATCTT3xFfGN0_hPNa5cD3xyTp8eeLd-tIBV5AQhfUNYwk8lHSuL9FN_WlCAQ3yKDfZURT0dOypsdJzHqpRl99A77V6DVTsvLEAUg7a43dwW25FfryWnvSdME6vQDg827UzSqXKFfP9Kvttm6NLqH-wLZLOk_cE4VV5skRE-erkvolAiWpIDNQ5A=F09C70EA
