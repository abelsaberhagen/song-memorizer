import speech_recognition as sr


class VoiceToText:

    def __init__(self):
        pass

    def transcribe_voice(self):
        """Listen from the microphone and return transcribed text."""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            r.adjust_for_ambient_noise(source, duration=0.2)
            audio_data = r.listen(source)
            print("Transcribing...")
        try:
            text = r.recognize_google(audio_data)
            print("You said: " + text)
            return text
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not reach Google Speech Recognition service; {e}")
            return None

def transcribe_file(self, file_path: str):
    import subprocess
    import tempfile

    # Convert webm to wav so SpeechRecognition can read it
    wav_path = file_path.replace(".webm", ".wav")
    subprocess.run(["ffmpeg", "-y", "-i", file_path, wav_path],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    r = sr.Recognizer()
    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = r.record(source)
        text = r.recognize_google(audio_data)
        print("Transcribed: " + text)
        return text
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Could not reach Google Speech Recognition service; {e}")
        return None
    except Exception as e:
        print(f"Error reading audio file: {e}")
        return None
    finally:
        # Clean up wav file
        try:
            os.remove(wav_path)
        except Exception:
            pass