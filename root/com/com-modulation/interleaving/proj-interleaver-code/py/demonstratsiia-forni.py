def run(inter, deinter, seq):
    chan = [inter.push(s) for s in seq]
    return chan, [deinter.push(s) for s in chan]


N, M = 6, 2
delay = M * N * (N - 1)                        # 60 символів наскрізної затримки
chan, out = run(ConvInterleaver(N, M), ConvDeinterleaver(N, M), list(range(1, 121)))
assert out[delay:] == list(range(1, 121))[:120 - delay]   # відновлено точно
print(out[delay:delay + 8])                    # [1, 2, 3, 4, 5, 6, 7, 8]
