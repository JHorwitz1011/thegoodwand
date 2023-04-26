**Setup a new Wand**
RPI Installer *LEGACY LITE*
Add "enable_uart=1" to the bottom of config.txt to enable Uart console from USB. Baud 115200 

**First: Install and configure git** 
sudo apt update 
sudo apt install git
git config --global user.name "Your Name" 
git config --global user.email "youremail@yourdomain.com"


**Second** 
Get the install scripts clone this library with git clone 
git clone --recurse-submodules https://x-token-auth:ATCTT3xFfGN0P5ueKcXaJ7IGf1oQpMmH8zYJsaT3AzJu-8TshaCggq_GusWUxf4UAB2e-si_khBLs8wPeI762CnI9hxiHPRs6N2-bzS60ZSUvyDJpnjgfocwYXl9BhO3hlu0l4BLt48AYpG2EdYTS1MbvfFALuxWnT-tRQPgdg0zYPKhs0558ZE=8B58877B@bitbucket.org/fishwandproto/wandsetup.git

git submodule update --init 

**Third: The install!**
Run the install script. DO NOT use SUDO all commands that need sudo are called with sudo in the script. 
./wandsetup/install_all.sh

**Forth: UPDATE SYSTEM PATH**
Add templates to path by
edit ~/.bashrc and add at the bottom

#Add directory to path
export PATH="~/templates:$PATH"

Reboot



**Fifth**
Run vlc.sh
OPTIONAL - ONLY if you need it - Run EdgeImpulse


**GIT SUBMODULES**

Audio Files
https://x-token-auth:ATCTT3xFfGN0pfR2mnnTjRT3uw40glSRZNUrYmo86VaknmGDGtNtbOR_wEVRzMl_d4q8Cd4jtmS2HS0WqMT8yOMG-8tnYNmAhukYgFAHUI0Gz3el9DtjQxD1EGTYwN9IZrClvJUH6FRxZpZfqmCEYAdhbDFL8rAoT33vw4QRljRfOhGsMwlL794=90EECB6D@bitbucket.org/fishwandproto/audio.git

IMU service
https://x-token-auth:2etLITtr00sAO0g4pAhe@bitbucket.org/fishwandproto/accel.git

LED service
https://x-token-auth:HbzF6APAo4UkbYJv3wsF@bitbucket.org/fishwandproto/lightarch.git

NFC service 
https://x-token-auth:0vLyzZAb7sz3g9L3aBiS@bitbucket.org/fishwandproto/mfr522_nfc.git

Haptic Feedback Service
https://x-token-auth:PvsfPcpmLd3wzyJuMoiW@bitbucket.org/fishwandproto/hapt-getic_feedback.git

UV LED service
https://x-token-auth:ATCTT3xFfGN0aWr015CelD7TSbOxKA0IMfR_zlAgF9Na4q_U_V0PN-A1G4Lnn47reNW1_xEecQyShwk5kd-fhzOtIx4HPZKi4Tk_cmCutW79x0H8GHhWiMeFkqlpLJdNvvUS9brO3nUt0QQxBv7qTNcn3oJiw3F7kKa7yZNZ_tLlVvU_bwr7tZc=57A127FA@bitbucket.org/fishwandproto/uvlight.git

Button service
https://x-token-auth:ATCTT3xFfGN0675ohcSR9os1nMicCGe16poookpn-vO5niiB-vx6Vfysv9mXfvxilcJLva8EJU0HSfzL18sLuv9F4CtGYM8LPPp3IgIWNbiR6_9TNuYDz1GXRq1Anr41D8G4qlz431YzegaFUI1bun4tS6d8_gcJHEDGVRWfeFD9pKYI71e9VUQ=F9B28C51@bitbucket.org/fishwandproto/button.git

Battery Charger
https://x-token-auth:1X6VkgHsknSXfbzEmDoW@bitbucket.org/fishwandproto/charger_bq24296m.git

Backend
https://x-token-auth:ATCTT3xFfGN0GsYH4kYng69TPYIbU0_XudZfcYQizMCnxtQ16Fzuwk7lUPHGUTQe8kX18v0TpRgeqLXt3qTu1CcTKbW41hLowH9w-_gavJclvStiPL3mI1U-aqiZ1Ek4mSs8mpKz7v5WQALp0Aae1jET4X5FGkL1XakGrkvEZe9JDUDl6Wx-wcM=62448804@bitbucket.org/fishwandproto/backend.git

Spells
https://x-token-auth:ATCTT3xFfGN0ll8EgHbgi4nSqtludcWS2RLMCmWEOBuQNVSC8IGYoQVy8Q2H-vltz_WNiBeJ3E2HeY5TCYaXR3FqUmbNJx-0vaOeV0tuDKoKU1D8e9Af1aisWdAhc7QAY0Y7lrFdq4ieQDuwwSEySoNm8U5vqtD3gNYaXWKe_H40wSegJ-f5luk=4EB9A742@bitbucket.org/fishwandproto/spells.git

Conductor
https://x-token-auth:ATCTT3xFfGN02QkYuvkmxnFWVM_iF2jefV72-bVC4Tv3HvMjJ4QuYuM-FU0-iN0T-G_oZW7o2uKxJLAf-TKFtyZt2oSGbXPAiJ22h7nJTclybKeM24UNvui-H9nw19FU8DfJRAJaP4YTO2RxLiHPjbohOJeS6advrvmYnsPYzHHSugAkKskOCV0=3DEC186B@bitbucket.org/fishwandproto/conductor.git