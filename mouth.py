import os
import subprocess
import shutil

class TotoMouth:
    def __init__(self):
        # Path to your Piper .onnx model
        self.model_path = "data/models/en_US-lessac-medium.onnx"
        
        # Check if 'piper' is installed in your path
        self.piper_path = shutil.which("piper")
        
        if not os.path.exists(self.model_path):
            print(f"❌ ERROR: Voice model not found at {self.model_path}")
        
        if not self.piper_path:
            print("❌ ERROR: 'piper' command not found. Did you run 'pip install piper-tts'?")

    def speak(self, text):
        if not text:
            return
            
        print(f"📢 Toto: {text}")
        
        # Clean text for shell safety
        clean_text = text.replace('"', '').replace("'", "")
        
        try:
            # We pipe the text to piper, and piper's output to aplay
            command = (
                f'echo "{clean_text}" | '
                f'piper --model {self.model_path} --output_raw | '
                f'aplay -r 22050 -f S16_LE -t raw'
            )
            subprocess.run(command, shell=True, check=True)
        except Exception as e:
            print(f"❌ Mouth Error: {e}")

if __name__ == "__main__":
    # Test Mouth
    mouth = TotoMouth()
    mouth.speak("Hello. I am testing my voice on Fedora. Can you hear me?")
    