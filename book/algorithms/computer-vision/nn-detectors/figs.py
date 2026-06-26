# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── anchors-iou: сітка клітинок + набір якорів на клітинці + IoU-перетин ───────
# Ідея: кадр ділять на сітку; у кожній клітинці сидить набір фіксованих
# форм-«якорів»; ground-truth-рамку приписують тому якореві, чий IoU із нею
# найбільший. Праворуч — як рахується сам IoU: перетин / об'єднання.

def fig_anchors_iou():
    W, H = 820, 388
    p = []

    # ── ЛІВА панель: кадр із сіткою S×S і набором якорів на одній клітинці ──
    gx, gy = 36, 70
    cell = 56
    S = 4
    p.append(text(gx + S * cell / 2, gy - 14, "сітка S×S на кадрі", size=11.5, color=INK, bold=True))
    # темне «зображення» під сіткою
    p.append(rect(gx, gy, S * cell, S * cell, fill="#0f172a", stroke=INK, sw=1.2, rx=6))
    for i in range(1, S):
        p.append(line(gx + i * cell, gy, gx + i * cell, gy + S * cell, color="#33415588", sw=1))
        p.append(line(gx, gy + i * cell, gx + S * cell, gy + i * cell, color="#33415588", sw=1))

    # ground-truth-рамка цілі (зелена) поперек кількох клітинок
    gt_x, gt_y, gt_w, gt_h = gx + cell * 0.7, gy + cell * 1.15, cell * 1.9, cell * 1.25
    p.append(rect(gt_x, gt_y, gt_w, gt_h, fill="#27ae6022", stroke=FIELD, sw=2.4, rx=3))
    p.append(text(gt_x + gt_w / 2, gt_y - 6, "ground-truth", size=9.5, color=FIELD, bold=True))

    # «відповідальна» клітинка (де центр цілі) — підсвітити
    cc, cr = 1, 1  # колонка, рядок клітинки з центром
    p.append(rect(gx + cc * cell, gy + cr * cell, cell, cell, fill="#c0392b22", stroke=POS, sw=2, rx=2))
    p.append(circle(gt_x + gt_w / 2, gt_y + gt_h / 2, 3.5, fill=POS, stroke=BG, sw=1))

    # набір із трьох якорів, намальованих із центру тієї клітинки (різні форми)
    acx, acy = gx + cc * cell + cell / 2, gy + cr * cell + cell / 2
    anchors = [(46, 30), (28, 46), (40, 40)]  # широкий, високий, квадрат
    acol = ["#60a5fa", "#fbbf24", "#f472b6"]
    for (aw, ah), col in zip(anchors, acol):
        p.append(rect(acx - aw / 2, acy - ah / 2, aw, ah, fill="none", stroke=col, sw=1.8, rx=2))
    p.append(text(gx + S * cell / 2, gy + S * cell + 22, "3 якорі на клітинці (фіксовані форми)",
                  size=9.5, color=MUTED))
    p.append(text(gx + S * cell / 2, gy + S * cell + 38, "центр цілі → ця клітинка відповідає за неї",
                  size=9.5, color=MUTED))

    # ── ПРАВА панель: як рахується IoU двох рамок ──
    rx0 = 470
    p.append(text(rx0 + 150, gy - 14, "IoU = перетин / об'єднання", size=11.5, color=INK, bold=True))
    # рамка A (передбачена) і рамка B (ground-truth), що частково накладені
    ax, ay, aw2, ah2 = rx0 + 20, gy + 24, 150, 110
    bx, by, bw2, bh2 = rx0 + 96, gy + 70, 150, 110
    # об'єднання-підкладка (легка заливка обох)
    p.append(rect(ax, ay, aw2, ah2, fill="#2457d611", stroke=NEG, sw=2, rx=4))
    p.append(rect(bx, by, bw2, bh2, fill="#27ae6011", stroke=FIELD, sw=2, rx=4))
    # перетин (червоний прямокутник)
    ix0, iy0 = max(ax, bx), max(ay, by)
    ix1, iy1 = min(ax + aw2, bx + bw2), min(ay + ah2, by + bh2)
    p.append(rect(ix0, iy0, ix1 - ix0, iy1 - iy0, fill="#c0392b55", stroke=POS, sw=1.8, rx=2))
    p.append(text(ax + 30, ay + 16, "A: pred", size=10, color=NEG, bold=True, anchor="start"))
    p.append(text(bx + bw2 - 56, by + bh2 - 10, "B: truth", size=10, color="#1e7d45", bold=True, anchor="start"))
    p.append(text((ix0 + ix1) / 2, (iy0 + iy1) / 2 + 4, "перетин", size=9, color="#7a1f15", bold=True))

    # формула знизу
    p.append(fitbox(rx0 + 6, gy + S * cell + 4, 320, 58,
                    "перетин = спільна площа · об'єднання = A + B − перетин\n"
                    "IoU = 1 — рамки збіглися · IoU = 0 — не торкаються",
                    size=10, fill=FILL, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "anchors-iou.svg"), W, H, *p,
           title="Якорі на сітці й міра збігу IoU")


