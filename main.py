from ears import TotoEars
from brain import TotoBrain
from mouth import TotoMouth
import time

def start_robot():
    ears = TotoEars()
    brain = TotoBrain()
    mouth = TotoMouth()

    mouth.speak("Hello! I am Toto Fryn. I am ready to learn with you.")
    
    while True:
        try:
            # Listen for the child
            text = ears.listen()
            print(f"I heard: {text}")

            if "stop" in text.lower() or "goodbye" in text.lower():
                mouth.speak("Goodbye for now!")
                break

            # Get answer from AI
            answer = brain.ask(text)
            
            # Speak answer
            mouth.speak(answer)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    start_robot()