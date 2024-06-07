from blockchain import Blockchain
import hashlib, json, copy, time, random, time
from fastapi import FastAPI, HTTPException, Request

app = FastAPI()
blockchain = Blockchain()

@app.post("/transactions/create")
async def createTransaction(request: Request):
    data = await request.json()
    sender = data['sender']
    recipient = data['recipient']
    amount = data['amount']
    timestamp = data['timestamp']
    privWifKey = data['privWifKey']
    return blockchain.createTransaction(sender, recipient, amount, timestamp, privWifKey)

@app.get("/transactions/mempool")
async def getMempool():
    return blockchain.memPool

@app.get("/mine")
def mineBlock():
    block = blockchain.createBlock()
    nonce = blockchain.mineProofOfWork(blockchain.prevBlock)
    return {'block': block, 'nonce': nonce}

@app.get("/chain")
def getChain():
    return blockchain.chain

@app.post("/nodes/register")
async def registerNodes(request: Request):
    data = await request.json()
    nodes = data["nodes"]
    
    for node in nodes:
        blockchain.nodes.add(node)
    
    return {"message": "Os nós foram registrados"}

@app.get("/nodes/resolve")
def resolveNodes():
    blockchain.resolveConflicts()
    return blockchain.chain

