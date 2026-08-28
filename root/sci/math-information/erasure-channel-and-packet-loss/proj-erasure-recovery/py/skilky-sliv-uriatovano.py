G = [[1,0,0,0, 1,1,0],
     [0,1,0,0, 0,1,1],
     [0,0,1,0, 1,1,1],
     [0,0,0,1, 1,0,1]]
H = [[1,0,1,1, 1,0,0],
     [1,1,1,0, 0,1,0],
     [0,1,1,1, 0,0,1]]

def encode(msg):
    return [sum(msg[i] * G[i][j] for i in range(4)) % 2 for j in range(7)]

rng = random.Random(7)
c = encode([1, 0, 1, 1])                      # 1 0 1 1 1 0 0
for p in (0.1, 0.3, 0.5):
    ok = sum(recover(H, erasure_channel(c, p, rng)) == c for _ in range(20000))
    print(f"p = {p}:  відновлено {ok / 20000:.3f}")
