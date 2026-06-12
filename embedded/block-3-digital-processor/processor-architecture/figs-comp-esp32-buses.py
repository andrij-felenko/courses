# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для ВСТАВКИ 🔌 «Гарвард на практиці: шини й пам'яті ESP32»
(до теми 3.5.7). Окремий скрипт — головний figs.py розділу не чіпаємо. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif;
«+» червоний, «−» синій, поле зелене (тут кольорами кодуємо шини: код=зелений,
дані=синій, повільний Flash=бурштин). Підписи фігур у тексті — «Рис. 3.5.7c.k».
Допоміжні функції — копія зі стилю розділу 18, щоб вигляд був єдиний.
"""
import os

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
MONO  = "Consolas, 'DejaVu Sans Mono', monospace"


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
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", AMBER: "aAmber"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def darrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    """Двобічна стрілка."""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} '
            f'marker-start="url(#{m})" marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", mono=False):
    fam = MONO if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, fill="none", stroke=INK, w=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def chip(x, y, w, h, title, sub="", fill="#ffffff", stroke=INK, tcol=INK, sw=2, rx=8,
         tsize=16, ssize=11.5):
    """Прямокутний блок із заголовком (і дрібним підписом під ним)."""
    s = rect(x, y, w, h, fill, stroke, sw, rx)
    if sub:
        s += text(x + w / 2, y + h / 2 - 4, title, tsize, tcol, "middle", "bold")
        s += text(x + w / 2, y + h / 2 + 14, sub, ssize, GREY, "middle", style="italic")
    else:
        s += text(x + w / 2, y + h / 2 + 5, title, tsize, tcol, "middle", "bold")
    return s


def badge(cx, cy, s, color, tcol="#ffffff", r=13):
    return circle(cx, cy, r, color, color, 0) + text(cx, cy + 4.5, s, 13, tcol, "middle", "bold")


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ═══════════ Рис. 3.5.7c.1 — карта шин і пам'ятей ESP32 (модиф. Гарвард) ════════
def fig_map():
    W, H = 980, 600
    s = header(W, H)
    s += text(W / 2, 32, "Шини й пам'яті ESP32: Гарвард, видимий неозброєним оком",
              20, INK, "middle", "bold")
    s += text(W / 2, 54,
              "одне ядро — дві окремі дороги: зелена шина команд і синя шина даних; повільний Flash під'єднано через кеш",
              12, GREY, "middle", style="italic")

    # ── ядро ──
    cx0, cy0, cw, chh = 410, 260, 160, 92
    s += chip(cx0, cy0, cw, chh, "Ядро CPU", "Xtensa LX6", "#f3f6ff", INK, INK)
    s += text(cx0 + cw / 2, cy0 - 12, "тут крутиться цикл вибірка→виконання (§3.5.3)",
              11, GREY, "middle", style="italic")

    # дві шини з ядра
    bus_y_i = cy0 + 22      # шина команд (горішня половина ядра)
    bus_y_d = cy0 + 66      # шина даних
    # ── шина команд (зелена) — ліворуч-вгору до IRAM, і праворуч до кеша Flash
    s += text(cx0 - 8, bus_y_i - 8, "шина КОМАНД", 12.5, GREEN, "end", "bold")
    # IRAM ліворуч
    ix, iy, iw, ih = 70, 150, 210, 74
    s += chip(ix, iy, iw, ih, "IRAM", "внутр. RAM під КОД", "#eaf6ee", GREEN, GREEN)
    s += text(ix + iw / 2, iy + ih + 17, "швидко, детерміновано", 11, GREEN, "middle", style="italic")
    s += darrow(cx0, bus_y_i, ix + iw, iy + ih - 18, GREEN, 3)
    # кеш + Flash праворуч (шина команд читає КОД звідти теж)
    kx, ky, kw, kh = 700, 150, 130, 74
    s += chip(kx, ky, kw, kh, "Кеш", "+ MMU", "#eaf6ee", GREEN, GREEN, ssize=11)
    s += darrow(cx0 + cw, bus_y_i, kx, ky + kh - 18, GREEN, 3)
    fx, fy, fw, fh = 860, 150, 96, 74
    s += chip(fx, fy, fw, fh, "Flash", "(зовнішня)", "#fbf3e0", AMBER, "#8a6a1e")
    s += darrow(kx + kw, ky + kh / 2, fx, fy + fh / 2, AMBER, 3)
    s += text((kx + kw + fx) / 2, ky - 12, "SPI", 11, "#8a6a1e", "middle", "bold")
    s += text((kx + kw + fx) / 2, ky + kh + 18, "повільно, серійно", 10.5, "#8a6a1e", "middle", style="italic")

    # ── шина даних (синя) — праворуч-вниз до DRAM, і ліворуч до периферії ──
    s += text(cx0 + cw + 8, bus_y_d - 8, "шина ДАНИХ", 12.5, BLUE, "start", "bold")
    dx, dy, dw, dh = 700, 360, 210, 74
    s += chip(dx, dy, dw, dh, "DRAM", "внутр. RAM під ДАНІ", "#eaf0fb", BLUE, BLUE)
    s += text(dx + dw / 2, dy + dh + 17, "змінні, стек, купа (§3.5.2)", 11, BLUE, "middle", style="italic")
    s += darrow(cx0 + cw, bus_y_d, dx, dy + 18, BLUE, 3)
    # периферія ліворуч від ядра по шині даних
    px, py, pw, ph = 70, 360, 210, 74
    s += chip(px, py, pw, ph, "Периферія", "регістри GPIO/UART…", "#eaf0fb", BLUE, BLUE, ssize=11)
    s += darrow(cx0, bus_y_d, px + pw, py + 18, BLUE, 3)

    # ── підпис-висновок ──
    s += rect(70, 500, W - 140, 74, "#fafafa", FAINT, 1.5, 8)
    s += text(90, 524, "Читай так:", 13.5, INK, "start", "bold")
    s += text(170, 524,
              "вибірка КОМАНДИ (зелена) і доступ до ДАНИХ (синя) їдуть РІЗНИМИ шинами — отже, можуть статися ЗА ОДИН",
              12.5, INK, "start")
    s += text(170, 544,
              "такт паралельно (§3.5.7). Це і є Гарвард. «Модифікований» він тому, що під обома шинами —",
              12.5, INK, "start")
    s += text(170, 564,
              "СПІЛЬНИЙ простір адрес, а величезний КОД лежить у зовнішньому Flash і потрапляє на шину команд через кеш.",
              12.5, INK, "start")
    save("fig-3-5-7c-1-esp32-map.svg", s)


# ═══════════ Рис. 3.5.7c.2 — кеш Flash: влучення проти промаху ═════════════════
def fig_cache():
    W, H = 980, 560
    s = header(W, H)
    s += text(W / 2, 32, "Кеш Flash: як повільна пам'ять вдає швидку шину команд",
              20, INK, "middle", "bold")
    s += text(W / 2, 54,
              "ядро просить команду за адресою; кеш або вже має її (влучення, швидко), або біжить по неї у Flash (промах, пауза)",
              12, GREY, "middle", style="italic")

    # ядро ліворуч
    ex, ey, ew, eh = 40, 235, 150, 96
    s += chip(ex, ey, ew, eh, "Ядро CPU", "потрібна команда", "#f3f6ff", INK, INK)
    # кеш посередині
    kx, ky, kw, kh = 360, 210, 220, 150
    s += rect(kx, ky, kw, kh, "#eaf6ee", GREEN, 2, 8)
    s += text(kx + kw / 2, ky + 30, "Кеш + MMU", 17, GREEN, "middle", "bold")
    s += text(kx + kw / 2, ky + 52, "тримає копії гарячих", 11, GREY, "middle", style="italic")
    s += text(kx + kw / 2, ky + 68, "шматків коду у швидкій RAM", 11, GREY, "middle", style="italic")
    # «рядки кеша»
    for i in range(3):
        ly = ky + 90 + i * 18
        filled = (i != 1)
        s += rect(kx + 24, ly, kw - 48, 14, "#cdeccd" if filled else "#ffffff", GREEN, 1.5, 3)
    # Flash праворуч
    fx, fy, fw, fh = 770, 235, 170, 96
    s += chip(fx, fy, fw, fh, "Flash", "увесь код, зовні", "#fbf3e0", AMBER, "#8a6a1e")
    s += text(fx + fw / 2, fy - 12, "велика, але повільна, по SPI", 11, "#8a6a1e", "middle", style="italic")

    # запит ядро → кеш
    s += arrow(ex + ew, ey + eh / 2, kx, ky + kh / 2, INK, 2.6)
    s += text((ex + ew + kx) / 2, ey + eh / 2 - 10, "адреса", 11.5, INK, "middle", "bold")

    # ВЛУЧЕННЯ (зелена відповідь назад)
    s += arrow(kx, ky + 96, ex + ew, ey + 30, GREEN, 2.8)
    s += text((ex + ew + kx) / 2, ey + 16, "ВЛУЧЕННЯ → команда вмить", 12, GREEN, "middle", "bold")
    s += text((ex + ew + kx) / 2, ey + 78, "як зі звичайної RAM", 10.5, GREEN, "middle", style="italic")

    # ПРОМАХ (бурштинова дорога до Flash і назад)
    s += arrow(kx + kw, ky + kh / 2, fx, fy + fh / 2, AMBER, 2.8)
    s += arrow(fx, fy + fh - 16, kx + kw, ky + kh - 16, AMBER, 2.8, dash="6 5")
    s += text((kx + kw + fx) / 2, fy + fh / 2 - 10, "ПРОМАХ:", 12, "#8a6a1e", "middle", "bold")
    s += text((kx + kw + fx) / 2, fy + fh / 2 + 8, "по шматок", 11, "#8a6a1e", "middle")
    s += text((kx + kw + fx) / 2, fy + fh + 18, "ядро ЧЕКАЄ сотні тактів", 11.5, RED, "middle", "bold")

    # нижній висновок
    s += rect(40, 470, W - 80, 70, "#fafafa", FAINT, 1.5, 8)
    s += text(60, 496, "Чому це важить:", 13.5, INK, "start", "bold")
    s += text(190, 496,
              "поки код у кеші — він летить; перший дотик до «холодного» шматка коштує паузи на читання з Flash.",
              12.5, INK, "start")
    s += text(190, 520,
              "А якщо кеш на мить ВИМКНЕНО (про це — наступна фігура), код у Flash стає геть недосяжним.",
              12.5, INK, "start")
    save("fig-3-5-7c-2-flash-cache.svg", s)


# ═══════════ Рис. 3.5.7c.3 — навіщо IRAM_ATTR ════════════════════════════════
def fig_iram():
    W, H = 980, 590
    s = header(W, H)
    s += text(W / 2, 32, "Навіщо IRAM_ATTR: код, що мусить працювати, коли кеш мовчить",
              20, INK, "middle", "bold")
    s += text(W / 2, 54,
              "під час запису у Flash кеш вимикають — і будь-яка функція з Flash на цей час зникає; рятунок — покласти її в IRAM",
              12, GREY, "middle", style="italic")

    midx = W / 2
    s += line(midx, 80, midx, 500, FAINT, 2, dash="4 5")

    # ── ЛІВОРУЧ: звичайна функція (в Flash) ──
    s += text(245, 104, "Звичайна функція", 17, INK, "middle", "bold")
    s += text(245, 124, "живе у Flash, біжить через кеш", 11.5, GREY, "middle", style="italic")
    s += chip(150, 148, 190, 60, "loop(), обробка…", "код у Flash", "#fbf3e0", AMBER, "#8a6a1e",
              tsize=14, ssize=10.5)
    s += arrow(245, 208, 245, 250, GREEN, 2.6)
    s += text(258, 230, "через кеш", 11, GREEN, "start")
    s += chip(150, 250, 190, 52, "виконується", "", "#eaf6ee", GREEN, GREEN, tsize=14)
    # сценарій збою
    s += rect(120, 330, 250, 150, "#fff4f3", RED, 1.8, 8)
    s += text(245, 354, "А якщо саме зараз…", 13, RED, "middle", "bold")
    s += text(245, 376, "іде запис у Flash →", 12, INK, "middle")
    s += text(245, 394, "КЕШ ВИМКНЕНО", 13.5, RED, "middle", "bold")
    s += chip(150, 410, 190, 50, "код недосяжний!", "", "#ffffff", RED, RED, tsize=13.5)
    s += text(245, 474, "переривання впаде — система зависне", 11, RED, "middle", style="italic")

    # ── ПРАВОРУЧ: IRAM_ATTR ──
    s += text(735, 104, "Функція з IRAM_ATTR", 17, INK, "middle", "bold")
    s += text(735, 124, "копія коду лежить у внутрішній IRAM", 11.5, GREY, "middle", style="italic")
    s += chip(640, 148, 190, 60, "IRAM_ATTR isr()", "код у IRAM, не у Flash", "#eaf6ee", GREEN, GREEN,
              tsize=13.5, ssize=10.5)
    s += arrow(735, 208, 735, 250, GREEN, 2.6)
    s += text(748, 230, "напряму", 11, GREEN, "start")
    s += chip(640, 250, 190, 52, "виконується", "", "#eaf6ee", GREEN, GREEN, tsize=14)
    # той самий сценарій — але працює
    s += rect(610, 330, 250, 150, "#f1f9f3", GREEN, 1.8, 8)
    s += text(735, 354, "Той самий момент:", 13, GREEN, "middle", "bold")
    s += text(735, 376, "іде запис у Flash →", 12, INK, "middle")
    s += text(735, 394, "КЕШ ВИМКНЕНО", 13.5, "#8a6a1e", "middle", "bold")
    s += chip(640, 410, 190, 50, "код усе одно поруч", "", "#ffffff", GREEN, GREEN, tsize=13)
    s += text(735, 474, "переривання спрацює вчасно", 11, GREEN, "middle", style="italic")

    # підпис унизу
    s += rect(40, 510, W - 80, 64, "#fafafa", FAINT, 1.5, 8)
    s += text(60, 534, "Правило:", 13.5, INK, "start", "bold")
    s += text(135, 534,
              "те, що МУСИТЬ працювати завжди — обробники переривань, код керування самим Flash — позначай",
              12.5, INK, "start")
    s += text(135, 558,
              "IRAM_ATTR, щоб воно жило в IRAM і не залежало від кеша. Решта спокійно лишається у Flash.",
              12.5, INK, "start")
    save("fig-3-5-7c-3-iram-attr.svg", s)


if __name__ == "__main__":
    fig_map()
    fig_cache()
    fig_iram()
    print("OK — 3 фігури вставки 3.5.7c згенеровано в", OUT)
