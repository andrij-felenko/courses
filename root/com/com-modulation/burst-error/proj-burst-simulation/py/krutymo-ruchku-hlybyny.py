from collections import Counter

NW, W = 64000, 7
rng = random.Random(1)
data = [[rng.randint(0, 1) for _ in range(4)] for _ in range(NW)]
codewords = [h74_encode(d) for d in data]
mask, runs = ge_mask(NW * W)           # маска каналу — одна на всі глибини

def run(D):
    air = interleave(codewords, D)
    air = [b ^ m for b, m in zip(air, mask)]     # канал псує біти
    recv = deinterleave(air, D, W, NW)
    bit_err = 0
    hist = Counter()
    for i in range(NW):
        chan = sum(a ^ b for a, b in zip(codewords[i], recv[i]))  # помилок каналу у слові
        hist[chan] += 1
        dec = h74_decode(recv[i])
        bit_err += sum(a ^ b for a, b in zip(data[i], dec))       # залишок у даних
    return bit_err / (NW * 4), hist

for D in [1, 2, 4, 8, 16, 32, 64, 128, 256]:
    ber, _ = run(D)
    print("D=%-4d  залишковий BER даних = %.6f" % (D, ber))
