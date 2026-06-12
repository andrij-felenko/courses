# -*- coding: utf-8 -*-
"""
Генератор SVG для 🧮-вставки §3.6.8m — «Тунелювання: електрон крізь ізолятор
(Фаулер—Нордгайм, чому запис у Flash зношує комірку)» (Модуль 3, Розділ 3.6,
до теми 3.6.8).

Окремий скрипт вставки (головний figs.py розділу НЕ чіпаємо). Чистий Python,
без сторонніх залежностей. Вивід → ./img/ тієї самої папки розділу.
Імена файлів унікальні: fig-19-8m-*.svg (8m = вставка до теми 3.6.8).

Стиль (AUTHORING §9): білий фон; sans-serif; стрілки через marker; «−» синій
(електрони), поле/успіх — зелене, ушкодження — червоне; єдиний вигляд із рештою
розділу — допоміжні функції скопійовано з figs.py розділу.
Підписи у тексті — «Рис. 3.6.8m.k».
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def poly(pts, fill="none", stroke=INK, sw=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polyline points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d} stroke-linejoin="round"/>\n'


def path(d, fill="none", stroke=INK, sw=2, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da} stroke-linejoin="round"/>\n'


def circle(cx, cy, r, fill="none", stroke=INK, sw=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def electron(cx, cy, r=7.0):
    """Електрон — синє кружальце зі знаком «−»."""
    s = circle(cx, cy, r, "#dfe6f7", BLUE, 1.6)
    s += text(cx, cy + r * 0.55, "−", r * 1.8, BLUE, "middle", "bold")
    return s


def wrap(s, n):
    words = s.split()
    out, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= n:
            cur = (cur + " " + w).strip()
        else:
            out.append(cur); cur = w
    if cur:
        out.append(cur)
    return out


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.6.8m.1 — енергетичний бар'єр оксиду й тунелювання крізь нього
#   ліворуч: товстий прямокутний бар'єр, нема поля → класично «стіна»;
#   праворуч: поле нахиляє бар'єр у трикутник (Фаулер—Нордгайм) → тонкий
#             кінчик, крізь який електрон просочується.
# ════════════════════════════════════════════════════════════════════════════
def fig_barrier():
    W, H = 940, 540
    s = header(W, H)
    s += text(W / 2, 32, "Чому електрон узагалі проходить крізь ізолятор: тунелювання", 20.5, INK, "middle", "bold")
    s += text(W / 2, 54, "оксид — енергетична «стіна»; класична частинка стала б, квантова — просочується, і то тим легше, чим стіна тонша",
              11.5, GREY, "middle", style="italic")

    def panel(x0, title, sub, tilt):
        s = rect(x0, 86, 400, 392, "#fcfcfc", FAINT, 1.4, 10)
        s2 = text(x0 + 200, 112, title, 15, INK, "middle", "bold")
        s2 += text(x0 + 200, 130, sub, 11, GREY, "middle", style="italic")
        # осі: горизонталь — координата крізь шари, вертикаль — енергія електрона
        ax, ay = x0 + 46, 452           # початок осей
        aw, ah = 320, 270               # ширина/висота поля
        s2 += arrow(ax, ay, ax, ay - ah - 8, INK, 1.6)         # вгору — енергія
        s2 += arrow(ax, ay, ax + aw + 6, ay, INK, 1.6)         # вправо — x
        s2 += text(ax - 8, ay - ah - 14, "енергія", 11, GREY, "middle")
        s2 += text(ax + aw + 6, ay + 16, "крізь шари →", 11, GREY, "end")
        # три зони по x: лівий електрод | оксид | плавучий затвор
        ox1 = ax + 120                  # лівий край оксиду
        ox2 = ax + 210                  # правий край оксиду
        # рівень електрона зліва (енергія Ферми)
        elev = ay - 70
        s2 += line(ax + 6, elev, ox1, elev, BLUE, 2.4)
        s2 += text(ax + 10, elev - 8, "рівень електрона", 10.5, BLUE, "start", "bold")
        # бар'єр оксиду
        btop = ay - ah + 14             # верх бар'єра (висота φ)
        if not tilt:
            # прямокутний бар'єр (нема поля)
            s2 += rect(ox1, btop, ox2 - ox1, ay - btop, "#f1f1f1", INK, 2.2)
            s2 += text((ox1 + ox2) / 2, btop - 8, "бар'єр φ", 11, INK, "middle", "bold")
            s2 += text((ox1 + ox2) / 2, (btop + ay) / 2, "оксид", 12, GREY, "middle", "bold")
            # товщина
            s2 += line(ox1, ay + 14, ox2, ay + 14, GREY, 1.4)
            s2 += text((ox1 + ox2) / 2, ay + 30, "повна товщина", 10, GREY, "middle")
            # класична частинка відбивається
            s2 += electron(ox1 - 26, elev)
            s2 += arrow(ox1 - 26, elev - 12, ox1 - 6, elev - 12, RED, 1.8)
            s2 += path(f"M {ox1-6} {elev-12} q 14 -10 0 -20", "none", RED, 1.8)
            s2 += text((ax + ox1) / 2 - 6, elev - 40, "класично:", 10.5, RED, "middle", "bold")
            s2 += text((ax + ox1) / 2 - 6, elev - 27, "відскік", 10.5, RED, "middle", "bold")
            # права зона
            s2 += line(ox2, elev, ax + aw - 4, elev, GREY, 1.6, "4 3")
            s2 += text(ax + aw - 6, elev - 8, "плавучий затвор", 10, GREY, "end")
        else:
            # трикутний бар'єр: поле нахиляє верх, права сторона з'їжджає вниз
            tip_y = elev                # на рівні електрона права грань опускається
            s2 += poly([(ox1, btop), (ox1, ay), (ox2, ay), (ox2, tip_y + (ay - elev) * 0.0)],
                       "#eef6ef", GREEN, 2.2)
            # власне трикутник «над рівнем електрона», крізь який тунелюють
            s2 += poly([(ox1, btop), (ox2, tip_y), (ox1, tip_y)], "#dff0e2", GREEN, 0)
            s2 += line(ox1, btop, ox2, tip_y, GREEN, 2.4)      # нахилена вершина
            s2 += text((ox1 + ox2) / 2 + 4, btop - 8, "нахилений полем", 10.5, GREEN, "middle", "bold")
            s2 += text((ox1 + ox2) / 2, (btop + ay) / 2 + 18, "оксид", 12, GREY, "middle", "bold")
            # ефективна (тонка) ширина бар'єра на рівні електрона
            # точка, де нахилена вершина перетинає рівень електрона:
            xc = ox1 + (ox2 - ox1) * (btop - elev) / (btop - tip_y) if (btop - tip_y) else ox2
            s2 += line(ox1, elev, xc, elev, RED, 2.6)
            s2 += text((ox1 + xc) / 2, elev - 8, "тонкий кінчик", 10, RED, "middle", "bold")
            s2 += text((ox1 + xc) / 2, ay + 30, "d_еф ≪ товщини", 10, RED, "middle")
            s2 += line(ox1, ay + 14, xc, ay + 14, RED, 1.6)
            # електрон тунелює крізь кінчик
            s2 += electron(ox1 - 26, elev)
            s2 += arrow(ox1 - 26, elev, xc + 26, elev, GREEN, 2.2, "5 3")
            s2 += electron(xc + 40, elev)
            s2 += text((xc + ox2) / 2 + 30, elev - 10, "пройшов!", 10.5, GREEN, "middle", "bold")
            # стрілка поля
            s2 += arrow(ox1 + 6, ay - 8, ox2 - 6, ay - 8, AMBER, 1.6)
            s2 += text((ox1 + ox2) / 2, ay - 14, "поле E", 10, AMBER, "middle", "bold")
        return s + s2

    s += panel(40, "Без поля: повна стіна", "товстий бар'єр — імовірність нікчемна", tilt=False)
    s += panel(500, "Сильне поле: бар'єр-трикутник", "Фаулер—Нордгайм: тонкий кінчик пропускає", tilt=True)

    # нижній підсумок
    s += text(W / 2, H - 14, "тунелювання експоненційно чутливе до ширини: нахилив бар'єр полем → кінчик тонкий → струм потік. Це і є запис/стирання Flash.",
              12, RED, "middle", "bold")
    save("fig-19-8m-1-barrier.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.6.8m.2 — два режими: запис (інжекція) і стирання (Фаулер—Нордгайм),
#   обидва женуть електрони КРІЗЬ той самий оксид, лише в різні боки.
# ════════════════════════════════════════════════════════════════════════════
def fig_program_erase():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 32, "Запис і стирання: електрони силою — крізь той самий оксид", 20.5, INK, "middle", "bold")
    s += text(W / 2, 54, "читання заряду не чіпає (швидке, безмежне); а от загнати/вигнати електрони можна лише ПРОТЯГНУВШИ їх крізь ізолятор",
              11.5, GREY, "middle", style="italic")

    def stack(x0, mode):
        # вертикальний «бутерброд»: керівний затвор / оксид / плавучий / тунельний оксид / канал
        s = ""
        cw = 300
        cx = x0 + cw / 2
        y = 92
        layers = [
            ("керівний затвор (control gate)", 30, "#e9edf7", BLUE),
            ("міжзатворний оксид", 18, "#f3f3f3", GREY),
            ("ПЛАВУЧИЙ ЗАТВОР (заряд тут)", 40, "#fff6da", AMBER),
            ("тунельний оксид (~ кілька нм)", 22, "#f7eceb", RED),
            ("канал / підкладка (channel)", 34, "#eef6ef", GREEN),
        ]
        ys = {}
        yy = y
        for name, h, fill, stroke in layers:
            s += rect(x0, yy, cw, h, fill, stroke, 2.0, 4)
            s += text(cx, yy + h / 2 + 4, name, 10.5, INK, "middle", "bold")
            ys[name] = (yy, h)
            yy += h + 6
        # координати тунельного оксиду й сусідів
        fg_y, fg_h = ys["ПЛАВУЧИЙ ЗАТВОР (заряд тут)"]
        ox_y, ox_h = ys["тунельний оксид (~ кілька нм)"]
        ch_y, ch_h = ys["канал / підкладка (channel)"]
        cgy, cgh = ys["керівний затвор (control gate)"]
        fg_mid = fg_y + fg_h / 2
        ch_mid = ch_y + ch_h / 2

        if mode == "program":
            s = text(cx, y - 28, "ЗАПИС (\"0\"): загнати електрони В пастку", 14.5, RED, "middle", "bold") + s
            s += text(cx, y - 12, "+висока напруга на керівний → поле тягне e⁻ з каналу вгору", 10.5, GREY, "middle", style="italic")
            # знаки напруги
            s += text(x0 - 14, cgy + cgh / 2 + 5, "+V", 14, RED, "end", "bold")
            s += text(x0 - 14, ch_mid + 5, "0", 13, INK, "end", "bold")
            # електрони йдуть угору крізь тунельний оксид
            for dx in (-60, 0, 60):
                s += electron(cx + dx, ch_mid)
                s += arrow(cx + dx, ch_y - 2, cx + dx, fg_y + fg_h - 4, RED, 2.0, "5 3")
            s += electron(cx - 30, fg_mid)
            s += electron(cx + 30, fg_mid)
            s += text(cx, fg_y + fg_h + 0, "", 1)
            # підпис механізму
            s += text(x0 + cw + 16, ox_y + ox_h / 2, "крізь оксид →", 11, RED, "start", "bold")
            s += text(x0 + cw + 16, ox_y + ox_h / 2 + 16, "інжекція носіїв", 10, GREY, "start")
            res = "результат: заряд замкнено → високий поріг → читається «0»"
        else:
            s = text(cx, y - 28, "СТИРАННЯ (\"1\"): вигнати електрони З пастки", 14.5, GREEN, "middle", "bold") + s
            s += text(cx, y - 12, "поле зворотного знаку (з боку каналу) → Фаулер—Нордгайм тягне e⁻ вниз", 10.5, GREY, "middle", style="italic")
            s += text(x0 - 14, cgy + cgh / 2 + 5, "0", 13, INK, "end", "bold")
            s += text(x0 - 14, ch_mid + 5, "+V", 14, GREEN, "end", "bold")
            for dx in (-60, 0, 60):
                s += electron(cx + dx, fg_mid)
                s += arrow(cx + dx, fg_y + fg_h + 2, cx + dx, ch_y + 4, GREEN, 2.0, "5 3")
            s += electron(cx - 30, ch_mid)
            s += electron(cx + 30, ch_mid)
            s += text(x0 + cw + 16, ox_y + ox_h / 2, "← крізь оксид", 11, GREEN, "start", "bold")
            s += text(x0 + cw + 16, ox_y + ox_h / 2 + 16, "Ф.—Н. тунелювання", 10, GREY, "start")
            res = "результат: пастка порожня → низький поріг → читається «1»"
        # підсумковий рядок під стеком
        s += rect(x0, ch_y + ch_h + 14, cw, 30, "#fbfbfb", FAINT, 1.3, 6)
        for j, ln in enumerate(wrap(res, 44)):
            s += text(cx, ch_y + ch_h + 14 + 19 + j * 0, ln, 10.5, INK, "middle", "bold")
        return s

    s += stack(70, "program")
    s += stack(560, "erase")

    # центральна вертикальна риска-роздільник
    s += line(W / 2, 100, W / 2, 360, FAINT, 1.4, "3 4")

    # спільний нижній висновок
    s += text(W / 2, H - 14, "обидва напрями — це примусове протягування заряду крізь оксид; саме воно повільне і саме воно зношує комірку (Рис. 3.6.8m.3)",
              12, RED, "middle", "bold")
    save("fig-19-8m-2-program-erase.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.6.8m.3 — чому кожен прохід зношує: пастки в оксиді накопичуються,
#   читацьке вікно між «0» і «1» звужується → ресурс ~10⁴–10⁵ циклів.
#   Ліворуч — оксид свіжий/зношений (дефекти); праворуч — графік зсуву порогів.
# ════════════════════════════════════════════════════════════════════════════
def fig_wear():
    W, H = 940, 540
    s = header(W, H)
    s += text(W / 2, 32, "Чому кожен запис зношує комірку: пастки в оксиді накопичуються", 20.5, INK, "middle", "bold")
    s += text(W / 2, 54, "протягуючи електрони, частину їх оксид «ловить» назавжди; дефекти ростуть, вікно між «0» і «1» звужується — звідси скінченний ресурс",
              11.5, GREY, "middle", style="italic")

    # ── ЛІВА панель: свіжий vs зношений оксид ────────────────────────────────
    def oxide(x0, y0, title, sub, traps, stuck, col):
        s = rect(x0, y0, 340, 150, "#fcfcfc", FAINT, 1.4, 8)
        s += text(x0 + 170, y0 + 22, title, 14, col, "middle", "bold")
        s += text(x0 + 170, y0 + 38, sub, 10.5, GREY, "middle", style="italic")
        ox_x, ox_y, ox_w, ox_h = x0 + 30, y0 + 52, 280, 70
        s += rect(ox_x, ox_y, ox_w, ox_h, "#f5f0ef", RED, 1.8, 4)
        s += text(ox_x - 4, ox_y + ox_h / 2 + 4, "оксид", 10, GREY, "end")
        # дефекти-пастки як маленькі ×
        import random
        rnd = random.Random(traps * 13 + 7)
        for _ in range(traps):
            px = ox_x + 14 + rnd.random() * (ox_w - 28)
            py = ox_y + 12 + rnd.random() * (ox_h - 24)
            s_ = 4
            s += line(px - s_, py - s_, px + s_, py + s_, RED, 1.4)
            s += line(px - s_, py + s_, px + s_, py - s_, RED, 1.4)
        # «застряглі» захоплені електрони (сині, обведені червоним)
        rnd2 = random.Random(stuck * 31 + 3)
        for _ in range(stuck):
            px = ox_x + 18 + rnd2.random() * (ox_w - 36)
            py = ox_y + 16 + rnd2.random() * (ox_h - 32)
            s += circle(px, py, 5.5, "#dfe6f7", RED, 1.6)
            s += text(px, py + 3, "−", 9, BLUE, "middle", "bold")
        return s

    lx = 40
    s += oxide(lx, 86, "Свіжий оксид", "майже бездоганний — заряд проходить чисто", 5, 0, GREEN)
    s += oxide(lx, 252, "Зношений оксид", "тисячі циклів: пастки й застряглі заряди", 26, 7, RED)
    # стрілка «тисячі циклів»
    s += arrow(lx + 170, 240, lx + 170, 250, GREY, 1.8)
    s += text(lx + 184, 247, "×10⁴–10⁵ циклів", 11, GREY, "start", "bold")
    s += text(lx + 14, 430, "Захоплений у дефектах заряд:", 11.5, INK, "start", "bold")
    for j, ln in enumerate(wrap("сам собою зсуває поріг (паразитний заряд, не той, що ми поклали), а ще полегшує витік накопиченого — комірка перестає чітко розрізняти «0» і «1».", 52)):
        s += text(lx + 14, 450 + j * 17, ln, 11, INK, "start")

    # ── ПРАВА панель: графік звуження вікна порогів від числа циклів ─────────
    gx, gy = 470, 470          # початок осей графіка
    gw, gh = 420, 300
    s += rect(gx - 14, gy - gh - 28, gw + 40, gh + 70, "#fcfcfc", FAINT, 1.4, 8)
    s += text(gx + gw / 2, gy - gh - 8, "Вікно читання звужується з кожною тисячею циклів", 13.5, INK, "middle", "bold")
    s += arrow(gx, gy, gx, gy - gh - 6, INK, 1.6)
    s += arrow(gx, gy, gx + gw + 6, gy, INK, 1.6)
    s += text(gx - 8, gy - gh - 2, "поріг Vt", 10.5, GREY, "end")
    s += text(gx + gw, gy + 18, "цикли запис/стирання (лог) →", 10.5, GREY, "end")
    # вісь циклів: позначки 1, 10², 10⁴, 10⁵, кінець
    xticks = [("1", 0.0), ("10²", 0.28), ("10⁴", 0.62), ("10⁵", 0.82), ("знос", 1.0)]
    for lab, fr in xticks:
        xx = gx + 20 + fr * (gw - 40)
        s += line(xx, gy, xx, gy + 5, GREY, 1.4)
        s += text(xx, gy + 18, lab, 10, GREY, "middle")

    def yv(level):  # level 0..1 (0 низ, 1 верх) → координата
        return gy - 10 - level * (gh - 30)

    # крива «0» (високий поріг) повзе вниз; крива «1» (низький поріг) повзе вгору
    n = 60
    hi, lo = [], []
    for i in range(n + 1):
        fr = i / n
        # «0»: старт 0.86, дрейф униз, що пришвидшується наприкінці
        v0 = 0.86 - 0.30 * (fr ** 1.6)
        # «1»: старт 0.20, дрейф угору (паразитний захоплений заряд)
        v1 = 0.20 + 0.34 * (fr ** 1.7)
        xx = gx + 20 + fr * (gw - 40)
        hi.append((xx, yv(v0)))
        lo.append((xx, yv(v1)))
    # заштрихована «вікно» між кривими
    s += poly(hi + lo[::-1], "#eef6ef", "none", 0)
    s += poly(hi, "none", RED, 2.6)
    s += poly(lo, "none", BLUE, 2.6)
    s += text(hi[2][0] + 4, hi[2][1] - 8, "поріг «0» (заряд є)", 11, RED, "start", "bold")
    s += text(lo[2][0] + 4, lo[2][1] + 18, "поріг «1» (заряду нема)", 11, BLUE, "start", "bold")
    # рівень опорного читання
    sense = yv(0.53)
    s += line(gx + 20, sense, gx + gw - 14, sense, GREY, 1.6, "5 4")
    s += text(gx + gw - 16, sense - 6, "рівень розрізнення", 10, GREY, "end", style="italic")
    # стрілки «вікно» на початку (широке) і в кінці (вузьке)
    s += arrow(hi[6][0], hi[6][1] + 4, lo[6][0], lo[6][1] - 4, GREEN, 1.6)
    s += arrow(lo[6][0], lo[6][1] - 4, hi[6][0], hi[6][1] + 4, GREEN, 1.6)
    s += text(hi[6][0] - 6, (hi[6][1] + lo[6][1]) / 2, "широке", 10, GREEN, "end", "bold")
    s += arrow(hi[n - 3][0], hi[n - 3][1] + 3, lo[n - 3][0], lo[n - 3][1] - 3, RED, 1.6)
    s += arrow(lo[n - 3][0], lo[n - 3][1] - 3, hi[n - 3][0], hi[n - 3][1] + 3, RED, 1.6)
    s += text(hi[n - 3][0] + 8, (hi[n - 3][1] + lo[n - 3][1]) / 2 + 4, "вузьке →", 10, RED, "start", "bold")
    # вертикаль «кінець ресурсу»
    xe = gx + 20 + 1.0 * (gw - 40)
    s += line(xe, gy, xe, yv(0.9), RED, 1.6, "3 3")
    s += text(xe - 4, yv(0.95), "ресурс вичерпано", 10.5, RED, "end", "bold")

    s += text(W / 2, H - 12, "коли поріг «0» і поріг «1» зближаються так, що датчик їх плутає, — комірка зношена; це і є межа ~10⁴–10⁵ циклів із §3.6.3",
              12, RED, "middle", "bold")
    save("fig-19-8m-3-wear.svg", s)


if __name__ == "__main__":
    fig_barrier()
    fig_program_erase()
    fig_wear()
    print("ch19 §3.6.8m insert figures done.")
