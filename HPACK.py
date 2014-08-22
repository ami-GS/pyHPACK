from tables import HuffmanTree, STATIC_TABLE, STATIC_TABLE_NUM, HeaderTable
HEADER_TABLE = HeaderTable()
huffmanRoot = HuffmanTree.create()

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

def packContent(content, huffman):
    wire = ""
    intRep = packIntRepresentation(len(content), 7)
    if huffman:
        intRep[0] = intRep[0] | 0x80
    #pack integer representation
    wire = wire + "".join([hex(b)[2:].zfill(2) for b in intRep]) 
    #pack content (header name or value)
    wire = wire + "".join([hex(ord(char))[2:].zfill(2) for char in content])

    return wire

def encode(headers, fromStaticTable, fromHeaderTable, huffman):
    wire = ""
    nameTable = [header[0] for header in STATIC_TABLE]

    for header in headers:

        # 7.1 Indexed Header Field Representation
        if fromStaticTable and header in STATIC_TABLE:
            # or header in HEADER_TALBE
            wire = wire + hex(STATIC_TABLE.index(header) | 0x80)[2:]
        
        # 7.2.1 Literal Header Field with Incremental Indexing
        elif fromStaticTable and header[0] in nameTable[:STATIC_TABLE_NUM]:
            if fromHeaderTalbe:
                wire = wire + hex(nameTable[:STATIC_TABLE_NUM].index(header) | 0x40)[2:]
            else:
                pass
                #wire = wire + hex(nameTable[:STATIC_TABLE_NUM].index(header))[2:]
                #wire = wire + hex(nameTable[:STATIC_TABLE_NUM].index(header) | 0x10)[2:]
            wire = wire + packContent(header[1], huffman)

        else:
            wire = wire + "00"# "10" "40"
            wire = wire + packContent(header[0], huffman)
            wire = wire + packContent(header[1], huffman)

    return wire


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
        content = huffmanRoot.decode(subBuf, length) 
    else:
        content = ""
        for i in range(length):
            content += chr(subBuf[i])
    return content

def parseHeader(index, subBuf, isIndexed):
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

    if 0 < index < STATIC_TABLE_NUM:
        header = STATIC_TABLE[index]
        name = header[0]
        value = value or header[1]
    elif STATIC_TABLE_NUM <= index <= STATIC_TABLE_NUM + HEADER_TABLE.currentEntryNum:
        header = HEADER_TABLE.get(index)
        name = header[0]
        value = value or header[1]
    else:
        pass #error
        
    return name, value, cursor

def decode(data):
    buf = [int(data[i:i+2], 16) for i in range(0, len(data), 2)]
    cursor = 0
    index = 0
    headers = []
    while cursor < len(buf):
        isIndexed = False
        isIncremental = False
        if buf[cursor] & 0xe0 == 0x20:
            # 7.3 Header Table Size Update
           HEADER_TABLE.setMaxHeaderTableSize(buf[cursor] & 0x1f)
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

        name, value, c = parseHeader(index, buf[cursor:], isIndexed)
        cursor += c

        if isIncremental:
            HEADER_TABLE.add(name, value)
        headers.append({name:value})

    return headers

if __name__ == "__main__":
    data = "1FA18DB701" #3000000
    data = "00073a6d6574686f640347455400073a736368656d650468747470000a3a617574686f726974790f7777772e7961686f6f2e636f2e6a7000053a70617468012f"
    #print(decode(data))
    for i in packIntRepresentation(3000000, 5):
        print hex(i)
    #print parseIntRepresentation("".join([str(hex(b))[2:] for b in buf]), 5)
