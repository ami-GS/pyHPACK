# 6.1 Integer Representation (encode)
def pack(I, N):
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

# 6.1 Integer Representation (decode)
def parse(buf, N):
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
