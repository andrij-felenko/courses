# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки §1.9.1m — «Центральна гранична
теорема: чому шум гаусів». Чистий Python, без залежностей. Вивід → ./img/
з УНІКАЛЬНИМИ іменами clt-*.svg.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація підписів: Рис. 1.9.1m.k.
НЕ чіпає головний figs.py розділу.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
ORANGE = "#e08030"
PURPLE = "#7a3ea8"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey"}


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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polygon(points, fill=INK, stroke="none", sw=0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def circle(cx, cy, r, fill=INK, stroke="none", sw=0):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.9.1m.1 — збіжність до Гаусса: розподіл суми n рівномірних доданків.
#  n=1 (плаский брусок) → n=2 (трикутник) → n=3 → n=12 (вже майже дзвін).
#  Точна згортка рівномірних (B-сплайн / функція Ірвіна—Голла), без random.
# ════════════════════════════════════════════════════════════════════════════

def _irwin_hall_pdf(x, n):
    """Щільність суми n незалежних U(0,1) у точці x (0<=x<=n). Точна формула."""
    if x < 0 or x > n:
        return 0.0
    total = 0.0
    for k in range(0, int(math.floor(x)) + 1):
        term = ((-1) ** k) * math.comb(n, k) * (x - k) ** (n - 1)
        total += term
    return total / math.factorial(n - 1)


def fig_convergence():
    W, H = 960, 470
    s = header(W, H)
    s += text(W / 2, 28, "Складаємо однакові «брусочки» — і сума сама стає дзвоном",
              18, INK, "middle", "bold")
    s += text(W / 2, 49,
              "Розподіл суми n незалежних рівномірних чисел U(0,1). Кожен доданок — плаский брусок; уже за n≈12 сума майже не відрізнити від Гаусса",
              11.3, GREY, "middle", style="italic")

    panels = [
        (1, "n = 1", "один доданок: плаский брусок", BLUE),
        (2, "n = 2", "сума двох: трикутник", PURPLE),
        (3, "n = 3", "сума трьох: уже горбок", ORANGE),
        (12, "n = 12", "сума дванадцяти ≈ дзвін", RED),
    ]
    pw = 218          # ширина панелі
    gap = 18
    x0 = (W - (pw * 4 + gap * 3)) / 2
    baseY = 360
    ph = 230          # висота поля під криву

    for idx, (n, lab, sub, col) in enumerate(panels):
        px = x0 + idx * (pw + gap)
        # центруємо й нормуємо по z = (x - n/2) / sqrt(n/12): один масштаб для всіх панелей
        mean = n / 2.0
        sd = math.sqrt(n / 12.0)
        # будуємо щільність у пікселях; шкала z від -3.4 до 3.4
        zlo, zhi = -3.4, 3.4
        # пік стандартного гаусса для відмасштабування висоти всіх панелей однаково
        # знайдемо макс щільності p(x) у z-одиницях: p_z(z) = p_x(mean+z*sd)*sd
        zz = [zlo + (zhi - zlo) * j / 200 for j in range(201)]
        dens = []
        for z in zz:
            xv = mean + z * sd
            p = _irwin_hall_pdf(xv, n) * sd
            dens.append(p)
        pmax = max(dens) if max(dens) > 0 else 1.0

        # рамка-фон
        s += rect(px, baseY - ph, pw, ph, "#fcfcfc", FAINT, 1.3, 4)
        # вісь
        s += line(px, baseY, px + pw, baseY, GREY, 1.4)

        # еталонний гаусів дзвін (пунктир) — той самий у кожній панелі
        gpts = []
        for j in range(161):
            z = zlo + (zhi - zlo) * j / 160
            g = math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)
            xpx = px + pw * (z - zlo) / (zhi - zlo)
            ypx = baseY - ph * 0.92 * (g / (1 / math.sqrt(2 * math.pi)))
            gpts.append((xpx, ypx))
        s += polyline(gpts, GREEN, 1.6, "5,4")

        # фактична крива/щільність суми (заливка + контур)
        fillpts = [(px, baseY)]
        for j, z in enumerate(zz):
            xpx = px + pw * (z - zlo) / (zhi - zlo)
            ypx = baseY - ph * 0.92 * (dens[j] / pmax) * (pmax / (1 / math.sqrt(2 * math.pi)) if False else 1.0)
            # масштаб: висота кривої = 0.92*ph для її власного піка (щоб форма читалась)
            ypx = baseY - ph * 0.92 * (dens[j] / pmax)
            fillpts.append((xpx, ypx))
        fillpts.append((px + pw, baseY))
        # світла заливка кольором панелі
        light = {BLUE: "#dbe6fa", PURPLE: "#e7dcf2", ORANGE: "#f6e6d4", RED: "#f6d9d6"}[col]
        s += polygon(fillpts, light)
        s += polyline(fillpts[1:-1], col, 2.6)

        # підписи
        s += text(px + pw / 2, baseY - ph - 10, lab, 15, col, "middle", "bold")
        s += text(px + pw / 2, baseY + 20, sub, 10.5, INK, "middle")
        s += text(px + pw / 2, baseY + 36, "(масштабовано до однакової ширини)", 9, GREY, "middle", style="italic")

    # легенда: зелений пунктир = ідеальний Гаусс
    ly = baseY + 60
    s += line(x0, ly, x0 + 34, ly, GREEN, 1.6, "5,4")
    s += text(x0 + 42, ly + 4, "ідеальний гаусів дзвін N(0,1) — спільний еталон у кожній панелі", 12, GREEN, "start", "bold")

    save("clt-convergence-uniform.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.9.1m.2 — фізична картина: тепловий шум = сума мільярдів крихітних
#  незалежних поштовхів. Зліва доріжки окремих внесків, праворуч їхня сума —
#  гаусів дзвін. Підкреслює σ_суми = √N · σ_внеску (зростання повільніше за N).
# ════════════════════════════════════════════════════════════════════════════

def _kick(t, seed):
    # детермінований «випадковий» внесок: сума несумірних синусоїд (стабільно між запусками)
    a = (seed * 0.7) % 6.283
    b = (seed * 1.9 + 1.1) % 6.283
    c = (seed * 3.3 + 0.4) % 6.283
    return (0.6 * math.sin(2.0 * t + a)
            + 0.5 * math.sin(3.7 * t + b)
            + 0.4 * math.sin(6.1 * t + c))


def fig_physical_sum():
    W, H = 960, 470
    s = header(W, H)
    s += text(W / 2, 28, "Чому шум гаусів: один замір — це сума мільярдів незалежних поштовхів",
              17.5, INK, "middle", "bold")
    s += text(W / 2, 49,
              "Кожен електрон штовхає напругу трішки й по-своєму (зліва). КОЖЕН внесок — будь-якої форми; їхня СУМА (справа) — завжди дзвін",
              11.0, GREY, "middle", style="italic")

    # ---- ліва панель: кілька окремих внесків, що накладаються ----
    lx, ly = 56, 350
    lw, lh = 470, 250
    midy = ly - lh / 2
    s += rect(lx, ly - lh, lw, lh, "#fcfcfc", FAINT, 1.3, 4)
    s += line(lx, midy, lx + lw, midy, GREY, 1.2, "6,4")
    s += text(lx + 6, ly - lh + 16, "окремі внески (кожен крихітний і незалежний)", 11.5, INK, "start", "bold")

    cols = [BLUE, GREEN, ORANGE, PURPLE, "#1aa0a0", "#b05a9a"]
    N = 360
    T = 24.0
    nsig = 6
    sub_amp = lh / 2 / 3.0   # амплітуда одного внеску (маленька)
    for si in range(nsig):
        pts = []
        for i in range(N + 1):
            t = T * i / N
            v = _kick(t, si + 1)
            x = lx + lw * i / N
            y = midy - v * sub_amp
            pts.append((x, y))
        s += polyline(pts, cols[si % len(cols)], 1.2)
    s += text(lx + lw - 6, midy - lh / 2 + 22, "… і так мільярди", 11, GREY, "end", style="italic")
    s += text(lx - 8, midy + 4, "ΔU", 12.5, INK, "end", "bold", "italic")

    # стрілка-перехід «сума»
    axc = (lx + lw + 545) / 2
    s += arrow(lx + lw + 8, midy, 560, midy, INK, 2.4)
    s += text((lx + lw + 8 + 560) / 2, midy - 12, "Σ", 22, INK, "middle", "bold")
    s += text((lx + lw + 8 + 560) / 2, midy + 22, "сума", 11, INK, "middle")

    # ---- права панель: сума всіх внесків у часі + її гістограма-дзвін збоку ----
    rx, ry = 580, 350
    rw, rh = 250, 250
    rmidy = ry - rh / 2
    s += rect(rx, ry - rh, rw, rh, "#fcfcfc", FAINT, 1.3, 4)
    s += line(rx, rmidy, rx + rw, rmidy, GREEN, 1.6, "6,4")
    s += text(rx + 6, ry - rh + 16, "їхня сума U(t)", 11.5, RED, "start", "bold")

    # сума: складаємо багато зсунутих внесків -> за CLT виходить «шумова» доріжка
    Ns = 700
    Ts = 24.0
    M = 40            # скільки внесків підсумовуємо для доріжки
    sumvals = []
    sumpts = []
    for i in range(Ns + 1):
        t = Ts * i / Ns
        acc = 0.0
        for k in range(M):
            acc += _kick(t, 1 + k * 1.000)  # фазово різні
        acc /= math.sqrt(M)   # нормуємо, щоб σ не «втекла»
        sumvals.append(acc)
    smax = max(abs(v) for v in sumvals)
    sc = (rh / 2) / (smax * 1.05)
    for i in range(Ns + 1):
        x = rx + rw * i / Ns
        y = rmidy - sumvals[i] * sc
        sumpts.append((x, y))
    s += polyline(sumpts, RED, 1.5)
    s += text(rx - 8, rmidy + 4, "U", 12.5, INK, "end", "bold", "italic")

    # гістограма суми збоку (вертикальна вісь значень спільна) -> дзвін
    hx0 = rx + rw + 16
    hw = 150
    nb = 21
    vmin, vmax = -smax * 1.05, smax * 1.05
    counts = [0] * nb
    for v in sumvals:
        bb = int((v - vmin) / (vmax - vmin) * nb)
        if 0 <= bb < nb:
            counts[bb] += 1
    cmax = max(counts)
    binh = rh / nb
    s += text(hx0, ry - rh + 16, "розподіл суми", 11.5, BLUE, "start", "bold")
    for bb in range(nb):
        vc = vmin + (bb + 0.5) / nb * (vmax - vmin)
        yc = rmidy - vc * sc
        bl = hw * counts[bb] / cmax
        s += rect(hx0, yc - binh / 2 + 0.8, bl, binh - 1.6, "#dbe6fa", BLUE, 0.9, 1.2)
    # накладений гаусів контур
    sigma_v = math.sqrt(sum(v * v for v in sumvals) / len(sumvals))
    gpts = []
    for j in range(121):
        v = vmin + (vmax - vmin) * j / 120
        g = math.exp(-0.5 * (v / sigma_v) ** 2)
        x = hx0 + g * hw
        y = rmidy - v * sc
        gpts.append((x, y))
    s += polyline(gpts, RED, 2.6)
    s += text(hx0 + hw, rmidy - 2.0 * sigma_v * sc, "гаусів", 11, RED, "end", "bold", "italic")
    s += line(hx0, rmidy, hx0 + hw, rmidy, GREEN, 1.2, "6,4")

    # нижня плашка з ключовим співвідношенням
    by = 420
    s += rect(lx, by, 778, 36, "#f3f7ef", GREEN, 1.3, 6)
    s += text(lx + 14, by + 23,
              "Ширина дзвону росте як √N, а не як N:  σ(сума) = √N · σ(внесок)  —  тому шум помітний, але не нескінченний.",
              13, "#0d5a26", "start", "bold")

    save("clt-physical-sum.svg", s)


if __name__ == "__main__":
    fig_convergence()
    fig_physical_sum()
    print("done")
