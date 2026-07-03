# -*- coding: utf-8 -*-
"""Фігури до теми «Ключові слова й події у звуці (KWS)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Крок від VAD до KWS: від «є звук?» до «яке слово?» ─────────────────────
def fig_leap():
    """Головний концептуальний крок теми. Детектор подій (VAD) з двох дешевих
    чисел (енергія + ZCR) відповідає лише «зараз щось звучить / ні». KWS
    відповідає на важче питання «ЯКЕ саме слово» — і для цього мало двох чисел:
    треба десятки ознак і навчена модель. Той самий стрибок, що від «є об'єкт
    у кадрі» до «що це за об'єкт»."""
    W, H = 900, 330
    f = [text(W / 2, 30, "Крок від сторожа до розпізнавача", size=17, bold=True)]

    # ліва панель — VAD
    lx = 60
    f.append(rect(lx, 70, 360, 200, fill=BG, stroke=NEG, sw=2))
    f.append(text(lx + 180, 98, "ДЕТЕКТОР ПОДІЙ (VAD)", size=13, bold=True, color=NEG))
    f.append(mtext(lx + 180, 128, "2 дешеві числа на кадр:\nенергія + нуль-перетини", size=11, color=MUTED))
    f.append(text(lx + 180, 178, "питання:", size=11, color=MUTED))
    f.append(text(lx + 180, 200, "«зараз щось звучить?»", size=13, bold=True, color=INK))
    f.append(text(lx + 180, 232, "відповідь: так / ні", size=12, color=NEG))
    f.append(text(lx + 180, 254, "кілька порівнянь", size=10, color=MUTED))

    # стрілка-міст
    f.append(arrow(lx + 368, 170, lx + 448, 170))
    f.append(text(lx + 408, 156, "важче", size=10, color=MUTED))

    # права панель — KWS
    rx = lx + 460
    f.append(rect(rx, 70, 360, 200, fill=BG, stroke=POS, sw=2))
    f.append(text(rx + 180, 98, "РОЗПІЗНАВАЧ СЛІВ (KWS)", size=13, bold=True, color=POS))
    f.append(mtext(rx + 180, 128, "десятки ознак + навчена\nмодель (крихітна CNN)", size=11, color=MUTED))
    f.append(text(rx + 180, 178, "питання:", size=11, color=MUTED))
    f.append(text(rx + 180, 200, "«ЯКЕ саме слово?»", size=13, bold=True, color=INK))
    f.append(text(rx + 180, 232, "«вперед» / «стоп» / шум", size=12, color=POS))
    f.append(text(rx + 180, 254, "один прохід мережі", size=10, color=MUTED))

    f.append(text(W / 2, H - 16,
                  "той самий стрибок, що від «є об'єкт у кадрі» до «ЩО це за об'єкт»",
                  size=12, color=INK))
    return render(os.path.join(IMG, "leap.svg"), W, H, *f)


# ── 2. Звук стає картинкою: лог-мел-спектрограма → CNN ────────────────────────
def fig_sound_to_image():
    """Ядро теми: секунду звуку ріжуть на кадри, кожен кадр → стовпчик енергій
    по частотних смугах (мел). Стос стовпчиків = двовимірна КАРТИНКА (час ×
    частота), де слово має характерний візерунок. Далі це — звичайна задача
    класифікації зображень, яку крихітна CNN уже вміє. Так розпізнавання звуку
    зводиться до розпізнавання образу."""
    W, H = 900, 380
    f = [text(W / 2, 30, "Звук стає картинкою: лог-мел-спектрограма", size=17, bold=True)]

    # хвиля зліва
    wx0, wx1, wcy = 50, 250, 150
    f.append(text((wx0 + wx1) / 2, 66, "1 секунда звуку", size=12, bold=True, color=INK))
    prev = None
    import random
    random.seed(7)
    for i in range(200):
        x = wx0 + i / 199 * (wx1 - wx0)
        env = math.exp(-((i - 100) ** 2) / 2500.0)      # обвідна — «слово» посередині
        amp = env * 42 * math.sin(i * 0.9) * (0.5 + random.random())
        y = wcy + amp
        if prev is not None:
            f.append(line(prev[0], prev[1], x, y, color=NEG, sw=1.0))
        prev = (x, y)
    f.append(arrow(wx1 + 4, wcy, wx1 + 44, wcy))
    f.append(text((wx1 + wx1 + 44) / 2, wcy - 12, "ріжемо", size=9, color=MUTED))
    f.append(text((wx1 + wx1 + 44) / 2, wcy + 20, "на кадри", size=9, color=MUTED))

    # спектрограма — сітка час × мел-смуги
    gx, gy = wx1 + 60, 90
    cols, rows = 24, 10
    cw, ch = 15, 15
    # синтетичний візерунок «слова»: дві формантні смуги, що ковзають
    for c in range(cols):
        t = c / (cols - 1)
        env = math.exp(-((t - 0.5) ** 2) / 0.06)         # енергія лише в середині
        for r in range(rows):
            band = rows - 1 - r                          # 0 знизу (низькі частоти)
            f1 = math.exp(-((band - (2 + 3 * t)) ** 2) / 1.3)   # форманта, що повзе вгору
            f2 = math.exp(-((band - (6 - 2 * t)) ** 2) / 1.6)   # друга форманта
            v = env * max(f1, 0.85 * f2)
            # заливка від світлої (мало) до темної (багато) через змішування
            g = int(245 - 205 * min(1.0, v))
            col = "#%02x%02x%02x" % (g, g, min(255, g + int(30 * v)))
            f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
                     % (gx + c * cw, gy + r * ch, cw, ch, col))
    f.append(rect(gx, gy, cols * cw, rows * ch, fill="none", stroke=LINE, sw=1.4))
    f.append(text(gx + cols * cw / 2, gy - 10, "час →", size=11, color=MUTED))
    f.append(text(gx - 12, gy + rows * ch / 2, "частота", size=11, color=MUTED, anchor="middle"))
    f.append(text(gx - 12, gy + rows * ch / 2 + 15, "(мел) ↑", size=10, color=MUTED, anchor="middle"))
    f.append(text(gx + cols * cw / 2, gy + rows * ch + 22,
                  "яскравіше = більше енергії у смузі", size=10, color=MUTED))

    # стрілка до CNN
    ax = gx + cols * cw + 12
    f.append(arrow(ax, gy + rows * ch / 2, ax + 40, gy + rows * ch / 2))

    # маленька CNN-коробка
    nx = ax + 48
    f.append(rect(nx, 118, 118, 120, fill=BG, stroke=FIELD, sw=2))
    f.append(mtext(nx + 59, 150, "крихітна\nCNN", size=13, bold=True, color=FIELD))
    f.append(mtext(nx + 59, 190, "класифікує\nкартинку", size=10, color=MUTED))
    f.append(arrow(nx + 118 + 2, 178, nx + 118 + 30, 178))
    f.append(mtext(nx + 118 + 48, 172, "«вперед»\n0.94", size=11, bold=True, color=POS, anchor="start"))

    f.append(text(W / 2, H - 16,
                  "розпізнавання звуку зводиться до розпізнавання образу — а це CNN уже вміє",
                  size=12, color=INK))
    return render(os.path.join(IMG, "sound-to-image.svg"), W, H, *f)


