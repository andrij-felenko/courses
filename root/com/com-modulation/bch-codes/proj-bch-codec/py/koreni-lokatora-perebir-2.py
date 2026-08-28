def decode(r):
    S = syndromes(r)
    if not any(S):                       # усі синдроми нулі — слово чисте
        return r, []
    sigma, L = berlekamp_massey(S)
    pos = chien_search(sigma)
    if len(pos) != L:                    # знайшли не L коренів → >t помилок
        raise ValueError("понад t помилок: декодування неможливе")
    corrected = r
    for p in pos:
        corrected ^= 1 << p              # у двійковому коді просто перевертаємо
    return corrected, pos
