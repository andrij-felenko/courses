# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 38 — «Бездротовий зв'язок на чіпі: Wi-Fi і Bluetooth» (Модуль 6).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif.
Підписи посекційно (Рис. C.S.N); історія до розділу — секція 0 (Рис. 38.0.N).
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
BTBLUE = "#0a3d91"   # синій Bluetooth
STONE = "#9a9488"    # рунний камінь
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LGREY = "#f3f3f3"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
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


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── руни й логотип ───────────────────────────────────────────────────────────
def rune_hagall(cx, cy, H=46, w=20, col="#fff", sw=4):
    """ᚼ Hagall: дві стійки + навскісна поперечка (H-подібна)."""
    s = line(cx - w, cy - H, cx - w, cy + H, col, sw)
    s += line(cx + w, cy - H, cx + w, cy + H, col, sw)
    s += line(cx - w, cy - H * 0.25, cx + w, cy + H * 0.25, col, sw)
    return s


def rune_bjarkan(cx, cy, H=46, w=26, col="#fff", sw=4):
    """ᛒ Bjarkan: стійка + два трикутники праворуч (B-подібна)."""
    s = line(cx, cy - H, cx, cy + H, col, sw)
    s += line(cx, cy - H, cx + w, cy - H * 0.5, col, sw)
    s += line(cx + w, cy - H * 0.5, cx, cy, col, sw)
    s += line(cx, cy, cx + w, cy + H * 0.5, col, sw)
    s += line(cx + w, cy + H * 0.5, cx, cy + H, col, sw)
    return s


def bt_logo(cx, cy, H=46, W=26, col="#fff", sw=4.5):
    """Логотип Bluetooth: біндруна ᚼ+ᛒ (стійка + дві навскісні + дві поперечки)."""
    s = line(cx, cy - H, cx, cy + H, col, sw)                       # стійка
    s += line(cx, cy - H, cx + W, cy + H * 0.5, col, sw)            # T → Rlow
    s += line(cx, cy + H, cx + W, cy - H * 0.5, col, sw)            # B → Rup
    s += line(cx + W, cy - H * 0.5, cx, cy - H * 0.5, col, sw)      # Rup → стійка (верх. чверть)
    s += line(cx + W, cy + H * 0.5, cx, cy + H * 0.5, col, sw)      # Rlow → стійка (нижн. чверть)
    return s


# ── Рис. 38.0.1 — таймлайн ───────────────────────────────────────────────────
def fig_timeline():
    W, H = 900, 640
    s = header(W, H)
    s += text(W / 2, 38, "Як радіо назвали іменем вікінга — ланцюг подій", 20, INK, "middle", "bold")
    s += text(W / 2, 60, "технологію зробили в Лунді, назвали жартома в Інтелі, а «серйозне» ім'я так і не встигли вигадати",
              12.5, GREY, "middle", style="italic")
    spine = 230
    top, bot = 96, H - 28
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("~960", "Гаральд Синьозубий",
         "Король данів об'єднує розрізнені племена в одне королівство — звідси й уся метафора", False, False),
        ("1994", "Ericsson, Лунд",
         "Яап Гаартсен і Свен Маттіссон починають дешеве коротке радіо, щоб з'єднати пристрої без дротів", False, False),
        ("~1997", "Джим Кардач, Intel",
         "Зі скандинавських саг («Рудий Орм») бере КОДОВУ назву: «об'єднає протоколи, як король — племена»", False, True),
        ("1998", "SIG: 5 компаній",
         "Ericsson, Intel, Nokia, IBM, Toshiba творять консорціум; шукають «серйозну» назву", False, False),
        ("1998", "PAN і RadioWire провалились",
         "PAN не пройшов перевірку торгової марки, RadioWire не встигли перевірити — лишився Bluetooth", False, False),
        ("Розділ 38", "Радіо на чіпі сьогодні",
         "Той самий Bluetooth (і Wi-Fi) уже всередині мікроконтролера — як ним користуватися", True, False),
    ]
    n = len(nodes)
    for i, (yr, who, q, dest, accent) in enumerate(nodes):
        y = top + 30 + (bot - top - 60) * i / (n - 1)
        col = GREY if dest else INK
        if accent:
            s += circle(spine, y, 10, "#fff", BTBLUE, 3)
            s += circle(spine, y, 4.5, BTBLUE, BTBLUE, 0)
        elif dest:
            s += rect(spine - 8, y - 8, 16, 16, "#fff", GREEN, 2.6, 3)
        else:
            s += circle(spine, y, 7, "#fff", col, 2.6)
        s += text(spine - 22, y + 5, yr, 12.5, (GREEN if dest else GREY), "end", "bold")
        s += text(spine + 26, y - 3, who, 15.5,
                  (BTBLUE if accent else (GREEN if dest else col)), "start", "bold")
        s += text(spine + 26, y + 17, q, 12, (INK if not dest else GREY), "start", style="italic")
    save("fig-38-0-1-timeline.svg", s)


# ── Рис. 38.0.2 — ідея об'єднання ────────────────────────────────────────────
def fig_unite():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 36, "Метафора назви: об'єднати — як король об'єднав племена", 19, INK, "middle", "bold")
    s += text(W / 2, 58, "Гаральд звів розрізнені данські племена в одне королівство; Bluetooth звів несумісні пристрої в одну мову",
              12, GREY, "middle", style="italic")
    # ліворуч: племена → королівство
    s += text(230, 100, "Гаральд (~960)", 13, INK, "middle", "bold")
    tribes = [(140, 150), (210, 140), (300, 155), (160, 210), (290, 215)]
    for tx, ty in tribes:
        s += circle(tx, ty, 16, "#efe7d5", AMBER, 2)
        s += text(tx, ty + 4, "плем'я", 7.5, GREY, "middle")
    s += arrow(230, 245, 230, 285, GREEN, 2.4)
    s += rect(150, 290, 160, 50, "#efe7d5", AMBER, 2, 10)
    s += text(230, 320, "одне королівство", 11.5, INK, "middle", "bold")
    # праворуч: пристрої → одна мова
    s += text(680, 100, "Bluetooth (1998)", 13, BTBLUE, "middle", "bold")
    devs = [("ПК", 600, 150), ("телефон", 700, 140), ("гарнітура", 790, 155), ("миша", 640, 215), ("колонка", 760, 215)]
    for nm, tx, ty in devs:
        s += circle(tx, ty, 18, LBLUE, BLUE, 2)
        s += text(tx, ty + 3, nm, 8, GREY, "middle")
    s += arrow(680, 245, 680, 285, GREEN, 2.4)
    s += rect(600, 290, 160, 50, LBLUE, BLUE, 2, 10)
    s += text(680, 320, "одна радіомова", 11.5, INK, "middle", "bold")
    # знак рівності
    s += text(455, 250, "≈", 30, GREY, "middle", "bold")

    s += rect(60, 360, W - 120, 44, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 386, "Саме цю паралель — «об'єднувач» — і мав на увазі Кардач, пропонуючи кодову назву.",
              12, INK, "middle", "bold")
    save("fig-38-0-2-unite.svg", s)


# ── Рис. 38.0.3 — логотип як біндруна ────────────────────────────────────────
def fig_logo():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 36, "Логотип — це ініціали короля рунами: ᚼ + ᛒ", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "руни молодшого футарка для H та B (Harald Blåtand), злиті в одну біндруну",
              12.5, GREY, "middle", style="italic")
    # Hagall
    s += rect(120, 110, 150, 180, "#23262b", "#111", 2, 12)
    s += rune_hagall(195, 200, 50, 22)
    s += text(195, 318, "ᚼ Hagall = H", 13, INK, "middle", "bold")
    s += text(195, 338, "(Harald)", 10.5, GREY, "middle")
    s += text(305, 205, "+", 30, GREY, "middle", "bold")
    # Bjarkan
    s += rect(350, 110, 150, 180, "#23262b", "#111", 2, 12)
    s += rune_bjarkan(410, 200, 50, 28)
    s += text(425, 318, "ᛒ Bjarkan = B", 13, INK, "middle", "bold")
    s += text(425, 338, "(Blåtand «синьозубий»)", 10.5, GREY, "middle")
    s += arrow(520, 200, 600, 200, GREEN, 2.6)
    s += text(560, 188, "злиття", 11, GREEN, "middle", "bold")
    # логотип
    s += rect(630, 110, 150, 180, BTBLUE, "#06245a", 2, 16)
    s += bt_logo(700, 200, 56, 30)
    s += text(705, 318, "логотип Bluetooth", 13, BTBLUE, "middle", "bold")
    s += text(705, 338, "біндруна H+B", 10.5, GREY, "middle")

    s += rect(60, 360, W - 120, 44, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 386, "Щодня ти бачиш на екрані тисячолітні скандинавські руни — ініціали данського короля.",
              12, INK, "middle", "bold")
    save("fig-38-0-3-logo.svg", s)


# ── Рис. 38.0.4 — як тимчасова назва стала вічною ────────────────────────────
def fig_placeholder():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 36, "Як «тимчасова» назва лишилася назавжди", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "Bluetooth мав бути лише робочою заглушкою, поки маркетинг вигадає «круте» ім'я",
              12.5, GREY, "middle", style="italic")
    # три кандидати
    cands = [
        ("PAN", "Personal Area Network", "✗ провалив перевірку\nторгової марки\n(десятки тисяч збігів)", RED),
        ("RadioWire", "«радіодріт»", "✗ не встигли перевірити\nмарку вчасно", RED),
        ("Bluetooth", "робоча заглушка", "✓ єдине, з чим могли\nвийти на запуск —\nі прижилось назавжди", GREEN),
    ]
    x = 60
    for nm, sub, note, col in cands:
        s += rect(x, 96, 270, 200, ("#eef6ef" if col == GREEN else "#fbfbfb"), col, 2, 12)
        s += text(x + 135, 128, nm, 16, col, "middle", "bold")
        s += text(x + 135, 150, sub, 10.5, GREY, "middle", style="italic")
        for j, ln in enumerate(note.split("\n")):
            s += text(x + 135, 184 + j * 20, ln, 11, INK, "middle")
        x += 290

    s += rect(60, 318, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 342, "Випадковість маркетингу: «серйозну» назву так і не встигли поставити — і заглушка стала світовим брендом.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 362, "Тому мільярди пристроїв носять ім'я короля, який жив понад тисячу років тому.",
              11, GREY, "middle", style="italic")
    save("fig-38-0-4-placeholder.svg", s)


# ── Рис. 38.0.5 — хто що зробив ──────────────────────────────────────────────
def fig_whodidit():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 36, "Хто що зробив: техніка, назва, стандарт — різні люди", 19, INK, "middle", "bold")
    s += text(W / 2, 58, "винахід колективний: одні створили радіо, інший дав назву, консорціум зробив стандартом",
              12.5, GREY, "middle", style="italic")
    cards = [
        ("ТЕХНІКА", "Ericsson, Лунд", ["Яап Гаартсен («батько Bluetooth»)", "Свен Маттіссон", "коротке дешеве радіо, з 1994"], GREEN),
        ("НАЗВА", "Intel", ["Джим Кардач", "кодова назва зі скандинавських саг", "ідея «об'єднувача»"], BTBLUE),
        ("СТАНДАРТ", "SIG (1998)", ["Ericsson + Intel + Nokia", "+ IBM + Toshiba", "спільний відкритий стандарт"], "#b08900"),
    ]
    x = 55
    for title, who, pts, col in cards:
        s += rect(x, 92, 270, 200, "#fbfbfb", col, 2.2, 12)
        s += text(x + 135, 120, title, 13.5, col, "middle", "bold")
        s += text(x + 135, 142, who, 12, INK, "middle", "bold")
        for j, p in enumerate(pts):
            s += circle(x + 22, y_ := 168 + j * 26, 3.5, col, col, 0)
            s += text(x + 36, y_ + 4, p, 10.3, INK, "start")
        x += 290

    s += rect(60, 312, W - 120, 44, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 338, "Як і з радіо чи транзистором, тут немає одного «винахідника»: техніка, назва й стандарт — праця різних команд.",
              11.5, INK, "middle", "bold")
    save("fig-38-0-5-whodidit.svg", s)


# ── допоміжне ────────────────────────────────────────────────────────────────
def pkt(x, y, w, lab, col=BLUE, fill=LBLUE, h=30):
    s = rect(x, y, w, h, fill, col, 1.8, 5)
    s += text(x + w / 2, y + h / 2 + 5, lab, 11, col, "middle", "bold")
    return s


def antenna(cx, cy, col=BTBLUE, h=18):
    s = line(cx, cy, cx, cy - h, col, 2)
    s += line(cx, cy - h, cx - 6, cy - h - 8, col, 2)
    s += line(cx, cy - h, cx + 6, cy - h - 8, col, 2)
    return s


