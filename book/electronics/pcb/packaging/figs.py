# -*- coding: utf-8 -*-
"""Фігури до теми «Корпусування» (book/electronics/pcb/packaging).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки (поза палітрою svgkit) для «фізичних» матеріалів на схемах
GOLD   = "#c79a2e"   # золотий дротик / контактні площадки леду
SILVER = "#9a9a9a"   # кулька припою
DIE    = "#9fb0c8"   # кремнієвий кристал
SUBSTR = "#2f6f3f"   # підкладка / основа корпусу
DARK   = "#3a3a3a"   # тіло корпусу (вид збоку)


def out(name, w, h, frags, title=None):
    render(os.path.join(IMG, name), w, h, *frags, title=title)


# ── 1. Навіщо корпус: три ролі ──────────────────────────────────────────────
def fig_why_package():
    W, H = 720, 300
    f = []
    cards = [
        (145, "Захист", ["крихкий кремній —", "у міцну оболонку", "від вологи й ударів"], NEG),
        (360, "Масштаб виводів", ["мікронні площадки →", "контакти, які", "можна паяти"], FIELD),
        (575, "Відведення тепла", ["тепло від кристала —", "назовні, до плати", "й радіатора"], POS),
    ]
    for cx, head, sub, accent in cards:
        x, y, bw, bh = cx - 105, 76, 210, 132
        f.append(rect(x, y, bw, bh, fill=FILL, stroke=accent, sw=2.2, rx=12))
        f.append(text(cx, y + 30, head, size=15, bold=True, color=accent))
        f.append(line(x + 16, y + 42, x + bw - 16, y + 42, color=accent, sw=1.2))
        f.append(mtext(cx, y + 66, sub, size=12, color=INK, lh=1.3))
    cap = ("Без корпуса кристал не вживеш: він мікроскопічний, крихкий і гарячий. "
           "Корпус робить його придатним до плати —")
    f.append(text(W / 2, 252, cap, size=12, color=MUTED, italic=True))
    f.append(text(W / 2, 270, "захищає, виводить контакти до паяльного масштабу й відводить тепло.",
                  size=12, color=MUTED, italic=True))
    out("why-package.svg", W, H, f, title="Навіщо кристалу корпус")


# ── 2. Wire bonding проти flip-chip ─────────────────────────────────────────
def fig_wirebond_flip():
    W, H = 760, 350
    f = []
    # --- ліва половина: wire bonding ---
    f.append(text(210, 58, "Wire bonding (дротяне з'єднання)", size=13, bold=True))
    f.append(rect(60, 200, 300, 30, fill=SUBSTR, stroke="#163b21", sw=2, rx=0))
    f.append(rect(150, 170, 120, 30, fill=DIE, stroke=INK, sw=2, rx=0))
    f.append(text(210, 190, "кристал (лицем угору)", size=10, color=INK))
    pads_l = [(160, 84), (190, 124), (230, 296 - 200 + 124), (260, 336 - 200 + 124)]
    bonds = [(160, 84), (190, 124), (230, 296), (260, 336)]
    for x0, xland in bonds:
        f.append('<path d="M %d,170 Q %.0f,118 %d,200" fill="none" stroke="%s" stroke-width="1.8"/>'
                 % (x0, (x0 + xland) / 2, xland, GOLD))
        f.append(rect(xland - 5, 196, 10, 8, fill="#888888", stroke=INK, sw=1, rx=0))
    f.append(text(210, 150, "тонкі золоті дротики", size=10.5, color="#a06000"))
    f.append(text(210, 250, "по одному дротику на контакт, лише з краю кристала",
                  size=10.5, color=MUTED))
    # --- права половина: flip-chip ---
    f.append(text(570, 58, "Flip-chip (перевернутий кристал)", size=13, bold=True))
    f.append(rect(420, 200, 300, 30, fill=SUBSTR, stroke="#163b21", sw=2, rx=0))
    f.append(rect(500, 150, 140, 34, fill=DIE, stroke=INK, sw=2, rx=0))
    f.append(text(570, 144, "кристал (лицем униз)", size=10, color=INK))
    for i in range(7):
        cx = 512 + i * 19
        f.append(circle(cx, 192, 6, fill="#c0c0c0", stroke=INK, sw=1.2))
    f.append(text(570, 250, "кульки припою прямо під кристалом", size=10.5, color=MUTED))
    f.append(text(570, 268, "коротший шлях — швидше й більше з'єднань",
                  size=10.5, color=FIELD))
    # --- підпис ---
    f.append(text(W / 2, 322, "Дротики дешеві й усюди; перевернутий кристал дає сотні коротких з'єднань",
                  size=11.5, color=MUTED, italic=True))
    f.append(text(W / 2, 340, "одразу під усією площею — його беруть, коли виводів багато або потрібна швидкість.",
                  size=11.5, color=MUTED, italic=True))
    out("wirebond-flip.svg", W, H, f, title="Два способи з'єднати кристал зі світом")


# ── 3. QFN проти BGA: край знизу проти решітки кульок ───────────────────────
def fig_qfn_bga():
    W, H = 760, 372
    f = []
    # --- QFN ---
    f.append(text(210, 58, "QFN — контакти по краю знизу", size=13, bold=True))
    f.append(rect(100, 80, 140, 140, fill="#dddddd", stroke=INK, sw=2, rx=0))
    # площадки по периметру (вид знизу)
    for i in range(8):
        x = 112 + i * 16
        f.append(rect(x, 82, 12, 11, fill=GOLD, stroke="#806010", sw=1, rx=0))   # верх
        f.append(rect(x, 207, 12, 11, fill=GOLD, stroke="#806010", sw=1, rx=0))  # низ
    for i in range(7):
        y = 96 + i * 16
        f.append(rect(102, y, 11, 12, fill=GOLD, stroke="#806010", sw=1, rx=0))  # лівий
        f.append(rect(227, y, 11, 12, fill=GOLD, stroke="#806010", sw=1, rx=0))  # правий
    f.append(rect(150, 130, 40, 40, fill="#b0b0b0", stroke=INK, sw=1.2, rx=0))
    f.append(text(170, 154, "тепло-", size=9, color=INK))
    f.append(text(170, 165, "поле", size=9, color=INK))
    f.append(text(170, 236, "вид знизу", size=10.5, color=MUTED))
    # вид збоку
    f.append(rect(100, 272, 140, 26, fill=DARK, stroke=INK, sw=1.6, rx=0))
    for i in range(7):
        x = 104 + i * 19
        f.append(rect(x, 296, 12, 6, fill=GOLD, stroke="#806010", sw=1, rx=0))
    f.append(text(170, 320, "плоскі площадки лише по периметру", size=10, color=MUTED))
    # --- BGA ---
    f.append(text(550, 58, "BGA — решітка кульок припою", size=13, bold=True))
    f.append(rect(470, 80, 140, 140, fill="#cfd8e8", stroke=INK, sw=2, rx=0))
    for cxN in range(7):
        for cyN in range(7):
            f.append(circle(486 + cxN * 18, 96 + cyN * 18, 6,
                            fill=SILVER, stroke="#444", sw=1))
    f.append(text(540, 236, "вид знизу (масив кульок)", size=10.5, color=MUTED))
    f.append(rect(470, 272, 140, 24, fill="#2f4f6f", stroke=INK, sw=1.6, rx=0))
    for i in range(8):
        f.append(circle(480 + i * 17, 302, 6, fill=SILVER, stroke="#444", sw=1))
    f.append(text(540, 322, "сотні виводів під усім корпусом", size=10, color=MUTED))
    # --- підпис ---
    f.append(text(W / 2, 348, "«Ніжки» — це й є виводи кристала назовні: у QFN — плоскі площадки по краю,",
                  size=11.5, color=MUTED, italic=True))
    f.append(text(W / 2, 366, "у BGA — кулькова решітка під усім корпусом, коли виводів сотні.",
                  size=11.5, color=MUTED, italic=True))
    out("qfn-bga.svg", W, H, f, title="Звідки беруться виводи: QFN і BGA")


# ── 4. (вставка) Родовід корпусів за способом з'єднання ─────────────────────
def fig_package_family():
    W, H = 760, 392
    f = []
    f.append(text(W / 2, 52, "Спосіб з'єднання кристала диктує форму ніжок", size=13, bold=True, color=MUTED))
    # дві гілки
    f.append(rect(50, 72, 300, 40, fill="#fdf6e8", stroke=GOLD, sw=2.2, rx=10))
    f.append(text(200, 90, "Дротяне з'єднання (wire bonding)", size=12.5, bold=True, color="#8a6a10"))
    f.append(text(200, 106, "контакт на леду — по периметру", size=10.5, color=MUTED))
    f.append(rect(410, 72, 300, 40, fill="#eef2fb", stroke=NEG, sw=2.2, rx=10))
    f.append(text(560, 90, "Flip-chip (перевернутий кристал)", size=12.5, bold=True, color=NEG))
    f.append(text(560, 106, "контакт масивом — під низом", size=10.5, color=MUTED))
    # представники гілок (сходинка дружності до рук)
    left = [("DIP", "наскрізь, крок 2.54 мм", FIELD),
            ("SOIC", "крила, крок 1.27 мм", FIELD),
            ("QFN", "площадки, крок 0.4–0.5 мм", POS)]
    for i, (name, sub, accent) in enumerate(left):
        y = 150 + i * 66
        f.append(rect(70, y, 260, 52, fill=FILL, stroke=accent, sw=2, rx=8))
        f.append(text(120, y + 24, name, size=14, bold=True, color=accent))
        f.append(text(210, y + 24, sub, size=11, color=INK))
        f.append(line(200, y + 36, 312, y + 36, color=accent, sw=1))
    f.append(rect(430, 216, 260, 52, fill=FILL, stroke=POS, sw=2, rx=8))
    f.append(text(485, 240, "BGA", size=14, bold=True, color=POS))
    f.append(text(580, 240, "решітка кульок, крок 0.5–1 мм", size=11, color=INK))
    # вісь «простіше паяти»
    f.append(arrow(70, 350, 690, 350, color=INK, sw=2))
    f.append(text(120, 372, "простіше для рук", size=11, color=FIELD, bold=True))
    f.append(text(640, 372, "лише піч", size=11, color=POS, bold=True))
    f.append(text(W / 2, 340, "що ширші й відкритіші виводи — то простіше посадити жалом",
                  size=10.5, color=MUTED, italic=True))
    out("package-family.svg", W, H, f, title="Родовід корпусів")


# ── 5. (вставка) Розріз: дротяне з'єднання проти flip-chip ──────────────────
def fig_bond_cross_section():
    W, H = 760, 340
    f = []
    # --- ліворуч: wire bonding у розрізі ---
    f.append(text(200, 56, "Дротяне з'єднання — контакт виходить на край", size=12, bold=True))
    f.append(rect(60, 200, 290, 34, fill=DARK, stroke=INK, sw=2, rx=0))       # корпус
    f.append(rect(110, 170, 100, 30, fill=DIE, stroke=INK, sw=2, rx=0))        # кристал
    f.append(text(160, 189, "кристал", size=10, color=INK))
    # ніжки по периметру
    for x in (60, 80, 330, 350):
        f.append(rect(x - 6, 234, 12, 22, fill=GOLD, stroke="#806010", sw=1.2, rx=0))
    # дротики
    for x0, xl in ((118, 78), (200, 332)):
        f.append('<path d="M %d,170 Q %.0f,128 %d,206" fill="none" stroke="%s" stroke-width="1.8"/>'
                 % (x0, (x0 + xl) / 2, xl, GOLD))
    f.append(text(200, 282, "дротик → леда → ніжка по краю", size=10.5, color=MUTED))
    f.append(text(200, 300, "до неї (якщо назовні) доходить жало", size=10.5, color=FIELD))
    # --- праворуч: flip-chip у розрізі ---
    f.append(text(560, 56, "Flip-chip — контакт під центром кристала", size=12, bold=True))
    f.append(rect(430, 200, 290, 30, fill="#2f4f6f", stroke=INK, sw=2, rx=0))   # підкладка
    f.append(rect(490, 150, 150, 34, fill=DIE, stroke=INK, sw=2, rx=0))         # кристал
    f.append(text(565, 143, "кристал (лицем униз)", size=10, color=INK))
    for i in range(7):
        f.append(circle(502 + i * 20, 192, 6, fill=SILVER, stroke="#444", sw=1))
    for i in range(8):
        f.append(circle(448 + i * 35, 244, 6, fill=SILVER, stroke="#444", sw=1))  # кульки BGA знизу
    f.append(text(575, 282, "кульки сховані під кристалом", size=10.5, color=MUTED))
    f.append(text(575, 300, "жалу нема куди — лише прогрів усього корпусу",
                  size=10.5, color=POS))
    f.append(text(W / 2, 326, "Дротяна гілка лишає контакт на краю (DIP/SOIC/QFN), flip-chip ховає його під низ (BGA).",
                  size=11, color=MUTED, italic=True))
    out("bond-cross-section.svg", W, H, f, title="Звідки беруться ніжки — у розрізі")


# ── 6. (вставка) QFN на столі: маршрут і пастка теплового поля ──────────────
def fig_qfn_soldering():
    W, H = 760, 320
    f = []
    steps = [
        (150, "1. Флюс і ключ", ["щедро флюсу на", "майданчики; кут-ключ", "(скіс) = вивід 1"], FIELD),
        (380, "2. Протягування", ["крапля жала вздовж", "ряду, надлишок —", "мідним обплетенням"], NEG),
        (610, "3. Теплове поле", ["велике поле під низом", "без via в платі", "знизу не прогріти"], POS),
    ]
    for cx, head, sub, accent in steps:
        x, y, bw, bh = cx - 105, 80, 210, 140
        f.append(rect(x, y, bw, bh, fill=FILL, stroke=accent, sw=2.2, rx=12))
        f.append(text(cx, y + 28, head, size=13, bold=True, color=accent))
        f.append(line(x + 16, y + 40, x + bw - 16, y + 40, color=accent, sw=1.2))
        f.append(mtext(cx, y + 64, sub, size=11.5, color=INK, lh=1.3))
    f.append(arrow(255, 150, 275, 150, color=INK, sw=2))
    f.append(arrow(485, 150, 505, 150, color=INK, sw=2))
    f.append(text(W / 2, 262, "QFN реально посадити на столі: головна пастка — теплове поле під центром,",
                  size=11.5, color=MUTED, italic=True))
    f.append(text(W / 2, 280, "яке без перехідних отворів (via) знизу прогріти майже неможливо.",
                  size=11.5, color=MUTED, italic=True))
    f.append(text(W / 2, 300, "BGA цей маршрут уже не бере — контакт під центром, лише повний розплав корпусу.",
                  size=11.5, color=POS, italic=True))
    out("qfn-soldering.svg", W, H, f, title="QFN на столі: маршрут і пастка")


if __name__ == "__main__":
    fig_why_package()
    fig_wirebond_flip()
    fig_qfn_bga()
    fig_package_family()
    fig_bond_cross_section()
    fig_qfn_soldering()
    print("OK: 6 SVG у", IMG)