# ── yolo-tensor: розкладка вихідного тензора S×S×(B·5+C) і вектор клітинки ─────
# Ідея: вихід детектора — куб чисел S×S×K; уздовж глибини кожної клітинки
# лежить B блоків по 5 (tx,ty,tw,th,obj) і C class-logits. Показуємо, як цей
# вектор читати.

def fig_yolo_tensor():
    W, H = 820, 392
    p = []

    # ── ЛІВА панель: куб S×S×K ──
    ox, oy = 70, 96
    S = 3
    cw = 46
    depth = 34
    p.append(text(ox + S * cw / 2 + depth / 2, oy - 22, "вихідний тензор", size=11.5, color=INK, bold=True))
    # передня грань — сітка S×S
    for r in range(S):
        for c in range(S):
            x = ox + c * cw
            y = oy + r * cw
            p.append(rect(x, y, cw, cw, fill="#eef2f7", stroke=INK, sw=1, rx=0))
    # бічна грань (ілюзія глибини K) для верхнього ряду
    for c in range(S):
        x = ox + c * cw
        p.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="#cfd8e3" stroke="%s" stroke-width="1"/>'
                 % (x, oy, x + depth, oy - depth, x + cw + depth, oy - depth, x + cw, oy, INK))
    # верхня грань правого стовпця
    x = ox + (S - 1) * cw
    for r in range(S):
        y = oy + r * cw
        p.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="#dbe3ec" stroke="%s" stroke-width="1"/>'
                 % (x + cw, y, x + cw + depth, y - depth, x + cw + depth, y + cw - depth, x + cw, y + cw, INK))
    p.append(text(ox + S * cw / 2, oy + S * cw + 18, "S × S клітинок", size=10, color=MUTED))
    p.append(text(ox + S * cw + depth + 6, oy - depth / 2 + 4, "глибина K", size=9.5, color=MUTED, anchor="start"))

    # підсвітити одну клітинку й тягнути від неї вектор глибини
    hc, hr = 1, 1
    hx, hy = ox + hc * cw, oy + hr * cw
    p.append(rect(hx, hy, cw, cw, fill="none", stroke=POS, sw=2.4, rx=0))

    # ── ПРАВА панель: вектор глибини клітинки = B блоків по 5 + C класів ──
    vx, vy = 360, 78
    seg = 30
    labels = [("tx", NEG), ("ty", NEG), ("tw", NEG), ("th", NEG), ("obj", POS),
              ("tx", NEG), ("ty", NEG), ("tw", NEG), ("th", NEG), ("obj", POS),
              ("c0", FIELD), ("c1", FIELD), ("c2", FIELD)]
    p.append(text(vx + len(labels) * 0 + 200, vy - 18, "вектор однієї клітинки (K = B·5 + C)",
                  size=11.5, color=INK, bold=True, anchor="middle"))
    x = vx
    for i, (lab, col) in enumerate(labels):
        fill = "#fdecea" if col == POS else ("#eaf0fd" if col == NEG else "#eafaf0")
        p.append(rect(x, vy, seg, seg, fill=fill, stroke=col, sw=1.4, rx=3))
        p.append(text(x + seg / 2, vy + seg / 2 + 4, lab, size=9, color=col, bold=True))
        x += seg
    # дужки під блоками
    b1_w = 5 * seg
    p.append(line(vx, vy + seg + 8, vx + b1_w, vy + seg + 8, color=NEG, sw=1.6))
    p.append(text(vx + b1_w / 2, vy + seg + 22, "якір 1: 5 чисел", size=9, color=NEG))
    p.append(line(vx + b1_w, vy + seg + 8, vx + 2 * b1_w, vy + seg + 8, color=NEG, sw=1.6))
    p.append(text(vx + b1_w + b1_w / 2, vy + seg + 22, "якір 2: 5 чисел", size=9, color=NEG))
    cstart = vx + 2 * b1_w
    p.append(line(cstart, vy + seg + 8, cstart + 3 * seg, vy + seg + 8, color=FIELD, sw=1.6))
    p.append(text(cstart + 1.5 * seg, vy + seg + 22, "C класів", size=9, color="#1e7d45"))

    # стрілка від клітинки до вектора
    p.append(arrow(hx + cw + 4, hy + cw / 2, vx - 8, vy + seg / 2, color=POS, sw=1.8))

    # розшифровка нижче
    p.append(fitbox(70, oy + S * cw + 40, W - 140, 96,
                    "Кожен блок із 5: tx, ty — зсув центру всередині клітинки (через σ → 0…1);\n"
                    "tw, th — лог-масштаб відносно якоря (bw = anchor_w · e^tw); obj — упевненість, що тут об'єкт.\n"
                    "Далі C class-logits → softmax дає ймовірність класу. Підсумкова оцінка рамки = obj · max(class).",
                    size=10, fill=FILL, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "yolo-tensor.svg"), W, H, *p,
           title="Як читати вихідний тензор YOLO-подібного детектора")