def waves(cx, cy, r0=10, n=3, col=BTBLUE, span=70):
    s = ""
    for k in range(n):
        rr = r0 + k * 12
        s += f'<path d="M {cx-rr*0.5:.1f},{cy-rr:.1f} A {rr:.1f} {rr:.1f} 0 0 1 {cx-rr*0.5:.1f},{cy+rr:.1f}" fill="none" stroke="{col}" stroke-width="1.8"/>\n'
    return s


# ============================================================================
#  §38.1 — Радіо на чіпі: що це й чому ненадійне
# ============================================================================

# ── Рис. 38.1.1 — радіо всередині чіпа ───────────────────────────────────────
def fig11_radiochip():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Радіо на чіпі: цілий приймач-передавач усередині МК", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "те, що колись було окремою платою, тепер уміщається в куточку кристала разом із процесором",
              12.5, GREY, "middle", style="italic")
    # МК
    s += rect(220, 110, 360, 180, "#23262b", "#111", 2.2, 14)
    s += text(400, 134, "мікроконтролер (напр. ESP32)", 12.5, "#e8e8e8", "middle", "bold")
    s += rect(250, 150, 130, 110, "#2c3038", "#3a3f48", 1.6, 8)
    s += text(315, 200, "ядро", 12, "#9be39b", "middle", "bold")
    s += text(315, 220, "процесор", 9.5, "#b9b9b9", "middle")
    s += rect(420, 150, 130, 110, "#2c3038", "#3a3f48", 1.6, 8)
    s += text(485, 196, "радіо", 12, "#7fd0ff", "middle", "bold")
    s += text(485, 214, "TX / RX", 9.5, "#b9b9b9", "middle")
    s += line(380, 205, 420, 205, "#7fd0ff", 1.6)
    # антена + хвилі
    s += antenna(600, 180, "#7fd0ff", 30)
    s += line(550, 205, 600, 180, "#7fd0ff", 1.6)
    s += waves(640, 165, 10, 3, BTBLUE)
    s += text(680, 170, "по повітрю", 11, BTBLUE, "start", "bold")

    s += rect(60, 308, W - 120, 44, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 334, "Кілька рядків коду — і пристрій уже говорить по радіо. Уся складність радіо схована всередині.",
              12, INK, "middle", "bold")
    save("fig-38-1-1-radiochip.svg", s)


# ── Рис. 38.1.2 — дріт проти повітря ─────────────────────────────────────────
def fig12_wire_vs_air():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Дріт проти повітря: приватний канал проти спільного", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "по дроту сигнал гарантовано доходить лише до адресата; у повітрі його «чують» усі й нічого не гарантовано",
              12, GREY, "middle", style="italic")
    # дріт
    s += rect(60, 90, 360, 230, "none", FAINT, 2, 12)
    s += text(240, 116, "дріт (UART/I2C/SPI)", 13, GREEN, "middle", "bold")
    s += rect(100, 180, 90, 50, "#fbfbfb", INK, 2, 8); s += text(145, 210, "A", 13, INK, "middle", "bold")
    s += rect(310, 180, 90, 50, "#fbfbfb", INK, 2, 8); s += text(355, 210, "B", 13, INK, "middle", "bold")
    s += line(190, 205, 310, 205, GREEN, 3)
    s += text(250, 196, "лише A↔B", 10, GREEN, "middle", "bold")
    s += text(240, 270, "доставка гарантована,", 11, INK, "middle", "bold")
    s += text(240, 290, "час сталий, ніхто чужий не чує", 10.5, GREY, "middle")
    # повітря
    s += rect(470, 90, 380, 230, "none", FAINT, 2, 12)
    s += text(660, 116, "повітря (радіо)", 13, BTBLUE, "middle", "bold")
    s += rect(510, 180, 80, 46, "#fbfbfb", INK, 2, 8); s += text(550, 208, "A", 12, INK, "middle", "bold")
    s += antenna(590, 180, BTBLUE, 14)
    s += waves(610, 175, 8, 4, BTBLUE, 80)
    for nm, bx, by in [("B", 760, 140), ("чужий", 790, 210), ("ще хтось", 740, 270)]:
        s += rect(bx - 30, by - 20, 80, 38, "#fbfbfb", (GREY if nm != "B" else INK), 1.6, 6)
        s += text(bx + 10, by + 4, nm, 10.5, (GREY if nm != "B" else INK), "middle", "bold")
    s += text(660, 308, "чують усі довкола; доставка — як пощастить", 10.5, GREY, "middle", style="italic")

    s += rect(60, 336, W - 120, 1, "none", "none", 0)
    save("fig-38-1-2-wire-vs-air.svg", s)


# ── Рис. 38.1.3 — вороги радіосигналу ────────────────────────────────────────
def fig13_enemies():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Чому радіо ненадійне: що псує сигнал у дорозі", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "поки сигнал летить від передавача до приймача, його тіснять відстань, перешкоди, завади й шум",
              12.5, GREY, "middle", style="italic")
    s += rect(60, 150, 90, 60, "#eef6ef", GREEN, 2, 8); s += text(105, 185, "TX", 13, GREEN, "middle", "bold")
    s += antenna(150, 150, GREEN, 14)
    s += rect(750, 150, 90, 60, "#fbfbfb", INK, 2, 8); s += text(795, 185, "RX", 13, INK, "middle", "bold")
    s += antenna(750, 150, INK, 14)
    # сигнал, що слабне
    s += waves(190, 165, 8, 4, BTBLUE)
    s += arrow(220, 180, 720, 180, BTBLUE, 2, dash="5,4")
    # вороги
    enemies = [
        (300, "стіна/перешкода", "поглинає"),
        (430, "відстань", "слабшає"),
        (560, "інше радіо", "завада/колізія"),
        (660, "відбиття", "багатопроменевість"),
    ]
    for ex, t1, t2 in enemies:
        s += line(ex, 180, ex, 230, RED, 1.6, dash="3,3")
        s += text(ex, 248, t1, 9.5, RED, "middle", "bold")
        s += text(ex, 262, t2, 8.5, GREY, "middle")
    s += text(470, 134, "сигнал слабшає й спотворюється", 11, RED, "middle", "bold")

    s += rect(60, 290, W - 120, 70, LRED, RED, 1.4, 10)
    s += text(W / 2, 314, "Жоден із цих ворогів не діє на дріт — а в повітрі вони є завжди й змінюються щомиті.",
              12, INK, "middle", "bold")
    s += text(W / 2, 336, "Підсумок: частина бітів спотворюється, а цілі пакети просто ЗНИКАЮТЬ — це норма радіо, не аварія.",
              11.5, GREY, "middle", style="italic")
    save("fig-38-1-3-enemies.svg", s)


# ── Рис. 38.1.4 — пакети губляться ───────────────────────────────────────────
def fig14_lost():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Наслідок: пакети губляться й псуються (на відміну від дроту)", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "радіо передає окремими ПАКЕТАМИ, і деякі з них до приймача просто не доходять",
              12.5, GREY, "middle", style="italic")
    s += text(120, 130, "надіслано:", 12, INK, "end", "bold")
    sent = [("P0", True), ("P1", False), ("P2", True), ("P3", "corrupt"), ("P4", True)]
    x0, cw = 150, 130
    for i, (lab, ok) in enumerate(sent):
        s += pkt(x0 + i * cw, 110, 90, lab, BLUE, LBLUE)
    s += text(120, 250, "отримано:", 12, INK, "end", "bold")
    for i, (lab, ok) in enumerate(sent):
        x = x0 + i * cw
        if ok is True:
            s += pkt(x, 230, 90, lab, GREEN, LGRN)
            s += arrow(x + 45, 142, x + 45, 228, GREY, 1.4)
        elif ok is False:
            s += rect(x, 230, 90, 30, "#f4f4f4", GREY, 1.4, 5)
            s += text(x + 45, 250, "— зник", 10, RED, "middle", "bold")
            s += line(x + 45, 142, x + 45, 226, RED, 1.4, dash="4,3")
            s += text(x + 45, 200, "✗", 14, RED, "middle", "bold")
        else:
            s += pkt(x, 230, 90, "P3?", RED, LRED)
            s += text(x + 45, 286, "CRC не зійшовся", 8.5, RED, "middle", "bold")
            s += arrow(x + 45, 142, x + 45, 228, RED, 1.4)

    s += rect(60, 300, W - 120, 44, LGREY, GREY, 1.3, 10)
    s += text(W / 2, 326, "На дроті це була б рідкісна аварія; у радіо втрати — буденність, і протокол має до них бути готовий.",
              11.5, INK, "middle", "bold")
    save("fig-38-1-4-lost.svg", s)


# ── Рис. 38.1.5 — підтвердження й перевідправлення ───────────────────────────
def fig15_ack_retry():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Як домогтися надійності: підтвердження (ACK) і перевідправлення", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "передавач шле пакет і чекає ACK; не дочекався за час очікування — шле ще раз",
              12.5, GREY, "middle", style="italic")
    lx, rx = 160, 740
    s += text(lx, 92, "передавач", 12, GREEN, "middle", "bold")
    s += text(rx, 92, "приймач", 12, INK, "middle", "bold")
    s += line(lx, 104, lx, 360, GREY, 1.4)
    s += line(rx, 104, rx, 360, GREY, 1.4)
    # успіх
    s += arrow(lx, 130, rx, 150, BLUE, 2.2); s += text(450, 132, "пакет", 10, BLUE, "middle", "bold")
    s += arrow(rx, 165, lx, 185, GREEN, 2.2); s += text(450, 168, "ACK ✓", 10, GREEN, "middle", "bold")
    s += text(lx - 90, 188, "доставлено", 10, GREEN, "start")
    # втрата + ретрай
    s += arrow(lx, 225, rx - 220, 245, BLUE, 2.2, dash="4,3"); s += text(380, 224, "пакет (загубився)", 10, RED, "middle", "bold")
    s += text(rx - 200, 250, "✗", 13, RED, "middle", "bold")
    s += line(lx - 14, 245, lx - 14, 290, "#b08900", 1.6, dash="3,3")
    s += text(lx - 70, 270, "час очікування", 9, "#b08900", "middle", "bold")
    s += text(lx - 70, 284, "вийшов — нема ACK", 8.5, GREY, "middle")
    s += arrow(lx, 300, rx, 320, BLUE, 2.2); s += text(450, 302, "пакет (ще раз)", 10, BLUE, "middle", "bold")
    s += arrow(rx, 335, lx, 352, GREEN, 2.2); s += text(450, 338, "ACK ✓", 10, GREEN, "middle", "bold")

    s += rect(60, 366, W - 120, 1, "none", "none", 0)
    save("fig-38-1-5-ack-retry.svg", s)


# ── Рис. 38.1.6 — best-effort проти надійного ────────────────────────────────
def fig16_besteffort():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Два режими: «вистрілив і забув» проти «з гарантією»", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "надійність купується затримкою: ACK і ретраї рятують дані, та роблять час непередбачуваним",
              12, GREY, "middle", style="italic")
    s += rect(70, 90, 360, 210, "#fbfbfb", "#b08900", 2, 12)
    s += text(250, 118, "best-effort («забув»)", 13, "#b08900", "middle", "bold")
    s += text(90, 148, "• без ACK, без ретраїв", 11, INK, "start")
    s += text(90, 172, "• швидко, мала затримка", 11, INK, "start")
    s += text(90, 196, "• частина пакетів губиться", 11, RED, "start")
    s += text(90, 220, "• годиться для потоку, де", 11, INK, "start")
    s += text(104, 240, "втрата кадру не страшна", 11, GREY, "start")
    s += text(250, 278, "напр. потокове відео, телеметрія", 10, GREY, "middle", style="italic")
    s += rect(470, 90, 380, 210, "#eef6ef", GREEN, 2, 12)
    s += text(660, 118, "надійний (з гарантією)", 13, GREEN, "middle", "bold")
    s += text(490, 148, "• ACK + перевідправлення", 11, INK, "start")
    s += text(490, 172, "• майже нічого не губиться", 11, GREEN, "start")
    s += text(490, 196, "• затримка ПЛАВАЄ (джитер)", 11, RED, "start")
    s += text(490, 220, "• годиться для команд, де", 11, INK, "start")
    s += text(504, 240, "втратити не можна", 11, GREY, "start")
    s += text(660, 278, "напр. команди керування, файли", 10, GREY, "middle", style="italic")

    s += rect(60, 314, W - 120, 44, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 340, "Вибір — за задачею: важлива швидкість і не страшна втрата → best-effort; важлива доставка → надійний.",
              11.5, INK, "middle", "bold")
    save("fig-38-1-6-besteffort.svg", s)


