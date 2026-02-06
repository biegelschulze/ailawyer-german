import google.generativeai as genai
import os

api_key = "AIzaSyAP613DBPLvcDJ1QLOn-9YPm6n6tpYZClw"
genai.configure(api_key=api_key)

print("Verfügbare Modelle (Generation):")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Fehler: {e}")
