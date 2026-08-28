    # 22 байти → 16 каналів по 11 біт, little-endian.
    def unpack_channels(self, p):
        acc  = 0   # накопичувач бітів
        bits = 0   # скільки валідних бітів зараз в acc
        ch   = 0   # індекс каналу
        for i in range(22):
            if ch >= 16:
                break
            acc |= p[i] << bits          # доливаємо байт зверху
            bits += 8
            while bits >= 11 and ch < 16:   # зчерпуємо всі готові канали
                self.channels[ch] = acc & 0x7FF   # нижні 11 біт
                ch += 1
                acc >>= 11
                bits -= 11