# ── 3. Каскад «завжди слухаю»: сторож → модель → хмара ───────────────────────
def fig_cascade():
    """Чому KWS будують сходинками потужності. Мікроватний сторож (VAD) слухає
    цілодобово; він будить міліватну модель KWS лише коли є звук; вона ж
    прокидає важку хмарну обробку лише на своє ключове слово. Кожна сходинка
    відсіює майже все — тому середнє споживання лишається крихітним. Та сама
    ідея, що «дешевий сторож попереду дорогої роботи», лише в три яруси."""
    W, H = 880, 420
    f = [text(W / 2, 30, "Каскад «завжди слухаю»: три яруси потужності", size=17, bold=True)]

    stages = [
        ("СТОРОЖ (VAD)", "енергія + ZCR", "цілодобово", "мікровати", NEG, "будить, коли є звук"),
        ("МОДЕЛЬ KWS", "CNN на спектрограмі", "лише коли є звук", "мілівати", FIELD, "спрацьовує на СВОЄ слово"),
        ("ХМАРА / важке", "повне розпізнавання", "лише на ключове слово", "вати (радіо)", POS, ""),
    ]
    # спадні за шириною коробки — «лійка»
    widths = [560, 400, 240]
    y = 70
    bh = 78
    for i, (name, how, when, power, col, note) in enumerate(stages):
        bw = widths[i]
        x = (W - bw) / 2
        f.append(rect(x, y, bw, bh, fill=BG, stroke=col, sw=2.2))
        f.append(text(W / 2, y + 24, name, size=13, bold=True, color=col))
        f.append(text(W / 2, y + 44, how, size=11, color=INK))
        f.append(text(W / 2, y + 62, "працює: " + when, size=10, color=MUTED))
        # ярлик споживання праворуч
        f.append(text(x + bw + 10, y + 30, power, size=11, bold=True, color=col, anchor="start"))
        f.append(text(x + bw + 10, y + 48, "цей ярус", size=9, color=MUTED, anchor="start"))
        if i < len(stages) - 1:
            f.append(arrow(W / 2, y + bh + 2, W / 2, y + bh + 24))
            if note:
                f.append(text(W / 2 + 12, y + bh + 18, note, size=10, color=MUTED, anchor="start"))
        y += bh + 26

    f.append(text(W / 2, H - 16,
                  "кожен ярус відсіює майже все → важке працює рідко → середнє споживання крихітне",
                  size=12, color=INK))
    return render(os.path.join(IMG, "cascade.svg"), W, H, *f)


# ── 4. Мел-фільтрбанк: трикутні смуги на РІВНОМІРНІЙ осі ШПФ (math-mfcc) ──────
def fig_melbank():
    """Серце мел-кроку. Вісь ШПФ рівномірна (кожен бін — однаково завширшки за
    Гц), а трикутні мел-фільтри на ній стоять густо на низах і широко на верхах:
    їхні ВЕРШИНИ рівновіддалені у мелах, тож у герцах розповзаються. Кожен
    фільтр — зважена сума енергій бінів під своїм трикутником: багато вузьких
    сум унизу, кілька широких угорі. Так 256 бінів згортаються у ~десяток смуг,
    а роздільність повторює вухо."""
    W, H = 900, 360
    f = [text(W / 2, 30, "Мел-фільтрбанк: трикутники на рівномірній осі ШПФ", size=17, bold=True)]

    # рамка графіка
    gx, gy, gw, gh = 70, 70, 760, 200
    baseY = gy + gh
    f.append(line(gx, baseY, gx + gw, baseY, color=INK, sw=1.6))          # вісь Гц
    f.append(line(gx, gy, gx, baseY, color=INK, sw=1.6))                  # вертикаль
    f.append(text(gx + gw, baseY + 26, "частота, Гц (рівномірно) →", size=11, color=MUTED, anchor="end"))
    f.append(text(gx - 8, gy + 6, "вага", size=10, color=MUTED, anchor="end"))

    # позначки лінійної осі частот
    for frac, lab in [(0.0, "0"), (0.25, "2к"), (0.5, "4к"), (0.75, "6к"), (1.0, "8к")]:
        x = gx + frac * gw
        f.append(line(x, baseY, x, baseY + 5, color=INK, sw=1.2))
        f.append(text(x, baseY + 18, lab, size=10, color=MUTED))

    # ВЕРШИНИ фільтрів рівновіддалені у мелах → у Гц згущені знизу.
    # mel = 2595*log10(1+f/700);  назад: f = 700*(10**(mel/2595) - 1)
    fmax = 8000.0
    mmax = 2595.0 * math.log10(1 + fmax / 700.0)
    NF = 8                                   # показуємо 8 фільтрів (щоб читались)
    # межі фільтрів: NF+2 рівновіддалених точок у мелах
    edges_hz = [700.0 * (10 ** (mmax * i / (NF + 1) / 2595.0) - 1) for i in range(NF + 2)]
    palette = [NEG, FIELD, POS, "#8e44ad", "#e67e22", "#16a085", "#2457d6", "#c0392b"]
    for k in range(NF):
        lo, ce, hi = edges_hz[k], edges_hz[k + 1], edges_hz[k + 2]
        col = palette[k % len(palette)]
        xl = gx + lo / fmax * gw
        xc = gx + ce / fmax * gw
        xr = gx + hi / fmax * gw
        top = gy + 14
        # трикутник: (xl,base)-(xc,top)-(xr,base)
        f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" '
                 'fill-opacity="0.18" stroke="%s" stroke-width="1.6"/>'
                 % (xl, baseY, xc, top, xr, baseY, col, col))
        f.append(line(xc, top, xc, baseY, color=col, sw=0.8, dash="2,3"))

    # позначки: перший фільтр вузький, останній широкий
    x_first = gx + edges_hz[1] / fmax * gw
    x_last = gx + edges_hz[NF] / fmax * gw
    f.append(text(x_first, gy + 4, "вузькі", size=10, color=NEG, anchor="middle"))
    f.append(text(x_last, gy + 4, "широкі", size=10, color=POS, anchor="middle"))

    # підпис під віссю — «рівні кроки в мелах»
    f.append(text(W / 2, H - 40,
                  "вершини рівновіддалені у МЕЛАХ → у герцах густо внизу, рідко вгорі",
                  size=12, color=INK))
    f.append(text(W / 2, H - 18,
                  "кожен фільтр = зважена сума енергій бінів ШПФ під його трикутником",
                  size=11, color=MUTED))
    return render(os.path.join(IMG, "melbank.svg"), W, H, *f)


