import struct
import json
from tables import HuffmanTree, STATIC_TABLE, HeaderTable
HEADER_TABLE = HeaderTable()
root = HuffmanTree.create()

def parseIntRepresentation(buf, N):
    I = (buf[0] & ((1 << N) - 1))
    cursor = 1
    if I < (1 << N) - 1: 
        return I, cursor
    else:
        M = 0
        while buf[cursor] & 0x80:
            I += (buf[cursor] & 0x7f) * (1 << M)
            M += 7
            cursor += 1
        I += (buf[cursor] & 0x7f) * (1 << M)
        return I, cursor + 1

def extractContent(subBuf, length, isHuffman):
    if isHuffman:
        content = root.decode(subBuf, length) 
    else:
        content = ""
        for i in range(length):
            content += chr(subBuf[i])
    return content

def parseHeader(index, subBuf):
    cursor = 0
    name = value = ""
    header = None
    if 0 < index < 62:
        header = STATIC_TABLE[index]
        name = header[0]
        value = header[1]
    elif not index:
        name_length, c = parseIntRepresentation(subBuf[cursor:], 7)
        cursor += c
        name = extractContent(subBuf[cursor:], name_length)
        cursor += name_length        

    if not value:
        value_length, c = parseIntRepresentation(subBuf[cursor:], 7)
        cursor += c
        value = extractContent(subBuf[cursor:], value_length)
        cursor += value_length
        
    return name, value, cursor

def decode(data):
    buf = [int(data[i:i+2], 16) for i in range(0, len(data), 2)]
    cursor = 0
    index = 0
    headers = []
    while cursor < len(buf):
        isIndexed = False
        isIncremental = False
        name = value = ""
        if buf[cursor] & 0xe0 == 0x20:
            # 7.3 Header Table Size Update
            #setMaxHeaderTableSize(buf[cursor] & 0x1f)
            cursor += 1
        elif buf[cursor] & 0x80:
            # 7.1 Indexd Header Field
            if not buf[cursor] & 0x7f:
                print("error")
            index, c = parseIntRepresentation(buf[cursor:], 7)
            cursor += c
            isIndexed = True
        else :
            if buf[cursor] & 0xc0 == 0x40:
                # 7.2.1 Literal Header Field with Incremental Indexing
                index, c = parseIntRepresentation(buf[cursor:], 6)
                isIncremental = True
            elif buf[cursor] & 0xf0 == 0xf0:
                # 7.2.3 Literal Header Field never Indexed
                index, c = parseIntRepresentation(buf[cursor:], 4)
            else:
                # 7.2.2 Literal Header Field without Indexing
                index, c = parseIntRepresentation(buf[cursor:], 4)
            cursor += c

        #name, value, c = parseHeader(index, buf[cursor:], isIndexed)
        #cursor += c
            if not index:
                isHuffman = buf[cursor] & 0x80
                name_length, c = parseIntRepresentation(buf[cursor:], 7)
                cursor += c
                name = extractContent(buf[cursor:], name_length, isHuffman)
                cursor += name_length

            isHuffman = buf[cursor] & 0x80
            value_length, c = parseIntRepresentation(buf[cursor:], 7)
            cursor += c
            value = extractContent(buf[cursor:], value_length, isHuffman)
            cursor += value_length

        if 0 < index < 62:
            header = STATIC_TABLE[index]
            name = header[0]
            value = value or header[1]
        elif 62 <= index <  63 + HEADER_TABLE.currentEntryNum:
            header = HEADER_TABLE.get(index)
            name = header[0]
            value = value or header[1]
        else:
            pass #error

        if isIncremental:
            HEADER_TABLE.add(name, value)
        headers.append({name:value})

    return headers

    

if __name__ == "__main__":
    testCase = []
    data = "1FA18DB701" #3000000
    data = "00073a6d6574686f640347455400073a736368656d650468747470000a3a617574686f726974790f7777772e7961686f6f2e636f2e6a7000053a70617468012f"
    print(decode(data))
