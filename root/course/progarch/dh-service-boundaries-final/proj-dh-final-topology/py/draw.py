# draw.py — SVG-топологія DH з ТИХ САМИХ даних, що й сторож. Дах стрілки = стиль зі СПИСКУ.
from topology import DEPLOYMENTS, SEAMS
BAND = {"client": 60, "door": 300, "cloud": 560, "edge": 60, "external": 830}   # x за місцем

def draw(path):
    lanes, pos = {}, {}
    for name, d in DEPLOYMENTS.items():                 # вузли стосами у своїй смузі-місці
        x = BAND[d["place"]]
        pos[name] = (x, 90 + lanes.get(x, 0) * 92)
        lanes[x] = lanes.get(x, 0) + 1
    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1040 640">']
    for s in SEAMS:                                     # ← ребра ЛИШЕ з даних
        (x1, y1), (x2, y2) = pos[s["from"]], pos[s["to"]]
        dash = "" if s["style"] == "sync" else ' stroke-dasharray="7,6"'   # СТИЛЬ → ДАХ стрілки
        p.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="#333"%s/>'
                 % (x1 + 60, y1, x2, y2, dash))
    for name, (x, y) in pos.items():
        mark = " ⛁" if DEPLOYMENTS[name]["db"] else ""                     # своя база — значок
        p.append('<rect x="%.0f" y="%.0f" width="120" height="42" rx="6" fill="#eef" stroke="#333"/>'
                 % (x, y - 21))
        p.append('<text x="%.0f" y="%.0f" font-size="11" text-anchor="middle">%s</text>'
                 % (x + 60, y + 4, name + mark))
    p.append("</svg>")
    open(path, "w", encoding="utf-8").write("\n".join(p))
