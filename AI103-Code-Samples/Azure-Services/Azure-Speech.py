# SLIDE 69
# ============================================================
# AZURE AI SPEECH - CONNECT TO THE SPEECH SERVICE
# Creates a Speech Translation configuration for Azure AI Speech using either an endpoint or a region.
# ============================================================

import azure.cognitiveservices.speech as speech_sdk

# CONNECT USING A FOUNDRY ENDPOINT
translation_cfg = speech_sdk.translation.SpeechTranslationConfig(
    subscription="FOUNDRY_KEY",
    endpoint="FOUNDRY_ENDPOINT"
)

# OR CONNECT USING AN AZURE REGION
translation_cfg = speech_sdk.translation.SpeechTranslationConfig(
    subscription="FOUNDRY_KEY",
    region="FOUNDRY_REGION"
)



# SLIDE 69
# ============================================================
# AZURE AI SPEECH - TRANSCRIBE AUDIO
# Converts speech in an audio file to text.
# ============================================================

from pathlib import Path

# Get the audio file
file_path = Path("speech.mp3")
audio_file = open(file_path, "rb")

# TRANSCRIBE USING MODEL
transcription = client.audio.transcriptions.create(
    model=YOUR_MODEL_DEPLOYMENT,
    file=audio_file,
    response_format="text"
)

print(transcription)

# TRANSCRIBE USING SPEECH SDK
# Create a speech recognizer
speech_recognizer = speech_sdk.SpeechRecognizer(
    speech_config=speech_config,
    audio_config=speech_sdk.audio.AudioConfig(
        filename="audio.wav"
    )
)

# Transcribe the audio
result = speech_recognizer.recognize_once_async().get()

# Display the recognized text
print(result.text)



# SLIDE 69
# ============================================================
# AZURE AI SPEECH - SPEECH SYNTHESIS
# Converts text into speech and saves the generated audio.
# ============================================================

from pathlib import Path

# Path for audio output file
speech_file_path = Path("output_speech.wav")

# Generate speech and save to file
with client.audio.speech.with_streaming_response.create(
    model=YOUR_MODEL_DEPLOYMENT,
    voice="alloy",
    input="This speech was AI-generated!",
    instructions="Speak in an upbeat, excited tone."
) as response:
    response.stream_to_file(speech_file_path)

print(f"Speech generated and saved to {speech_file_path}")

# SPEECH SYNTHESIS USING THE SPEECH SDK
# Create SpeechConfig using endpoint and key
speech_config = speech_sdk.SpeechConfig(
    subscription="YOUR_FOUNDRY_KEY",
    endpoint="YOUR_FOUNDRY_ENDPOINT"
)

# Audio output configuration (Defaults to the system speaker)
audio_config = speech_sdk.audio.AudioOutputConfig(
    use_default_speaker=True
)

# Create a speech synthesizer
speech_synthesizer = speech_sdk.SpeechSynthesizer(
    speech_config=speech_config,
    audio_config=audio_config
)

# Text to synthesize
text = "My voice is my password!"

# Convert text to speech
speech_synthesis_result = (
    speech_synthesizer.speak_text_async(text).get()
)



# SLIDE 69
# ==========================================================
# AZURE AI SPEECH - SSML (SPEECH SYNTHESIS MARKUP LANGUAGE)
# ==========================================================

# <speak version="1.0"
#        xmlns="http://www.w3.org/2001/10/synthesis"
#        xmlns:mstts="https://www.w3.org/2001/mstts"
#        xml:lang="en-US">
#     <!-- Voice 1: Cheerful speaking style -->
#     <voice name="en-US-AriaNeural">
#         <mstts:express-as style="cheerful">
#             I say tomato
#         </mstts:express-as>
#     </voice>
#     <!-- Voice 2: Custom pronunciation -->
#     <voice name="en-US-GuyNeural">
#         I say
#         <phoneme alphabet="sapi" ph="t ao m ae t ow">
#             tomato
#         </phoneme>.
#         <break strength="weak"/>
#         Lets call the whole thing off!
#     </voice>
# </speak>



# SLIDE 69
# ============================================================
# AZURE AI SPEECH - TRANSLATE SPEECH TO TEXT
# Translates spoken language from a microphone into one or more target languages.
# ============================================================

# Configure source and target languages
translation_cfg.speech_recognition_language = "en-US"

translation_cfg.add_target_language("fr")
translation_cfg.add_target_language("ja")

print(
    "Ready to translate from",
    translation_cfg.speech_recognition_language
)

# CONFIGURE AUDIO INPUT
audio_cfg = speech_sdk.AudioConfig(
    use_default_microphone=True
)

# CREATE A TRANSLATION RECOGNIZER
translator = speech_sdk.translation.TranslationRecognizer(
    translation_config=translation_cfg,
    audio_config=audio_cfg
)

# CAPTURE SPEECH AND TRANSLATE
print("Speak now...")

translation_results = (
    translator.recognize_once_async().get()
)

print(
    f"Translating '{translation_results.text}'"
)

# DISPLAY TRANSLATIONS
translations = translation_results.translations

for translation_language in translations:

    print(
        f"{translation_language}: "
        f"'{translations[translation_language]}'"
    )

# Example Output:
# Translating 'Hello everyone'
# fr: 'Bonjour tout le monde'
# ja: 'こんにちは皆さん'



# SLIDE 69
# ============================================================
# AZURE AI SPEECH - TRANSLATE SPEECH TO SPEECH
# Translates spoken language into one or more target languages and speaks the translated results aloud.
# ============================================================

# Configure source and target languages
translation_cfg.speech_recognition_language = "en-US"

translation_cfg.add_target_language("fr")
translation_cfg.add_target_language("ja")

print(
    "Ready to translate from",
    translation_cfg.speech_recognition_language
)

# CONFIGURE AUDIO INPUT
audio_cfg = speech_sdk.AudioConfig(
    use_default_microphone=True
)

# CONFIGURE SPEECH SYNTHESIS
speech_cfg = speech_sdk.SpeechConfig(
    subscription="FOUNDRY_KEY",
    endpoint="FOUNDRY_ENDPOINT"
)

audio_out_cfg = speech_sdk.audio.AudioOutputConfig(
    use_default_speaker=True
)

# Voices used for translated speech
voices = {
    "fr": "fr-FR-HenriNeural",
    "ja": "ja-JP-NanamiNeural"
}

# CAPTURE SPEECH AND TRANSLATE
translator = speech_sdk.translation.TranslationRecognizer(
    translation_config=translation_cfg,
    audio_config=audio_cfg
)

print("Speak now...")

translation_results = (
    translator.recognize_once_async().get()
)

print(
    f"Translating '{translation_results.text}'"
)


# PROCESS THE TRANSLATION RESULTS
translations = translation_results.translations

for translation_language in translations:

    # Print results
    print(
        f"{translation_language}: "
        f"'{translations[translation_language]}'"
    )

    # Speak results
    speech_cfg.speech_synthesis_voice_name = (
        voices.get(translation_language)
    )

    speech_synthesizer = speech_sdk.SpeechSynthesizer(
        speech_cfg,
        audio_out_cfg
    )

    speak = speech_synthesizer.speak_text_async(
        translations[translation_language]
    ).get()