import os
import json
from HPACK import decode


TESTCASE = [
    'hpack-test-case/haskell-http2-naive/',
#    'hpack-test-case/haskell-http2-naive-huffman/',
#    'hpack-test-case/haskell-http2-static/',
#    'hpack-test-case/haskell-http2-static-huffman/',
#    'hpack-test-case/haskell-http2-linear/',
#    'hpack-test-case/haskell-http2-linear-huffman/',
]


if __name__ == "__main__":
    headers = None
    for i in range(len(TESTCASE)):
        cases = [TESTCASE[i] + name for name in os.listdir(TESTCASE[i])]
        for case in cases:
            allPass = False
            with open(case) as f:
                data = json.loads(f.read())
                for seqno in range(len(data['cases'])):
                    try:
                        headers = decode(data['cases'][seqno]['wire'])
                    except Exception as e:
                        print(e)
                    for header in data['cases'][seqno]['headers']:
                        if header not in headers:
                            print header
                            print headers[header.keys()[0]]
                            print('Missed the in %s seqno %d' % (case, seqno))
                            break
                    if seqno == len(data['cases'])-1:
                        allPass = True
            if allPass:
                print('Passed the %s' % case)