# ── Рис. 38.1.7 — стек ховає, але failsafe — твій ────────────────────────────
def fig17_failsafe():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Стек ховає ретраї — але повну втрату зв'язку маєш ловити ТИ", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "чіп сам перешле загублений пакет; та якщо пристрій вийшов за межу — жодні ретраї не допоможуть",
              12, GREY, "middle", style="italic")
    layers = [
        ("твій застосунок", "send() / on_receive()  +  FAILSAFE на тривалу тишу", GREEN, 100),
        ("стек радіо (Wi-Fi/BT)", "пакети, CRC, ACK, ретраї — усе ховається тут", BLUE, 168),
        ("радіо на чіпі", "антена, модуляція, біти по повітрю", "#b08900", 236),
    ]
    for name, desc, col, y in layers:
        s += rect(120, y, 660, 56, ("#eef6ef" if col == GREEN else "#fbfbfb"), col, 2, 10)
        s += text(150, y + 24, name, 12.5, col, "start", "bold")
        s += text(150, y + 44, desc, 10.5, INK, "start")
    s += arrow(450, 156, 450, 168, GREY, 1.6)
    s += arrow(450, 224, 450, 236, GREY, 1.6)

    s += rect(60, 306, W - 120, 56, LRED, RED, 1.4, 10)
    s += text(W / 2, 330, "Межа відповідальності: ретраї окремих пакетів — справа чіпа; реакція на ПОВНУ втрату зв'язку — твоя.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 352, "Тому надійний бездротовий пристрій завжди має failsafe «що робити, якщо команд давно немає» (§38.7).",
              11, GREY, "middle", style="italic")
    save("fig-38-1-7-failsafe.svg", s)


# ============================================================================
#  §38.2 — Канал, смуга, пакет (2.4 ГГц)
# ============================================================================
def _bandbar(x, y, w, h, col=GREY):
    """Смуга спектра з підписами країв 2.400…2.4835 ГГц."""
    s = rect(x, y, w, h, "#f7f7f7", col, 1.6, 4)
    s += text(x, y + h + 16, "2.400 ГГц", 10, GREY, "start")
    s += text(x + w, y + h + 16, "2.4835 ГГц", 10, GREY, "end")
    return s


# ── Рис. 38.2.1 — хто живе у смузі 2.4 ГГц ───────────────────────────────────
def fig21_band():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Смуга 2.4 ГГц: безліцензійна — тому переповнена", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ISM-смуга (промислова/наукова/медична) вільна для всіх у світі, тож сюди набилися всі підряд",
              12.5, GREY, "middle", style="italic")
    bx, by, bw = 90, 150, 720
    s += _bandbar(bx, by, bw, 60)
    users = [("Wi-Fi", 0.12, BLUE), ("Bluetooth", 0.38, BTBLUE), ("Zigbee", 0.6, GREEN),
             ("мікрохвильовка", 0.78, RED), ("радіотелефон", 0.93, "#b08900")]
    for nm, frac, col in users:
        cx = bx + bw * frac
        s += rect(cx - 40, by + 8, 80, 44, "#ffffff", col, 1.6, 5)
        s += text(cx, by + 30, nm.split()[0], 9, col, "middle", "bold")
        if len(nm.split()) > 1:
            s += text(cx, by + 44, nm.split()[1] if len(nm.split()) > 1 else "", 7.5, GREY, "middle")
    s += text(bx + bw / 2, by - 14, "усі тиснуться в ту саму смугу", 11, RED, "middle", "bold")

    s += rect(60, 268, W - 120, 70, LRED, RED, 1.4, 10)
    s += text(W / 2, 292, "«Безліцензійна» означає «нічия» — користуватися можна без дозволу, але й захисту від сусідів немає.",
              12, INK, "middle", "bold")
    s += text(W / 2, 314, "Звідси головна біда 2.4 ГГц — теснота й завади: Wi-Fi, Bluetooth і навіть піч ділять одне небо.",
              11.5, GREY, "middle", style="italic")
    save("fig-38-2-1-band.svg", s)


# ── Рис. 38.2.2 — канали ─────────────────────────────────────────────────────
def fig22_channels():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Канали: смугу ділять на частини — але вони перекриваються", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "канал Wi-Fi широкий (~20 МГц), тож із 13 каналів не перекриваються лише 1, 6, 11",
              12, GREY, "middle", style="italic")
    bx, by, bw = 80, 150, 740
    s += _bandbar(bx, by, bw, 20)
    # вузькі позначки каналів Wi-Fi (центри)
    for ch in range(1, 14):
        cx = bx + bw * (ch - 1) / 13
        s += line(cx, by, cx, by - 6, GREY, 1.2)
        s += text(cx, by - 10, str(ch), 7.5, GREY, "middle")
    # три неперекривні 20-МГц канали
    for ch, cx_frac, col in [(1, 0.06, GREEN), (6, 0.42, BLUE), (11, 0.78, "#b08900")]:
        cx = bx + bw * cx_frac
        s += rect(cx - 70, 200, 140, 50, ("#eef6ef" if col == GREEN else "#fbfbfb"), col, 2, 8)
        s += text(cx, 222, "канал %d" % ch, 11, col, "middle", "bold")
        s += text(cx, 240, "20 МГц", 9, GREY, "middle")
        s += line(cx, by, cx, 200, col, 1.4, dash="3,3")
    s += text(bx + bw / 2, 286, "↑ лише 1, 6, 11 не перекривають одне одного — на них і ставлять Wi-Fi", 11, INK, "middle", "bold")
    # BT вузькі
    s += text(bx + bw / 2, 314, "Bluetooth ділить ту саму смугу на десятки ВУЗЬКИХ каналів (1–2 МГц) і стрибає по них", 10.5, BTBLUE, "middle", "bold")

    s += rect(60, 330, W - 120, 1, "none", "none", 0)
    save("fig-38-2-2-channels.svg", s)


# ── Рис. 38.2.3 — смуга каналу проти швидкості ───────────────────────────────
def fig23_bandwidth():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Ширина каналу ↔ швидкість: компроміс", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "ширший канал везе більше даних, та займає більше спектра і ловить більше завад",
              12.5, GREY, "middle", style="italic")
    # вузький
    s += text(230, 110, "вузький канал", 12.5, GREEN, "middle", "bold")
    bx = 90
    s += _bandbar(bx, 130, 280, 24)
    for k in range(7):
        cx = bx + 20 + k * 38
        s += rect(cx, 134, 30, 16, LGRN, GREEN, 1.2, 3)
    s += text(230, 188, "багато каналів влазить", 10.5, INK, "middle")
    s += text(230, 206, "менше даних у кожному", 10.5, GREY, "middle")
    # широкий
    s += text(660, 110, "широкий канал", 12.5, BLUE, "middle", "bold")
    bx2 = 520
    s += _bandbar(bx2, 130, 280, 24)
    for k in range(2):
        s += rect(bx2 + 10 + k * 135, 134, 120, 16, LBLUE, BLUE, 1.2, 3)
    s += text(660, 188, "мало каналів влазить", 10.5, INK, "middle")
    s += text(660, 206, "більше даних у кожному", 10.5, GREEN, "middle", "bold")

    s += rect(60, 240, W - 120, 96, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 266, "Більше спектра → вища швидкість (натяк на межу Шеннона, §40), але й більше завад і менше «слотів».",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 288, "83 МГц смуги / 20 МГц на канал → лише ~3-4 неперекривні Wi-Fi-канали на всіх.", 11.5, INK, "middle")
    s += text(W / 2, 310, "Тому в людному місці Wi-Fi-канали 1/6/11 завжди переповнені сусідами.", 11, GREY, "middle", style="italic")
    save("fig-38-2-3-bandwidth.svg", s)


# ── Рис. 38.2.4 — як уживаються в спільній смузі ─────────────────────────────
def fig24_coexist():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Як уживатися в спільній смузі: три стратегії", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "не можна змусити інших мовчати — можна лише розумно ділити час і частоту",
              12.5, GREY, "middle", style="italic")
    panels = [
        ("обрати тихий канал", "Wi-Fi сидить на одному\nканалі — обери найвільніший", BLUE),
        ("стрибати частотою", "Bluetooth скаче по каналах\n~1600 раз/с, оминаючи зайняті", BTBLUE),
        ("слухати перед передачею", "Wi-Fi: \"вільно? — кажу\";\nзайнято — чекаю (CSMA/CA)", GREEN),
    ]
    x = 60
    for title, body, col in panels:
        s += rect(x, 96, 270, 150, "#fbfbfb", col, 2, 12)
        s += text(x + 135, 124, title, 12.5, col, "middle", "bold")
        for j, ln in enumerate(body.split("\n")):
            s += text(x + 135, 158 + j * 20, ln, 10.5, INK, "middle")
        x += 290

    s += rect(60, 266, W - 120, 70, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 290, "Усі три — про чемність у спільному ефірі: вибір частоти, стрибки по ній і «послухай, перш ніж казати».",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 312, "Жодна не дає гарантії (хтось завжди може заглушити) — лише знижує ймовірність зіткнень.",
              11, GREY, "middle", style="italic")
    save("fig-38-2-4-coexist.svg", s)


# ── Рис. 38.2.5 — стрибки частотою оминають заваду ──────────────────────────
def fig25_hopping():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Стрибки частотою: одна забита частота не валить зв'язок", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "пристрій щомиті міняє канал за відомою послідовністю; забитий канал коштує лише ОДНОГО пакета",
              12, GREY, "middle", style="italic")
    ox, oy = 120, 110
    nch, nt = 6, 8
    cw, rh = 86, 32
    # сітка час × канал
    for c in range(nch):
        s += text(ox - 12, oy + c * rh + rh - 10, "к%d" % (c + 1), 9.5, GREY, "end")
    for t in range(nt):
        s += text(ox + t * cw + cw / 2, oy + nch * rh + 16, "t%d" % t, 9, GREY, "middle")
    for c in range(nch):
        for t in range(nt):
            s += rect(ox + t * cw, oy + c * rh, cw, rh, "#fbfbfb", FAINT, 1)
    # завадний канал 3 (рядок index 2) — забитий весь час
    for t in range(nt):
        s += rect(ox + t * cw, oy + 2 * rh, cw, rh, LRED, RED, 1)
    s += text(ox + nt * cw + 8, oy + 2 * rh + 20, "← забитий канал", 10, RED, "start", "bold")
    # послідовність стрибків
    hops = [0, 4, 2, 5, 1, 3, 0, 4]
    prev = None
    for t, c in enumerate(hops):
        cx = ox + t * cw + cw / 2
        cy = oy + c * rh + rh / 2
        hit = (c == 2)
        s += circle(cx, cy, 9, ("#fdeaea" if hit else LGRN), (RED if hit else GREEN), 2)
        s += text(cx, cy + 4, ("✗" if hit else "✓"), 10, (RED if hit else GREEN), "middle", "bold")
        if prev:
            s += line(prev[0], prev[1], cx, cy, GREY, 1.4)
        prev = (cx, cy)

    s += rect(60, 318, W - 120, 44, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 344, "Із восьми стрибків лише один влучив у забитий канал → 1 втрачений пакет, решта пройшла.",
              11.5, INK, "middle", "bold")
    save("fig-38-2-5-hopping.svg", s)


# ── Рис. 38.2.6 — анатомія радіопакета ──────────────────────────────────────
def fig26_packet():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Анатомія радіопакета: преамбула · заголовок · дані · CRC", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "у повітря йде не потік, а окремі самодостатні пакети — за структурою як у §35.6, лише з преамбулою",
              12, GREY, "middle", style="italic")
    fields = [
        ("ПРЕАМБУЛА", 150, "#b08900", "відома послідовність —\nприймач «ловить» і синхронізується"),
        ("ЗАГОЛОВОК", 160, BLUE, "адреси, довжина,\nтип пакета"),
        ("ДАНІ", 180, INK, "корисне\nнавантаження"),
        ("CRC", 90, GREEN, "контроль\nцілості"),
    ]
    x = 90
    for lab, w, col, desc in fields:
        s += rect(x, 130, w, 50, ("#eef6ef" if col == GREEN else "#fbfbfb"), col, 1.8, 6)
        s += text(x + w / 2, 160, lab, 11.5, col, "middle", "bold")
        for j, ln in enumerate(desc.split("\n")):
            s += text(x + w / 2, 206 + j * 16, ln, 9.5, GREY, "middle")
        x += w + 6
    s += arrow(90, 110, x - 6, 110, GREY, 1.6)
    s += text((90 + x) / 2, 102, "час →", 10, GREY, "middle")

    s += rect(60, 268, W - 120, 70, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 292, "Преамбула — нове проти дроту: приймач не «під'єднаний», тож мусить спершу ВПІЙМАТИ й налаштуватися на сигнал.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 314, "Решта знайома: заголовок з адресами, дані, CRC — той самий пакет, що ми будували для UART (§35.6).",
              11, GREY, "middle", style="italic")
    save("fig-38-2-6-packet.svg", s)


