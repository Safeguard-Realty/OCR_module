import re
import json
import time
from together import Together
from dotenv import load_dotenv
import os

load_dotenv()

client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

# ==================== Required Fields Configuration ====================
REQUIRED_FIELDS = {
    'aadhar': ['Name', 'Date_Of_Birth', 'Gender', 'Aadhar_No', 'Address'],
    'pan': ['panCardNumber', 'name', 'fatherName', 'dateOfBirth'],
    'passport': ['Passport_No', 'Surname', 'Given_Name', 'Nationality', 'Sex',
                 'Date_of_Birth', 'Place_of_Birth', 'Date_of_Issue',
                 'Date_of_Expiry', 'Place_of_Issue']
}

# ==================== Aadhar Card Functions ====================
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
    details = {
        'Name': '',
        'Date_Of_Birth': '',
        'Gender': '',
        'Aadhar_No': '',
        'Address': ''
    }
    
    # First try JSON parsing
    try:
        json_match = re.search(r'\{[\s\S]*?\}(?=\s*\Z|\s*\{)', text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group().strip())
            for key in details:
                val = data.get(key, '').strip()
                if val: details[key] = val
    except:
        pass
    
    # Regex fallback
    patterns = {
        'Name': r'(?:Name|NAME)[\s:*]+([A-Za-z\s]+)',
        'Date_Of_Birth': r'(?:Date\s*Of?\s*Birth|DOB)[\s:*]+(\d{2}/\d{2}/\d{4})',
        'Gender': r'(?:Gender|GENDER)[\s:*]+(\w+)',
        'Aadhar_No': r'(?:Aadhar\s*No|Aadhaar\s*Number)[\s:*]+(\d{4}[\s-]?\d{4}[\s-]?\d{4})',
        'Address': r'(?:Address|ADDRESS)[\s:*]+([^*]+?)(?=\s*\*|$)'
    }

    for line in text.split('\n'):
        line = line.strip()
        for key, pattern in patterns.items():
            if details[key]:  # Skip if already found
                continue
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                details[key] = match.group(1).strip()
    
    return details

# ==================== PAN Card Functions ====================
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
        max_tokens=300,
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>", "<|eom_id|>"],
        stream=False
    )
    return response.choices[0].message.content

def parse_pan_details(text):
    details = {
        'panCardNumber': '',
        'name': '',
        'fatherName': '',
        'dateOfBirth': ''
    }
    
    # Try JSON parsing first
    try:
        data = json.loads(text)
        for key in details:
            val = data.get(key, '').strip()
            if val: details[key] = val
    except:
        pass
    
    # Regex patterns with improved formatting handling
    patterns = {
        'panCardNumber': r'(?:\*|\#|-|\s)*PAN Card Number(?:\*|\#|-|\s)*:(?:\*|\#|-|\s)*(\w{10})',
        'name': r'(?:\*|\#|-|\s)*Name(?:\*|\#|-|\s)*:(?:\*|\#|-|\s)*([\w\s]+)',
        'fatherName': r'(?:\*|\#|-|\s)*Father\'s Name(?:\*|\#|-|\s)*:(?:\*|\#|-|\s)*([\w\s]+)',
        'dateOfBirth': r'(?:\*|\#|-|\s)*Date of Birth(?:\*|\#|-|\s)*:(?:\*|\#|-|\s)*(\d{2}/\d{2}/\d{4})'
    }
    
    for key, pattern in patterns.items():
        if details[key]:  # Skip if already found
            continue
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            details[key] = match.group(1).strip()
    
    return details

# ==================== Passport Functions ====================
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
        max_tokens=500,
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>", "<|eom_id|>"],
        stream=False
    )
    return response.choices[0].message.content