# ── 5. DCT-декореляція: чому крихітна CNN любить корельовані лог-мел ──────────
def fig_decorrelate():
    """Розв'язка вставки. ЛОГ-МЕЛ: сусідні смуги СИЛЬНО корельовані (форманта
    засвічує кілька смуг поспіль) → на карті «час×частота» видно суцільні
    ковзні хребти-форманти; згорткове ядро CNN саме такі локальні форми й
    ловить. MFCC (після DCT): ті самі дані РОЗПЛУТАНІ у майже незалежні числа —
    компактно й чудово для дерева/GMM, але просторова сусідність зруйнована, і
    ядру CNN нема за що вхопитись. Тому для крихітної CNN беруть лог-мел, для
    класики — MFCC."""
    W, H = 900, 400
    f = [text(W / 2, 30, "DCT розплутує смуги: що любить CNN, а що — класика", size=17, bold=True)]

    random.seed(11)

    def spectro(ox, oy, cols, rows, cw, ch, decorr):
        """Малює міні-карту час×частота. decorr=False — корельовані формантні
        хребти; True — розсипана шумоподібна текстура (як після DCT)."""
        frags = []
        for c in range(cols):
            t = c / (cols - 1)
            for r in range(rows):
                band = rows - 1 - r
                if not decorr:
                    env = math.exp(-((t - 0.5) ** 2) / 0.10)
                    f1 = math.exp(-((band - (2 + 4 * t)) ** 2) / 1.6)
                    f2 = math.exp(-((band - (7 - 2 * t)) ** 2) / 2.0)
                    v = env * max(f1, 0.8 * f2)
                else:
                    v = random.random() ** 2 * (0.6 if band > rows // 2 else 1.0)
                g = int(245 - 205 * min(1.0, v))
                col = "#%02x%02x%02x" % (g, g, min(255, g + int(28 * v)))
                frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
                             % (ox + c * cw, oy + r * ch, cw, ch, col))
        frags.append(rect(ox, oy, cols * cw, rows * ch, fill="none", stroke=LINE, sw=1.4))
        return "".join(frags)

    cols, rows, cw, ch = 22, 12, 12, 12
    # ліва панель — лог-мел (корельовані)
    lx, ly = 80, 90
    f.append(text(lx + cols * cw / 2, ly - 30, "ЛОГ-МЕЛ (корельовані)", size=13, bold=True, color=POS))
    f.append(text(lx + cols * cw / 2, ly - 12, "сусідні смуги залежні → видно хребти-форманти", size=10, color=MUTED))
    f.append(spectro(lx, ly, cols, rows, cw, ch, decorr=False))
    f.append(text(lx + cols * cw / 2, ly + rows * ch + 20, "час →", size=10, color=MUTED))
    f.append(text(lx - 10, ly + rows * ch / 2, "мел ↑", size=10, color=MUTED, anchor="end"))

    # DCT-стрілка
    mx = lx + cols * cw + 30
    f.append(arrow(mx, ly + rows * ch / 2, mx + 56, ly + rows * ch / 2))
    f.append(text(mx + 28, ly + rows * ch / 2 - 10, "DCT", size=12, bold=True, color=INK))
    f.append(text(mx + 28, ly + rows * ch / 2 + 20, "розплутує", size=9, color=MUTED))

    # права панель — MFCC (декорельовані)
    rx = mx + 86
    f.append(text(rx + cols * cw / 2, ly - 30, "MFCC (розплутані)", size=13, bold=True, color=NEG))
    f.append(text(rx + cols * cw / 2, ly - 12, "майже незалежні числа → просторова форма зникла", size=10, color=MUTED))
    f.append(spectro(rx, ly, cols, rows, cw, ch, decorr=True))
    f.append(text(rx + cols * cw / 2, ly + rows * ch + 20, "час →", size=10, color=MUTED))
    f.append(text(rx - 10, ly + rows * ch / 2, "коеф. ↑", size=10, color=MUTED, anchor="end"))

    # висновок — дві адреси застосування
    f.append(line(80, H - 66, W - 80, H - 66, color=LINE, sw=1.0, dash="3,4"))
    f.append(text(lx + cols * cw / 2, H - 44, "→ згортка CNN ловить локальні хребти", size=11, bold=True, color=POS))
    f.append(text(rx + cols * cw / 2, H - 44, "→ дерево / GMM / щільний шар люблять незалежні", size=11, bold=True, color=NEG))
    f.append(text(W / 2, H - 18,
                  "крихітна CNN → лишай ЛОГ-МЕЛ; класичний класифікатор → бери MFCC",
                  size=12, color=INK))
    return render(os.path.join(IMG, "decorrelate.svg"), W, H, *f)


