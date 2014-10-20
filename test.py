import os, sys
import json
from HPACK import decode, encode
from tables import Table



TESTCASE = [
    'hpack-test-case/haskell-http2-naive/',
    'hpack-test-case/haskell-http2-naive-huffman/',
    'hpack-test-case/haskell-http2-static/',
    'hpack-test-case/haskell-http2-static-huffman/',
    'hpack-test-case/haskell-http2-linear/',
    'hpack-test-case/haskell-http2-linear-huffman/',
    'hpack-test-case/go-hpack/',
    'hpack-test-case/nghttp2/',
    'hpack-test-case/nghttp2-16384-4096/',
    'hpack-test-case/nghttp2-change-table-size/',
    'hpack-test-case/node-http2-hpack/'
]

def encodeTest():
    table = Table()
    for i in range(len(TESTCASE)):
        cases = [TESTCASE[i] + name for name in os.listdir(TESTCASE[i])]
        for case in cases:
            allPass = True
            with open(case) as f:
                data = json.loads(f.read())
                for seqno in range(len(data["cases"])):
                    if data["cases"][seqno].has_key("header_table_size"):
                        table.setMaxHeaderTableSize(int(data["cases"][seqno]["header_table_size"]))

                    headers = [[h.keys()[0], h.values()[0]]for h in data["cases"][seqno]["headers"]]
                    code = encode(headers, 'static' in case or 'linear' in case, 'linear' in case, 'huffman' in case, table) #init header table or not
                    if code != data["cases"][seqno]["wire"]:
                        allPass = False
                        print('encoder: %s' % code)
                        print('answer: %s' % data["cases"][seqno]["wire"])
                        print("Missed in %s seqno %d" % (case, seqno))
                        break
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
                    if data["cases"][seqno].has_key("header_table_size"):
                        table.setMaxHeaderTableSize(int(data["cases"][seqno]["header_table_size"]))
                    headers = decode(data['cases'][seqno]['wire'], table)
                    if headers != data['cases'][seqno]['headers']:
                        allPass = False
                        print('Missed in %s seqno %d' % (case, seqno))
                        break
            if allPass:
                print('Passed the %s' % case)

def encode2decode():
    encoderTable = Table()
    decoderTable = Table()
    for i in range(len(TESTCASE)):
        stories = [TESTCASE[i] + name for name in os.listdir(TESTCASE[i])]
        for story in stories:
            allPass = True
            with open(story) as f:
                data = json.loads(f.read())
                for seqno in range(len(data["cases"])):
                    if data["cases"][seqno].has_key("header_table_size"):
                        encoderTable.setMaxHeaderTableSize(int(data["cases"][seqno]["header_table_size"]))

                    headers = [[h.keys()[0], h.values()[0]] for h in data["cases"][seqno]["headers"]]
                    wire = encode(headers, 'static' in story or 'linear' in story, 'linear' in story, 'huffman' in story, encoderTable) #init header table or not
                    try:
                        if data["cases"][seqno].has_key("header_table_size"):
                            decoderTable.setMaxHeaderTableSize(int(data["cases"][seqno]["header_table_size"]))
                        decodedHeaders = decode(wire, decoderTable)
                        if decodedHeaders != data["cases"][seqno]["headers"]:
                            allPass = False
                            print('Missed in %s seqno %d' % (story, seqno))
                            break
                    except Exception as e:
                        print("Error at %s seqno %d" % (story, seqno))
                        allPass = False
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


