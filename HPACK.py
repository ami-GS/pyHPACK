from tables import HuffmanTree

huffmanRoot = HuffmanTree.create()
    
# 6.1 Integer Representation (encode)
def packIntRepresentation(I, N):
    if I < (1 << N) - 1:
        return [I]
    else:
        buf = [(1 << N) - 1]
        I -= (1 << N) - 1
        while I >= 0x80:
            buf.append(I & 0x7f | 0x80)
            I = (I >> 7)
        buf.append(I)
        return buf

def serialize(content, isString = False):
    wire = 0
    for c in content:
        wire <<= 8
        wire |= ord(c) if isString else c
    return hex(wire)[2:].rstrip("L").zfill(len(content) * 2)

def packContent(content, huffman):
    wire = ""
    if huffman:
        if not content:
            # when value is ''
            return '80'
        enc, actualLen = HuffmanTree.encode(content)
        intRep = packIntRepresentation(actualLen, 7)
        intRep[0] |= 0x80
        wire += serialize(intRep) + enc
    else:
        if not content:
            return "00"
        intRep = packIntRepresentation(len(content), 7)
        wire += serialize(intRep) + serialize(content, True)
    return wire

def encode(headers, fromStaticTable, fromHeaderTable, huffman, table, headerTableSize = -1):
    wire = ""
    if headerTableSize != -1:
        intRep = packIntRepresentation(headerTableSize, 5)
        intRep[0] |= 0x20
        wire += serialize(intRep)

    for header in headers:
        match = table.find(header[0], header[1])
        # 7.1 Indexed Header Field Representation
        if fromStaticTable and match[0]:
            indexLen = 7 if fromHeaderTable else 4
            intRep = packIntRepresentation(match[1], indexLen)
            intRep[0] |= 0x80 if fromHeaderTable else 0x00
            wire += serialize(intRep)
            if not fromHeaderTable:
                wire += packContent(header[1], huffman)

        # 7.2.1 Literal Header Field with Incremental Indexing
        elif fromStaticTable and not match[0] and match[1]:
            if fromHeaderTable:
                intRep = packIntRepresentation(match[1], 6)
                intRep[0] |= 0x40
                table.add(header)
            else:
                intRep = packIntRepresentation(match[1], 4)
                intRep[0] |= 0x00
            wire += serialize(intRep) + packContent(header[1], huffman)
        else:
            content = packContent(header[0], huffman) + packContent(header[1], huffman)
            prefix = "40" if fromHeaderTable else "00"
            wire += prefix + content
            if fromHeaderTable:
                table.add(header)

    return wire

# 6.1 Integer Representation (decode)
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
        return huffmanRoot.decode(subBuf, length) 
    else:
        return "".join([chr(subBuf[i]) for i in range(length)])

def parseHeader(index, table, subBuf, isIndexed):
    def parseFromByte(buf):
        isHuffman = buf[0] & 0x80
        length, cursor = parseIntRepresentation(buf, 7)
        content = extractContent(buf[cursor:], length, isHuffman)
        cursor += length
        return content, cursor

    cursor = 0
    name = value = ""
    if not isIndexed:
        if not index:
            name, c = parseFromByte(subBuf[cursor:])
            cursor += c
        value, c = parseFromByte(subBuf[cursor:])
        cursor += c

    if index:
        header = table.get(index)
        name = header[0]
        value = value or header[1]
        
    return name, value, cursor

def decode(data, table):
    buf = [int(data[i:i+2], 16) for i in range(0, len(data), 2)]
    cursor = 0
    headers = []
    while cursor < len(buf):
        isIndexed = False
        isIncremental = False
        if buf[cursor] & 0xe0 == 0x20:
            # 7.3 Header Table Size Update
           table.setMaxHeaderTableSize(buf[cursor] & 0x1f)
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

        name, value, c = parseHeader(index, table, buf[cursor:], isIndexed)
        cursor += c

        if isIncremental:
            table.add([name, value])
        headers.append({name:value})

    return headers

if __name__ == "__main__":
    data = "1FA18DB701" #3000000
    data = "00073a6d6574686f640347455400073a736368656d650468747470000a3a617574686f726974790f7777772e7961686f6f2e636f2e6a7000053a70617468012f"
    for i in packIntRepresentation(3000000, 5):
        print(hex(i))
    #print parseIntRepresentation("".join([str(hex(b))[2:] for b in buf]), 5)
