import os
from together import Together
from dotenv import load_dotenv

load_dotenv()
client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

def extract_aadhar_details(image_url: str):
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
    print(image_url)
    return response.choices[0].message.content

def extract_pan_card_details(image_url: str):

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
    

def extract_passport_details(image_url: str):
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