import os, sys
import json
from HPACK import decode, encode


TESTCASE = [
    'hpack-test-case/haskell-http2-naive/',
    'hpack-test-case/haskell-http2-naive-huffman/',
    'hpack-test-case/haskell-http2-static/',
    'hpack-test-case/haskell-http2-static-huffman/',
    'hpack-test-case/haskell-http2-linear/',
    'hpack-test-case/haskell-http2-linear-huffman/',
]

def encodeTest():
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
                    code = encode(headers, False, False, False)
                    if code != data["cases"][seqno]["wire"]:
                        print("Missed in %s seqno %d" % (case, seqno))
                        miss = True
                        break
                if miss:
                    break
                if seqno == len(data["cases"]) - 1:
                    allPass = True
            if allPass:
                print('Passed the %s' % case)                        

def decodeTest():
    headers = None
    for i in range(len(TESTCASE)):
        cases = [TESTCASE[i] + name for name in os.listdir(TESTCASE[i])]
        for case in cases:
            allPass = False
            miss = False
            with open(case) as f:
                data = json.loads(f.read())
                for seqno in range(len(data['cases'])):
                    try:
                        headers = decode(data['cases'][seqno]['wire'])
                    except Exception as e:
                        print(e)
                    for i, header in enumerate(headers):
                        if header not in data['cases'][seqno]['headers']:
                            miss = True
                            print i, header
                            print('Missed in %s seqno %d' % (case, seqno))
                    if miss:
                        break
                    if seqno == len(data['cases'])-1:
                        allPass = True
            if allPass:
                print('Passed the %s' % case)


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2 and args[1] == "-e":
        encodeTest()
    elif len(args) == 1 or (len(args) == 2 and args[1] == "-d"):
        decodeTest()
