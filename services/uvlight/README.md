# UV Service #

packets published to /goodwand/ui/view/uv

To run automatically, see daemons.sh in [initializeboard](https://bitbucket.org/fishwandproto/initializeboard/src/master/)

packets formatted as follows

```json
{
	"header": {
			"type": "UI_UV",
			"version": 1
	}
	"data": {
		"state": "on" or "off"
		"brightness": 0-100%
	}
}
```
