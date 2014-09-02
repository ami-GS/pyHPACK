import os, sys
import json
from HPACK import decode, encode
from tables import Table

TESTCASE = [
    #'hpack-test-case/haskell-http2-naive/',
    #'hpack-test-case/haskell-http2-naive-huffman/',
    #'hpack-test-case/haskell-http2-static/',
    #'hpack-test-case/haskell-http2-static-huffman/',
    'hpack-test-case/haskell-http2-linear/',
    #'hpack-test-case/haskell-http2-linear-huffman/',
]

def encodeTest():
    table = Table()
    for i in range(len(TESTCASE)):
        cases = [TESTCASE[i] + name for name in os.listdir(TESTCASE[i])]
        for case in cases:
            allPass = False
            miss = False
            with open(case) as f:
                data = json.loads(f.read())
                for seqno in range(len(data["cases"])):
                    try:
                        headers = [[h.keys()[0], h.values()[0]]for h in data["cases"][seqno]["headers"]]
                    except Exception as e:
                        print(e)
                    code = encode(headers, 'static' in case or 'linear' in case, 'linear' in case, 'huffman' in case, table) #init header table or not
                    if code != data["cases"][seqno]["wire"]:
                        print 'encoder:', code
                        print 'answer:', data["cases"][seqno]["wire"]
                        print("Missed in %s seqno %d" % (case, seqno))
                        miss = True
                        break
                #if miss:
                #    break
                if seqno == len(data["cases"]) - 1:
                    allPass = True
            if allPass:
                print('Passed the %s' % case)                        

def decodeTest():
    headers = None
    table = Table()
    for i in range(len(TESTCASE)):
        cases = [TESTCASE[i] + name for name in os.listdir(TESTCASE[i])]
        for case in cases:
            allPass = True
            with open(case) as f:
                data = json.loads(f.read())
                for seqno in range(len(data['cases'])):
                    try:
                        headers = decode(data['cases'][seqno]['wire'], table)
                    except Exception as e:
                        print(e)
                    if headers != data['cases'][seqno]['headers']:
                        allPass = False
                        print('Missed in %s seqno %d' % (case, seqno))
                        break
            if allPass:
                print('Passed the %s' % case)

def encode2decode():
    cases = [
        "hpack-test-case/haskell-http2-linear/",
        "hpack-test-case/haskell-http2-linear-huffman/",
    ]
    encoderTable = Table()
    decoderTable = Table()
    for i in range(len(cases)):
        stories = [cases[i] + name for name in os.listdir(cases[i])]
        for story in stories:
            allPass = True
            with open(story) as f:
                data = json.loads(f.read())
                for seqno in range(len(data["cases"])):
                    try:
                        headers = [[h.keys()[0], h.values()[0]] for h in data["cases"][seqno]["headers"]]
                    except Exception as e:
                        print(e)
                    wire = encode(headers, 'static' in story or 'linear' in story, 'linear' in story, 'huffman' in story, encoderTable) #init header table or not
                    headers = decode(wire, decoderTable)
                    if headers != data["cases"][seqno]["headers"]:
                        allPass = False
                        print(headers)
                        print('Missed in %s seqno %d' % (story, seqno))
                        break
            if allPass:
                print("Passed the %s" % story)



if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2 and args[1] == "-e":
        encodeTest()
    elif len(args) == 2 and args[1] == "-a":
        encode2decode()
    elif len(args) == 1 or (len(args) == 2 and args[1] == "-d"):
        decodeTest()


