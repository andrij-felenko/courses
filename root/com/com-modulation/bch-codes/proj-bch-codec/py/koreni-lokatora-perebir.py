def chien_search(sigma):
    pos = []
    for i in range(N):                   # позиція x^i у слові
        val = 0
        for deg, c in enumerate(sigma):  # σ(α⁻ⁱ)
            if c:
                val ^= gf_mul(c, antilog[(N - (i * deg) % N) % N])
        if val == 0:
            pos.append(i)
    return pos
