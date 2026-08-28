# LZW-кодування. Словник: ключ (prefix, byte) -> номер. Рядок ніколи не
# зберігаємо цілком — лише його останній байт і номер «хвоста без останнього».
CLEAR, END, FIRST = 256, 257, 258
MAXBITS = 12
MAXCODE = (1 << MAXBITS) - 1   # 4095

def lzw_encode(src, bw):
    dict_ = {}                          # (prefix, byte) -> номер
    next_, width = FIRST, 9
    bw.put(CLEAR, width)                # почати зі скидання — поширена угода

    w = -1                              # -1 = «порожній рядок»
    for c in src:
        if w == -1:                     # перший байт — просто стає w
            w = c
            continue
        found = dict_.get((w, c))
        if found is not None:
            w = found                   # wc у словнику — нарощуємо
        else:
            bw.put(w, width)            # видати код(w)
            dict_[(w, c)] = next_       # додати wc
            next_ += 1
            if next_ > (1 << width) and width < MAXBITS:
                width += 1              # номер переріс ширину — +1 біт
            if next_ > MAXCODE:         # словник повний
                bw.put(CLEAR, width)    # сигнал скидання
                dict_.clear()
                next_, width = FIRST, 9
            w = c                       # новий збіг
    if w != -1:
        bw.put(w, width)               # хвіст
    bw.put(END, width)
