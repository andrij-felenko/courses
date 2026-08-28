def create_table():
    a = []
    for i in range(256):
        k = i
        for j in range(8):
            if k & 1:
                k ^= 0x1db710640
            k >>= 1
        a.append(k)
    return a

def crc_update(buf, crc_table, crc):
    for k in buf:
        crc = (crc >> 8) ^ crc_table[(crc & 0xff) ^ k]
    return crc

crc_table = create_table()

file_crc = 0                                   # ← початкове значення НУЛЬ
for line in open(filename, "rb"):
    file_crc = crc_update(line, crc_table, file_crc)
                                               # ← фінального інвертування НЕМАЄ