def parse_passport_details(text):
    details = {
        'Passport_No': '',
        'Surname': '',
        'Given_Name': '',
        'Nationality': '',
        'Sex': '',
        'Date_of_Birth': '',
        'Place_of_Birth': '',
        'Date_of_Issue': '',
        'Date_of_Expiry': '',
        'Place_of_Issue': '',
        'Full_Name': ''
    }
    
    # Try JSON parsing first
    try:
        data = json.loads(text)
        for key in details:
            val = data.get(key, '').strip()
            if val: details[key] = val
    except:
        pass
    
    # Enhanced regex patterns
    patterns = {
        'Passport_No': r'(?:Passport\s*(?:No|Number)[:\s\-*"]*)([A-Z]{1,2}\d{7})',
        'Surname': r'(?:Surname[:\s\-*"]*)([A-Za-z]+)',
        'Given_Name': r'(?:Given\s*Name[:\s\-*"]*)([A-Za-z\s]+)',
        'Nationality': r'(?:Nationality[:\s\-*"]*)([A-Za-z]+)',
        'Sex': r'(?:Sex[:\s\-*"]*)([MF])',
        'Date_of_Birth': r'(?:Date\s*of\s*Birth[:\s\-*"]*)(\d{2}/\d{2}/\d{4})',
        'Place_of_Birth': r'(?:Place\s*of\s*Birth[:\s\-*"]*)([A-Za-z\s]+)',
        'Date_of_Issue': r'(?:Date\s*of\s*Issue[:\s\-*"]*)(\d{2}/\d{2}/\d{4})',
        'Date_of_Expiry': r'(?:Date\s*of\s*Expiry[:\s\-*"]*)(\d{2}/\d{2}/\d{4})',
        'Place_of_Issue': r'(?:Place\s*of\s*Issue[:\s\-*"]*)([A-Za-z\s]+)',
        'Full_Name': r'(?:Full\s*Name[:\s\-*"]*)([A-Za-z\s]+)'
    }
    
    for key, pattern in patterns.items():
        if details[key]:  # Skip if already found
            continue
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            details[key] = match.group(1).strip()
    
    # Construct Full_Name if missing
    if not details['Full_Name'] and details['Surname'] and details['Given_Name']:
        details['Full_Name'] = f"{details['Surname']} {details['Given_Name']}"
    
    return details

# ==================== Unified Processor with Retry Logic ====================
def process_document(image_url, doc_type, max_retries=3):
    """Main processing function with retry mechanism"""
    best_result = None
    retries = 0
    
    while retries <= max_retries:
        try:
            # Extract and parse
            if doc_type == 'aadhar':
                raw = extract_aadhar_details(image_url)
                parsed = parse_aadhar_details(raw)
            elif doc_type == 'pan':
                raw = extract_pan_card_details(image_url)
                parsed = parse_pan_details(raw)
            elif doc_type == 'passport':
                raw = extract_passport_details(image_url)
                parsed = parse_passport_details(raw)
            else:
                raise ValueError("Unsupported document type")
            
            # Create current result
            current_result = {
                "document_type": doc_type,
                "raw_output": raw,
                "parsed_data": parsed
            }
            
            # Check required fields
            required = REQUIRED_FIELDS[doc_type]
            all_present = all(parsed.get(field, '') for field in required)
            
            if all_present:
                best_result = current_result
                break
            else:
                # Update best result if better than previous
                if best_result is None or sum(len(v) for v in parsed.values()) > sum(len(v) for v in best_result['parsed_data'].values()):
                    best_result = current_result
                
                retries += 1
                if retries <= max_retries:
                    time.sleep(1)  # API rate limit protection
                    
        except Exception as e:
            print(f"Error during processing: {str(e)}")
            retries += 1
            if retries <= max_retries:
                time.sleep(1)
    
    # Post-retry validation
    if best_result is None:
        raise RuntimeError("Failed to process document after maximum retries")
    
    # Final check for missing fields
    required = REQUIRED_FIELDS[doc_type]
    missing = [field for field in required if not best_result['parsed_data'].get(field, '')]
    if missing:
        print(f"Warning: Missing fields after {max_retries} retries: {', '.join(missing)}")
    
    return best_result

# ==================== Main Execution ====================
if __name__ == "__main__":
    print("Please specify the document type:")
    print("1. Aadhar Card")
    print("2. PAN Card")
    print("3. Passport")
    choice = input("Enter your choice (1/2/3): ").strip()
    
    doc_type_map = {
        '1': 'aadhar',
        '2': 'pan',
        '3': 'passport'
    }
    
    if choice not in doc_type_map:
        print("Invalid choice. Please run the program again and select 1, 2, or 3.")
        exit(1)
    
    doc_type = doc_type_map[choice]
    image_url = input(f"Enter the {doc_type} image URL: ").strip()
    
    # Process with retries
    result = process_document(image_url, doc_type, max_retries=3)
    
    print("\nDocument Type:", result['document_type'])
    print("\nRaw Output:")
    print(result['raw_output'])
    print("\nParsed Data:")
    print(json.dumps(result['parsed_data'], indent=2))