# ── Рис. 38.2.7 — 2.4 проти 5 ГГц ────────────────────────────────────────────
def fig27_2v5():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "2.4 ГГц проти 5 ГГц: дальність проти швидкості", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "нижча частота краще огинає й проникає; вища дає більше чистих каналів і швидкості",
              12.5, GREY, "middle", style="italic")
    s += rect(70, 90, 360, 180, "#fbf3df", "#b08900", 2, 12)
    s += text(250, 116, "2.4 ГГц", 14, "#b08900", "middle", "bold")
    for i, t in enumerate(["+ далі бере, краще крізь стіни", "+ є майже всюди (сумісність)",
                           "− мало каналів, дуже людно", "− нижча швидкість"]):
        s += text(90, 144 + i * 26, t, 11, INK, "start")
    s += rect(470, 90, 380, 180, "#e9eefb", BLUE, 2, 12)
    s += text(660, 116, "5 ГГц", 14, BLUE, "middle", "bold")
    for i, t in enumerate(["+ багато чистих каналів", "+ вища швидкість",
                           "− коротша дальність", "− гірше крізь стіни"]):
        s += text(490, 144 + i * 26, t, 11, INK, "start")

    s += rect(60, 286, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 311, "Малі пристрої (ESP32, давачі) — здебільшого 2.4 ГГц: дальність і сумісність важливіші за швидкість.",
              11.5, INK, "middle", "bold")
    save("fig-38-2-7-2v5.svg", s)


# ============================================================================
#  §38.3 — Wi-Fi: клієнт, точка доступу, IP
# ============================================================================
def _dev(x, y, w, h, name, addr=None, col=INK, fill="#fbfbfb"):
    s = rect(x, y, w, h, fill, col, 2, 8)
    s += text(x + w / 2, y + (h / 2 + 4 if not addr else h / 2 - 5), name, 11.5, col, "middle", "bold")
    if addr:
        s += text(x + w / 2, y + h / 2 + 13, addr, 9.5, GREY, "middle")
    return s


# ── Рис. 38.3.1 — інфраструктурний режим ─────────────────────────────────────
def fig31_infra():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Wi-Fi: клієнти спілкуються ЧЕРЕЗ точку доступу", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "точка доступу (AP) — це вузол-міст: вона з'єднує клієнтів між собою та з рештою мережі",
              12.5, GREY, "middle", style="italic")
    # AP по центру
    s += rect(380, 150, 140, 70, "#e9eefb", BLUE, 2.2, 12)
    s += text(450, 178, "точка доступу", 11.5, BLUE, "middle", "bold")
    s += text(450, 196, "(роутер, AP)", 9.5, GREY, "middle")
    s += antenna(450, 150, BLUE, 14)
    s += text(450, 128, 'SSID: "MyHome"', 10, BLUE, "middle", "bold")
    # клієнти
    clients = [("телефон", 110, 130), ("ноутбук", 110, 250), ("ESP32", 700, 130), ("ще пристрій", 700, 250)]
    for nm, cx, cy in clients:
        s += _dev(cx - 55, cy - 22, 110, 44, nm)
        # хвиля до AP
        if cx < 450:
            s += line(cx + 55, cy, 380, 185, BTBLUE, 1.8, dash="4,4")
        else:
            s += line(cx - 55, cy, 520, 185, BTBLUE, 1.8, dash="4,4")
    s += text(250, 196, "по радіо", 9, BTBLUE, "middle")
    # до інтернету
    s += arrow(520, 185, 600, 185, GREEN, 2.2)
    s += text(560, 175, "дріт", 9, GREEN, "middle", "bold")
    s += circle(640, 185, 26, LGRN, GREEN, 2)
    s += text(640, 189, "мережа", 9, GREEN, "middle", "bold")

    s += rect(60, 300, W - 120, 56, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 324, "Клієнти не говорять напряму один з одним — усе йде через AP (інфраструктурний режим).",
              12, INK, "middle", "bold")
    s += text(W / 2, 344, "SSID — це ім'я мережі, яке ти обираєш у списку Wi-Fi.",
              11, GREY, "middle", style="italic")
    save("fig-38-3-1-infra.svg", s)


# ── Рис. 38.3.2 — як приєднатися ─────────────────────────────────────────────
def fig32_joining():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Приєднання до мережі: сканування → пароль → IP", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "чотири кроки, що їх роблять і телефон, і ESP32, заходячи в Wi-Fi",
              12.5, GREY, "middle", style="italic")
    steps = [
        ("1. СКАН", "знайти мережі\n(SSID у ефірі)", BLUE),
        ("2. АВТЕНТИФІКАЦІЯ", "довести пароль\n(WPA2/WPA3)", "#b08900"),
        ("3. АСОЦІАЦІЯ", "AP приймає клієнта\nдо мережі", GREEN),
        ("4. IP-АДРЕСА", "роутер видає адресу\n(DHCP) — тепер у мережі", INK),
    ]
    x0, bw, gap, y = 50, 195, 18, 120
    for i, (title, body, col) in enumerate(steps):
        x = x0 + i * (bw + gap)
        s += rect(x, y, bw, 90, "#fbfbfb", col, 2, 12)
        s += text(x + bw / 2, y + 28, title, 12, col, "middle", "bold")
        for j, ln in enumerate(body.split("\n")):
            s += text(x + bw / 2, y + 50 + j * 16, ln, 9.8, INK, "middle")
        if i < 3:
            s += arrow(x + bw, y + 45, x + bw + gap, y + 45, INK, 2)

    s += rect(60, 250, W - 120, 70, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 274, "У коді ESP32 це здебільшого один рядок: WiFi.begin(\"MyHome\", \"пароль\") — решту робить стек.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 296, "Доки нема IP — пристрій ще «не в мережі»; саме видача IP завершує приєднання.",
              11, GREY, "middle", style="italic")
    save("fig-38-3-2-joining.svg", s)


# ── Рис. 38.3.3 — STA проти AP ───────────────────────────────────────────────
def fig33_sta_ap():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Два режими чипа: приєднатися (STA) чи створити мережу (AP)", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ESP32 вміє і те, і те — а часом обидва одразу (AP+STA)",
              12.5, GREY, "middle", style="italic")
    # STA
    s += rect(60, 92, 360, 210, "none", FAINT, 2, 12)
    s += text(240, 118, "режим STA (клієнт)", 13, GREEN, "middle", "bold")
    s += _dev(100, 200, 110, 50, "ESP32", "клієнт", GREEN, "#eef6ef")
    s += rect(280, 150, 110, 50, "#e9eefb", BLUE, 2, 8); s += text(335, 180, "чужий AP", 10.5, BLUE, "middle", "bold")
    s += antenna(335, 150, BLUE, 12)
    s += line(210, 215, 300, 185, BTBLUE, 1.8, dash="4,4")
    s += text(240, 278, "приєднується до наявної мережі", 10.5, INK, "middle", "bold")
    s += text(240, 294, "(як телефон до домашнього Wi-Fi)", 9.5, GREY, "middle", style="italic")
    # AP
    s += rect(470, 92, 380, 210, "none", FAINT, 2, 12)
    s += text(660, 118, "режим AP (точка доступу)", 13, "#b08900", "middle", "bold")
    s += _dev(590, 150, 120, 50, "ESP32", "сам AP", "#b08900", "#fbf3df")
    s += antenna(650, 150, "#b08900", 12)
    for cx in (520, 760):
        s += _dev(cx - 40, 230, 80, 40, "клієнт", None, INK)
        s += line(cx, 230, 650, 200, BTBLUE, 1.6, dash="4,4")
    s += text(660, 296, "сам роздає Wi-Fi, інші заходять до НЬОГО", 10, INK, "middle", "bold")

    s += rect(60, 314, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 339, "STA — щоб вийти в інтернет; AP — щоб віддати дані напряму (напр. сторінка налаштувань пристрою).",
              11.5, INK, "middle", "bold")
    save("fig-38-3-3-sta-ap.svg", s)


# ── Рис. 38.3.4 — IP-адреси й DHCP ───────────────────────────────────────────
def fig34_ip_dhcp():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "IP-адреси: роутер сам роздає їх (DHCP)", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "приєднавшись, кожен пристрій отримує адресу в локальній мережі — за нею його й знаходять",
              12.5, GREY, "middle", style="italic")
    s += rect(360, 100, 180, 70, "#e9eefb", BLUE, 2.2, 12)
    s += text(450, 126, "роутер (DHCP)", 11.5, BLUE, "middle", "bold")
    s += text(450, 146, "192.168.1.1", 11, INK, "middle", "bold")
    s += text(450, 162, "шлюз (gateway)", 8.5, GREY, "middle")
    devs = [("телефон", "192.168.1.10", 120, 250), ("ноутбук", "192.168.1.11", 380, 250), ("ESP32", "192.168.1.12", 640, 250)]
    for nm, ip, cx, cy in devs:
        s += _dev(cx - 65, cy - 24, 130, 48, nm, ip, INK)
        s += arrow(450, 172, cx, cy - 26, GREEN, 1.6)
    s += text(450, 210, "роздає адреси .10, .11, .12 …", 10.5, GREEN, "middle", "bold")

    s += rect(60, 296, W - 120, 56, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 320, "Локальні адреси 192.168.x.x видає роутер автоматично; .1 зазвичай він сам (шлюз у інтернет).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 340, "Тому IP пристрою може МІНЯТИСЯ при переприєднанні — для сталості задають фіксовану адресу.",
              11, GREY, "middle", style="italic")
    save("fig-38-3-4-ip-dhcp.svg", s)


# ── Рис. 38.3.5 — MAC проти IP ───────────────────────────────────────────────
def fig35_mac_ip():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Дві адреси пристрою: MAC (залізна) і IP (мережева)", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "MAC зашита в радіо назавжди; IP видає мережа й вона може мінятись",
              12.5, GREY, "middle", style="italic")
    s += rect(80, 100, 360, 150, "#fbf3df", "#b08900", 2, 12)
    s += text(260, 128, "MAC-адреса", 13, "#b08900", "middle", "bold")
    s += text(260, 154, "A4:CF:12:9B:5E:07", 13, INK, "middle", "bold")
    for i, t in enumerate(["• зашита виробником у чип", "• унікальна, НЕ міняється", "• «паспорт» заліза"]):
        s += text(100, 180 + i * 22, t, 11, INK, "start")
    s += rect(470, 100, 380, 150, "#e9eefb", BLUE, 2, 12)
    s += text(660, 128, "IP-адреса", 13, BLUE, "middle", "bold")
    s += text(660, 154, "192.168.1.12", 13, INK, "middle", "bold")
    for i, t in enumerate(["• видає мережа (DHCP)", "• може мінятися при переході", "• «адреса в цій мережі»"]):
        s += text(490, 180 + i * 22, t, 11, INK, "start")

    s += rect(60, 268, W - 120, 56, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 292, "Аналогія: MAC — як ім'я людини (незмінне), IP — як її поточна адреса проживання (може змінитись).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 312, "Маршрутизація в мережі працює з IP; MAC — для доставки в межах однієї локальної ланки.",
              11, GREY, "middle", style="italic")
    save("fig-38-3-5-mac-ip.svg", s)


# ── Рис. 38.3.6 — з IP відкривається весь інтернет ───────────────────────────
def fig36_internet():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "З IP-адресою відкривається весь звичний інтернет", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "щойно пристрій у мережі, він користується тим самим TCP/IP, що й комп'ютери — і дотягується до серверів",
              12, GREY, "middle", style="italic")
    chain = [("ESP32", "192.168.1.12", GREEN), ("роутер", "шлюз", BLUE), ("інтернет", "TCP/IP", "#b08900"), ("сервер/хмара", "напр. MQTT, HTTP", INK)]
    x = 70
    prev = None
    for nm, sub, col in chain:
        s += rect(x, 130, 170, 70, ("#eef6ef" if col == GREEN else "#fbfbfb"), col, 2, 10)
        s += text(x + 85, 160, nm, 12.5, col, "middle", "bold")
        s += text(x + 85, 182, sub, 9.5, GREY, "middle")
        if prev:
            s += arrow(prev, 165, x, 165, INK, 2)
        prev = x + 170
        x += 200

    s += rect(60, 240, W - 120, 80, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 264, "Радіо стало ВОРОТАМИ в мережу: маленький чіп шле дані в хмару, тягне час, оновлення, команди.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 286, "Уся складність інтернету (маршрути, DNS, сервери) працює так само, як для ноутбука.",
              11, INK, "middle")
    s += text(W / 2, 306, "Саме тому Wi-Fi-пристрій так легко зробити «розумним» — він просто ще один вузол мережі.",
              10.5, GREY, "middle", style="italic")
    save("fig-38-3-6-internet.svg", s)


