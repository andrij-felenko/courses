CODEBOOK = {0: (0, 0, 0), 1: (1, 1, 1)}

def hamming(u, v):
    """Відстань Геммінга — скільки позицій різняться."""
    return sum(a != b for a, b in zip(u, v))

def decode_nearest(recv):
    """Загальний декодер: у кожному блоці обрати найближче кодове слово."""
    out = []
    for i in range(0, len(recv), 3):
        block = recv[i:i+3]
        out.append(min(CODEBOOK, key=lambda m: hamming(block, CODEBOOK[m])))
    return out
