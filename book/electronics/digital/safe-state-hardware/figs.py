# -*- coding: utf-8 -*-
"""Фігури до теми «Апаратне забезпечення безпечного стану».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

SAFE = "#e8f6ec"   # заливка «безпечно»
DANGER = "#fdecea"  # заливка «небезпечно»


# ── 1. Хто задає стан: софт проти заліза ────────────────────────────────────
def fig_who_decides():
    W, H = 720, 340
    els = []
    # ліва панель — надія лише на софт
    els.append(fitbox(30, 60, 300, 40, "Надія лише на софт", size=15, bold=True,
                      fill="#eef1f4", stroke=MUTED))
    # CPU завис
    els.append(rect(90, 120, 180, 60, fill=DANGER, stroke=POS, sw=2))
    els.append(text(180, 145, "процесор", size=13, bold=True))
    els.append(text(180, 165, "завис / просів", size=12, color=POS))
    els.append(arrow(180, 180, 180, 225, color=MUTED, sw=2))
    els.append(text(210, 208, "?", size=22, bold=True, color=POS))
    b, w, h = textbox(180, 250, "вихід у ПОВІТРІ\n(невідомий рівень)", size=12,
                      fill=DANGER, stroke=POS, color=POS)
    els.append(b)
    els.append(text(180, 300, "мотор може лишитись УВІМКНЕНИМ", size=11, color=POS, bold=True))

    # роздільник
    els.append(line(360, 50, 360, 315, color=MUTED, sw=1, dash="4,4"))

    # права панель — заліза тримає стан
    els.append(fitbox(390, 60, 300, 40, "Залізо тримає стан", size=15, bold=True,
                      fill=SAFE, stroke=FIELD))
    els.append(rect(450, 120, 180, 60, fill=DANGER, stroke=POS, sw=2))
    els.append(text(540, 145, "процесор", size=13, bold=True))
    els.append(text(540, 165, "завис / просів", size=12, color=POS))
    els.append(arrow(540, 180, 540, 225, color=FIELD, sw=2))
    # підтяжка збоку
    els.append(text(605, 208, "↓ підтяжка", size=11, color=FIELD))
    b, w, h = textbox(540, 250, "вивід сам паде\nу безпечний рівень", size=12,
                      fill=SAFE, stroke=FIELD, color="#1e6b3a")
    els.append(b)
    els.append(text(540, 300, "мотор ГАРАНТОВАНО вимкнено", size=11, color="#1e6b3a", bold=True))

    render(os.path.join(IMG, 'who-decides.svg'), W, H, *els,
           title="Хто задає рівень на виводі, коли процесора «нема»")


# ── 2. Знеструмлення-в-стоп проти живлення-в-стоп ───────────────────────────
def fig_dtt_vs_ett():
    W, H = 720, 360
    els = []

    def panel(x, title, coil_txt, ok_line, fault_line, good, note):
        out = []
        fill = SAFE if good else "#fff6e6"
        stroke = FIELD if good else "#c9922b"
        out.append(fitbox(x, 55, 300, 38, title, size=14, bold=True, fill=fill, stroke=stroke))
        # котушка + контакт (спрощене реле)
        out.append(rect(x + 30, 120, 90, 50, fill="#eef1f4", stroke=LINE))
        out.append(text(x + 75, 150, coil_txt, size=12, bold=True))
        out.append(text(x + 150, 130, "→", size=18, color=INK))
        # навантаження
        out.append(circle(x + 220, 145, 26, fill=FILL, stroke=LINE, sw=1.8))
        out.append(text(x + 220, 150, "M", size=15, bold=True))
        # нормальна робота
        out.append(text(x + 150, 210, ok_line, size=11, color=MUTED, anchor="middle"))
        # зникло живлення
        b, w, h = textbox(x + 150, 255, "живлення зникло →", size=12, fill="#eef1f4", stroke=MUTED)
        out.append(b)
        out.append(text(x + 150, 300, fault_line, size=13, bold=True,
                        color="#1e6b3a" if good else "#c0392b"))
        out.append(text(x + 150, 328, note, size=10, color=MUTED))
        return out

    els += panel(30, "Знеструмлення-в-стоп (DTT)", "котушка\nпід струмом",
                 "струм тримає мотор увімкненим", "мотор САМ вимкнувся", True,
                 "втрата живлення = безпечний стан «задарма»")
    els.append(line(360, 50, 360, 340, color=MUTED, sw=1, dash="4,4"))
    els += panel(390, "Живлення-в-стоп (ETT)", "котушка\nбез струму",
                 "щоб СТОП — треба ще подати струм", "стоп НЕ спрацював", False,
                 "втрата живлення = стоп не настане")

    render(os.path.join(IMG, 'dtt-vs-ett.svg'), W, H, *els,
           title="Куди падає система, коли зникає живлення")


# ── 3. Три опори безпечного стану в залізі ──────────────────────────────────
def fig_three_pillars():
    W, H = 740, 320
    els = []
    cols = [
        (40, "Підтяжка на вводах/виводах",
         ["резистор тягне лінію", "у визначений рівень,", "поки драйвера нема"],
         "reset/зависання → лінія не «плаває»"),
        (280, "Вимкнення драйвера (Hi-Z→стоп)",
         ["на скиді вивід", "відпускається, а зовні", "підтяжка веде у стоп"],
         "мотор/реле знеструмлюється саме"),
        (520, "Watchdog + дефолт скиду",
         ["зависання → скид,", "після скиду виводи —", "у безпечнім дефолті"],
         "оживлення завжди через безпечний старт"),
    ]
    for x, title, body, foot in cols:
        els.append(fitbox(x, 55, 200, 46, title, size=12, bold=True, fill=SAFE, stroke=FIELD))
        els.append(rect(x, 120, 200, 110, fill=FILL, stroke=LINE))
        els.append(mtext(x + 100, 150, body, size=12, color=INK))
        els.append(text(x + 100, 258, "▼", size=13, color=FIELD))
        els.append(mtext(x + 100, 285, foot, size=10, color="#1e6b3a"))

    render(os.path.join(IMG, 'three-pillars.svg'), W, H, *els,
           title="Три опори, на яких залізо тримає безпечний стан")


# ── 4. Історія: чому «нема струму» = «стій» (для hist-вставки) ───────────────
def fig_deenergize_to_safe():
    W, H = 740, 380
    els = []

    els.append(fitbox(40, 52, 300, 34, "Семафор на дроті (1876)", size=14, bold=True,
                      fill="#eef1f4", stroke=MUTED))
    els.append(fitbox(400, 52, 300, 34, "Vital-реле (закрите коло)", size=14, bold=True,
                      fill="#eef1f4", stroke=MUTED))
    els.append(line(370, 46, 370, 360, color=MUTED, sw=1, dash="4,4"))

    # ліва панель: вантаж повертає арм у «стій»
    els.append(rect(120, 110, 12, 200, fill="#d9d2c7", stroke=LINE, sw=1))
    els.append(line(132, 130, 250, 130, color=POS, sw=7))
    els.append(circle(132, 130, 6, fill="#fff", stroke=LINE, sw=1.5))
    els.append(text(250, 122, "СТІЙ", size=12, bold=True, color=POS))
    els.append(circle(150, 300, 12, fill="#555", stroke=LINE, sw=1.5))
    els.append(text(150, 305, "W", size=11, bold=True, color="#fff"))
    els.append(arrow(150, 288, 150, 250, color=FIELD, sw=2))
    els.append(text(196, 268, "тяжіння →", size=11, color=FIELD))
    els.append(text(196, 284, "у «стій»", size=11, color=FIELD))
    b, w, h = textbox(210, 340, "дріт обірвано / нема сили →\nарм САМ падає у «стій»", size=11,
                      fill=SAFE, stroke=FIELD, color="#1e6b3a")
    els.append(b)

    # права панель: котушка тримає «дозвіл»
    els.append(rect(430, 120, 96, 54, fill="#eef1f4", stroke=LINE))
    els.append(text(478, 143, "котушка", size=12, bold=True))
    els.append(text(478, 162, "під струмом", size=11, color=FIELD))
    els.append(arrow(560, 150, 610, 150, color=INK, sw=1.8))
    els.append(text(585, 138, "дозвіл", size=11, color=INK))
    els.append(text(585, 168, "«їдь»", size=11, color=INK))
    els.append(arrow(478, 176, 478, 214, color=POS, sw=2))
    els.append(text(478, 200, "струм зник", size=11, color=POS, anchor="middle"))
    b, w, h = textbox(560, 300, "якір падає (тяжіння/пружина) →\nпередній контакт РОЗМИКАЄТЬСЯ →\nнайобмежувальніший стан", size=11,
                      fill=SAFE, stroke=FIELD, color="#1e6b3a")
    els.append(b)

    els.append(text(W / 2, 372, "спільне: відсутність енергії = найбезпечніший стан, а не випадковий",
                    size=11, color=MUTED, bold=True))

    render(os.path.join(IMG, 'deenergize-to-safe.svg'), W, H, *els,
           title="Чому «нема струму» мусить означати «стій»")


if __name__ == '__main__':
    fig_who_decides()
    fig_dtt_vs_ett()
    fig_three_pillars()
    fig_deenergize_to_safe()
    print("OK: 4 figures ->", IMG)
