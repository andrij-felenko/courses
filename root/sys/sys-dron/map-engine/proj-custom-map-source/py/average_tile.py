# average_tile.py — виміряти середній тайл свого сервера на робочому рівні
import random, statistics, urllib.request

TEMPLATE = "https://tiles.skylark.example/ortho/{z}/{x}/{y}.jpg"
TOKEN    = "ce9f4a2b18"
Z        = 18
X0, X1   = 153280, 153320      # прямокутник типової ділянки в номерах клітинок
Y0, Y1   = 88370,  88400

sizes = []
for _ in range(100):
    x, y = random.randint(X0, X1), random.randint(Y0, Y1)
    req = urllib.request.Request(TEMPLATE.format(z=Z, x=x, y=y),
                                 headers={"User-Token": TOKEN})
    with urllib.request.urlopen(req) as r:
        if r.status == 200:
            sizes.append(len(r.read()))

print("середнє", round(statistics.mean(sizes)))
print("медіана", round(statistics.median(sizes)))
