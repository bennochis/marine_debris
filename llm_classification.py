import google.generativeai as genai
from dotenv import load_dotenv
from googletrans import Translator
import os
     
# Authenticate
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Translator
translator = Translator()

def auto_translate(text):
    try:
        result = translator.translate(text, dest='en')
        return result.text
    except:
        return text

# Marine debris categories
DEBRIS_CATEGORIES = [
    "Plastic", "Metal", "Glass", "Rubber", 
    "Processed Wood", "Fabric", "Other"
]

# Prompt Template
PROMPT_TEMPLATE = """
You are a marine debris classification expert.

Here is a description of an item found: "{description}"

Classify the item strictly into one of the following categories:
   - Plastic
   - Metal
   - Glass
   - Rubber
   - Processed Wood
   - Fabric
   - Other

Apply the following guidelines:
    Fragments: If the item is a broken piece from an unidentifiable larger item, classify it based on its material type.

    Identifiable Items: If the item can be identified (even if incomplete), classify it according to its predominant material.

    Unidentifiable Items: If the item is unidentifiable but appears complete enough that someone else might identify it, classify it as 'Other'.

    Unknown Material: If the material is unidentifiable or not listed among the categories, classify it as 'Other'.

Respond ONLY with one of the category names listed above.
"""

def classify_debris(image_path, description):
    model = genai.GenerativeModel("gemini-2.0-flash")

    # Input Text auto-translation
    if description:
        description = auto_translate(description)

    prompt = PROMPT_TEMPLATE.format(description=description)

    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        return result
    except Exception as e:
        print(f"Gemini classification failed: {e}")
        return "Other"