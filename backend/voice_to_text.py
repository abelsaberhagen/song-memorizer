import os
import speech_recognition as sr

class VoiceToText:

    def __init__(self):
        pass

    # Initialize the recognizer

    def transcribe_file(self, file_path):
        import tempfile
        from pydub import AudioSegment

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = tmp.name

        try:
            audio = AudioSegment.from_file(file_path)
            audio.export(wav_path, format="wav")

            r = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio_data = r.record(source)
            try:
                text = r.recognize_google(audio_data)
                return text
            except sr.UnknownValueError:
                print("Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
        finally:
            os.remove(wav_path)

        return None

    def transcribe_voice(self):
        r = sr.Recognizer()

        # Use the default microphone as the audio source
        with sr.Microphone() as source:
            print("Listening...")
            # Adjust for ambient noise for better accuracy
            r.adjust_for_ambient_noise(source, duration=0.2)
            # Listen for the first phrase and extract the audio data
            audio_data = r.listen(source)
            print("Transcribing...")

    
        # Transcribe the audio data using the Google Web Speech API
        try:
            text = r.recognize_google(audio_data)
            print("You said: " + text)
            return text
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

    