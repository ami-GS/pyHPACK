import struct
import json

STATIC_TABLE = [
    ["",""],
    [":authority" ""],
    [":method", "GET"],
    [":method", "POST"],
    [":path", "/"],
    [":path", "/index.html"],
    [":scheme", "http"],
    [":scheme", "https"],
    [":status", "200"],
    [":status", "204"],
    [":status", "206"],
    [":status", "304"],
    [":status", "400"],
    [":status", "404"],
    [":status", "500"],
    ["accept-charset", ""],
    ["accept-encoding", "gzip,deflate"],
    ["accept-language", ""],
    ["accept-ranges", ""],
    ["accept", ""],
    ["access-control-allow-origin", ""],
    ["age", ""],
    ["allow", ""],
    ["authorization", ""],
    ["cache-control", ""],
    ["content-disposition", ""],
    ["content-encoding", ""],
    ["content-language", ""],
    ["content-length", ""],
    ["content-location", ""],
    ["content-range", ""],
    ["content-type", ""],
    ["cookie", ""],
    ["date", ""],
    ["etag", ""],
    ["expect", ""],
    ["expires", ""],
    ["from", ""],
    ["host", ""],
    ["if-match", ""],
    ["if-modified-since", ""],
    ["if-none-match", ""],
    ["if-range", ""],
    ["if-unmodified-since", ""],
    ["last-modified", ""],
    ["link", ""],
    ["location", ""],
    ["max-forwards", ""],
    ["proxy-authenticate", ""],
    ["proxy-authorization", ""],
    ["range", ""],
    ["referer", ""],
    ["refresh", ""],
    ["retry-after", ""],
    ["server", ""],
    ["set-cookie", ""],
    ["strict-transport-security", ""],
    ["transfer-encoding", ""],
    ["user-agent", ""],
    ["vary", ""],
    ["via", ""],
    ["www-authenticate", ""],
]

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

def extractContent(subBuf, length):
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
            isIncremental = False
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
                name_length, c = parseIntRepresentation(buf[cursor:], 7)
                cursor += c
                name = extractContent(buf[cursor:], name_length)
                cursor += name_length
            
            value_length, c = parseIntRepresentation(buf[cursor:], 7)
            cursor += c
            value = extractContent(buf[cursor:], value_length)
            cursor += value_length
        
        if index > 0:
            header = STATIC_TABLE[index]
            name = header[0]
            value = value or header[1]

        headers.append({name:value})

    return headers

    

if __name__ == "__main__":
    testCase = []
    data = "1FA18DB701" #3000000
    buf = []
    buf = [int(data[i:i+2], 16) for i in range(0, len(data), 2)]    
    print(buf)
    print(parseIntRepresentation(buf, 5))

