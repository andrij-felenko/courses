from collections import Counter

D, N = 5, 8                                       # 5 слів по 8 символів
msg = [(w, p) for w in range(D) for p in range(N)]
perm = block_perm(D, N)
chan = interleave(msg, perm)

burst = range(12, 22)                             # канал б'є: 10 символів поспіль
chan = ["×" if k in burst else s for k, s in enumerate(chan)]

recv = Counter(k // N for k, s in enumerate(deinterleave(chan, perm)) if s == "×")
print(dict(sorted(recv.items())))                 # {0: 2, 1: 2, 2: 2, 3: 2, 4: 2}
