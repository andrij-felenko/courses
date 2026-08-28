# draw.py — SVG-мапа DH з ТИХ САМИХ даних, що й ворота. Ребра беремо з MAP, не з голови.
import math

SHORT = {"partnership": "партн.", "customer-supplier": "зам.-пост.",
         "conformist": "конф.", "published-language": "оп. мова",
         "shared-kernel": "ядро", "separate-ways": "окр. шляхи", "acl": "ACL"}

def draw(path):
    names = list(MAP)
    cx, cy, R = 430, 300, 250
    pos = {n: (cx + R * math.cos(-math.pi / 2 + 2 * math.pi * i / len(names)),
               cy + R * math.sin(-math.pi / 2 + 2 * math.pi * i / len(names)))
           for i, n in enumerate(names)}
    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 620">']
    for n, meta in MAP.items():                       # ← ребра лише з даних
        for to, kind in meta["allow"].items():
            (x1, y1), (x2, y2) = pos[n], pos[to]
            p.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="#333"/>'
                     % (x1, y1, x2, y2))
            p.append('<text x="%.0f" y="%.0f" font-size="10" text-anchor="middle">%s</text>'
                     % ((x1 + x2) / 2, (y1 + y2) / 2, SHORT[kind]))
    for n, (x, y) in pos.items():
        p.append('<circle cx="%.0f" cy="%.0f" r="34" fill="#eef" stroke="#333"/>' % (x, y))
        p.append('<text x="%.0f" y="%.0f" font-size="11" text-anchor="middle">%s</text>'
                 % (x, y, n))
    p.append("</svg>")
    open(path, "w", encoding="utf-8").write("\n".join(p))
