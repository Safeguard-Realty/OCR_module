import re
import json

def parse_aadhar_details(text: str):
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
    

def parse_pan_details(text: str):
    # Define regex patterns for each field
    # patterns = {
    #     'panCardNumber': r'(?:Permanent\s*Account\s*Number|PAN)[:\s\-*]*([A-Z0-9]{10})',
    #     'name': r'(?:Name\s*on\s*Card|Name)[:\s\-*]*([A-Z\s]+)',
    #     'fatherName': r'(?:Father\'?s?\s*Name)[:\s\-*]*([A-Z\s]+)',
    #     'dateOfBirth': r'(?:Date\s*of\s*Birth|DOB)[:\s\-*]*(\d{2}/\d{2}/\d{4})'
    # }
    patterns = {
        'panCardNumber': r'(?:\*|\#|-|\s)*PAN Card Number(?:\*|\#|-|\s)*:(?:\*|\#|-|\s)*(\w{10})',
        'name': r'(?:\*|\#|-|\s)*Name(?:\*|\#|-|\s)*:(?:\*|\#|-|\s)*([\w\s]+)',
        'fatherName': r'(?:\*|\#|-|\s)*Father\'s Name(?:\*|\#|-|\s)*:(?:\*|\#|-|\s)*([\w\s]+)',
        'dateOfBirth': r'(?:\*|\#|-|\s)*Date of Birth(?:\*|\#|-|\s)*:(?:\*|\#|-|\s)*(\d{2}/\d{2}/\d{4})'
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

def parse_passport_details(text: str):
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