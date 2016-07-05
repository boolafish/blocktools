from blocktools import *
from decimal import *
import hashlib


class BlockHeader:

    def __init__(self, blockchain):
        self.version = uint4(blockchain)
        self.previousHash = hash32(blockchain)
        self.merkleHash = hash32(blockchain)
        self.time = uint4(blockchain)
        self.bits = uint4(blockchain)
        self.nonce = uint4(blockchain)

    @property
    def difficulty(self):
        difficulty_1_target = 0x00000000FFFF0000000000000000000000000000000000000000000000000000
        last_six_bits = self.bits & 0x00FFFFFF
        nShift = int((self.bits >> 24) & 0xFF)
        dDiff = Decimal(0x0000FFFF) / Decimal(self.bits & 0x00FFFFFF)
        while nShift < 29:
            dDiff *= 256
            nShift += 1
        while nShift > 29:
            dDiff /= 256
            nShift -= 1
        return dDiff

    @property
    def blockhash(self):
        header_hex = (intLE(self.version) + hashStrLE(self.previousHash) + hashStrLE(self.merkleHash)
                      + intLE(self.time) + intLE(self.bits) + intLE(self.nonce))
        header_bin = header_hex.decode('hex')
        hash_ = hashlib.sha256(hashlib.sha256(header_bin).digest()).digest()
        return hash_[::-1].encode('hex_codec')

    @property
    def blockwork(self):
    	last_six_bits = self.bits & 0x00FFFFFF
    	first_two_bits = (self.bits >> 24) & 0xFF
    	target = last_six_bits * 2**(8*(first_two_bits-3))
    	return 2**256 / (target+1)
    
    def toString(self):
        print "Version:\t %d" % self.version
        print "Previous Hash\t %s" % hashStr(self.previousHash)
        print "Merkle Root\t %s" % hashStr(self.merkleHash)
        print "Time\t\t %s" % str(self.time)
        print "Bits\t\t %8x" % self.bits
        print "Difficulty\t %.8f" % self.difficulty
        print "Nonce\t\t %s" % self.nonce
        print "Hash\t\t %s" % self.blockhash


class Block:

    def __init__(self, blockchain):
        self.continueParsing = True
        self.magicNum = 0
        self.blocksize = 0
        self.blockheader = ''
        self.txCount = 0
        self.Txs = []
        self.scriptSig = ''

        if self.hasLength(blockchain, 8):
            self.magicNum = uint4(blockchain)
            self.blocksize = uint4(blockchain)
        else:
            self.continueParsing = False
            return

        if self.blocksize <= 0:
            self.continueParsing = False
            return

        if self.hasLength(blockchain, self.blocksize):
            self.setHeader(blockchain)
            self.txCount = varint(blockchain)
            self.Txs = []

            for i in range(0, self.txCount):
                tx = Tx(blockchain)
                self.Txs.append(tx)

            self.scriptLen = varint(blockchain)
            self.scriptSig = blockchain.read(self.scriptLen)
        else:
            self.continueParsing = False

    def continueParsing(self):
        return self.continueParsing

    def getBlocksize(self):
        return self.blocksize

    def hasLength(self, blockchain, size):
        curPos = blockchain.tell()
        blockchain.seek(0, 2)

        fileSize = blockchain.tell()
        blockchain.seek(curPos)

        tempBlockSize = fileSize - curPos
        print tempBlockSize
        if tempBlockSize < size:
            return False
        return True

    def setHeader(self, blockchain):
        self.blockHeader = BlockHeader(blockchain)

    def toString(self):
        print ""
        print "Magic No: \t%8x" % self.magicNum
        print "Blocksize: \t", self.blocksize
        print ""
        print "#" * 10 + " Block Header " + "#" * 10
        self.blockHeader.toString()
        print
        print "Script Sig: \t %s" % hashStr(self.scriptSig)
        print "##### Tx Count: %d" % self.txCount
        for t in self.Txs:
            t.toString()


class Tx:

    def __init__(self, blockchain):
        self.version = uint4(blockchain)
        self.inCount = varint(blockchain)
        self.inputs = []
        for i in range(0, self.inCount):
            input = txInput(blockchain)
            self.inputs.append(input)
        self.outCount = varint(blockchain)
        self.outputs = []
        if self.outCount > 0:
            for i in range(0, self.outCount):
                output = txOutput(blockchain)
                self.outputs.append(output)
        self.lockTime = uint4(blockchain)
        self.txType = uint4(blockchain)

    def toString(self):
        print ""
        print "=" * 10 + " New Transaction " + "=" * 10
        print "Tx Version:\t %d" % self.version
        print "Inputs:\t\t %d" % self.inCount
        for i in self.inputs:
            i.toString()

        print "Outputs:\t %d" % self.outCount
        for o in self.outputs:
            o.toString()
        print "Lock Time:\t %d" % self.lockTime
        print "TX TYPE:\t %d" % self.txType


class txInput:

    def __init__(self, blockchain):
        self.prevhash = hash32(blockchain)
        self.txOutId = uint4(blockchain)
        self.scriptLen = varint(blockchain)
        self.scriptSig = blockchain.read(self.scriptLen)
        self.seqNo = uint4(blockchain)

    def toString(self):
        print "--------------TX IN------------------------"
        print "Previous Hash:\t %s" % hashStr(self.prevhash)
        print "Tx Out Index:\t %8x" % self.txOutId
        print "Script Length:\t %d" % self.scriptLen
        print "Script Sig:\t %s" % hashStr(self.scriptSig)
        print "Sequence:\t %8x" % self.seqNo
        print "--------------------------------------------"


class txOutput:

    def __init__(self, blockchain):
        self.value = uint8(blockchain)
        self.scriptLen = varint(blockchain)
        self.pubkey = blockchain.read(self.scriptLen)
        self.color = uint4(blockchain)

    def toString(self):
        print "--------------TX OUT------------------------"
        print "Value:\t\t %d" % self.value
        print "Script Len:\t %d" % self.scriptLen
        print "Pubkey:\t\t %s" % hashStr(self.pubkey)
        print "Color:\t\t %d" % self.color
        print "---------------------------------------------"