# ── Рис. 38.3.7 — IP : порт = адреса послуги ─────────────────────────────────
def fig37_ipport():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "IP знаходить пристрій, ПОРТ — потрібну послугу на ньому", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "на одному пристрої може бути багато служб; порт каже, до якої саме звертаємось",
              12.5, GREY, "middle", style="italic")
    s += rect(250, 120, 400, 70, "#fbfbfb", INK, 2, 10)
    s += text(360, 163, "192.168.1.12", 18, BLUE, "middle", "bold")
    s += text(470, 163, ":", 18, GREY, "middle", "bold")
    s += text(540, 163, "1883", 18, GREEN, "middle", "bold")
    s += text(360, 110, "↑ IP — який пристрій", 10.5, BLUE, "middle", "bold")
    s += text(540, 110, "↑ порт — яка служба", 10.5, GREEN, "middle", "bold")
    # приклади портів
    ports = [("80", "веб (HTTP)"), ("1883", "MQTT"), ("22", "віддалений вхід"), ("своя", "власна служба")]
    x = 130
    for p, what in ports:
        s += rect(x, 220, 160, 50, "#f6f6f6", GREY, 1.4, 8)
        s += text(x + 80, 242, "порт " + p, 11.5, GREEN, "middle", "bold")
        s += text(x + 80, 260, what, 9.5, GREY, "middle")
        x += 170

    s += rect(60, 292, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 317, "Аналогія: IP — це будинок, порт — квартира в ньому. А НАДІЙНО чи ШВИДКО доставляти — вирішує TCP/UDP (§38.4).",
              11.5, INK, "middle", "bold")
    save("fig-38-3-7-ipport.svg", s)


# ============================================================================
#  §38.4 — TCP vs UDP: надійно vs швидко
# ============================================================================

# ── Рис. 38.4.1 — порівняльна таблиця ────────────────────────────────────────
def fig41_table():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "TCP проти UDP: два транспорти поверх IP", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "це знову той самий вибір «надійно vs швидко» з §38.1 — лише на рівні мережі",
              12.5, GREY, "middle", style="italic")
    bx, by, rw = 100, 92, 700
    s += rect(bx, by, rw, 32, "#f0f0f0", GREY, 1.3, 6)
    s += text(bx + 16, by + 21, "ознака", 11.5, INK, "start", "bold")
    s += text(bx + 330, by + 21, "TCP", 12, GREEN, "middle", "bold")
    s += text(bx + 560, by + 21, "UDP", 12, "#b08900", "middle", "bold")
    rows = [
        ("з'єднання", "так (рукостискання)", "ні (просто шлеш)"),
        ("доставка", "гарантована", "як вийде (втрати)"),
        ("порядок", "по порядку", "може плутатись"),
        ("швидкість/затримка", "повільніше, джитер", "швидко, мала затримка"),
        ("накладні витрати", "більші", "мінімальні"),
        ("модель", "потік байтів", "окремі датаграми"),
    ]
    yy = by + 32
    for feat, t, u in rows:
        s += rect(bx, yy, rw, 38, "#ffffff", GREY, 1)
        s += text(bx + 16, yy + 24, feat, 11, INK, "start", "bold")
        s += text(bx + 330, yy + 24, t, 11, GREEN, "middle")
        s += text(bx + 560, yy + 24, u, 11, "#b08900", "middle")
        yy += 38

    s += rect(60, 348, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 373, "TCP — як надійна служба доставки з підписом; UDP — як кинути листівку в скриньку: швидко й без гарантій.",
              11.5, INK, "middle", "bold")
    save("fig-38-4-1-table.svg", s)


# ── Рис. 38.4.2 — рукостискання TCP ──────────────────────────────────────────
def fig42_handshake():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "TCP спершу встановлює з'єднання (рукостискання)", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "перш ніж слати дані, сторони тричі обмінюються службовими пакетами — це коштує час",
              12.5, GREY, "middle", style="italic")
    lx, rx = 220, 680
    s += text(lx, 92, "клієнт", 12, GREEN, "middle", "bold")
    s += text(rx, 92, "сервер", 12, INK, "middle", "bold")
    s += line(lx, 104, lx, 300, GREY, 1.4)
    s += line(rx, 104, rx, 300, GREY, 1.4)
    s += arrow(lx, 130, rx, 155, BLUE, 2.2); s += text(450, 130, "1) SYN — «з'єднаймось?»", 10.5, BLUE, "middle", "bold")
    s += arrow(rx, 175, lx, 200, GREEN, 2.2); s += text(450, 176, "2) SYN-ACK — «згода»", 10.5, GREEN, "middle", "bold")
    s += arrow(lx, 220, rx, 245, BLUE, 2.2); s += text(450, 220, "3) ACK — «домовились»", 10.5, BLUE, "middle", "bold")
    s += text(450, 278, "з'єднання встановлено → тепер ідуть дані", 11.5, INK, "middle", "bold")

    s += rect(60, 308, W - 120, 44, LGREY, GREY, 1.3, 10)
    s += text(W / 2, 334, "Рукостискання дає надійність, але додає затримку на старті — для коротких частих повідомлень це дорого.",
              11.5, INK, "middle", "bold")
    save("fig-38-4-2-handshake.svg", s)


# ── Рис. 38.4.3 — TCP: по порядку й без втрат ────────────────────────────────
def fig43_tcp_reliable():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "TCP: дані приходять ПОВНІ й ПО ПОРЯДКУ", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "хай у дорозі щось губиться чи переплутується — TCP усе перешле й вишикує, перш ніж віддати застосунку",
              12, GREY, "middle", style="italic")
    s += text(120, 130, "у дорозі:", 11.5, INK, "end", "bold")
    chaos = [("3", 160), ("1", 250), ("—", 340), ("2", 430), ("4", 520)]
    for lab, x in chaos:
        if lab == "—":
            s += rect(x, 110, 70, 30, "#f4f4f4", RED, 1.4, 5); s += text(x + 35, 130, "2 зник", 9, RED, "middle", "bold")
        else:
            s += pkt(x, 110, 70, lab, GREY, "#f0f0f0")
    s += text(620, 130, "(переплутані,", 9.5, GREY, "start")
    s += text(620, 144, "є втрата)", 9.5, GREY, "start")
    s += arrow(360, 165, 360, 200, GREEN, 2)
    s += text(420, 185, "TCP лагодить: перешле 2, вишикує всі", 10.5, GREEN, "middle", "bold")
    s += text(120, 250, "застосунку:", 11.5, INK, "end", "bold")
    for i, lab in enumerate(["1", "2", "3", "4"]):
        s += pkt(160 + i * 90, 230, 70, lab, GREEN, LGRN)

    s += rect(60, 280, W - 120, 44, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 306, "Застосунок бачить рівний потік 1-2-3-4 — увесь безлад мережі схований усередині TCP.",
              11.5, INK, "middle", "bold")
    save("fig-38-4-3-tcp-reliable.svg", s)


# ── Рис. 38.4.4 — UDP: швидко й без гарантій ─────────────────────────────────
def fig44_udp():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "UDP: датаграми летять без з'єднання й без гарантій", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "шлеш і не чекаєш — швидко й дешево, але частина пакетів губиться чи приходить не по черзі",
              12, GREY, "middle", style="italic")
    s += text(120, 130, "надіслано:", 11.5, INK, "end", "bold")
    for i, lab in enumerate(["1", "2", "3", "4", "5"]):
        s += pkt(160 + i * 90, 110, 70, lab, "#b08900", "#fbf3df")
    s += text(120, 250, "отримано:", 11.5, INK, "end", "bold")
    got = [("1", True), ("3", True), ("2", True), ("—", False), ("5", True)]
    for i, (lab, ok) in enumerate(got):
        x = 160 + i * 90
        if ok:
            s += pkt(x, 230, 70, lab, INK, "#eef4ff")
        else:
            s += rect(x, 230, 70, 30, "#f4f4f4", RED, 1.4, 5); s += text(x + 35, 250, "4 зник", 9, RED, "middle", "bold")
    s += text(620, 210, "порядок інший, 4 загубився — і ніхто не перешле", 10, RED, "middle", "bold")

    s += rect(60, 282, W - 120, 44, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 308, "Зате жодних затримок на ретраї й сортування: дані свіжі. Надійність, якщо треба, будуєш сам.",
              11.5, INK, "middle", "bold")
    save("fig-38-4-4-udp.svg", s)


# ── Рис. 38.4.5 — блокування «голови черги» ──────────────────────────────────
def fig45_hol():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Чому TCP погано для реального часу: блокування голови черги", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "один загублений пакет тримає ВСІ наступні, аж поки його не перешлють — для відео це згубно",
              12, GREY, "middle", style="italic")
    # TCP
    s += text(110, 110, "TCP:", 13, GREEN, "start", "bold")
    s += pkt(160, 96, 70, "1", GREEN, LGRN)
    s += rect(240, 96, 70, 30, "#f4f4f4", RED, 1.6, 5); s += text(275, 116, "2 загубл.", 8.5, RED, "middle", "bold")
    for i, lab in enumerate(["3", "4", "5"]):
        s += pkt(320 + i * 80, 96, 70, lab, GREY, "#f0f0f0")
    s += line(310, 90, 310, 150, RED, 1.6, dash="3,3")
    s += text(470, 144, "3,4,5 прийшли, але ЧЕКАЮТЬ, поки перешлеться 2", 10.5, RED, "middle", "bold")
    s += text(470, 162, "→ велика затримка («затор»)", 10.5, RED, "middle", "bold")
    # UDP
    s += text(110, 230, "UDP:", 13, "#b08900", "start", "bold")
    s += pkt(160, 216, 70, "1", INK, "#eef4ff")
    s += rect(240, 216, 70, 30, "#f4f4f4", GREY, 1.4, 5); s += text(275, 236, "2 нема", 8.5, GREY, "middle")
    for i, lab in enumerate(["3", "4", "5"]):
        s += pkt(320 + i * 80, 216, 70, lab, INK, "#eef4ff")
    s += text(470, 264, "3,4,5 віддаються ОДРАЗУ — пропуск замість затору", 10.5, GREEN, "middle", "bold")
    s += text(470, 282, "→ дані свіжі, кадр-два просто зникли", 10.5, GREEN, "middle", "bold")

    s += rect(60, 312, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 336, "Для відео/голосу/гри свіжість важливіша за повноту: краще пропустити кадр, ніж застрягти на ньому.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 356, "Тому реальний час майже завжди йде по UDP, а не TCP.", 11, GREY, "middle", style="italic")
    save("fig-38-4-5-hol.svg", s)


# ── Рис. 38.4.6 — коли що ────────────────────────────────────────────────────
def fig46_when():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Коли TCP, а коли UDP", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен байт важливий → TCP; важлива свіжість, втрата кадру не страшна → UDP",
              12.5, GREY, "middle", style="italic")
    s += rect(70, 92, 360, 200, "#eef6ef", GREEN, 2, 12)
    s += text(250, 120, "TCP — коли важливий кожен байт", 12, GREEN, "middle", "bold")
    for i, t in enumerate(["команди керування", "передача файлів / прошивок", "веб (HTTP) і захищений веб",
                           "MQTT — типова IoT-телеметрія", "будь-що, де втрата неприпустима"]):
        s += circle(96, 150 + i * 27, 3.5, GREEN, GREEN, 0)
        s += text(110, 154 + i * 27, t, 11, INK, "start")
    s += rect(470, 92, 380, 200, "#fbf3df", "#b08900", 2, 12)
    s += text(660, 120, "UDP — коли важлива свіжість", 12, "#b08900", "middle", "bold")
    for i, t in enumerate(["потокове відео й голос", "ігровий стан у реальному часі", "жива телеметрія (часто оновлюється)",
                           "широкомовлення (broadcast)", "власна легка надійність зверху"]):
        s += circle(496, 150 + i * 27, 3.5, "#b08900", "#b08900", 0)
        s += text(510, 154 + i * 27, t, 11, INK, "start")

    s += rect(60, 308, W - 120, 40, LGREY, GREY, 1.3, 10)
    s += text(W / 2, 333, "Підказка: разовий важливий обмін → TCP; безперервний потік, де старе вже не потрібне → UDP.",
              11.5, INK, "middle", "bold")
    save("fig-38-4-6-when.svg", s)


