# Keyword Classifier

## Description

Recognizes the following words via [Edge Impulse](https://www.edgeimpulse.com/) project found [here](https://studio.edgeimpulse.com/studio/242676).

|name | description |
|-|-|
|extivious| ?? |
|lumos| lights up wand|
|colos| launches color game|
|mousike| launches music game|

Service is off by default and must be turned on via mqtt interface

## MQTT API

### DATA

Publishes recognized keywords on `goodwand/ui/controller/keyword` of format:

```json
{
	"header": {
		"type": "UI_KEYWORD",
		"version": 1
    },
    "data": {
        "keyword" : one keyword from above list
    }
}
```

```json
{
	"header": {
		"type": "UI_KEYWORD",
		"version": 1
    },
    "data": {
        "type" : "state",
        "state" : 1

    }
}
```

### COMMAND

Listens on topic `goodwand/ui/controller/keyword/command` for packets of the following format

```json
{
	"header": {
		"type": "UI_KEYWORD",
		"version": 1
    },
    "data": {
        "type" : "state",
        "state" : 1

    }
}
```

```json
{
	"header": {
		"type": "UI_KEYWORD",
		"version": 1
    },
    "data": {
        "type" : "state",
        "state" : 0

    }
}
```

!! not yet implemented vv
```json
{
	"header": {
		"type": "UI_KEYWORD",
		"version": 1
    },
    "data": {
        "type" : "fs",
        "fs" : int between 1-50

    }
}
```

idk if theres a better word than "state" but its the best i got now... - jim


## known bugs

- segmentation fault on ctrl-c
    - not rly sure what to do

## other misc notes
- at fs=10, the model consumes 22% cpu and the python script consumes 15% cpu