# ── 6. Streaming-конвеєр: кільце → розгортання → квантування → рішення (proj) ──
def fig_kws_pipeline():
    """Чотири стики робочого streaming-KWS, яких НЕ було в разовій класифікації
    картинки. (1) Потік стовпчиків НАМОТУЄТЬСЯ в кільце сталого розміру; head
    показує найстарішу комірку. (2) У мить прогону кільце РОЗГОРТАЮТЬ у лінійний
    тензор за часом: i-й стовпчик береться з (head+i)%N — попри розрив по краю.
    (3) Тензор КВАНТУЮТЬ у масштаб моделі (обрізання в int8). (4) Вихід CNN
    ЗГЛАДЖУЮТЬ і женуть в автомат станів, що видає одне чисте спрацювання.
    Кожен стик — місце, де перша самостійна спроба тихо ламається."""
    W, H = 900, 470
    f = [text(W / 2, 28, "Робочий streaming-KWS: чотири стики потоку", size=17, bold=True)]

    NF = 5                                  # стільки комірок кільця показуємо
    head = 2                                # обраний head для прикладу
    # за часом: комірка (head+i)%NF несе i-й стовпчик (0 — найстаріший)
    order = [(head + i) % NF for i in range(NF)]   # [2,3,4,0,1]

    # ── (1) ПОТІК → КІЛЬЦЕ ────────────────────────────────────────────────────
    f.append(text(60, 66, "1. потік намотується в кільце", size=13, bold=True, color=NEG, anchor="start"))
    # спадні стрілочки «нові стовпчики згори»
    rx0, ry0, cw = 70, 96, 46               # ліво, верх, ширина комірки
    for j in range(3):
        sx = rx0 + (NF - 1) * cw + 24 - j * 6
        f.append(line(sx, ry0 - 24, sx, ry0 - 6, color=MUTED, sw=1.0))
    f.append(text(rx0 + (NF - 1) * cw + 70, ry0 - 14, "нові", size=9, color=MUTED, anchor="start"))
    f.append(text(rx0 + (NF - 1) * cw + 70, ry0 - 2, "≈10 мс", size=9, color=MUTED, anchor="start"))
    # комірки кільця (у ПОРЯДКУ пам'яті 0..NF-1)
    for k in range(NF):
        x = rx0 + k * cw
        is_head = (k == head)
        col = POS if is_head else NEG
        f.append(rect(x, ry0, cw - 6, 40, fill=BG, stroke=col, sw=2.2 if is_head else 1.6))
        f.append(text(x + (cw - 6) / 2, ry0 + 25, "к%d" % k, size=12, color=INK))
    # дужка «замкнене в кільце»
    f.append(text(rx0 + NF * cw / 2 - 3, ry0 + 66, "масив на місці — рухається лише head", size=10, color=MUTED))
    # маркер head
    hx = rx0 + head * cw + (cw - 6) / 2
    f.append(arrow(hx, ry0 - 30, hx, ry0 - 4, color=POS))
    f.append(text(hx, ry0 - 36, "head", size=11, bold=True, color=POS))
    f.append(text(hx, ry0 + 55, "найстаріший", size=9, color=POS))

    # ── (2) РОЗГОРТАННЯ за часом ───────────────────────────────────────────────
    uy = 210
    f.append(text(60, uy - 8, "2. розгортання: i-й за ЧАСОМ = комірка (head+i)%N",
                  size=13, bold=True, color=FIELD, anchor="start"))
    lx0 = rx0
    for i in range(NF):
        x = lx0 + i * cw
        src = order[i]
        f.append(rect(x, uy, cw - 6, 40, fill=BG, stroke=FIELD, sw=1.8))
        f.append(text(x + (cw - 6) / 2, uy + 18, "час %d" % i, size=10, color=INK))
        f.append(text(x + (cw - 6) / 2, uy + 33, "= к%d" % src, size=10, color=MUTED))
    # підпис розрахунку порядку
    f.append(text(lx0 + NF * cw / 2 - 3, uy + 62,
                  "порядок комірок: %s  (через край %% заверне на початок)"
                  % " ".join("к%d" % s for s in order), size=10, color=MUTED))
    # стрілка з кільця в розгортку — РОЗІРВАНА навколо заголовка секції 2 (bbox y≈192..204),
    # щоб конектор не різав напис: верхній сегмент (лінія) над написом, нижній (стрілка) під ним
    scx = rx0 + NF * cw + 4
    f.append(line(scx, ry0 + 20, scx, 188, color=MUTED, sw=1.8))
    f.append(arrow(scx, 208, scx, uy + 20, color=MUTED))
    f.append(text(rx0 + NF * cw + 12, (ry0 + uy) / 2 + 20, "раз на HOP", size=9, color=MUTED, anchor="start"))
    f.append(text(rx0 + NF * cw + 12, (ry0 + uy) / 2 + 33, "стовпчиків", size=9, color=MUTED, anchor="start"))

    # ── (3) КВАНТУВАННЯ + (4) CNN + РІШЕННЯ — горизонтальний ланцюг ────────────
    cy = 340
    bx = 70
    # квантування
    f.append(fitbox(bx, cy, 150, 62,
                    "3. квантувати\nу int8 (масштаб\nмоделі) + обрізання",
                    size=11, stroke=FIELD, color=INK, pad=6))
    f.append(arrow(bx + 150 + 4, cy + 31, bx + 150 + 30, cy + 31, color=INK))
    # CNN
    cnx = bx + 150 + 34
    f.append(fitbox(cnx, cy, 120, 62, "крихітна\nCNN\n(Invoke)", size=12, stroke=FIELD, color=FIELD, pad=6, bold=True))
    f.append(arrow(cnx + 120 + 4, cy + 31, cnx + 120 + 30, cy + 31, color=INK))
    f.append(text(cnx + 120 + 60, cy + 22, "probs[]", size=10, color=MUTED))
    # автомат рішення
    dx = cnx + 120 + 34 + 44
    f.append(fitbox(dx, cy, 190, 62,
                    "4. згладити → поріг →\nспокій → «чуже»",
                    size=11, stroke=POS, color=POS, pad=6, bold=True))
    f.append(arrow(dx + 190 + 4, cy + 31, dx + 190 + 28, cy + 31, color=POS))
    f.append(mtext(dx + 190 + 30, cy + 26, "«вперед»\nраз на слово", size=10, bold=True, color=POS, anchor="start"))

    f.append(text(W / 2, H - 16,
                  "уся складність, якої не було в разовій класифікації картинки, живе в цих чотирьох стиках",
                  size=12, color=INK))
    return render(os.path.join(IMG, "kws-pipeline.svg"), W, H, *f)


# ── 7. Історична смуга: психоакустика 1937 → чип у вусі 2018 (hist-kws) ───────
def fig_kws_timeline():
    """Для вставки-історії. Вісімдесят років, стиснуті в один KWS-конвеєр. ВУЗЛИ
    подій стоять на осі за СПРАВЖНІМ роком (хронологія чесна — видно згущення
    2014-2015-2018 праворуч), а виносні КОРОБКИ рознесені по рівних колонках і
    з'єднані з вузлом коліном, тож підписи не налазять попри тісні дати. Колір:
    холодний (NEG) — фундаментальна психоакустика/сигнали, робили заради вуха;
    зелений (FIELD) — перелам «вивчене з даних б'є ручні HMM»; червоний (POS) —
    відкриті дані, що винесли все це в руки кожного."""
    W, H = 1040, 520
    f = [text(W / 2, 30, "Вісімдесят років психоакустики → чип у вусі", size=17, bold=True)]

    ax0, ax1, ay = 70, W - 70, 262
    f.append(line(ax0, ay, ax1, ay, color=INK, sw=2.4))
    f.append(arrow(ax1 - 2, ay, ax1 + 6, ay, color=INK))

    def xat(year):
        return ax0 + (year - 1930) / (2020 - 1930) * (ax1 - ax0)

    # підписи десятиліть — окремим НИЖНІМ рядком (ay+38), щоб не збіглися з роками подій (ay+20)
    for yr in (1940, 1960, 1980, 2000, 2020):
        x = xat(yr)
        f.append(line(x, ay - 5, x, ay + 5, color=MUTED, sw=1.4))
        f.append(text(x, ay + 38, str(yr), size=11, color=MUTED))

    events = [
        (1937, "МЕЛ",     "Стівенс·Фолькманн·Ньюмен\nяк вухо чує висоту",       NEG),
        (1980, "MFCC",    "Девіс·Мермельштейн\nмел + лог + кепстр",             NEG),
        (2000, "GMM-HMM", "мову розпізнають\nручними моделями (≈30 р.)",        MUTED),
        (2014, "DNN",     "Чень·Парада·Гайгольд\nмережа викидає HMM",           FIELD),
        (2015, "CNN",     "Сайнат·Парада: згортка\nдешевша, слово = картинка", FIELD),
        (2018, "ДАНІ",    "Ворден: Speech Commands\n105k кліпів, відкрито",     POS),
    ]
    n = len(events)
    slot0, slot1 = 130, W - 130
    slots = [slot0 + (slot1 - slot0) * i / (n - 1) for i in range(n)]
    top_y, bot_y = 96, 396

    for i, (yr, name, sub, col) in enumerate(events):
        up = (i % 2 == 0)                   # чергуємо рівні → у межах рівня коробки не налазять
        nx = xat(yr)                        # вузол — за справжнім роком
        bx = slots[i]                       # коробка — рознесена по колонках
        f.append(circle(nx, ay, 7, fill=BG, stroke=col, sw=2.4))
        f.append(text(nx, ay - 14 if up else ay + 20, str(yr), size=11, bold=True, color=col))
        cy = top_y if up else bot_y
        body, bw, bh = textbox(bx, cy, name + "\n" + sub, size=11, pad=9,
                               stroke=col, color=INK, bold=False)
        shelf = (top_y + ay) / 2 if up else (bot_y + ay) / 2
        near = ay - 20 if up else ay + 34
        edge = cy + bh / 2 if up else cy - bh / 2
        f.append(line(nx, near, nx, shelf, color=col, sw=1.2, dash="3,3"))
        f.append(line(nx, shelf, bx, shelf, color=col, sw=1.2, dash="3,3"))
        f.append(line(bx, shelf, bx, edge, color=col, sw=1.2, dash="3,3"))
        f.append(body)

    f.append(text(xat(1958), H - 40,
                  "фундаментальна психоакустика й сигнали — робили заради розуміння вуха",
                  size=11, color=NEG))
    f.append(text(W / 2, H - 16,
                  "вивчене з даних б'є ручне  →  дозріле залізо (always-on)  →  відкриті дані для всіх",
                  size=12, color=INK))
    return render(os.path.join(IMG, "kws-timeline.svg"), W, H, *f)


