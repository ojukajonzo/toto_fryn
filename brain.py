import ollama

class TotoBrain:
    def __init__(self, model_name='llama3.2:1b'):
        """
        Initializes the AI brain using Ollama.
        
        """
        self.model = model_name
        
        # This is the 'personality' and 'knowledge base' for the robot
        self.system_instruction = (
            "You are Toto Fryn, an AI tutor for children in Uganda (ages 3-12). "
            "Your tone is encouraging, patient, and friendly. "
            "IMPORTANT RULES: "
            "1. Use simple English suitable for primary school learners. "
            "2. Use Ugandan examples (e.g., currency is Shillings, fruits are Mangoes/Matooke). "
            "3. Keep answers very short (1-3 sentences). "
            "4. If asked about science or math, relate it to daily life in Uganda."
        )

    def ask(self, child_speech):
        """Sends the question to the AI and returns the text response."""
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': self.system_instruction},
                {'role': 'user', 'content': child_speech},
            ])
            return response['message']['content']
        except Exception as e:
            # Error handling if Ollama is not running
            return f"I am having trouble connecting to my memory. Please make sure Ollama is running. (Error: {e})"

if __name__ == "__main__":
    # Internal test: Run this file directly to check if the AI is 'alive'
    brain = TotoBrain()
    print("Testing Toto's Brain...")
    test_answer = brain.ask("Who is the president of Uganda?")
    print(f"Toto's Test Answer: {test_answer}")