# ── Рис. 38.4.7 — той самий вибір + код ──────────────────────────────────────
def fig47_trade():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Той самий вибір, що й у радіо — тепер у коді", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "«надійно vs швидко» (§38.1) на рівні мережі стає TCP vs UDP — і обирається класом у бібліотеці",
              12, GREY, "middle", style="italic")
    s += rect(80, 96, 360, 130, "#1e2330", "#111", 1.6, 8)
    s += text(100, 122, "// надійно (TCP)", 11, "#7f9cc0", "start")
    s += text(100, 146, "WiFiClient tcp;", 12, "#9be39b", "start", "bold")
    s += text(100, 168, 'tcp.connect(ip, 1883);', 11.5, "#9be39b", "start")
    s += text(100, 190, "tcp.print(data);", 11.5, "#9be39b", "start")
    s += text(100, 212, "// з'єднання, ACK — усе сховано", 10, "#7f9cc0", "start")
    s += rect(470, 96, 380, 130, "#1e2330", "#111", 1.6, 8)
    s += text(490, 122, "// швидко (UDP)", 11, "#7f9cc0", "start")
    s += text(490, 146, "WiFiUDP udp;", 12, "#ffd479", "start", "bold")
    s += text(490, 168, "udp.beginPacket(ip, port);", 11.5, "#ffd479", "start")
    s += text(490, 190, "udp.write(data); udp.endPacket();", 11, "#ffd479", "start")
    s += text(490, 212, "// шлеш і не чекаєш", 10, "#7f9cc0", "start")

    s += rect(60, 246, W - 120, 76, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 270, "Та сама дилема проходить через увесь зв'язок: ACK-надійність коштує затримки, її швидкість — втрат.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 292, "Обирай транспорт за природою даних, а не «про всяк випадок надійно».",
              11, INK, "middle")
    s += text(W / 2, 312, "(Часто беруть і те, й те: команди по TCP, потік телеметрії по UDP.)",
              10.5, GREY, "middle", style="italic")
    save("fig-38-4-7-trade.svg", s)


# ============================================================================
#  §38.5 — Bluetooth Classic (SPP): бездротовий UART
# ============================================================================

# ── Рис. 38.5.1 — точка-точка, неперервний потік ─────────────────────────────
def fig51_classic():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Bluetooth Classic: постійне з'єднання двох пристроїв", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "не мережа з багатьма, а проста пара «точка-точка» з неперервним двостороннім потоком",
              12.5, GREY, "middle", style="italic")
    s += _dev(120, 150, 150, 70, "телефон", "спарений", BLUE, "#e9eefb")
    s += _dev(630, 150, 150, 70, "ESP32", "спарений", GREEN, "#eef6ef")
    s += antenna(195, 150, BLUE, 14)
    s += antenna(705, 150, GREEN, 14)
    s += waves(290, 175, 8, 3, BTBLUE)
    s += arrow(300, 175, 600, 175, BTBLUE, 2.2)
    s += arrow(600, 200, 300, 200, BTBLUE, 2.2)
    s += text(450, 165, "неперервний потік", 11, BTBLUE, "middle", "bold")
    s += text(450, 224, "в обидва боки, поки тримається з'єднання", 10, GREY, "middle")

    s += rect(60, 256, W - 120, 66, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 280, "Classic — для тривалого потоку між ДВОМА пристроями: звук, файли, послідовні дані.",
              12, INK, "middle", "bold")
    s += text(W / 2, 302, "З'єднання «завжди увімкнене», тож і енергії бере відчутно — на відміну від BLE (§38.6).",
              11, GREY, "middle", style="italic")
    save("fig-38-5-1-classic.svg", s)


# ── Рис. 38.5.2 — SPP = бездротовий UART ─────────────────────────────────────
def fig52_spp():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "SPP: Bluetooth прикидається послідовним портом", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "профіль Serial Port Profile робить радіоканал НЕВІДРІЗНИМ від UART — той самий потік байтів",
              12, GREY, "middle", style="italic")
    # було: дріт
    s += rect(60, 92, 360, 110, "none", FAINT, 2, 12)
    s += text(240, 116, "було: дріт UART", 12.5, INK, "middle", "bold")
    s += _dev(90, 145, 90, 40, "A", None, INK)
    s += _dev(310, 145, 90, 40, "B", None, INK)
    for dy in (158, 172):
        s += line(180, dy, 310, dy, GREY, 2)
    s += text(245, 196, "TX/RX/GND", 9, GREY, "middle")
    # стало: BT
    s += rect(470, 92, 380, 110, "none", FAINT, 2, 12)
    s += text(660, 116, "стало: Bluetooth SPP", 12.5, BTBLUE, "middle", "bold")
    s += _dev(500, 145, 90, 40, "A", None, INK)
    s += _dev(740, 145, 90, 40, "B", None, INK)
    s += antenna(545, 145, BTBLUE, 10)
    s += antenna(785, 145, BTBLUE, 10)
    s += line(590, 165, 740, 165, BTBLUE, 2, dash="4,4")
    s += text(665, 196, "той самий потік — без дроту", 9, BTBLUE, "middle")

    s += rect(60, 230, W - 120, 92, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 256, "Код майже не міняється: де був Serial — тепер SerialBT, з тими ж print()/read().",
              12, INK, "middle", "bold")
    s += text(W / 2, 278, "Тому SPP — улюблений спосіб «перерізати дріт»: керувати роботом чи читати давач із телефона.",
              11.5, INK, "middle")
    s += text(W / 2, 300, "Під капотом — уся ненадійність радіо, але SPP дає ілюзію надійного дроту (ретраї сховані).",
              11, GREY, "middle", style="italic")
    save("fig-38-5-2-spp.svg", s)


# ── Рис. 38.5.3 — спарювання ─────────────────────────────────────────────────
def fig53_pairing():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Спарювання: встановити довіру один раз", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "перш ніж обмінюватися даними, пристрої «знайомляться» — і запам'ятовують одне одного",
              12.5, GREY, "middle", style="italic")
    steps = [
        ("1. ВИЯВЛЕННЯ", "знайти пристрій\nу списку поруч", BLUE),
        ("2. КЛЮЧ", "ввести PIN (0000/1234)\nчи звірити число", "#b08900"),
        ("3. ДОВІРА", "обмін ключами —\nтепер вони «свої»", GREEN),
        ("4. ПАМ'ЯТЬ", "наступного разу\nз'єднаються самі", INK),
    ]
    x0, bw, gap, y = 50, 195, 18, 110
    for i, (title, body, col) in enumerate(steps):
        x = x0 + i * (bw + gap)
        s += rect(x, y, bw, 90, "#fbfbfb", col, 2, 12)
        s += text(x + bw / 2, y + 28, title, 12, col, "middle", "bold")
        for j, ln in enumerate(body.split("\n")):
            s += text(x + bw / 2, y + 50 + j * 16, ln, 9.8, INK, "middle")
        if i < 3:
            s += arrow(x + bw, y + 45, x + bw + gap, y + 45, INK, 2)

    s += rect(60, 244, W - 120, 56, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 268, "Спарювання — це безпека: лише довірені пристрої отримують доступ, і ключ зберігається.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 290, "Тому смартфон «бачить» гарнітуру одразу — вони спарені раніше й пам'ятають одне одного.",
              11, GREY, "middle", style="italic")
    save("fig-38-5-3-pairing.svg", s)


# ── Рис. 38.5.4 — профілі Bluetooth ──────────────────────────────────────────
def fig54_profiles():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Профілі Bluetooth: готові «сценарії» під різні задачі", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "Bluetooth домовляється не лише як передавати біти, а й ЩО саме — профіль під кожен випадок",
              12.5, GREY, "middle", style="italic")
    profs = [
        ("SPP", "послідовні дані", "наш «бездротовий UART»", GREEN),
        ("A2DP", "стереозвук", "навушники, колонки", BLUE),
        ("HID", "клавіатури/миші", "ввід", "#b08900"),
        ("HFP", "гарнітура/дзвінки", "голос", INK),
    ]
    x = 60
    for nm, what, ex, col in profs:
        s += rect(x, 100, 195, 130, ("#eef6ef" if col == GREEN else "#fbfbfb"), col, 2, 12)
        s += text(x + 97, 130, nm, 16, col, "middle", "bold")
        s += text(x + 97, 156, what, 11, INK, "middle", "bold")
        s += text(x + 97, 180, ex, 9.5, GREY, "middle")
        if nm == "SPP":
            s += text(x + 97, 210, "← цей беремо ми", 10, GREEN, "middle", "bold")
        x += 207

    s += rect(60, 252, W - 120, 56, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 276, "Профіль — це домовленість про роль: SPP дає простий двосторонній потік байтів, як UART.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 298, "Інші профілі (звук, ввід) — спеціалізовані; нам для даних потрібен саме SPP.",
              11, GREY, "middle", style="italic")
    save("fig-38-5-4-profiles.svg", s)


# ── Рис. 38.5.5 — що під капотом ─────────────────────────────────────────────
def fig55_underhood():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Під капотом SPP: чистий потік над брудним ефіром", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "ти бачиш рівний UART-потік, а стек унизу б'ється з усією ненадійністю радіо (§38.1)",
              12, GREY, "middle", style="italic")
    s += rect(120, 96, 660, 46, "#eef6ef", GREEN, 2, 10)
    s += text(150, 124, "застосунок:", 11.5, GREEN, "start", "bold")
    s += text(300, 124, "SerialBT.print() / .read() — рівний потік байтів", 11, INK, "start")
    s += rect(120, 158, 660, 46, "#e9eefb", BLUE, 2, 10)
    s += text(150, 186, "стек BT:", 11.5, BLUE, "start", "bold")
    s += text(300, 186, "пакети, CRC, ACK, перевідправлення, стрибки частоти", 11, INK, "start")
    s += rect(120, 220, 660, 46, "#fbf3df", "#b08900", 2, 10)
    s += text(150, 248, "ефір:", 11.5, "#b08900", "start", "bold")
    s += text(300, 248, "спільне 2.4 ГГц із втратами й завадами", 11, INK, "start")
    s += arrow(450, 142, 450, 158, GREY, 1.6)
    s += arrow(450, 204, 450, 220, GREY, 1.6)

    s += rect(60, 284, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 309, "Зручність SPP — у цій ілюзії дроту; та пам'ятай: при поганому зв'язку «дріт» усе одно може обірватися.",
              11.5, INK, "middle", "bold")
    save("fig-38-5-5-underhood.svg", s)


# ── Рис. 38.5.6 — у коді: SerialBT ≈ Serial ──────────────────────────────────
def fig56_code():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 34, "У коді: SerialBT майже не відрізняється від Serial", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "хто вмів працювати з UART (§35), той одразу вміє і з Bluetooth SPP",
              12.5, GREY, "middle", style="italic")
    s += rect(120, 92, 660, 150, "#1e2330", "#111", 1.6, 10)
    code = [
        ("#include \"BluetoothSerial.h\"", "#7f9cc0"),
        ("BluetoothSerial SerialBT;", "#9be39b"),
        ("SerialBT.begin(\"ESP32-robot\");   // ім'я в списку Bluetooth", "#9be39b"),
        ("SerialBT.println(\"привіт з ESP32\");  // як Serial.println", "#9be39b"),
        ("if (SerialBT.available()) c = SerialBT.read();  // як Serial.read", "#9be39b"),
    ]
    yy = 120
    for ln, col in code:
        s += text(140, yy, ln, 11.5, col, "start", "bold" if col == "#9be39b" else "normal")
        yy += 26

    s += rect(60, 260, W - 120, 48, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 284, "Спар із телефона, відкрий Bluetooth-термінал — і шли/приймай байти, як по дроту.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 302, "Жодних антен і модуляції в коді — лише знайомий потік print/read.", 10.5, GREY, "middle", style="italic")
    save("fig-38-5-6-code.svg", s)


# ── Рис. 38.5.7 — Classic проти BLE (анонс) ──────────────────────────────────
def fig57_classic_vs_ble():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Classic проти BLE: потік проти ощадливих сплесків", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "два різні Bluetooth під різні задачі — BLE детально в наступній темі",
              12.5, GREY, "middle", style="italic")
    s += rect(70, 92, 360, 200, "#e9eefb", BLUE, 2, 12)
    s += text(250, 120, "Bluetooth Classic", 13, BLUE, "middle", "bold")
    for i, t in enumerate(["неперервний потік", "з'єднання завжди увімкнене", "більше енергії",
                           "звук, файли, серійні дані", "профіль SPP (ця тема)"]):
        s += circle(96, 150 + i * 27, 3.5, BLUE, BLUE, 0)
        s += text(110, 154 + i * 27, t, 11, INK, "start")
    s += rect(470, 92, 380, 200, "#eef6ef", GREEN, 2, 12)
    s += text(660, 120, "BLE (Low Energy)", 13, GREEN, "middle", "bold")
    for i, t in enumerate(["короткі сплески, не потік", "більшість часу СПИТЬ", "мізерна енергія",
                           "давачі, маячки, носимі", "характеристики, GATT (§38.6)"]):
        s += circle(496, 150 + i * 27, 3.5, GREEN, GREEN, 0)
        s += text(510, 154 + i * 27, t, 11, INK, "start")

    s += rect(60, 304, W - 120, 1, "none", "none", 0)
    save("fig-38-5-7-classic-vs-ble.svg", s)