# ── 8. Геометрія кадрової сітки: вікно, крок, перекриття → 49 стовпчиків ───────
def fig_frame_grid():
    """Детальна: як із секунди звуку виходить рівно 49 стовпчиків. Вікно 30 мс
    (досить довге для частоти голосу, досить коротке проти розмазування), крок
    20 мс задає перекриття, формула floor((T-L)/H)+1 = 49. Кожен стовпчик — 40
    мел-енергій; разом 49×40 замість 16000 сирих відліків (стиснення 8×)."""
    W, H = 1000, 480
    f = [text(W / 2, 30, "Геометрія кадрової сітки: звідки 49 стовпчиків", size=17, bold=True)]

    # вісь часу — секунда звуку
    ax0, ax1, ay = 70, 820, 92
    f.append(line(ax0, ay, ax1, ay, color=INK, sw=2))
    f.append(text(ax0, ay - 14, "0 мс", size=11, color=MUTED, anchor="start"))
    f.append(text(ax1, ay - 14, "1000 мс", size=11, color=MUTED, anchor="end"))
    f.append(text((ax0 + ax1) / 2, ay - 14, "1 секунда звуку", size=12, bold=True, color=INK))

    # кілька перших вікон із перекриттям (малюємо тільки перші, далі «…»)
    L_ms, H_ms = 30.0, 20.0
    px_per_ms = (ax1 - ax0) / 1000.0
    rows_y = [116, 140, 164, 188]           # чотири вікна сходинкою вниз
    for i, wy in enumerate(rows_y):
        wx0 = ax0 + i * H_ms * px_per_ms
        wx1 = wx0 + L_ms * px_per_ms
        f.append(rect(wx0, wy, wx1 - wx0, 16, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
        if i == 0:
            f.append(text(wx1 + 8, wy + 12, "вікно 30 мс", size=10, color=NEG, anchor="start"))
        if i == 1:
            f.append(text(wx1 + 8, wy + 12, "крок 20 мс → сусіди перекриваються", size=10, color=MUTED, anchor="start"))
    f.append(text(ax0 + 2 * H_ms * px_per_ms, 226, "…  і так 49 вікон до кінця секунди  …",
                  size=11, color=MUTED, anchor="start"))

    # формула числа кадрів
    fx = W / 2
    box, bw, bh = textbox(fx, 268, "N = ⌊(T − L) / H⌋ + 1 = ⌊(1000 − 30)/20⌋ + 1 = 49",
                          size=13, pad=12, fill=FILL, stroke=FIELD, sw=2, bold=True)
    f.append(box)

    # два стовпчики: перший і 49-й, кожен = 40 мел-смуг
    def mel_column(cx, top, label):
        parts = [text(cx, top - 10, label, size=11, bold=True, color=INK)]
        n, cellw, cellh = 8, 34, 13         # показуємо 8 клітин + «…» замість 40
        random.seed(hash(label) & 255)
        for r in range(n):
            y = top + r * cellh
            v = random.random()
            g = int(30 + 200 * (1 - v))
            shade = "#%02x%02x%02x" % (g, g, g)
            parts.append(rect(cx - cellw / 2, y, cellw, cellh - 1, fill=shade, stroke="#cccccc", sw=0.5, rx=0))
        parts.append(text(cx, top + n * cellh + 12, "⋮", size=14, color=MUTED))
        parts.append(text(cx, top + n * cellh + 30, "40 смуг", size=10, color=MUTED))
        return parts, cellw

    # спільний підпис над обома стовпчиками (вище за їхні заголовки)
    f.append(text(190, 316, "кожен кадр → 40 мел-енергій", size=11, color=INK))
    c1, _ = mel_column(130, 340, "стовпчик 1")
    c2, _ = mel_column(260, 340, "стовпчик 49")
    f.extend(c1)
    f.extend(c2)

    # порівняння обсягу праворуч (у своїй колонці, з великим запасом)
    cmp_x = 610
    b1, w1, h1 = textbox(cmp_x, 360, "сирих відліків:\n16 000 чисел / с", size=12, pad=12,
                         fill=BG, stroke=NEG, sw=2, color=NEG, bold=True)
    f.append(b1)
    f.append(text(cmp_x + 150, 346, "стиснення ≈ 8×", size=12, bold=True, color=FIELD))
    f.append(arrow(cmp_x + w1 / 2 + 8, 360, cmp_x + 116, 360))
    b2, w2, h2 = textbox(cmp_x + 250, 360, "ознак:\n49 × 40 = 1960 чисел / с", size=12, pad=12,
                         fill=BG, stroke=POS, sw=2, color=POS, bold=True)
    f.append(b2)

    f.append(text(W / 2, H - 16,
                  "вікно — компроміс: досить довге для частоти голосу, досить коротке проти розмазування переходу",
                  size=11, color=INK))
    return render(os.path.join(IMG, "frame-grid.svg"), W, H, *f)


# ── 9. Звичайна згортка проти глибинно-роздільної: арифметика виграшу ─────────
def fig_ds_conv():
    """Детальна: чому DS-CNN дешевша. Звичайна згортка змішує простір і канали
    одним важким кроком (C_in·C_out·k·k). Глибинно-роздільна розкладає на дві
    легкі: глибинна (просторова, по каналах окремо) + точкова 1×1 (змішує
    канали). Виграш = (C_out·k·k)/(k·k+C_out) ≈ 8× для k=3, C_out=64."""
    W, H = 940, 430
    f = [text(W / 2, 30, "Звичайна згортка проти глибинно-роздільної", size=17, bold=True)]

    # ліва половина: звичайна
    lx = 210
    f.append(text(lx, 66, "ЗВИЧАЙНА ЗГОРТКА", size=13, bold=True, color=NEG))
    f.append(fitbox(lx - 150, 82, 300, 46,
                    "один важкий крок:\nпростір + канали разом", size=12,
                    fill="#eaf0fd", stroke=NEG, sw=1.5, color=INK))
    f.append(fitbox(lx - 150, 150, 300, 40,
                    "C_in · C_out · k · k", size=15,
                    fill=BG, stroke=NEG, sw=2, color=NEG, bold=True))
    f.append(text(lx, 214, "множень на позицію", size=10, color=MUTED))

    # роздільник
    f.append(line(W / 2, 60, W / 2, 300, color="#cccccc", sw=1.5, dash="4 4"))

    # права половина: роздільна — два кроки
    rx = 690
    f.append(text(rx, 66, "ГЛИБИННО-РОЗДІЛЬНА", size=13, bold=True, color=POS))
    f.append(fitbox(rx - 165, 82, 330, 42,
                    "крок 1 — глибинна: простір,\nпо каналах ОКРЕМО", size=11,
                    fill="#fdecea", stroke=POS, sw=1.5, color=INK))
    f.append(fitbox(rx - 168, 132, 150, 34, "C_in · k · k", size=13,
                    fill=BG, stroke=POS, sw=1.5, color=POS, bold=True))
    f.append(text(rx - 8, 154, "+", size=18, bold=True, color=INK))
    f.append(fitbox(rx + 18, 132, 150, 34, "C_in · C_out", size=13,
                    fill=BG, stroke=POS, sw=1.5, color=POS, bold=True))
    f.append(fitbox(rx - 165, 176, 330, 40,
                    "крок 2 — точкова 1×1: змішує канали", size=11,
                    fill="#fdecea", stroke=POS, sw=1.5, color=INK))

    # рядок виграшу
    box, bw, bh = textbox(W / 2, 262,
                          "виграш = (C_out · k·k) / (k·k + C_out)", size=14, pad=12,
                          fill=FILL, stroke=FIELD, sw=2, bold=True)
    f.append(box)

    # підстановка чисел
    box2, bw2, bh2 = textbox(W / 2, 320,
                             "k = 3, C_out = 64  →  (64·9)/(9+64) = 576/73 ≈ 7.9×",
                             size=13, pad=11, fill=BG, stroke=INK, sw=1.5, bold=True)
    f.append(box2)

    f.append(text(W / 2, H - 40,
                  "та сама форма шару — майже увосьмеро менше множень",
                  size=13, bold=True, color=FIELD))
    f.append(text(W / 2, H - 16,
                  "тому DS-CNN виграє всі три бюджети «Hello Edge» (95.4%)",
                  size=11, color=MUTED))
    return render(os.path.join(IMG, "ds-conv.svg"), W, H, *f)


# ── 10. Згладжування виходу як фільтр: сира ймовірність проти згладженої ───────
def fig_posterior_smooth():
    """Детальна: сирий вихід мережі смикається й кілька разів пробиває поріг →
    черга хибних спрацювань. Експоненційне середнє (однополюсний IIR, τ≈1/A
    прогонів) робить криву плавною: поріг пробито раз, далі період спокою
    блокує повтори. Показуємо обидва ряди на спільній часовій осі."""
    W, H = 940, 470
    f = [text(W / 2, 30, "Згладжування виходу: сира ймовірність проти згладженої", size=17, bold=True)]

    ax0, ax1 = 90, 880
    thr = 0.75
    # синтетичний ряд прогонів: смикається біля піку слова
    random.seed(11)
    n = 26
    base = []
    for i in range(n):
        # горб навколо i=12..18 (слово у вікні), плюс дрижання
        peak = math.exp(-((i - 15) ** 2) / 20.0)
        val = 0.15 + 0.8 * peak + (random.random() - 0.5) * 0.28
        base.append(max(0.02, min(0.99, val)))
    # згладжене EMA
    A = 0.4
    sm = []
    s = 0.0
    for v in base:
        s = s + A * (v - s)
        sm.append(s)

    def panel(top, series, title, color, show_thr_hit_at=None, refractory=None):
        ph = 150
        parts = [text(ax0, top - 8, title, size=12, bold=True, color=INK, anchor="start")]
        # рамка панелі
        parts.append(rect(ax0, top, ax1 - ax0, ph, fill=BG, stroke="#dddddd", sw=1))
        # вісь порогу
        thy = top + ph - thr * ph
        parts.append(line(ax0, thy, ax1, thy, color=POS, sw=1.5, dash="6 4"))
        parts.append(text(ax1 - 4, thy - 6, "поріг θ = 0.75", size=10, color=POS, anchor="end"))
        # період спокою (сірий) — тільки в нижній панелі
        if refractory:
            rx0 = ax0 + refractory[0] / (n - 1) * (ax1 - ax0)
            rx1 = ax0 + refractory[1] / (n - 1) * (ax1 - ax0)
            parts.append(rect(rx0, top, rx1 - rx0, ph, fill="#eeeeee", stroke="none", sw=0))
            parts.append(text((rx0 + rx1) / 2, top + ph - 8, "період спокою", size=10, color=MUTED))
        # лінія ряду
        pts = []
        for i, v in enumerate(series):
            x = ax0 + i / (n - 1) * (ax1 - ax0)
            y = top + ph - v * ph
            pts.append((x, y))
        d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
        parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, color))
        # точки прогонів
        for x, y in pts:
            parts.append(circle(x, y, 2.6, fill=color, stroke=color, sw=1))
        # позначки пробиття порогу
        if show_thr_hit_at is not None:
            for idx in show_thr_hit_at:
                x = ax0 + idx / (n - 1) * (ax1 - ax0)
                y = top + ph - series[idx] * ph
                parts.append(circle(x, y, 6, fill="none", stroke=POS, sw=2.2))
        return parts

    # верх — сира: позначаємо кілька пробиттів порогу
    raw_hits = [i for i in range(n) if base[i] > thr]
    f.extend(panel(78, base, "сира ймовірність (смикається — кілька пробиттів порогу)",
                   NEG, show_thr_hit_at=raw_hits))
    f.append(text(ax0, 78 + 150 + 22,
                  "кожне пробиття → окреме спрацювання: черга хибних і подвійних тривог",
                  size=11, color=NEG, anchor="start"))

    # низ — згладжена: одне пробиття + період спокою
    sm_hit = next((i for i in range(n) if sm[i] > thr), None)
    f.extend(panel(300, sm, "згладжена (експоненційне середнє, τ ≈ 1/A ≈ 2.5 прогони ≈ 100 мс)",
                   FIELD, show_thr_hit_at=[sm_hit] if sm_hit is not None else None,
                   refractory=(sm_hit + 0.5, min(n - 1, sm_hit + 8)) if sm_hit is not None else None))
    f.append(text(ax0, 300 + 150 + 22,
                  "одне чисте спрацювання; період спокою блокує повтор на те саме слово",
                  size=11, color=FIELD, anchor="start"))
    return render(os.path.join(IMG, "posterior-smooth.svg"), W, H, *f)


