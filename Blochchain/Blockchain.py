import hashlib
import json
from os import curdir
import re
from time import time
from traceback import print_tb
from urllib.parse import urlparse
from uuid import uuid4
import pymongo
from bson.objectid import ObjectId

class Block:
    def toJSON(self):
        return json.dumps(self,default=lambda o: o.__dict__,sort_keys=True,indent=4)

    def __init__(self) -> None:
        self.sender_id = None
        self.receiver_id = None
        self.amount = None
        self.desp = None
        self.time = None
        self.purpose = None
        self.state = None
        self.district = None
        self.bill_no = None
        self.prev_hash = None

class Blockchain:
    def __init__(self) -> None:
        self.client= pymongo.MongoClient("mongodb://Admin:root@localhost:27017/")
        self.mydb = self.client["fundtracker"]
        self.transactions = self.mydb["transaction"]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def create_genesis_block(self,block_obj):
        block_obj.prev_hash = "-1"
        data_dict = block_obj.__dict__
        res = self.transactions.insert_one(data_dict)
        return "success"
    
    def add_transaction(self,block_obj,role):
        blocks=self.find_chain(block_obj.bill_no,block_obj.state,block_obj.district)
        print(blocks)
        last_block=self.transactions.find_one({"_id":{"$eq":ObjectId(blocks[-1])}})
        print(last_block)
        prev_hash=last_block["prev_hash"]
        block_obj.prev_hash=prev_hash
        block_obj.prev_hash = self.hash(block_obj.toJSON())
        data_dict = block_obj.__dict__
        if role == 'Contractor':
            data_dict["leaf"]=True

        res = self.transactions.insert_one(data_dict)
        return "success"
        
    def find_chain(self,bill_no,state,district):
        chain = []
        trans = self.transactions.find_one({"bill_no":{"$eq":bill_no},"prev_hash":{"$eq":"-1"}})
        chain.append(str(trans["_id"]))
        
        if state != "NA":
            trans = self.transactions.find_one({"bill_no":{"$eq":bill_no},"state":{"$eq":state},"district":{"$eq":"NA"}})
            
            if trans:
                chain.append(str(trans["_id"]))
        
        if district != "NA":
            trans = self.transactions.find_one({"bill_no":{"$eq":bill_no},"district":{"$eq":district},"leaf":{"$exists":False}})
            if trans:
                chain.append(str(trans["_id"]))
            
        return chain
    
    def get_full_chain_using_bill_no(self,bill_no):
        resp=[]
        trans = self.transactions.find_one({"bill_no":{"$eq":bill_no},"prev_hash":{"$eq":"-1"}})
        temp_list=[]
        if trans["state"]=="NA":
            temp_list.append({
                "v":"India",
                "f":"India<br>"+str(trans["amount"])
            })
            temp_list.append("")
            temp_list.append("")
        resp.append(temp_list)
        transs = self.transactions.find({"$and":[{"state":{"$ne":"NA"}},{"bill_no":{"$eq":bill_no}},{"district":{"$eq":"NA"}}]})
        states=[]
        
        for i in transs:
            temp_list=[]
            states.append(i["state"])
            temp_list.append({
                "v":i["state"],
                "f":str(i["state"])+"<br>"+str(i["amount"])
            })
            temp_list.append("India")
            temp_list.append("")
            resp.append(temp_list)
            trans_dist = self.transactions.find({"bill_no":{"$eq":bill_no},"state":{"$eq":i["state"]},"prev_hash":{"$ne":"-1"},"district":{"$ne":"NA"}})
            for d in trans_dist:
                print(d)
                temp_list=[]
                temp_list.append({
                    "v":d["district"],
                    "f":str(d["district"])+"<br>"+str(d["amount"])
                })
                temp_list.append(i["state"])
                temp_list.append("")
                resp.append(temp_list)
                cont_trans =  self.transactions.find({"bill_no":{"$eq":bill_no},"leaf":{"$eq":True},"state":{"$eq":i["state"]},"district":{"$eq":d["district"]},"prev_hash":{"$ne":"-1"}})
                for c in cont_trans:
                    temp_list=[]
                    temp_list.append({
                        "v":c["purpose"]+d["district"],
                        "f":str(c["purpose"])+"<br>"+str(c["amount"])
                    })
                    temp_list.append(d["district"])
                    temp_list.append("")
                    resp.append(temp_list)
        return resp

    def check_chain(self,block_obj):
        blocks=self.find_chain(block_obj.bill_no,block_obj.state,block_obj.district)
        for i in range(len(blocks)-1,0,-1):
            curr_block=self.transactions.find_one({"_id":{"$eq":ObjectId(str(blocks[i]))}})
            prev_block=self.transactions.find_one({"_id":{"$eq":ObjectId(str(blocks[i-1]))}})
            curr_block_obj=Block()
            curr_block_obj.amount=curr_block["amount"]
            curr_block_obj.bill_no=curr_block["bill_no"]
            curr_block_obj.desp=curr_block["desp"]
            curr_block_obj.district=curr_block["district"]
            curr_block_obj.state=curr_block["state"]
            curr_block_obj.time=curr_block["time"]
            curr_block_obj.sender_id=curr_block["sender_id"]
            curr_block_obj.receiver_id=curr_block["receiver_id"]
            curr_block_obj.prev_hash=curr_block["prev_hash"]
            curr_block_obj.purpose=curr_block["purpose"]
            prev_block_obj=Block()
            prev_block_obj.amount=prev_block["amount"]
            prev_block_obj.bill_no=prev_block["bill_no"]
            prev_block_obj.desp=prev_block["desp"]
            prev_block_obj.time=prev_block["time"]
            prev_block_obj.district=prev_block["district"]
            prev_block_obj.state=prev_block["state"]
            prev_block_obj.sender_id=prev_block["sender_id"]
            prev_block_obj.receiver_id=prev_block["receiver_id"]
            prev_block_obj.prev_hash=prev_block["prev_hash"]
            prev_block_obj.purpose=prev_block["purpose"]
            curr_hash=curr_block_obj.prev_hash
            curr_block_obj.prev_hash=prev_block_obj.prev_hash
            if (self.hash(curr_block_obj.toJSON())) != curr_hash:
                return False
        return True