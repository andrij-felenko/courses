def interleave(words, D):
    """Пише D слів у рядки, читає стовпцями → плаский потік бітів ефіру."""
    W = len(words[0]); air = []
    for base in range(0, len(words), D):
        block = words[base:base + D]
        for col in range(W):
            for row in range(D):
                air.append(block[row][col])
    return air

def deinterleave(air, D, W, nwords):
    """Зворотна дія: складає стовпці назад у D×W і повертає слова."""
    words = []; per = D * W
    for base in range(0, len(air), per):
        chunk = air[base:base + per]
        block = [[0] * W for _ in range(D)]
        k = 0
        for col in range(W):
            for row in range(D):
                block[row][col] = chunk[k]; k += 1
        words.extend(block)
    return words[:nwords]