# ── 11. DET-крива: дві похибки як крива, робоча точка під ціну помилки ─────────
def fig_det_curve():
    """Детальна: модель — це ВСЯ крива похибок, не одне число. Кожна точка —
    окремий поріг θ. Ось: хибні спрацювання за годину (лог) × хибні пропуски %.
    Дві робочі точки під різну ціну помилки. Краща модель — крива ближче до
    кута «нуль-нуль»."""
    W, H = 900, 500
    f = [text(W / 2, 30, "Дві похибки як крива: DET і робоча точка", size=17, bold=True)]

    # осі
    ox, oy = 130, 400            # початок (лівий-нижній кут поля)
    ax_w, ax_h = 640, 300
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))       # вісь Y
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))       # вісь X
    # підписи осей
    f.append(text(ox + ax_w / 2, oy + 34, "хибні спрацювання за годину (FA/h, лог-шкала)",
                  size=12, bold=True, color=INK))
    f.append(mtext(ox - 92, oy - ax_h / 2, "хибні\nпропуски\n(%)", size=12, color=INK, bold=True))
    # мітки X (лог)
    for i, lbl in enumerate(["0.01", "0.1", "1", "10"]):
        x = ox + (i + 0.5) / 4 * ax_w
        f.append(text(x, oy + 16, lbl, size=10, color=MUTED))
    # мітки Y
    for i, lbl in enumerate(["30", "20", "10", "0"]):
        y = oy - i / 3 * ax_h
        f.append(text(ox - 16, y + 4, lbl, size=10, color=MUTED, anchor="end"))

    # DET-крива: спадна опукла (менше FA → більше пропусків)
    import math as _m
    pts = []
    for k in range(41):
        t = k / 40.0
        # x росте зліва (мало FA) направо (багато FA); пропуски падають
        x = ox + t * ax_w
        miss = 30 * _m.exp(-3.2 * t) + 1.5     # спадна крива
        y = oy - (30 - miss) / 30 * 0  # placeholder
        y = oy - (miss / 30) * 0
        y = oy - (1 - miss / 32) * ax_h
        pts.append((x, y))
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, INK))
    f.append(text(ox + ax_w - 6, pts[-1][1] - 12, "крива моделі", size=11, bold=True, color=INK, anchor="end"))

    # напрямок «краще»
    f.append(arrow(ox + 150, oy - 40, ox + 70, oy - ax_h + 40, color=FIELD, sw=2))
    f.append(text(ox + 120, oy - ax_h + 60, "краще", size=12, bold=True, color=FIELD))
    f.append(text(ox + 116, oy - ax_h + 78, "(до кута 0–0)", size=10, color=FIELD))

    # дві робочі точки
    # «увімкни світло» — охоче: більше FA, менше пропусків (правіше)
    px1, py1 = pts[30]
    f.append(circle(px1, py1, 7, fill=POS, stroke=INK, sw=1.5))
    f.append(text(px1 + 12, py1 + 4, "«увімкни світло» — охоче", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(px1 + 12, py1 + 20, "дешевий пропуск, терпимо до FA", size=10, color=MUTED, anchor="start"))
    # «пуск двигуна» — обережно: мало FA, більше пропусків (лівіше-вище)
    px2, py2 = pts[9]
    f.append(circle(px2, py2, 7, fill=NEG, stroke=INK, sw=1.5))
    f.append(text(px2 + 12, py2 - 8, "«пуск двигуна» — обережно", size=11, bold=True, color=NEG, anchor="start"))
    f.append(text(px2 + 12, py2 + 8, "дороге хибне спрацювання", size=10, color=MUTED, anchor="start"))

    # нижній підпис із числом планки
    box, bw, bh = textbox(W / 2, oy + 66,
                          "0.1 FA/год при 90 000 прогонів/год  →  P(хибне на прогін) ≈ 1.1·10⁻⁶",
                          size=12, pad=11, fill=FILL, stroke=FIELD, sw=1.5, bold=True)
    f.append(box)
    return render(os.path.join(IMG, "det-curve.svg"), W, H, *f)


# (головний блок — у кінці файлу, після всіх визначень фігур)


# ── 12. Геометрія потокової згортки: доробляємо лише крайову смужку ───────────
def fig_stream_conv_strip():
    """Серце proj-вставки про потокову згортку. Прийшов ОДИН новий вхідний
    стовпчик (час t) — і в стрічці активацій stride-1 causal-згортки міняється
    рівно ОДНА нова вихідна колонка (її рецептивне поле — Kt останніх входів).
    Кожен шар тримає своє КІЛЬЦЕ з Kt колонок входу; на новий крок: заштовхнув
    вхід (виштовхнув найстаріший) → порахував 1 вихідну колонку → вона стає
    новим входом наступного шару. Рецептивне поле по глибині РОСТЕ."""
    W, H = 940, 660
    f = [text(W / 2, 30, "Потокова згортка: на новий стовпчик — лише крайова смужка", size=17, bold=True)]

    Kt = 3
    cellw, cellh = 26, 12
    ncols = 12                     # показуємо 12 останніх колонок часу
    x0 = 250
    # три ряди: ВХІД → L1 → L2, кожен зсунутий, щоб видно ріст поля
    rows = [
        ("вхід (лог-мел)", 90,  FILL,  None),
        ("після L1 (Kt=3)", 250, "#eef5ee", 1),
        ("після L2 (Kt=3)", 410, "#eaf0fd", 2),
    ]
    # колонки, що ЩОЙНО змінилися (крайова смужка) — праворуч
    for label, y, base, depth in rows:
        f.append(text(x0 - 20, y - 6, label, size=12, bold=True, anchor="start", color=INK))
        for c in range(ncols):
            cx = x0 + c * (cellw + 2)
            # висота колонки — умовні 8 клітин
            hot = (c == ncols - 1)            # найновіша колонка — «гаряча»
            for r in range(8):
                cy = y + r * cellh
                fill = base
                stroke = LINE
                if hot:
                    fill = "#fde8e8"; stroke = POS
                f.append(rect(cx, cy, cellw, cellh, fill=fill, stroke=stroke, sw=1.0, rx=1))
        # позначити «нову колонку»
        nx = x0 + (ncols - 1) * (cellw + 2)
        f.append(text(nx + cellw/2, y - 8, "нова", size=10, bold=True, color=POS))

    # рамка рецептивного поля: остання вихідна колонка L2 ← 3 колонки L1 ← 5 колонок входу
    def rf_box(y, cols_from_right, color):
        rx = x0 + (ncols - cols_from_right) * (cellw + 2) - 2
        rw = cols_from_right * (cellw + 2)
        f.append(rect(rx, y - 3, rw, 8*cellh + 6, fill="none", stroke=color, sw=2.2, rx=3))
    rf_box(410, 1, POS)           # 1 нова колонка L2
    rf_box(250, Kt, POS)          # 3 колонки L1, що її живлять
    rf_box(90, 2*Kt-1, POS)      # 5 колонок входу під ними

    # стрілки «звужується до однієї колонки»
    f.append(arrow(x0 + (ncols-2.5)*(cellw+2), 90 + 8*cellh + 8,
                   x0 + (ncols-1.5)*(cellw+2), 250 - 8, color=POS, sw=1.6))
    f.append(arrow(x0 + (ncols-1.5)*(cellw+2), 250 + 8*cellh + 8,
                   x0 + (ncols-0.5)*(cellw+2), 410 - 8, color=POS, sw=1.6))

    # знизу окремою смугою — схема одного кільця шару (з великим просвітом від сітки)
    lx, ly = 120, 560
    f.append(text(lx, ly - 16, "кільце одного шару (Kt колонок його входу):", size=12, bold=True, color=INK, anchor="start"))
    for i in range(Kt):
        bx = lx + i * 54
        col = "#fde8e8" if i == Kt-1 else FILL
        st = POS if i == Kt-1 else LINE
        f.append(rect(bx, ly, 46, 48, fill=col, stroke=st, sw=1.5, rx=4))
        f.append(text(bx + 23, ly + 29, "t%+d" % (i - (Kt-1)) if i != Kt-1 else "t", size=12, bold=(i==Kt-1),
                      color=(POS if i==Kt-1 else MUTED)))
    f.append(arrow(lx + Kt*54 + 8, ly + 24, lx + Kt*54 + 66, ly + 24, color=INK, sw=1.8))
    box = fitbox(lx + Kt*54 + 74, ly + 4, 170, 42,
                 "1 нова\nвихідна колонка", size=11, fill="#eef5ee", stroke=FIELD, sw=1.5, bold=True)
    f.append(box)

    f.append(text(W / 2, H - 16,
                  "рецептивне поле росте вглиб (1 → 3 → 5 колонок), але доробляємо тільки крайову смужку",
                  size=12, color=INK))
    return render(os.path.join(IMG, "stream-conv-strip.svg"), W, H, *f)


# ── 13. Коли потік виграє, а коли разовий прохід: перетин за HOP ──────────────
def fig_stream_vs_oneshot():
    """Компроміс streaming ↔ one-shot. По осі X — HOP (як рідко кличемо мережу,
    у стовпчиках). Потокова згортка робить ~1 колонку/крок ЗАВЖДИ (тримати
    кільця теплими), плюс несе постійну RAM під активаційні кільця всіх шарів.
    Разовий прохід нічого не тримає між викликами, зате раз на HOP перераховує
    всі T колонок → амортизовано T/HOP колонок/крок. Перетин по такту — біля
    HOP≈T; по RAM перевага one-shot стала (він не тримає кілець)."""
    W, H = 900, 470
    f = [text(W / 2, 30, "Коли потік виграє, а коли — разовий прохід", size=17, bold=True)]

    ox, oy = 90, 360           # початок осей
    ax_w, ax_h = 720, 280
    T = 49
    # осі
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))
    f.append(text(ox + ax_w, oy + 46, "HOP — як рідко кличемо мережу (стовпчиків)", size=12, bold=True, anchor="end", color=INK))
    f.append(text(ox - 72, oy - ax_h + 8, "колонок", size=11, bold=True, anchor="start", color=INK))
    f.append(text(ox - 72, oy - ax_h + 24, "на крок", size=11, bold=True, anchor="start", color=INK))

    hop_max = 60
    def X(h): return ox + (h / hop_max) * ax_w
    ymax = 5.0
    def Y(v): return oy - min(v, ymax) / ymax * ax_h

    # позначки HOP
    for h in [1, 10, 20, 30, 40, 49, 60]:
        f.append(line(X(h), oy, X(h), oy + 5, color=INK, sw=1.2))
        f.append(text(X(h), oy + 20, str(h), size=10, color=MUTED))
    # горизонтальна лінія-орієнтир «1 колонка/крок» (обрізана, щоб не різати підпис)
    f.append(line(ox, Y(1), X(44), Y(1), color=MUTED, sw=1.0, dash="4 4"))
    f.append(text(ox + ax_w, Y(1) + 16, "орієнтир: 1 колонка/крок", size=10, color=MUTED, anchor="end"))

    # STREAMING: ~1 колонка/крок завжди (плоска лінія трохи вище 1 — накладні кільця)
    sy = Y(1.3)
    f.append(line(ox, sy, ox + ax_w, sy, color=POS, sw=2.6))
    f.append(text(X(4), sy - 10, "ПОТІК: ~1 колонка/крок завжди", size=12, bold=True, color=POS, anchor="start"))

    # ONE-SHOT: T/HOP колонок/крок (амортизовано) — гіпербола
    pts = []
    h = 1.0
    while h <= hop_max:
        pts.append((X(h), Y(T / h)))
        h += 0.5
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, NEG))
    f.append(text(X(30), Y(T/30) - 12, "РАЗОВИЙ: T/HOP колонок/крок", size=12, bold=True, color=NEG, anchor="start"))

    # перетин біля HOP=T (де T/HOP = 1) — підпис ЗНИЗУ, щоб не потрапити під лінію потоку
    f.append(circle(X(T), Y(1), 7, fill="none", stroke=INK, sw=2))
    f.append(text(X(T) + 12, Y(1) + 26, "перетин ≈ HOP=T", size=11, bold=True, color=INK, anchor="middle"))

    # зони
    f.append(text(X(6), Y(4.4), "тут дешевший ПОТІК", size=12, bold=True, color=POS, anchor="start"))
    f.append(text(X(6), Y(4.0), "(кличемо мережу часто)", size=10, color=POS, anchor="start"))
    f.append(text(X(52), Y(2.2), "тут дешевший РАЗОВИЙ", size=12, bold=True, color=NEG, anchor="start"))
    f.append(text(X(52), Y(1.95), "(кличемо рідко)", size=10, color=NEG, anchor="start"))

    # плашка про RAM
    box, bw, bh = textbox(W / 2, oy + 70,
                          "RAM: потік ДОДАТКОВО тримає активаційні кільця всіх шарів (десятки КБ); разовий — ні",
                          size=12, pad=11, fill=FILL, stroke=FIELD, sw=1.5, bold=True)
    f.append(box)
    return render(os.path.join(IMG, "stream-vs-oneshot.svg"), W, H, *f)


if __name__ == "__main__":
    fig_leap()
    fig_sound_to_image()
    fig_cascade()
    fig_melbank()
    fig_decorrelate()
    fig_kws_pipeline()
    fig_kws_timeline()
    fig_frame_grid()
    fig_ds_conv()
    fig_posterior_smooth()
    fig_det_curve()
    fig_stream_conv_strip()
    fig_stream_vs_oneshot()
    print("OK: 13 фігур у", IMG)
