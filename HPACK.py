import struct
import json

def parseIntRepresentation(buf, N):
    I = (buf[0] & ((1 << N) - 1))
    if I < (1 << N) - 1: 
        return I, 1
    else:
        cursor = 1
        M = 0
        while buf[cursor] & 0x80 == 0x80:
            I += (buf[cursor] & 0x7f) * (1 << M)
            M += 7
            cursor += 1
        I += (buf[cursor] & 0x7f) * (1 << M)
        return I, cursor


def encode(data):
    buf = [int(data[i:i+2], 16) for i in range(0, len(data), 2)]
    cursor = 0
    headers = []
    while cursor < len(buf):
        index = 0
        name = value = ""
        if buf[cursor] & 0x80:
            # 7.1 Indexd Header Field
            index, c = parseIntRepresentation(buf[cursor:], 7)
            cursor += c
        else :
            if buf[cursor] & 0x40:
                # 7.2.1 Literal Header Field with Incremental Indexing
                index, c = parseIntRepresentation(buf[cursor:], 6)
                cursor += c
            else if buf[cursor] & 0x10:
                # 7.2.3 Literal Header Field never Indexed
                index, c = parseIntRepresentation(buf[cursor:], 4)
                cursor += c
            else if buf[cursor] & 0x20:
                # 7.3 Header Table Size Update
                setMaxHeaderTableSize(buf[cursor] & 0x1f)
                cursor += 1        
            else:
                # 7.2.2 Literal Header Field without Indexing
                index, c = parseIntRepresentation(buf[cursor:], 4)
                cursor += c
            
            if not index:
                length, c = parseIntRepresentation(buf[cursor:], 7)
                cursor += c
    return headers

    

if __name__ == "__main__":
    testCase = []
    data = "1FA18DB701" #3000000
    buf = []
    buf = [int(data[i:i+2], 16) for i in range(0, len(data), 2)]    
    print(buf)
    print(parseIntRepresentation(buf, 5))

