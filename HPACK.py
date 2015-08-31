from tables import HuffmanTree
import int_representation as intRepresent
from binascii import unhexlify
import struct

huffmanRoot = HuffmanTree.create()

def serialize(content, isString = False):
    wire = 0
    for c in content:
        wire <<= 8
        wire |= ord(c) if isString else c
    return unhexlify(hex(wire)[2:].rstrip("L").zfill(len(content) * 2))

def packContent(content, huffman):
    wire = ""
    if not content:
        # when value is ''
        return '\x80' if huffman else '\x00'
    if huffman:
        enc, actualLen = HuffmanTree.encode(content)
        intRep = intRepresent.pack(actualLen, 7)
        intRep[0] |= 0x80
        wire += serialize(intRep) + enc
    else:
        intRep = intRepresent.pack(len(content), 7)
        wire += serialize(intRep) + serialize(content, True)
    return wire

def encode(headers, fromStaticTable, fromDynamicTable, huffman, table, dynamicTableSize = -1):
    wire = ""
    if dynamicTableSize != -1:
        intRep = intRepresent.pack(dynamicTableSize, 5)
        intRep[0] |= 0x20
        wire += serialize(intRep)

    for header in headers:
        match = table.find(header[0], header[1])
        # 7.1 Indexed Header Field Representation
        if fromStaticTable and match[0]:
            suffix = ""
            if fromDynamicTable:
                intRep = intRepresent.pack(match[1], 7)
                intRep[0] |= 0x80
                wire += serialize(intRep)
            else:
                intRep = intRepresent.pack(match[1], 4)
                wire += serialize(intRep) + packContent(header[1], huffman)
        # 7.2.1 Literal Header Field with Incremental Indexing
        elif fromStaticTable and not match[0] and match[1]:
            if fromDynamicTable:
                intRep = intRepresent.pack(match[1], 6)
                intRep[0] |= 0x40
                table.add(header)
            else:
                intRep = intRepresent.pack(match[1], 4)
            wire += serialize(intRep) + packContent(header[1], huffman)
        else:
            content = packContent(header[0], huffman) + packContent(header[1], huffman)
            prefix = "\x00"
            if fromDynamicTable:
                prefix = "\x40"
                table.add(header)
            wire += prefix + content

    return wire

def parseHeader(index, table, subBuf, isIndexed):
    def parseFromByte(buf):
        length, cursor = intRepresent.parse(buf, 7)
        if buf[0] & 0x80:
            content = huffmanRoot.decode(buf[cursor:], length)
        else:
            content = "".join([chr(buf[cursor+i]) for i in range(length)])
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
    buf = struct.unpack(">"+str(len(data))+"B", data)
    cursor = 0
    headers = []
    while cursor < len(buf):
        isIndexed = False
        if buf[cursor] & 0xe0 == 0x20:
            # 7.3 Header Table Size Update
            size, c = intRepresent.parse(buf[cursor:], 5)
            table.setHeaderTableSize(size)
            cursor += c

        nLen = 0
        if buf[cursor] & 0x80:
            # 7.1 Indexd Header Field
            if not buf[cursor] & 0x7f:
                print("error")
            nLen = 7
            isIndexed = True
        else :
            if buf[cursor] & 0xc0 == 0x40:
                # 7.2.1 Literal Header Field with Incremental Indexing
                nLen = 6
            else:
                # 7.2.3 Literal Header Field never Indexed
                # 7.2.2 Literal Header Field without Indexing
                nLen = 4
        index, c1 = intRepresent.parse(buf[cursor:], nLen)
        name, value, c2 = parseHeader(index, table, buf[cursor+c1:], isIndexed)
        cursor += c1 + c2

        if nLen == 6:
            table.add([name, value])
        headers.append({name:value})

    return headers

if __name__ == "__main__":
    data = "1FA18DB701" #3000000
    data = "00073a6d6574686f640347455400073a736368656d650468747470000a3a617574686f726974790f7777772e7961686f6f2e636f2e6a7000053a70617468012f"
    for i in intRepresent.pack(3000000, 5):
        print(hex(i))
    #print intRepresent.parse("".join([str(hex(b))[2:] for b in buf]), 5)
