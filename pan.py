import os
from together import Together
import re
import json

# Use environment variable for API key
client = Together(api_key="39656070d13a550e3638ce21dad42231137f331e10647d97064f5f050779363c")

def extract_pan_card_details(image_url):
    """Extract key-value pairs from a PAN Card image."""
    response = client.chat.completions.create(
        model="meta-llama/Llama-Vision-Free",
        messages=[
            {
                "role": "system",
                "content": """
                You are an expert data extractor. For the given PAN card image, STRICTLY extract the following details:

1. Extract ONLY the exact values for these fields
2. Return ONLY a valid JSON format
3. Do not add any explanatory text

Required Fields:
- PAN Card Number: Exact 10-digit alphanumeric code
- Name: Full name exactly as printed
- Father's Name: Exact father's name 
- Date of Birth: Exact date printed

Output Format (MANDATORY):
{
  "panCardNumber": "",
  "name": "",
  "fatherName": "",
  "dateOfBirth": ""
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
                        "text": "Extract important key-value pairs from it"
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
        max_tokens=300,  # Set a reasonable max token limit
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>", "<|eom_id|>"],
        stream=False
    )

    # Directly access the response content
    return response.choices[0].message.content

def parse_to_dict(text):
    # Define regex patterns for each field
    patterns = {
        'panCardNumber': r'\*\*PAN Card Number:\*\*\s*(\w+)',
        'name': r'\*\*Name:\*\*\s*([\*\s]*[^\n]+)',
        'fatherName': r'\*\*Father\'s Name:\*\*\s*([\*\s]*[^\n]+)',
        'dateOfBirth': r'\*\*Date of Birth:\*\*\s*(\d{2}/\d{2}/\d{4})'
    }
    
    details = {
        'panCardNumber': '',
        'name': '',
        'fatherName': '',
        'dateOfBirth': ''
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            # Clean up the extracted value by removing leading asterisks and extra spaces
            details[key] = match.group(1).replace('*', '').strip()
    
    return details

if __name__ == "__main__":
    image_url = "https://5.imimg.com/data5/SB/WU/KT/ANDROID-33737889/product-jpeg-500x500.jpg"
    result = extract_pan_card_details(image_url)
    result_dict = parse_to_dict(result)
    print(json.dumps(result_dict, indent=2))
    # print(result)