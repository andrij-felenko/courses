import math

m, phi = 2.0, math.radians(20)
N1, N2 = 20, 40

# ділильні, основні кола й кола вершин (головка зуба заввишки m)
r1, r2 = m*N1/2, m*N2/2
rb1, rb2 = r1*math.cos(phi), r2*math.cos(phi)
ra1, ra2 = r1 + m, r2 + m               # радіуси кіл вершин
a = r1 + r2                             # міжосьова відстань

# довжина активної ділянки лінії зачеплення (перетини кіл вершин з лінією)
line = (math.sqrt(ra1**2 - rb1**2) + math.sqrt(ra2**2 - rb2**2)
        - a*math.sin(phi))
pb = math.pi * m * math.cos(phi)        # основний крок
eps = line / pb

print(round(pb, 3), round(eps, 3))      # 5.904  1.635
