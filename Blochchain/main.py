import imp
from fastapi import FastAPI
from schemas import block_struct,otp_struct,chain_bill,send_complaint
from Blockchain import Block,Blockchain
import datetime
import random
from send_email import send_email_async,send_complaint_email
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/create_genesis_block")
def create_genesis_block(request:block_struct):
    Block_obj = Block()
    Block_obj.sender_id = request.sender_id
    Block_obj.receiver_id = request.receiver_id
    Block_obj.amount = request.amount
    Block_obj.desp = request.desp
    Block_obj.bill_no = request.bill_no
    Block_obj.district = request.district
    Block_obj.state = request.state
    Block_obj.purpose = request.purpose
    Block_obj.time = str(datetime.datetime.now())
    obj = Blockchain()
    res = obj.create_genesis_block(Block_obj)
    return res

@app.post("/add_transaction")
def Add_transaction(request:block_struct):
    Block_obj = Block()
    Block_obj.sender_id = request.sender_id
    Block_obj.receiver_id = request.receiver_id
    Block_obj.amount = request.amount
    Block_obj.desp = request.desp
    Block_obj.bill_no = request.bill_no
    Block_obj.district = request.district
    Block_obj.state = request.state
    Block_obj.purpose = request.purpose
    Block_obj.time = str(datetime.datetime.now())
    obj = Blockchain()
    res = obj.add_transaction(Block_obj,request.role)
    return {"body":res}

@app.post("/sendotp")
async def sendotp(request:otp_struct):
    await send_email_async(subject="Verify your email",email_to=request.email,body={"Title":"Verify Your OTP","otp":str(request.otp)})
    return {"otp":"1"}

@app.post("/get_tree_from_bill")
def get_chain(request:chain_bill):
    obj=Blockchain()
    data=obj.get_full_chain_using_bill_no(request.bill_no)
    return str(data)

@app.post("/validate_chain")
def validate(request:block_struct):
    Block_obj = Block()
    Block_obj.sender_id = request.sender_id
    Block_obj.receiver_id = request.receiver_id
    Block_obj.amount = request.amount
    Block_obj.desp = request.desp
    Block_obj.bill_no = request.bill_no
    Block_obj.district = request.district
    Block_obj.state = request.state
    Block_obj.purpose = request.purpose
    Block_obj.time = str(datetime.datetime.now())
    obj = Blockchain()
    resp=obj.check_chain(Block_obj)
    return resp

@app.post("/send_complaint")
async def send_complaint(request:send_complaint):
    await send_complaint_email(subject="Complaint about bill no:-"+str(request.bill_no),email_to="rushikesh5001@gmail.com",body={"bill_no":str(request.bill_no),"desc":request.desc,"state":request.state,"district":request.district})
    return {"email":"sent"}