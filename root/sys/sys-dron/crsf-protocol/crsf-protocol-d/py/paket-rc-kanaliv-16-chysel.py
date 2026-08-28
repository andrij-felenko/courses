# 22 байти даних → 16 каналів по 11 біт, little-endian
# Ідея: тримаємо «конвеєр бітів» у цілочисловому акумуляторі
def crsf_unpack_channels(data):
    ch = []
    acc = 0    # накопичувач бітів
    bits = 0   # скільки валідних бітів зараз в acc
    for i in range(22):
        if len(ch) >= 16:
            break
        acc |= data[i] << bits   # додаємо байт зверху
        bits += 8
        if bits >= 11:           # назбиралось на канал
            ch.append(acc & 0x7FF)  # нижні 11 біт = 0x7FF
            acc >>= 11            # прибираємо їх
            bits -= 11
    return ch

# data = bytes([0xE8, 0x03, 0x9F, ...]):
#   i=0: acc = 0x0000_00E8, bits = 8   (8 < 11, ще рано)
#   i=1: acc |= 0x03 << 8 = 0x0000_03E8, bits = 16
#        16 >= 11 → ch[0] = 0x03E8 & 0x7FF = 0x3E8 = 1000
#        acc >>= 11 → 0, bits = 5
#   … канал 0 = 1000 (сире значення CRSF)