# ── nms: багато рамок на одну ціль → залишити найвпевненішу ───────────────────
# Ідея: мережа кидає по кілька рамок на той самий об'єкт; NMS бере найвпевненішу
# й викидає всі, що сильно з нею перекриваються (IoU > поріг).

def fig_nms():
    W, H = 820, 332
    p = []
    bw, bh = 300, 190
    ys = 70

    # ── ЛІВА: купа рамок (до NMS) ──
    x1 = 40
    p.append(text(x1 + bw / 2, ys - 14, "до NMS: купа рамок на ціль", size=11, color=INK, bold=True))
    p.append(rect(x1, ys, bw, bh, fill="#0f172a", stroke=INK, sw=1.2, rx=6))
    # «ціль» (силует)
    tcx, tcy = x1 + bw / 2, ys + bh / 2
    p.append(rect(tcx - 34, tcy - 58, 68, 116, fill="#1e293b", stroke="#33415588", sw=1, rx=10))
    # чотири майже однакові рамки з різними conf
    boxes = [(-26, -64, 120, 132, 0.91, POS), (-14, -52, 116, 128, 0.84, "#fbbf24"),
             (-34, -58, 128, 126, 0.62, "#60a5fa"), (-8, -44, 110, 120, 0.55, "#f472b6")]
    for dx, dy, w, h, conf, col in boxes:
        bxx, byy = tcx + dx, tcy + dy
        p.append(rect(bxx, byy, w, h, fill="none", stroke=col, sw=1.8, rx=2))
        p.append(text(bxx + 2, byy - 4, "%.2f" % conf, size=9, color=col, bold=True, anchor="start"))

    # ── ПРАВА: одна рамка (після NMS) ──
    x2 = 470
    p.append(text(x2 + bw / 2, ys - 14, "після NMS: лишилась найвпевненіша", size=11, color=INK, bold=True))
    p.append(rect(x2, ys, bw, bh, fill="#0f172a", stroke=INK, sw=1.2, rx=6))
    t2cx, t2cy = x2 + bw / 2, ys + bh / 2
    p.append(rect(t2cx - 34, t2cy - 58, 68, 116, fill="#1e293b", stroke="#33415588", sw=1, rx=10))
    p.append(rect(t2cx - 26, t2cy - 64, 120, 132, fill="none", stroke=FIELD, sw=2.6, rx=2))
    p.append(text(t2cx - 24, t2cy - 68, "0.91 ✓", size=9.5, color=FIELD, bold=True, anchor="start"))

    p.append(arrow(x1 + bw + 6, ys + bh / 2, x2 - 6, ys + bh / 2, color=INK, sw=2))
    p.append(text((x1 + bw + x2) / 2, ys + bh / 2 - 10, "IoU > поріг", size=9, color=MUTED))
    p.append(text((x1 + bw + x2) / 2, ys + bh / 2 + 16, "→ викинути", size=9, color=MUTED))

    render(os.path.join(OUT, "nms.svg"), W, H, *p,
           title="Non-Maximum Suppression: одна рамка на ціль")


