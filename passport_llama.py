import os
from together import Together
import re
import json

# Initialize the Together API client
client = Together(api_key="39656070d13a550e3638ce21dad42231137f331e10647d97064f5f050779363c")

def extract_passport_details(image_url):
    """Extract key-value pairs from a Passport image."""
    response = client.chat.completions.create(
        model="meta-llama/Llama-Vision-Free",
        messages=[
            {
                "role": "system",
                "content": """
                You are an expert data extractor specializing in passport information. 
                For the given passport image, STRICTLY extract the following details:

                1. Extract ONLY the exact values for these fields
                2. Return ONLY a valid JSON format
                3. Do not add any explanatory text

                Required Fields:
                - Passport Number: Exact alphanumeric passport number
                - Surname: Exact surname as printed
                - Given Name: Full given name(s)
                - Nationality: Exact nationality
                - Sex: M or F
                - Date of Birth: Exact date format DD/MM/YYYY
                - Place of Birth: Exact location
                - Date of Issue: Exact date format DD/MM/YYYY
                - Date of Expiry: Exact date format DD/MM/YYYY
                - Place of Issue: Exact location

                Output Format (MANDATORY):
                {
                  "Passport_No": "",
                  "Surname": "",
                  "Given_Name": "",
                  "Full_Name": "",
                  "Nationality": "",
                  "Sex": "",
                  "Date_of_Birth": "",
                  "Place_of_Birth": "",
                  "Date_of_Issue": "",
                  "Date_of_Expiry": "",
                  "Place_of_Issue": ""
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
                        "text": "Extract all key-value pairs from the passport image"
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
        max_tokens=500,  # Increased token limit for passport details
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>", "<|eom_id|>"],
        stream=False
    )

    # Directly access the response content
    return response.choices[0].message.content

def parse_passport_details(text):
    patterns = {
        'Passport_No': r'(?:Passport\s*(?:No|Number)\s*[:.]?\s*)([A-Z]{1,2}\d{7})',  
        'Surname': r'(?:Surname:?\s*)([A-Z]+)',
        'Given_Name': r'(?:Given\s*[Nn]ame:?\s*)([A-Z\s]+)',
        'Nationality': r'(?:Nationality:?\s*)([A-Z]+)',
        'Sex': r'(?:Sex:?\s*)([MF])',
        'Date_of_Birth': r'(?:Date\s*of\s*[Bb]irth:?\s*)(\d{2}/\d{2}/\d{4})',
        'Place_of_Birth': r'(?:Place\s*of\s*[Bb]irth:?\s*)([A-Za-z\s]+)',
        'Date_of_Issue': r'(?:Date\s*of\s*[Ii]ssue:?\s*)(\d{2}/\d{2}/\d{4})',
        'Date_of_Expiry': r'(?:Date\s*of\s*[Ee]xpiry:?\s*)(\d{2}/\d{2}/\d{4})',
        'Place_of_Issue': r'(?:Place\s*of\s*[Ii]ssue:?\s*)([A-Za-z\s]+)'
    }
    
    details = {key: '' for key in patterns}
    details['Full_Name'] = ''
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        if match:
            details[key] = match.group(1).strip()
    
    # Combine Surname and Given Name
    if details['Surname'] and details['Given_Name']:
        details['Full_Name'] = f"{details['Surname']} {details['Given_Name']}".strip()
    
    return details

if __name__ == "__main__":
    image_url = "https://i0.wp.com/mumbaiairport.in/wp-content/uploads/1000095894.jpg?fit=984%2C668&ssl=1"  # Replace with actual passport image URL
    result = extract_passport_details(image_url)
    result_dict = parse_passport_details(result)
    print(result)
    print(json.dumps(result_dict, indent=2))