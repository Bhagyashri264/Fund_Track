from typing import List
from pydantic import BaseModel

class block_struct(BaseModel):
    sender_id:str
    receiver_id:str
    amount:int
    purpose:str
    desp:str
    state:str
    district:str
    bill_no:int
    role:str

class otp_struct(BaseModel):
    otp:int
    email:str

class chain_bill(BaseModel):
    bill_no:int

class send_complaint(BaseModel):
    bill_no:int
    desc:str
    state:str
    district:str