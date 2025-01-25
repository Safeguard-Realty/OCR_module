# AI-based OCR

This Python script extracts key information from Aadhar cards, PAN cards, and Passports using the Together API and Llama Vision model. It processes the image URL provided by the user and returns the extracted details in a structured JSON format.

## Features
- **Supports Three Document Types**:
  - Aadhar Card
  - PAN Card
  - Passport
- **Automatic Parsing**:
  - Extracts key fields like name, date of birth, document number, and address.
- **Structured Output**:
  - Returns parsed data in a clean JSON format.

## Requirements
- Docker (for containerized installation)
- Python 3.x (for local installation)
- `together` Python package (`pip install together`) (for local installation)
- API key for Together API

---

## Installation

### Option 1: Using Docker (Recommended)
1. **Install Docker**:
   - Download and install Docker from [https://www.docker.com/get-started](https://www.docker.com/get-started).

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/Safeguard-Realty/OCR_module.git
   cd OCR_module

3. **Build the Docker Image**:

   ```bash

   docker build -t document-extractor .
4. **Run the Docker Container**:

   ```bash
 
   docker run -it --rm -e TOGETHER_API_KEY="your_api_key_here" ocr-module
  ##Replace your_api_key_here with your actual Together API key.

### Option 2 Local Installation

1. **Clone the Repository:**:
   ```bash
   git clone https://github.com/Safeguard-Realty/OCR_module.git
   cd OCR_module

2. **Install Dependencies:**:
   ```bash
   pip install -r requirements.txt
   

3. **Set the Together API Key:**:
   ```bash
   export TOGETHER_API_KEY="your_api_key_here"

-Export the API key as an environment variable:

   

-Alternatively, you can hardcode the API key in the script (not recommended for security reasons).

4. **Run the Script:**:

   ```bash
 
   python main.py


# Example Inputs
## Aadhar Card:

Document Type: 1

Image URL: https://cf-img-a-in.tosshub.com/sites/visualstory/wp/2024/06/Aadhar-card.jpg?size=*:900

## PAN Card:

Document Type: 2

Image URL: https://5.imimg.com/data5/SB/WU/KT/ANDROID-33737889/product-jpeg-500x500.jpg

## Passport:

Document Type: 3

Image URL: https://i0.wp.com/mumbaiairport.in/wp-content/uploads/1000095894.jpg?fit=984%2C668&ssl=1

