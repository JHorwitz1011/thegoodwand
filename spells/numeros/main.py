import pyttsx3


# Initialize the TTS engine
speaker = pyttsx3.init()
# Set properties (optional)
speaker.setProperty('rate', 150)  # Speed of speech (words per minute)
speaker.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
voices = speaker.getProperty('voices')
for voice in voices:
    speaker.setProperty('voice', voice)
    # Text to be converted to speech
    text = "Cheetos!"
    # Convert text to speech and play it
    speaker.say(text)
    # Wait for the speech to finish
    speaker.runAndWait()