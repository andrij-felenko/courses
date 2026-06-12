# -*- coding: utf-8 -*-
"""
Генератор SVG для ⚙️-вставки до §3.4.8 — «UTF-8 декодер вручну».
Окремий скрипт вставки (головний figs.py розділу не чіпаємо). Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; «1» червоний, «0» синій; «корисне/безпечне»
зелене; стрілки через marker; шрифт sans-serif. Підписи — Рис. 3.4.8a.k.
Допоміжні функції скопійовані з figs.py розділу (щоб скрипти не ділили файлів).

Бітові патерни звірені з еталонним кодуванням Python str.encode('utf-8'):
  'A' U+0041 -> 41                          (1 байт, ASCII)
  'ї' U+0457 -> D1 97   = 11010001 10010111 (2 байти)
  '€' U+20AC -> E2 82 AC                     (3 байти)
  '😀' U+1F600 -> F0 9F 98 80                (4 байти)
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"   # біти-«1», небезпека/обгортка
BLUE  = "#1f47b5"   # біти-«0»
GREEN = "#1f8a3b"   # корисне навантаження / безпечно
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"
MONO  = "Consolas, 'Courier New', monospace"


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


def mono(x, y, s, size=13, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{MONO}" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def bitcells(x, y, bits, cw=26, ch=30, roles=None, size=15):
    """Намалювати рядок бітів кольоровими комірками.
    roles[i]: 'p' префікс/маркер (сірий фон), '1'/'0' навантаження (синь/черв),
              'x' вільний слот навантаження (зелений фон, текст-плейсхолдер)."""
    s = ""
    for i, b in enumerate(bits):
        cx = x + i * cw
        role = roles[i] if roles else b
        if role == 'p':
            fill, bcol, tcol, wt = "#eeeeee", GREY, INK, "bold"
        elif role == 'x':
            fill, bcol, tcol, wt = "#eaf5ec", GREEN, GREEN, "bold"
        else:  # навантаження-біт
            fill = "#ffffff"
            bcol = FAINT
            tcol = RED if b == '1' else BLUE
            wt = "bold"
        s += rect(cx, y, cw, ch, fill, bcol, 1.2, 4)
        s += mono(cx + cw / 2, y + ch / 2 + size * 0.35, b, size, tcol, "middle", wt)
    return s


# ── Рис. 3.4.8a.1 — карта провідного байта: префікси задають довжину ────────
def fig_lead_byte_map():
    W, H = 960, 580
    s = header(W, H)
    s += text(W / 2, 34, "Провідний байт сам каже свою довжину — старшими бітами", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "префікс (сірий) — це маркер; вільні слоти (зелені) несуть біти коду символу",
              12, GREY, "middle", style="italic")

    cw = 18
    x0 = 196
    rows = [
        # (підпис, бітшаблон-літери, діапазон, скільки біт навантаження)
        ("1 байт (ASCII)", "0xxxxxxx", "U+0000 … U+007F", "7 біт"),
        ("2 байти", "110xxxxx 10xxxxxx", "U+0080 … U+07FF", "11 біт"),
        ("3 байти", "1110xxxx 10xxxxxx 10xxxxxx", "U+0800 … U+FFFF", "16 біт"),
        ("4 байти", "11110xxx 10xxxxxx 10xxxxxx 10xxxxxx", "U+10000 … U+10FFFF", "21 біт"),
    ]

    def roles_for(part):
        return ['x' if ch == 'x' else 'p' for ch in part]

    # шапка-«лінійка» байтів
    s += text(x0, 90, "байт 1", 11, GREY, "start", "bold")
    s += text(x0 + 9 * cw, 90, "байт 2", 11, GREY, "start", "bold")
    s += text(x0 + 18 * cw, 90, "байт 3", 11, GREY, "start", "bold")
    s += text(x0 + 27 * cw, 90, "байт 4", 11, GREY, "start", "bold")

    y = 100
    gap = 6
    for label, tmpl, rng, paybits in rows:
        s += text(56, y + 21, label, 13.5, INK, "start", "bold")
        bx = x0
        for part in tmpl.split(" "):
            s += bitcells(bx, y, list(part), cw, 30, roles_for(part))
            bx += len(part) * cw + gap
        s += text(56, y + 40, rng, 10.5, GREY, "start")
        # навантаження-підпис праворуч від останнього байта
        s += text(bx + 8, y + 14, paybits, 12, GREEN, "start", "bold")
        s += text(bx + 8, y + 30, "коду", 11, GREEN, "start")
        y += 64

    # рамка-пояснення провідних маркерів
    by = y + 8
    s += rect(56, by, 848, 116, "#fafafa", INK, 1.4, 10)
    s += text(78, by + 28, "Як читати перший байт:", 13.5, INK, "start", "bold")
    s += mono(78, by + 54, "0xxxxxxx", 13, INK)
    s += text(168, by + 54, "— старший біт 0 → це звичайний ASCII, 1 байт (див. Рис. 3.4.8a.3).", 12, INK, "start")
    s += mono(78, by + 76, "11…0", 13, INK)
    s += text(168, by + 76, "— кількість одиниць до першого нуля = скільки байтів у символі (110→2, 1110→3, 11110→4).", 12, INK, "start")
    s += mono(78, by + 98, "10xxxxxx", 13, RED)
    s += text(168, by + 98, "— байт-продовження; таким перший байт не буває ніколи — звідси й самосинхронізація.", 12, RED, "start")
    save("fig-17-8a-1-lead-byte-map.svg", s)


# ── Рис. 3.4.8a.2 — зшивання бітів: декодуємо 'ї' (U+0457) ──────────────────
def fig_stitch():
    W, H = 920, 500
    s = header(W, H)
    s += text(W / 2, 34, "Зшивання бітів: декодуємо «ї» з двох байтів D1 97", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "відкидаємо префікси (сірі), зчіплюємо лише навантаження (зелені) у код-точку",
              12, GREY, "middle", style="italic")

    cw = 30
    # Байт 1: 11010001 (D1) — префікс 110, навантаження 10001
    # Байт 2: 10010111 (97) — префікс 10,  навантаження 010111
    b1 = list("11010001")
    r1 = ['p', 'p', 'p', 'x', 'x', 'x', 'x', 'x']
    b2 = list("10010111")
    r2 = ['p', 'p', 'x', 'x', 'x', 'x', 'x', 'x']

    y1 = 96
    s += text(60, y1 + 22, "Байт 1", 14, INK, "start", "bold")
    s += mono(60, y1 + 42, "0xD1", 12.5, GREY)
    x1 = 200
    s += bitcells(x1, y1, b1, cw, 32, r1)
    s += text(x1, y1 - 8, "110 = «2 байти»", 11.5, GREY, "start", "bold")
    s += text(x1 + 3 * cw + 8, y1 - 8, "5 біт коду", 11.5, GREEN, "start", "bold")

    y2 = 168
    s += text(60, y2 + 22, "Байт 2", 14, INK, "start", "bold")
    s += mono(60, y2 + 42, "0x97", 12.5, GREY)
    s += bitcells(x1, y2, b2, cw, 32, r2)
    s += text(x1, y2 - 8, "10 = «продовження»", 11.5, RED, "start", "bold")
    s += text(x1 + 2 * cw + 8, y2 - 8, "6 біт коду", 11.5, GREEN, "start", "bold")

    # стрілки від навантаження вниз до зшитого рядка
    pay1_x = x1 + 3 * cw
    pay2_x = x1 + 2 * cw
    yj = 300
    xj = 250
    # зшитий рядок: 10001 + 010111 = 11 біт
    payload = "10001" + "010111"
    s += text(60, yj + 24, "Зчеплено", 14, GREEN, "start", "bold")
    s += text(60, yj + 44, "11 біт", 12, GREEN, "start")
    s += bitcells(xj, yj, list(payload), cw, 32, ['x'] * 11)
    # дуги-стрілки
    s += arrow(pay1_x + 2.5 * cw, y1 + 34, xj + 2.5 * cw, yj - 2, GREEN, 1.8)
    s += arrow(pay2_x + 3 * cw, y2 + 34, xj + 8 * cw, yj - 2, GREEN, 1.8)
    s += text(xj + 5.5 * cw, yj - 10, "5 біт  ‖  6 біт = 11 біт коду", 11.5, GREEN, "middle", "bold")

    # підсумок: число
    yv = 392
    s += rect(60, yv, 800, 84, "#eaf5ec", GREEN, 1.6, 10)
    s += text(80, yv + 28, "11 біт →  10001 010111₂", 14, INK, "start", "bold")
    s += text(360, yv + 28, "=  0x457  =  1111₁₀  =  U+0457  =  «ї»", 14, GREEN, "start", "bold")
    s += text(80, yv + 56, "Перевірка: будь-який код у діапазоні U+0080…U+07FF влазить рівно в ці 11 біт —",
              12, INK, "start")
    s += text(80, yv + 74, "тому кирилиця, грецька, іврит, арабиця кодуються двома байтами.", 12, INK, "start")
    save("fig-17-8a-2-stitch.svg", s)


# ── Рис. 3.4.8a.3 — чому ASCII вцілів і що таке самосинхронізація ────────────
def fig_ascii_resync():
    W, H = 920, 520
    s = header(W, H)
    s += text(W / 2, 34, "Чому ASCII лишився сумісним і чому потік самосинхронний", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "усі «нові» байти мають старший біт 1 → ніколи не зіткнуться зі 128 байтами ASCII",
              12, GREY, "middle", style="italic")

    # Верх: числова вісь 0..255 з трьома зонами
    ax = 70
    ay = 110
    aw = 780
    s += line(ax, ay, ax + aw, ay, INK, 2)
    for val, lab in [(0, "0x00"), (128, "0x80"), (192, "0xC0"), (256, "0xFF")]:
        px = ax + aw * (val / 256.0)
        s += line(px, ay - 6, px, ay + 6, INK, 1.6)
        s += mono(px, ay + 22, lab, 11.5, GREY, "middle")
    # зони
    def band(v0, v1, col, fill, label, sub):
        x0 = ax + aw * (v0 / 256.0)
        x1 = ax + aw * (v1 / 256.0)
        s_ = rect(x0, ay - 46, x1 - x0, 34, fill, col, 1.5, 6)
        s_ += text((x0 + x1) / 2, ay - 24, label, 12.5, col, "middle", "bold")
        s_ += text((x0 + x1) / 2, ay + 44, sub, 11, col, "middle")
        return s_
    s += band(0, 128, BLUE, "#eef2fb", "ASCII  0x00–0x7F", "біт 7 = 0")
    s += band(128, 192, RED, "#fbeeee", "продовження", "0x80–0xBF · 10xxxxxx")
    s += band(192, 256, AMBER, "#fdf6e9", "провідні 2/3/4-байт", "0xC0–0xFF · 110/1110/11110")

    s += text(W / 2, ay + 70, "Ключ: жоден байт ASCII (ліворуч) не з'являється всередині багатобайтового символу (праворуч).",
              12.5, INK, "middle", "bold")

    # Низ ліворуч: старий ASCII-сканер, що шукає роздільник ','
    bx, by = 60, 220
    s += rect(bx, by, 400, 250, "#fafafa", INK, 1.5, 10)
    s += text(bx + 200, by + 26, "Старий код, що сканує байти", 13.5, INK, "middle", "bold")
    s += text(bx + 200, by + 44, "(шукає кому ',' = 0x2C, рве рядок на поля)", 11, GREY, "middle", style="italic")
    # потік: "ї,A"  => D1 97 2C 41
    seq = [("D1", AMBER, "ї[1]"), ("97", RED, "ї[2]"), ("2C", BLUE, "','"), ("41", BLUE, "'A'")]
    sx = bx + 28
    sy = by + 92
    for i, (h, col, note) in enumerate(seq):
        cx = sx + i * 88
        s += rect(cx, sy, 70, 40, "#ffffff", col, 1.6, 6)
        s += mono(cx + 35, sy + 25, "0x" + h, 13, col, "middle", "bold")
        s += text(cx + 35, sy + 58, note, 10.5, GREY, "middle")
    # вказати, що 0x2C видно, а 0x80+ — ні
    s += text(bx + 200, by + 178, "Сканер шукає байт 0x2C і знаходить його —", 11.5, INK, "middle")
    s += text(bx + 200, by + 196, "бо байти символу «ї» (≥ 0x80) на нього не схожі.", 11.5, INK, "middle")
    s += text(bx + 200, by + 224, "→ розбивка за ASCII-роздільниками працює як є,", 11.5, GREEN, "middle", "bold")
    s += text(bx + 200, by + 242, "навіть нічого не знаючи про UTF-8.", 11.5, GREEN, "middle", "bold")

    # Низ праворуч: ресинхронізація після втрати байта
    rx, ry = 480, 220
    s += rect(rx, ry, 380, 250, "#fafafa", INK, 1.5, 10)
    s += text(rx + 190, ry + 26, "Ресинхронізація після збою", 13.5, INK, "middle", "bold")
    s += text(rx + 190, ry + 44, "загубили байт — знайдемо наступний старт", 11, GREY, "middle", style="italic")
    seq2 = [("XX", GREY, "втрачено"), ("97", RED, "10…"), ("E2", AMBER, "1110…"), ("82", RED, "10…"), ("AC", RED, "10…")]
    sx2 = rx + 18
    sy2 = ry + 92
    for i, (h, col, note) in enumerate(seq2):
        cx = sx2 + i * 70
        s += rect(cx, sy2, 56, 40, "#ffffff", col, 1.6, 6)
        s += mono(cx + 28, sy2 + 25, "0x" + h, 12, col, "middle", "bold")
        s += text(cx + 28, sy2 + 58, note, 10, GREY, "middle")
    # стрілка: пропускаємо 10xxxxxx, чіпляємось за 1110xxxx
    s += arrow(sx2 + 70 + 28, sy2 + 78, sx2 + 2 * 70 + 28, sy2 + 50, GREEN, 1.8)
    s += text(rx + 190, ry + 180, "Декодер пропускає байти 10xxxxxx (продовження),", 11.5, INK, "middle")
    s += text(rx + 190, ry + 198, "доки не зустріне провідний (0xxx або 11xx) —", 11.5, INK, "middle")
    s += text(rx + 190, ry + 224, "і знову в синхроні. Втрата псує ОДИН символ,", 11.5, GREEN, "middle", "bold")
    s += text(rx + 190, ry + 242, "а не весь решту потоку.", 11.5, GREEN, "middle", "bold")
    save("fig-17-8a-3-ascii-resync.svg", s)


if __name__ == "__main__":
    fig_lead_byte_map()
    fig_stitch()
    fig_ascii_resync()
    print("done.")
