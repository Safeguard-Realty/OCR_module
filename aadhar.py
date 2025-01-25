import os
from dotenv import load_dotenv
from together import Together
import re
import json
load_dotenv()

client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

def extract_aadhar_details(image_url):
    """Extract key-value pairs from an Aadhar card image."""
    response = client.chat.completions.create(
        model="meta-llama/Llama-Vision-Free",
        messages=[
            {
                "role": "system",
                "content": """
                You are an expert data extractor specializing in Aadhar card information. 
                For the given Aadhar card image, STRICTLY extract the following details:

                1. Extract ONLY the exact values for these fields
                2. Return ONLY a valid JSON format
                3. Do not add any explanatory text

                Required Fields:
                - Name: Full name as printed
                - Date Of Birth: Exact date format DD/MM/YYYY
                - Gender: M, F, or Other
                - Aadhar No: Exact 12-digit Aadhar number
                - Address: Full address as printed

                Output Format (MANDATORY):
                {
                  "Name": "",
                  "Date_Of_Birth": "",
                  "Gender": "",
                  "Aadhar_No": "",
                  "Address": ""
                }

                DO NOT include any additional text or explanation.
                ONLY return the JSON object with extracted values.
                """
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract required key-value pairs from the Aadhar card image"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ],
        max_tokens=500,
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>", "<|eom_id|>"],
        stream=False
    )
    return response.choices[0].message.content

def parse_aadhar_details(text):
    # First try to extract valid JSON
    try:
        # Match FIRST valid JSON object only
        json_match = re.search(r'\{[\s\S]*?\}(?=\s*\Z|\s*\{)', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group().strip())
    except:
        pass

    # If JSON extraction fails, proceed with regex patterns
    patterns = {
        'Name': r'(?:Name|NAME)[\s:*]+([A-Za-z\s]+)',
        'Date_Of_Birth': r'(?:Date\s*Of?\s*Birth|DOB)[\s:*]+(\d{2}/\d{2}/\d{4})',
        'Gender': r'(?:Gender|GENDER)[\s:*]+(\w+)',
        'Aadhar_No': r'(?:Aadhar\s*No|Aadhaar\s*Number)[\s:*]+(\d{4}[\s-]?\d{4}[\s-]?\d{4})',
        'Address': r'(?:Address|ADDRESS)[\s:*]+([^*]+?)(?=\s*\*|$)'
    }

    details = {}
    for line in text.split('\n'):
        line = line.strip()
        for key, pattern in patterns.items():
            match = re.search(pattern, line, re.IGNORECASE)
            if match and not details.get(key):
                details[key] = match.group(1).strip()

    # Normalization logic remains same
    return details

if __name__ == "__main__":
    image_url = "https://cf-img-a-in.tosshub.com/sites/visualstory/wp/2024/06/Aadhar-card.jpg?size=*:900"  # Replace with actual Aadhar card image URL
    result = extract_aadhar_details(image_url)
    result_dict = parse_aadhar_details(result)
    print(result)
    print(json.dumps(result_dict, indent=2))