# ── backbone-neck-head: загальна схема детектора з розмірами feature-map ───────
# Ідея: backbone стискає кадр у компактні ознаки (feature-map меншає, глибшає);
# neck зводить кілька масштабів; head видає рамки. Backbone беруть претренований.

def fig_backbone():
    W, H = 840, 348
    p = []
    midy = 150

    # вхідний кадр
    x = 24
    iw, ih = 86, 86
    p.append(rect(x, midy - ih / 2, iw, ih, fill="#0f172a", stroke=INK, sw=1.3, rx=6))
    p.append(text(x + iw / 2, midy + ih / 2 + 18, "кадр", size=10, color=INK, bold=True))
    p.append(text(x + iw / 2, midy + ih / 2 + 33, "416×416×3", size=9, color=MUTED))

    # BACKBONE: три блоки feature-map, що меншають і глибшають
    bx = 150
    fmaps = [(64, "104×104", "×32"), (46, "52×52", "×96"), (32, "26×26", "×320")]
    cx = bx
    prev_right = x + iw
    p.append(rect(bx - 10, midy - 96, 246, 192, fill="#eef6ff", stroke=NEG, sw=1.6, rx=12))
    p.append(text(bx + 113, midy - 80, "BACKBONE (MobileNet)", size=10.5, color=NEG, bold=True))
    p.append(text(bx + 113, midy - 64, "претренований · групова згортка", size=9, color="#1e4fb0"))
    for sz, dim, dep in fmaps:
        p.append(rect(cx, midy - sz / 2, sz, sz, fill="#dbeafe", stroke=NEG, sw=1.4, rx=3))
        p.append(text(cx + sz / 2, midy + 58, dim, size=9, color="#1e4fb0", bold=True))
        p.append(text(cx + sz / 2, midy + 71, dep, size=9, color=MUTED))
        p.append(arrow(prev_right + 3, midy, cx - 3, midy, color=INK, sw=1.6))
        prev_right = cx + sz
        cx += sz + 34

    # NECK: зводить масштаби
    nx = prev_right + 30
    nw = 92
    p.append(rect(nx, midy - 60, nw, 120, fill="#fff7e6", stroke="#d98a00", sw=1.6, rx=10))
    p.append(text(nx + nw / 2, midy - 4, "NECK", size=10.5, color="#b06b00", bold=True))
    p.append(text(nx + nw / 2, midy + 14, "зводить", size=9, color="#8a5300"))
    p.append(text(nx + nw / 2, midy + 28, "масштаби", size=9, color="#8a5300"))
    p.append(arrow(prev_right + 3, midy, nx - 3, midy, color=INK, sw=1.6))

    # HEAD: видає рамки (тензор)
    hx = nx + nw + 30
    hw = 96
    p.append(rect(hx, midy - 60, hw, 120, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=10))
    p.append(text(hx + hw / 2, midy - 6, "HEAD", size=10.5, color="#1e7d45", bold=True))
    p.append(text(hx + hw / 2, midy + 12, "тензор", size=9, color="#1e7d45"))
    p.append(text(hx + hw / 2, midy + 26, "рамок", size=9, color="#1e7d45"))
    p.append(arrow(nx + nw + 3, midy, hx - 3, midy, color=INK, sw=1.6))
    p.append(arrow(hx + hw + 3, midy, hx + hw + 30, midy, color=INK, sw=1.8))
    p.append(text(hx + hw + 50, midy + 4, "рамки", size=9.5, color="#1e7d45", bold=True, anchor="start"))

    # нижня смуга
    p.append(fitbox(24, midy + 104, W - 48, 58,
                    "Карта ознак уздовж backbone меншає й глибшає: дрібні деталі згортаються в насичений сенс.\n"
                    "Backbone беруть навчений на велетенському наборі — лишається донавчити neck і head під свої класи.",
                    size=10, fill=FILL, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "backbone-neck-head.svg"), W, H, *p,
           title="Будова детектора: backbone → neck → head")


if __name__ == "__main__":
    fig_anchors_iou()
    fig_yolo_tensor()
    fig_nms()
    fig_backbone()
    print("OK: figures written to", OUT)
