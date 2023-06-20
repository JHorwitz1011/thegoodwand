# Lights Service

listens for packets on topics:

```
goodwand/ui/view/lightbar
goodwand/ui/view/main_led
```

## LIGHTBAR API

Send the following packets on `goodwand/ui/view/main_led`

### Solid Lightbar Control

To set the entire lightbar to one color:

```json
{
    "header": {
        "type": "UI_LIGHTBAR",
        "version": 1,
    },
    "data": {
        "format": "solid",
        "color": 0x00FF00
    }
}
```

### Raw Lightbar Control

for raw control over the LEDs:

```json
{
    "header": {
        "type": "UI_LIGHTBAR",
        "version": 1,
    },
    "data": {
        "format": "raw",
        "raw": [0xFFFFFF, 0xFF0000, 0xFFFFFF, 0xFF0000, 0xFFFFFF, 0xFF0000, 0xFFFFFF, 0xFFFFFF, 0xFF0000, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0x00FF00, 0x00FF00, 0x00FF00, 0x00FF00]
    }
}
```

### Heartbeat Lightbar Control

To set the entire lightbar to heartbeat:

```json
{
    "header": {
        "type": "UI_LIGHTBAR",
        "version": 1,
    },
    "data": {
        "format": "heartbeat",
        "color": 0x00FF00,
        "min_brightness": 0, (uint8_t)
        "max_brightness": 255, (uint8_t)
        "ramp_time": 500000,
        "delay_time": 500000
    }
}
```

### Fire Lightbar Control

To set the entire lightbar to flames:

```json
{
    "header": {
        "type": "UI_LIGHTBAR",
        "version": 1,
    },
    "data": {
        "format": "fire",
        "color": 0x00FF00
    }
}
```

### System Default CSV

To play a system default animation, "animation" must be a valid name of default system animations of format `___.csv` in `thegoodwand/services/lights/assets`:

```json
{
    "header": {
        "type": "UI_LIGHTBAR",
        "version": 1,
    },
    "data": {
        "format": "animation",
        "animation": "no_failed"
    }
}
```

### Custom CSV

To play a custom animation, "animation" can also be a valid filepath pointing to a file of format `___.csv`:

```json
{
    "header": {
        "type": "UI_LIGHTBAR",
        "version": 1,
    },
    "data": {
        "format": "animation",
        "animation": "thegoodwand/spells/pooftos/assets/poof.csv"
    }
}
```

### Clear Lightbar

To erase current lightbar format and turn off all lightbar LEDs:

```json
{
    "header": {
        "type": "UI_LIGHTBAR",
        "version": 1,
    },
    "data": {
        "format": "none",
    }
}
```

## BUTTON LED API

Send the following packets on `goodwand/ui/view/main_led`

### Clear Button

To erase current button format and turn off the button LED:

```json
{
    "header": {
        "type": "UI_MAINLED",
        "version": 1,
    },
    "data": {
        "format": "none",
    }
}
```

### Solid Button LED Control

To set the button led to one color:

```json
{
    "header": {
        "type": "UI_MAINLED",
        "version": 1,
    },
    "data": {
        "format": "solid",
        "color": 0x00FF00
    }
}
```

### Heartbeat Button LED Control

To set the button led to heartbeat:

```json
{
    "header": {
        "type": "UI_MAINLED",
        "version": 1,
    },
    "data": {
        "format": "heartbeat",
        "color": 0x00FF00
    }
}
```

## Color Spaces (optional)

Every packet can have an optional field `color_space` appended inside the `data` dictionary of a light service packet. `color_spaces` modifies how the `color` field is interpreted. If `color_space` is not present, the service defaults to the `rgb` color space.

Valid color spaces are as follows:

| Name | Description |
| - | - |
`rgb` | Red, Green, Blue color space of format `0xRRGGBB`
`hsv` | Hue, Saturation, Value color space of format `0xHHSSVV`