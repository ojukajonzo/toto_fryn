import vosk
import sys
import sounddevice as sd
import json
import os

class TotoEars:
    def __init__(self):
        # Path to the model - double check this matches your folder name!
        self.model_path = "data/models/stt_model"
        self.sample_rate = 16000
        
        if not os.path.exists(self.model_path):
            print(f"❌ ERROR: STT Model not found at {self.model_path}")
            print("Please ensure you downloaded and unzipped the Vosk model there.")
            sys.exit(1)
            
        self.model = vosk.Model(self.model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)

    def listen(self):
        print("👂 Toto is listening...")
        # This opens the microphone stream
        with sd.RawInputStream(samplerate=self.sample_rate, blocksize=8000, 
                               dtype='int16', channels=1) as stream:
            while True:
                data, overflowed = stream.read(8000)
                if self.recognizer.AcceptWaveform(bytes(data)):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        return text

if __name__ == "__main__":
    # Test Ears
    ears = TotoEars()
    print("Say something...")
    print(f"You said: {ears.listen()}")