[<- back](../README.md)

Click the embedded link for more details on each service (MQTT packet format, individual details on how each service works, etc).

| Service | Description | Publish Topics | Subscribe Topics |
| :-: | :-: | - | - |
| [IMU](imu/README.md) | Handles communication between LSM6DSOX | `goodwand/ui/controller/gesture` <br /> `goodwand/ui/controller/gesture/data` | `goodwand/ui/controller/gesture/command`|
| [Haptic Feedback](haptic_feedback/README.md) | vibration on the wand | n/a | n/a|
| [Button](button/README.md) | interfaces between push button | n/a | n/a|
| [Keyword Recognition](keyword_classifier/README.md) | voice recognition  | n/a | n/a|
| [Gesture Recognition](gesture_classifier/README.md) | voice recognition  | n/a | n/a|
| [NFC](nfc/README.md) | polls nfc chip to read nfc tags  | n/a | n/a|
| [UV Light](uvlight/README.md) | turns on/off the uv tip  | n/a | n/a|
| [Conductor](conductor/README.md) | handles state machine, idle animations, and experiences  | n/a | n/a|