# ============================================================================
#  §38.6 — BLE: реклама, характеристики, GATT (низька енергія)
# ============================================================================

# ── Рис. 38.6.1 — філософія: спить, прокидається на мить ─────────────────────
def fig61_philosophy():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "BLE: більшість часу СПИТЬ — звідси роки від батарейки", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "замість постійного потоку — рідкі короткі прокидання; середній струм мізерний",
              12.5, GREY, "middle", style="italic")
    # Classic — рівний високий
    s += text(110, 110, "Classic:", 12, BLUE, "start", "bold")
    s += text(110, 126, "увесь час «на»", 9.5, GREY, "start")
    s += line(200, 130, 800, 130, BLUE, 2.6)
    s += text(500, 122, "~30 мА постійно", 10.5, BLUE, "middle", "bold")
    s += text(810, 134, "I", 10, GREY, "start")
    # BLE — біля нуля зі сплесками
    s += text(110, 200, "BLE:", 12, GREEN, "start", "bold")
    s += text(110, 216, "спить + сплески", 9.5, GREY, "start")
    base = 250
    s += line(200, base, 800, base, GREEN, 2.4)
    for sx in range(240, 800, 90):
        s += line(sx, base, sx, base - 50, GREEN, 2)
        s += line(sx, base - 50, sx + 6, base - 50, GREEN, 2)
        s += line(sx + 6, base - 50, sx + 6, base, GREEN, 2)
    s += text(500, base + 22, "майже 0, зрідка короткий сплеск → середнє ~мікроампери", 10.5, GREEN, "middle", "bold")

    s += rect(60, 296, W - 120, 70, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 320, "Приклад: монетка 220 мА·год. Classic при 30 мА → ~7 годин; BLE при ~10 мкА → роки.",
              12, INK, "middle", "bold")
    s += text(W / 2, 342, "Тому BLE — для давачів, маячків і носимих: рідко й потроху, зате батарейка живе роками.",
              11, GREY, "middle", style="italic")
    save("fig-38-6-1-philosophy.svg", s)


# ── Рис. 38.6.2 — реклама ────────────────────────────────────────────────────
def fig62_advertising():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Реклама (advertising): пристрій сповіщає про себе без з'єднання", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "периферія час від часу шле короткі пакети-сповіщення; центральний (телефон) їх слухає",
              12.5, GREY, "middle", style="italic")
    s += _dev(80, 160, 150, 60, "давач (BLE)", "периферія", GREEN, "#eef6ef")
    s += antenna(155, 160, GREEN, 14)
    for k in range(3):
        s += waves(230 + k * 0, 178, 8 + k * 14, 1, BTBLUE)
    s += text(360, 130, "«я тут, ось моє ім'я/дані»", 10.5, BTBLUE, "middle", "bold")
    for k, dx in enumerate([300, 420, 540]):
        s += pkt(dx, 200, 70, "ADV", "#b08900", "#fbf3df", 26)
    s += text(420, 246, "короткі пакети-сповіщення, періодично", 10, GREY, "middle")
    s += _dev(670, 160, 150, 60, "телефон", "центральний", BLUE, "#e9eefb")
    s += antenna(745, 160, BLUE, 14)
    s += text(745, 240, "сканує й чує", 10, BLUE, "middle", "bold")

    s += rect(60, 278, W - 120, 70, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 302, "Так працюють маячки (beacons): шлють дані ШИРОКОМОВНО, узагалі не з'єднуючись.",
              12, INK, "middle", "bold")
    s += text(W / 2, 324, "Хочеш двосторонній обмін — центральний за рекламою ЗНАХОДИТЬ периферію й під'єднується.",
              11, GREY, "middle", style="italic")
    save("fig-38-6-2-advertising.svg", s)


# ── Рис. 38.6.3 — ролі ───────────────────────────────────────────────────────
def fig63_roles():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 34, "Дві ролі: периферія (має дані) і центральний (хоче дані)", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "периферія рекламує й віддає свої значення; центральний сканує, під'єднується й читає",
              12.5, GREY, "middle", style="italic")
    s += rect(80, 92, 360, 150, "#eef6ef", GREEN, 2, 12)
    s += text(260, 120, "ПЕРИФЕРІЯ (peripheral)", 12.5, GREEN, "middle", "bold")
    for i, t in enumerate(["• рекламує себе", "• тримає дані (GATT-сервер)", "• зазвичай давач/гаджет"]):
        s += text(100, 150 + i * 26, t, 11, INK, "start")
    s += rect(470, 92, 380, 150, "#e9eefb", BLUE, 2, 12)
    s += text(660, 120, "ЦЕНТРАЛЬНИЙ (central)", 12.5, BLUE, "middle", "bold")
    for i, t in enumerate(["• сканує й під'єднується", "• читає/пише дані (клієнт)", "• зазвичай телефон/ПК"]):
        s += text(490, 150 + i * 26, t, 11, INK, "start")
    s += arrow(440, 167, 470, 167, GREY, 2)

    s += rect(60, 256, W - 120, 56, LGREY, GREY, 1.3, 10)
    s += text(W / 2, 280, "Не плутай із Classic: тут не «потік», а сервер даних (периферія) і клієнт (центральний).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 300, "ESP32 може бути будь-ким: периферією-давачем або центральним-збирачем.",
              11, GREY, "middle", style="italic")
    save("fig-38-6-3-roles.svg", s)


# ── Рис. 38.6.4 — GATT: ієрархія даних ───────────────────────────────────────
def fig64_gatt():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "GATT: дані як дерево сервісів і характеристик", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "замість потоку байтів — іменовані значення з властивостями (читати/писати/сповіщати)",
              12, GREY, "middle", style="italic")
    # сервер
    s += rect(330, 84, 240, 44, "#eef6ef", GREEN, 2, 10)
    s += text(450, 112, "GATT-СЕРВЕР (периферія)", 11.5, GREEN, "middle", "bold")
    # сервіс
    s += line(450, 128, 450, 150, GREY, 1.6)
    s += rect(300, 150, 300, 44, "#e9eefb", BLUE, 2, 10)
    s += text(450, 170, "СЕРВІС «Оточення»", 11.5, BLUE, "middle", "bold")
    s += text(450, 186, "UUID …181A", 9, GREY, "middle")
    # характеристики
    chars = [
        ("Температура", "23.4 °C", "read · notify", 110),
        ("Вологість", "57 %", "read · notify", 450),
        ("Поріг", "30 °C", "read · write", 790),
    ]
    for nm, val, props, cx in chars:
        s += line(450, 194, cx, 230, GREY, 1.4)
        s += rect(cx - 130, 230, 260, 70, "#fbf3df", "#b08900", 1.8, 10)
        s += text(cx, 254, "Характеристика: " + nm, 11, "#b08900", "middle", "bold")
        s += text(cx, 274, "значення: " + val, 11, INK, "middle", "bold")
        s += text(cx, 292, props, 9.5, GREY, "middle")

    s += rect(60, 324, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 348, "Сервер → сервіси (групи) → характеристики (окремі значення з UUID і властивостями).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 368, "Центральний не «читає потік», а звертається до КОНКРЕТНОЇ характеристики за її UUID.",
              11, GREY, "middle", style="italic")
    save("fig-38-6-4-gatt.svg", s)


# ── Рис. 38.6.5 — операції: read/write/notify ────────────────────────────────
def fig65_operations():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Три операції: читати, писати й СПОВІЩАТИ", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "notify — головний трюк ощадливості: периферія сама штовхає нове значення, не треба опитувати",
              12, GREY, "middle", style="italic")
    ops = [
        ("READ", "центральний ТЯГНЕ значення\n(коли захоче)", BLUE, "→"),
        ("WRITE", "центральний ШТОВХАЄ значення\n(напр. поріг, команду)", "#b08900", "←"),
        ("NOTIFY", "периферія САМА штовхає, щойно\nзначення змінилось", GREEN, "↩"),
    ]
    x = 60
    for nm, body, col, d in ops:
        s += rect(x, 96, 270, 160, ("#eef6ef" if col == GREEN else "#fbfbfb"), col, 2, 12)
        s += text(x + 135, 126, nm, 14, col, "middle", "bold")
        for j, ln in enumerate(body.split("\n")):
            s += text(x + 135, 160 + j * 20, ln, 10.5, INK, "middle")
        if nm == "NOTIFY":
            s += text(x + 135, 230, "← економить енергію!", 10, GREEN, "middle", "bold")
        x += 290

    s += rect(60, 274, W - 120, 70, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 298, "Опитування (постійно READ) тримало б радіо ввімкненим; NOTIFY дає прокидатися лише при новині.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 320, "Тому пульсометр чи давач шлють дані через notify: телефон підписався — і отримує оновлення сам.",
              11, GREY, "middle", style="italic")
    save("fig-38-6-5-operations.svg", s)


# ── Рис. 38.6.6 — потік (SPP) проти структури (GATT) ─────────────────────────
def fig66_stream_vs_struct():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Дві моделі даних: потік (SPP) проти структури (GATT)", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "Classic дає «трубу для байтів»; BLE — набір названих значень, до яких звертаєшся за іменем",
              12, GREY, "middle", style="italic")
    s += rect(70, 92, 360, 170, "#e9eefb", BLUE, 2, 12)
    s += text(250, 118, "SPP (Classic): потік", 12.5, BLUE, "middle", "bold")
    for i, b in enumerate(["4A", "12", "FF", "00", "7E"]):
        s += pkt(110 + i * 44, 140, 40, b, INK, "#fff", 26)
    s += text(250, 200, "просто байти підряд —", 10.5, INK, "middle")
    s += text(250, 218, "структуру вигадуєш сам", 10.5, GREY, "middle")
    s += rect(470, 92, 380, 170, "#eef6ef", GREEN, 2, 12)
    s += text(660, 118, "GATT (BLE): названі значення", 12, GREEN, "middle", "bold")
    for i, (nm, v) in enumerate([("Температура", "23.4"), ("Вологість", "57"), ("Заряд", "88%")]):
        s += rect(500, 138 + i * 36, 320, 30, "#fbf3df", "#b08900", 1.2, 5)
        s += text(516, 158 + i * 36, nm, 10.5, "#b08900", "start", "bold")
        s += text(800, 158 + i * 36, v, 11, INK, "end", "bold")

    s += rect(60, 278, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 302, "SPP зручний, коли вже маєш свій байтовий протокол; GATT — коли дані природно розкладаються на значення.",
              11, INK, "middle", "bold")
    s += text(W / 2, 322, "Телефонні застосунки легко читають стандартні GATT-сервіси (пульс, батарея) без жодного коду.",
              10.5, GREY, "middle", style="italic")
    save("fig-38-6-6-stream-vs-struct.svg", s)


# ── Рис. 38.6.7 — на практиці + вибір ────────────────────────────────────────
def fig67_practice():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "На практиці й короткий вибір: BLE / Classic / Wi-Fi", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "ESP32 може бути BLE-периферією: підняв сервіс із характеристиками — і телефон їх читає/підписується",
              11.5, GREY, "middle", style="italic")
    rows = [
        ("давач на батарейці, рідкі дані", "→ BLE", GREEN, "роки автономності, notify"),
        ("бездротовий «дріт», пульт, потік", "→ Bluetooth Classic (SPP)", BLUE, "простий потік байтів"),
        ("вихід у мережу / інтернет / хмару", "→ Wi-Fi", "#b08900", "IP, TCP/UDP, сервери"),
    ]
    yy = 100
    for case, pick, col, why in rows:
        s += rect(90, yy, 720, 50, ("#eef6ef" if col == GREEN else "#fbfbfb"), col, 1.8, 10)
        s += text(110, yy + 31, case, 12, INK, "start", "bold")
        s += text(440, yy + 31, pick, 12, col, "start", "bold")
        s += text(620, yy + 20, why, 9.5, GREY, "start")
        yy += 62

    s += rect(60, 296, W - 120, 50, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 320, "Три бездротові інструменти під три задачі: BLE — ощадливі сплески, Classic — потік, Wi-Fi — мережа.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 338, "ESP32 вміє всі три — обирай за енергією, дальністю й тим, чи потрібен інтернет.",
              10.5, GREY, "middle", style="italic")
    save("fig-38-6-7-practice.svg", s)


# ============================================================================
#  §38.7 — Проєктування надійного обміну + failsafe на втрату зв'язку
# ============================================================================

