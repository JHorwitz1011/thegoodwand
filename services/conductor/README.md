# Conductor #


#Setup#
Add to the supervisorctl damons list by creating a file /etc/supervisor/conf.d/conductor.conf:
[program:conductor]
command=python3 -u TGWconductor.py
directory=home/pi/conductor
autostart=true
autorestart=true
priority=50
user=root

Starts and stops applications on the wand.

* only 1 app runs at a time
* upon scanning NFC, json file will appear on topic [goodwand/ui/controller/nfc](https://docs.google.com/document/d/1EQ_fzZ6YO6zBUwkgNV-5BrYl-nJrFWuGkKr-3ds7GKU/edit#) in form of:

```json
{
    header: {
        type: "UI_NFC",
        version: 1
    },
    card_data: {
    uuid : UUID,
    records:[
        {type: RECORD_TYPE,  data: RECORD_DATA},
        {type: RECORD_TYPE,  data: RECORD_DATA}
    ]
}
```

If the current packets have a record of form
```
Content-Type: tgw/[valid_game_name]
data: {
    
}
```

* Quick summary
* Version
* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

### How do I get set up? ###

* Summary of set up
* Configuration
* Dependencies
* Database configuration
* How to run tests
* Deployment instructions

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact