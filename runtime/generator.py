import os
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class Generator:
    def __init__(self, provider="gemini"):
        self.provider = provider
        if provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment")
            genai.configure(api_key=api_key)
            
            # Auto-discover available models
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # Prioritize models
            priority = ["models/gemini-2.0-flash", "models/gemini-1.5-flash", "models/gemini-pro"]
            self.model_name = next((m for m in priority if m in available_models), None)
            
            if not self.model_name:
                # Fallback to any model if priority list fails
                self.model_name = next((m for m in available_models if "gemini" in m.lower()), "models/gemini-pro")
            
            print(f"Using Gemini model: {self.model_name}")
            self.model = genai.GenerativeModel(self.model_name)
            
        elif provider == "groq":
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            self.model_name = "llama-3.3-70b-versatile"

    def generate(self, prompt):
        if self.provider == "gemini":
            response = self.model.generate_content(prompt)
            return response.text
        elif self.provider == "groq":
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
            )
            return chat_completion.choices[0].message.content