# ── Рис. 38.7.1 — серцебиття (heartbeat) ─────────────────────────────────────
def fig71_heartbeat():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Серцебиття (heartbeat): «я живий» через рівні проміжки", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "пристрій періодично шле короткий сигнал; зник на надто довго — значить, зв'язок утрачено",
              12.5, GREY, "middle", style="italic")
    x0, y = 110, 170
    s += arrow(x0, y, 800, y, INK, 1.6)
    s += text(800, y + 22, "час →", 11, GREY, "start")
    beats = [150, 250, 350, 450]  # рівні удари
    for bx in beats:
        s += line(bx, y, bx, y - 40, GREEN, 2.6)
        s += text(bx, y - 48, "♥", 12, GREEN, "middle", "bold")
    s += text(300, y + 22, "рівні удари: «живий, живий…»", 10.5, GREEN, "middle", "bold")
    # пропуск
    s += rect(490, y - 44, 230, 44, "#fdeeee", RED, 1.4, 5)
    s += text(605, y - 18, "немає ударів", 10.5, RED, "middle", "bold")
    s += line(745, y, 745, y - 60, RED, 2, dash="3,3")
    s += text(745, y - 68, "тиша задовга → ВТРАТА", 10, RED, "middle", "bold")

    s += rect(60, 248, W - 120, 70, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 272, "Радіо рідко дає чітку подію «від'єднано» — тож втрату ловлять саме за ВІДСУТНІСТЮ серцебиття.",
              12, INK, "middle", "bold")
    s += text(W / 2, 294, "Той самий heartbeat ми ще зустрінемо в протоколі MAVLink (§42).",
              11, GREY, "middle", style="italic")
    save("fig-38-7-1-heartbeat.svg", s)


# ── Рис. 38.7.2 — виявлення за таймаутом ─────────────────────────────────────
def fig72_timeout():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Виявлення втрати: не «подія», а ТАЙМАУТ тиші", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "стережемо час від останнього повідомлення; перевищив поріг — запускаємо failsafe",
              12.5, GREY, "middle", style="italic")
    s += rect(120, 96, 660, 130, "#1e2330", "#111", 1.6, 10)
    s += text(140, 124, "// у головному циклі (патерн millis, §24.5)", 11, "#7f9cc0", "start")
    s += text(140, 150, "if (gotMessage) lastMsg = millis();", 12, "#9be39b", "start", "bold")
    s += text(140, 176, "if (millis() - lastMsg > TIMEOUT)", 12, "#ffd479", "start", "bold")
    s += text(165, 200, "failsafe();   // зв'язок утрачено", 12, "#ff9b9b", "start", "bold")

    s += rect(60, 242, W - 120, 76, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 266, "Поріг TIMEOUT беруть із запасом: напр. серцебиття кожні 100 мс, дозволяємо 3 пропуски → 300 мс.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 288, "Замало — хибні спрацювання від випадкових втрат; забагато — пізно реагуємо на справжню втрату.",
              11, INK, "middle")
    s += text(W / 2, 308, "Це той самий watchdog-підхід (§24.7), лише для зв'язку.", 10.5, GREY, "middle", style="italic")
    save("fig-38-7-2-timeout.svg", s)


# ── Рис. 38.7.3 — дії failsafe ───────────────────────────────────────────────
def fig73_failsafe():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Що робити при втраті: безпечна дія, а НЕ «лети як летів»", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен пристрій має заздалегідь визначену безпечну реакцію — головне, не продовжувати останню команду",
              12, GREY, "middle", style="italic")
    devs = [
        ("дрон", "зависнути / повернутись\nдодому / сісти", GREEN),
        ("робот / ровер", "зупинити мотори", GREEN),
        ("виконавчий механізм", "перейти в безпечне\nположення", GREEN),
    ]
    x = 60
    for nm, act, col in devs:
        s += rect(x, 96, 270, 110, "#eef6ef", col, 2, 12)
        s += text(x + 135, 124, nm, 12.5, col, "middle", "bold")
        for j, ln in enumerate(act.split("\n")):
            s += text(x + 135, 152 + j * 18, ln, 11, INK, "middle")
        x += 290

    s += rect(120, 226, 660, 64, LRED, RED, 2, 12)
    s += text(450, 252, "✗ НІКОЛИ: «продовжувати останню команду»", 13.5, RED, "middle", "bold")
    s += text(450, 274, "втратив зв'язок на повному газу → і далі мчить = найгірший результат", 11, INK, "middle")

    s += rect(60, 304, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 328, "Золоте правило: відсутність команд — це теж команда, і вона має означати «БЕЗПЕЧНО зупинись».",
              12, INK, "middle", "bold")
    s += text(W / 2, 348, "Саме failsafe відрізняє іграшку від апарата, якому можна довірити рух.",
              11, GREY, "middle", style="italic")
    save("fig-38-7-3-failsafe.svg", s)


# ── Рис. 38.7.4 — стан проти команд ──────────────────────────────────────────
def fig74_state_vs_cmd():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Шли СТАН, а не приріст: втрата сама виправляється", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "абсолютне значення наступне оновлення лагодить; приріст («+10») при втраті зникає назавжди",
              12, GREY, "middle", style="italic")
    # стан
    s += text(110, 110, "СТАН (добре):", 12, GREEN, "start", "bold")
    vals = [("газ=30", True), ("газ=50", False), ("газ=70", True)]
    x0 = 130
    for i, (lab, ok) in enumerate(vals):
        x = x0 + i * 200
        if ok:
            s += pkt(x, 130, 120, lab, GREEN, LGRN)
        else:
            s += rect(x, 130, 120, 30, "#f4f4f4", RED, 1.4, 5); s += text(x + 60, 150, lab + " зник", 9, RED, "middle", "bold")
    s += text(450, 184, "втратили «50» — але «70» одразу все виправило (приймач знає точне значення)", 10, INK, "middle", "bold")
    # команди
    s += text(110, 240, "ПРИРІСТ (погано):", 12, RED, "start", "bold")
    cmds = [("+10", True), ("+10", False), ("+10", True)]
    for i, (lab, ok) in enumerate(cmds):
        x = x0 + i * 200
        if ok:
            s += pkt(x, 260, 120, lab, INK, "#eef4ff")
        else:
            s += rect(x, 260, 120, 30, "#f4f4f4", RED, 1.4, 5); s += text(x + 60, 280, lab + " зник", 9, RED, "middle", "bold")
    s += text(450, 314, "втратили один «+10» — і приймач НАЗАВЖДИ на 10 нижче, ніж мав бути", 10, RED, "middle", "bold")

    s += rect(60, 330, W - 120, 1, "none", "none", 0)
    save("fig-38-7-4-state-vs-cmd.svg", s)


# ── Рис. 38.7.5 — номери послідовності ───────────────────────────────────────
def fig75_sequence():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 34, "Номери послідовності: відкидати застарілі команди", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "нумеруй повідомлення — і ігноруй ті, що прийшли із запізненням, після свіжіших",
              12.5, GREY, "middle", style="italic")
    x0, y = 130, 150
    pkts = [("#5", True), ("#6", True), ("#8", True), ("#7", False), ("#9", True)]
    for i, (lab, ok) in enumerate(pkts):
        x = x0 + i * 130
        col = GREEN if ok else RED
        s += pkt(x, y, 90, lab, col, ("#eef6ef" if ok else LRED))
        if ok:
            s += text(x + 45, y + 50, "беремо", 9, GREEN, "middle", "bold")
        else:
            s += text(x + 45, y + 50, "старіший за #8", 8.5, RED, "middle", "bold")
            s += text(x + 45, y + 64, "→ ігнор", 9, RED, "middle", "bold")

    s += rect(60, 240, W - 120, 70, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 264, "Команда #7 прийшла ПІСЛЯ #8 (переплутався порядок) — виконати її означало б «відкотити» стан назад.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 286, "Правило: бери лише номер, БІЛЬШИЙ за вже прийнятий; менший — застарілий, відкидай.",
              11, GREY, "middle", style="italic")
    save("fig-38-7-5-sequence.svg", s)


# ── Рис. 38.7.6 — ACK для важливого, best-effort для потоку ──────────────────
def fig76_ack_besteffort():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Розділяй: критичні команди з ACK, потік — best-effort", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "одне має дійти напевно (і повторюй, поки не підтвердять), інше можна й загубити",
              12.5, GREY, "middle", style="italic")
    s += rect(70, 92, 360, 180, "#eef6ef", GREEN, 2, 12)
    s += text(250, 120, "критичні — з ACK + ретраї", 12, GREEN, "middle", "bold")
    for i, t in enumerate(["«увімкнути мотори» (arm)", "«вимкнути» (disarm)", "зміна режиму", "→ повторюй, поки не підтвердять"]):
        s += circle(96, 150 + i * 28, 3.5, GREEN, GREEN, 0)
        s += text(110, 154 + i * 28, t, 11, INK, "start")
    s += rect(470, 92, 380, 180, "#fbf3df", "#b08900", 2, 12)
    s += text(660, 120, "потік — best-effort", 12, "#b08900", "middle", "bold")
    for i, t in enumerate(["телеметрія (часто оновлюється)", "позиція, кут, заряд", "відеопотік", "→ загубилось — байдуже, прийде свіже"]):
        s += circle(496, 150 + i * 28, 3.5, "#b08900", "#b08900", 0)
        s += text(510, 154 + i * 28, t, 11, INK, "start")

    s += rect(60, 288, W - 120, 40, LGREY, GREY, 1.3, 10)
    s += text(W / 2, 313, "Не плати за надійність там, де вона не потрібна, і не економ на ній там, де команда мусить дійти.",
              11.5, INK, "middle", "bold")
    save("fig-38-7-6-ack-besteffort.svg", s)


# ── Рис. 38.7.7 — шари надійності + підсумок ─────────────────────────────────
def fig77_layers():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Три шари надійності — і підсумок бездротового", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен шар ловить свій клас бід; разом вони дають передбачуваний пристрій на ненадійному радіо",
              12, GREY, "middle", style="italic")
    layers = [
        ("стек радіо", "ретраї ОКРЕМИХ пакетів (CRC, ACK) — сховано", BLUE, 96),
        ("твій протокол", "номери послідовності + слати СТАН, а не приріст", "#b08900", 152),
        ("твій застосунок", "серцебиття, таймаут і FAILSAFE на повну втрату", GREEN, 208),
    ]
    for nm, desc, col, y in layers:
        s += rect(120, y, 660, 46, ("#eef6ef" if col == GREEN else "#fbfbfb"), col, 2, 10)
        s += text(150, y + 28, nm, 12, col, "start", "bold")
        s += text(310, y + 28, desc, 10.5, INK, "start")
    s += arrow(450, 142, 450, 152, GREY, 1.6)
    s += arrow(450, 198, 450, 208, GREY, 1.6)

    s += rect(60, 268, W - 120, 76, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 292, "Радіо ненадійне за визначенням — тож надійність будують ШАРАМИ, а не сподіваються на «гарний сигнал».",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 314, "Це підсумок усього розділу: зручні Wi-Fi/Bluetooth ховають фізику, але failsafe лишається за тобою.",
              11, INK, "middle")
    s += text(W / 2, 334, "Далі — сама фізика радіохвиль: що ж насправді летить «по повітрю».", 10.5, GREY, "middle", style="italic")
    save("fig-38-7-7-layers.svg", s)


if __name__ == "__main__":
    # — історія (секція 0) —
    fig_timeline()
    fig_unite()
    fig_logo()
    fig_placeholder()
    fig_whodidit()
    # — §38.1 —
    fig11_radiochip()
    fig12_wire_vs_air()
    fig13_enemies()
    fig14_lost()
    fig15_ack_retry()
    fig16_besteffort()
    fig17_failsafe()
    # — §38.2 —
    fig21_band()
    fig22_channels()
    fig23_bandwidth()
    fig24_coexist()
    fig25_hopping()
    fig26_packet()
    fig27_2v5()
    # — §38.3 —
    fig31_infra()
    fig32_joining()
    fig33_sta_ap()
    fig34_ip_dhcp()
    fig35_mac_ip()
    fig36_internet()
    fig37_ipport()
    # — §38.4 —
    fig41_table()
    fig42_handshake()
    fig43_tcp_reliable()
    fig44_udp()
    fig45_hol()
    fig46_when()
    fig47_trade()
    # — §38.5 —
    fig51_classic()
    fig52_spp()
    fig53_pairing()
    fig54_profiles()
    fig55_underhood()
    fig56_code()
    fig57_classic_vs_ble()
    # — §38.6 —
    fig61_philosophy()
    fig62_advertising()
    fig63_roles()
    fig64_gatt()
    fig65_operations()
    fig66_stream_vs_struct()
    fig67_practice()
    # — §38.7 —
    fig71_heartbeat()
    fig72_timeout()
    fig73_failsafe()
    fig74_state_vs_cmd()
    fig75_sequence()
    fig76_ack_besteffort()
    fig77_layers()
    print("done.")
