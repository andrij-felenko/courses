# LZW-декодування. Єдина тонкість — гілка code == next (випадок cScSc).
def lzw_decode(br, dst):
    dict_ = {i: bytes([i]) for i in range(256)}   # номер -> байти рядка
    next_, width = FIRST, 9

    prev = None
    first_of_prev = 0
    while True:
        code = br.get(width)
        if code == END:
            break
        if code == CLEAR:                    # скидання — почати наново
            dict_ = {i: bytes([i]) for i in range(256)}
            next_, width = FIRST, 9
            prev = None
            continue

        if code in dict_:                    # код є — звичайний випадок
            s = dict_[code]                  # розкласти запис у байти
        elif code == next_ and prev is not None:  # cScSc: код = наступний-вільний
            s = dict_[prev] + bytes([first_of_prev])  # це prev + перший байт prev
        else:
            return                           # зіпсований потік

        dst.extend(s)                        # вивести рядок
        first_of_cur = s[0]

        if prev is not None:                 # додати prev + перший байт поточного
            dict_[next_] = dict_[prev] + bytes([first_of_cur])
            next_ += 1
            if next_ > (1 << width) and width < MAXBITS:
                width += 1
        prev = code if code < next_ - 1 else next_ - 1   # новий prev (його номер)
        first_of_prev = first_of_cur
