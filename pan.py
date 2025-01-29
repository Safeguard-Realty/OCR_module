import os
import re
import json
import time
from together import Together

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
- PAN Card Number: Exact 10-digit alphanumeric code (e.g., ABCD1234E)
- Name: Full name exactly as printed
- Father's Name: Exact father's name 
- Date of Birth: Exact date printed in DD/MM/YYYY format

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
        max_tokens=300,
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>", "<|eom_id|>"],
        stream=False
    )
    return response.choices[0].message.content

def parse_to_dict(text):
    details = {
        'panCardNumber': '',
        'name': '',
        'fatherName': '',
        'dateOfBirth': ''
    }
    
    # First, attempt to parse as JSON
    try:
        data = json.loads(text)
        details['panCardNumber'] = data.get('panCardNumber', '').strip()
        details['name'] = data.get('name', '').strip()
        details['fatherName'] = data.get('fatherName', '').strip()
        details['dateOfBirth'] = data.get('dateOfBirth', '').strip()
    except json.JSONDecodeError:
        pass  # Proceed to regex parsing if JSON fails
    
    # If any field is missing, use regex to extract
    if not all(details.values()):
        patterns = {
        'panCardNumber': r'(?:\*|\#|-|\s)*PAN Card Number(?:\*|\#|-|\s)*:(?:\*|\#|-|\s)*(\w{10})',
        'name': r'(?:\*|\#|-|\s)*Name(?:\*|\#|-|\s)*:(?:\*|\#|-|\s)*([\w\s]+)',
        'fatherName': r'(?:\*|\#|-|\s)*Father\'s Name(?:\*|\#|-|\s)*:(?:\*|\#|-|\s)*([\w\s]+)',
        'dateOfBirth': r'(?:\*|\#|-|\s)*Date of Birth(?:\*|\#|-|\s)*:(?:\*|\#|-|\s)*(\d{2}/\d{2}/\d{4})'
    }
        
        for key, pattern in patterns.items():
            if details[key]:  # Skip if already found via JSON
                continue
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details[key] = match.group(1).strip()
    
    return details

if __name__ == "__main__":
    image_url = "https://5.imimg.com/data5/SB/WU/KT/ANDROID-33737889/product-jpeg-500x500.jpg"
    max_retries = 5
    retries = 0
    result_dict = {}
    
    while retries <= max_retries:
        result = extract_pan_card_details(image_url)
        current_dict = parse_to_dict(result)
        

        if all(current_dict.values()):
            result_dict = current_dict
            break
        else:

            result_dict = current_dict
            retries += 1
            if retries <= max_retries:
                time.sleep(1)  # Short delay before retry
    else:
        print("Please submit the image again")
    
    print(json.dumps(result_dict, indent=2))
    print("Retries taken",retries)