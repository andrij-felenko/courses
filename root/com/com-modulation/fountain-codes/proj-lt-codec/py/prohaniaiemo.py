import os
k, bs = 1000, 64
data   = os.urandom(k * bs)
blocks = [data[i * bs:(i + 1) * bs] for i in range(k)]
mu  = robust_soliton(k)
enc = LTEncoder(blocks, mu)
dec = LTDecoder(k, mu)

seed = 0
while not dec.done():
    dec.add(*enc.droplet(seed))
    seed += 1

assert dec.file() == data
print(f"зібрано з {seed} крапель — надлишок {seed / k:.3f}")
