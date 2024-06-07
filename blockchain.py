import hashlib, json, copy, time, random, time
import bitcoinlib 
import http.client
import requests 

DIFFICULTY = 4 

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.memPool = []
        self.nodes = set() 
        self.createGenesisBlock()

    def createGenesisBlock(self): 
        genesis_block = self.createBlock()
        self.mineProofOfWork(self.prevBlock)
        return genesis_block

    def createBlock(self):
        block = {
            'index': len(self.chain),
            'timestamp': int(time.time()),
            'transactions': self.memPool,
            'merkleRoot': self.generateMerkleRoot(self.memPool),
            'nonce': 0,
            'previousHash': self.getBlockID(self.chain[-1]) if (len(self.chain)) else '0'*64
        }
        self.memPool = []
        self.chain.append(block)
        return block

    def mineProofOfWork(self, block):
        nonce = 0
        while self.isValidProof(block, nonce) is False:
            nonce += 1
        return nonce
    
    def isValidChain(chain): 
        for i in reversed(range(len(chain))):
            block = chain[i]
            
            if not Blockchain.isValidProof(block, block['nonce']):
                return False
            if not Blockchain.isValidMerkleRoot(block['merkleRoot'], block['transactions']):
                return False
            if not Blockchain.isValidTransaction(block['transactions']):
                return False
            if i-1 >= 0 and not Blockchain.isValidLastBlockHash(block['previousHash'], chain[i-1]):
                return False
        
        return True

    def resolveConflicts(self):
        for node in self.nodes:
            nodeChain = requests.get(f'{node}/chain').json()
            
            if len(nodeChain) > len(self.chain):
                self.chain = nodeChain

    @staticmethod
    def isValidProof(block, nonce):
        block['nonce'] = nonce
        return Blockchain.getBlockID(block)[:DIFFICULTY] == '0' * DIFFICULTY
    
    def isValidLastBlockHash(lastBlockHash, block):
        return lastBlockHash == Blockchain.getBlockID(block)
    
    def isValidTransaction(transactions):
        for transaction in transactions:
            if not Blockchain.verifySignature(transaction['sender'], transaction['signature'], json.dumps(transaction, sort_keys=True)):
                return False
        return True

    def createTransaction(self, sender, recipient, amount, timestamp, privWifKey): 
        tx = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'timestamp': timestamp
        }
 
        tx['signature'] = Blockchain.sign(privWifKey, json.dumps(tx, sort_keys=True))
        self.memPool.append(tx)

        return tx

    @staticmethod
    def generateMerkleRoot(transactions):
        if len(transactions) == 0:
            return '0'*64

        txHashes = [] 
        for tx in transactions:
            txHashes.append(Blockchain.generateHash(tx))

        return Blockchain._hashTxHashes(txHashes)

    @staticmethod
    def _hashTxHashes(txHashes):
        if len(txHashes) == 1: 
            return txHashes[0]

        if len(txHashes)%2 != 0:  
            txHashes.append(txHashes[-1])

        newTxHashes = []
        for i in range(0,len(txHashes),2):       
            newTxHashes.append(Blockchain.generateHash(txHashes[i] + txHashes[i+1]))
        
        return Blockchain._hashTxHashes(newTxHashes)

    def isValidMerkleRoot(merkleRoot, transactions):
        return Blockchain.generateMerkleRoot(transactions) == merkleRoot
    
    @staticmethod
    def generateHash(data):
        blkSerial = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(blkSerial).hexdigest()

    @staticmethod
    def getBlockID(block):
        blockCopy = copy.copy(block)
        blockCopy.pop("transactions", None)
        return Blockchain.generateHash(blockCopy)

    @property
    def prevBlock(self):
        return self.chain[-1]

    @staticmethod
    def getWifCompressedPrivateKey(private_key=None):
        if private_key is None:
            private_key = bitcoinlib.random_key()
        return bitcoinlib.encode_privkey(bitcoinlib.decode_privkey((private_key + '01'), 'hex'), 'wif')
        
    @staticmethod
    def getBitcoinAddressFromWifCompressed(wif_pkey):
        return bitcoinlib.pubtoaddr(bitcoinlib.privkey_to_pubkey(wif_pkey))

    @staticmethod
    def sign(wifCompressedPrivKey, message):
        return bitcoinlib.ecdsa_sign(message, wifCompressedPrivKey)

    @staticmethod
    def verifySignature(address, signature, message): 
        return bitcoinlib.ecdsa_verify(message, signature, address)

    def printChain(self):

        for block in reversed(self.chain) :

            if (block['index'] < len(self.chain)):
                print(32*' ', 'A', 39*' ')
                print(32*' ', '|', 39*' ')

            print(' __________________________________________________________________\n| {0:<0} |\
                \n ------------------------------------------------------------------\
                \n| Índice:         Timestamp:              Nonce:                   |\n| {1:<16d}{2:<24d}{3:<25d}|\
                \n|                                                                  |\
                \n| Merkle Root:                                                     |\n| {4:<0} |\
                \n|                                                                  |\
                \n| Transações:                                                      |\n| {5:<16d}                                                 |\
                \n|                                                                  |\
                \n| Hash do último bloco:                                            |\n| {6:<0} |\
                \n ------------------------------------------------------------------'\
                .format(Blockchain.getBlockID(block),block['index'],block['timestamp'],block['nonce'],block['merkleRoot'],len(block['transactions']),block['previousHash']))


