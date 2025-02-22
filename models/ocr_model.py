from pydantic import BaseModel

class AadharExtraction(BaseModel):
    Name: str
    Date_Of_Birth: str
    Gender: str
    Aadhar_No: str
    Address: str

class PANExtraction(BaseModel):
    panCardNumber: str
    name: str
    fatherName: str
    dateOfBirth: str

class PassportExtraction(BaseModel):
    Passport_No: str
    Surname: str
    Given_Name: str
    Full_Name: str
    Nationality: str
    Sex: str
    Date_of_Birth: str
    Place_of_Birth: str
    Date_of_Issue: str
    Date_of_Expiry: str
    Place_of_Issue: str