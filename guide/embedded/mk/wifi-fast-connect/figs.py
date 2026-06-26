# -*- coding: utf-8 -*-
"""Фігури до теми «Швидке підключення Wi-Fi: кешування PMK і IP».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Куди йдуть секунди: бюджет часу холодного й кешованого підключення ────────
def fig_time_budget():
    W, H = 780, 430
    f = [text(W / 2, 28,
              "Куди йдуть секунди: три фази підключення, ширина — час",
              size=15, bold=True)]

    ox = 150          # ліво смуг
    span = 560        # повна ширина = найдовший рядок (холодний)
    bar_h = 54

    # фази холодного підключення: (підпис, частка, колір)
    # пошук ~0.3, рукостискання+PBKDF2 ~0.9, DHCP ~0.5 (умовні частки для наочності)
    cold = [("пошук AP", 0.20, FIELD),
            ("рукостискання + PMK", 0.55, POS),
            ("DHCP", 0.25, NEG)]
    # кешоване: пошук за каналом-підказкою, PMK з кешу, IP з кешу — лишається тонка смужка
    warm = [("канал", 0.06, FIELD),
            ("PMKSA", 0.10, POS),
            ("IP", 0.05, NEG)]

    def draw_bar(y, segs, label):
        f.append(text(ox - 14, y + bar_h / 2 + 5, label, size=12.5,
                      bold=True, anchor="end"))
        x = ox
        for name, frac, col in segs:
            w = span * frac
            f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" '
                     'fill="%s" fill-opacity="0.30" stroke="%s" stroke-width="1.6"/>'
                     % (x, y, w, bar_h, col, col))
            if w > 46:
                f.append(text(x + w / 2, y + bar_h / 2 + 5, name, size=11.5,
                              bold=True, color=INK))
            x += w
        return x   # правий край

    y1 = 80
    end_cold = draw_bar(y1, cold, "холодне")
    # шкала часу під холодним
    f.append(line(ox, y1 + bar_h + 10, end_cold, y1 + bar_h + 10, color=MUTED, sw=1.2))
    f.append(text((ox + end_cold) / 2, y1 + bar_h + 28,
                  "≈ кілька секунд", size=11.5, color=MUTED))

    y2 = 200
    end_warm = draw_bar(y2, warm, "кешоване")
    f.append(line(ox, y2 + bar_h + 10, end_warm, y2 + bar_h + 10, color=MUTED, sw=1.2))
    f.append(text(end_warm + 8, y2 + bar_h / 2 + 5,
                  "← усе з пам'яті", size=11.5, bold=True, color=FIELD, anchor="start"))

    # вертикалі-орієнтири від кінця кешованого
    f.append(line(end_warm, y1, end_warm, y2 + bar_h, color=MUTED, sw=1.0, dash="4,4"))

    b, _, _ = textbox(W / 2, 366,
                      "Холодне: повний пошук, виведення PMK, повний DHCP.\nКешоване зрізає кожну фазу — лишається перевірка, а не побудова з нуля",
                      size=11.5, fill="#f4f6f8", stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "time-budget.svg"), W, H, *f)


# ── 4-стороннє рукостискання: що рахуємо щоразу і що бере PMKSA з кешу ─────────
def fig_handshake():
    W, H = 780, 470
    f = [text(W / 2, 28,
              "Рукостискання WPA2: дороге виведення PMK проти готового з кешу",
              size=15, bold=True)]

    # дві колони акторів
    sx, ax = 150, 600
    top, bot = 150, 380
    f.append(line(sx, top, sx, bot, color=MUTED, sw=1.4))
    f.append(line(ax, top, ax, bot, color=MUTED, sw=1.4))
    b1, _, _ = textbox(sx, top - 22, "Станція (ESP32)", size=12, bold=True,
                       fill="#eaf0fd", stroke=NEG)
    b2, _, _ = textbox(ax, top - 22, "Точка доступу", size=12, bold=True,
                       fill="#eaf0fd", stroke=NEG)
    f.append(b1); f.append(b2)

    # дороге виведення PMK — зліва над лінією станції
    bp, _, _ = textbox(sx - 6, 100,
                       "PMK = PBKDF2(пароль, SSID, 4096×)\n— сотні мс рахунку",
                       size=10.5, fill="#fdecea", stroke=POS, color=POS, bold=True)
    f.append(bp)
    # перекреслення «з кешу» — праворуч від блоку PMK
    f.append(text(sx + 165, 96, "з кешу: пропускаємо", size=10.5, bold=True,
                  color=FIELD, anchor="start"))
    f.append(line(sx + 158, 100, sx + 300, 100, color=FIELD, sw=1.4, dash="5,3"))

    # чотири повідомлення
    msgs = [
        (top + 20,  ax, sx, "1. ANonce  (+ PMKID)"),
        (top + 70,  sx, ax, "2. SNonce + MIC"),
        (top + 120, ax, sx, "3. GTK + MIC (став ключ)"),
        (top + 170, sx, ax, "4. ACK"),
    ]
    for y, x1, x2, lbl in msgs:
        f.append(arrow(x1, y, x2, y, color=INK, sw=1.8))
        midx = (x1 + x2) / 2
        f.append(text(midx, y - 7, lbl, size=11, color=INK))

    # PTK виводиться з PMK — підпис між 1 і 2
    f.append(text(sx + 90, top + 48, "PTK з PMK", size=10, italic=True,
                  color=MUTED, anchor="start"))

    b, _, _ = textbox(W / 2, 426,
                      "PMKID у повідомленні 1 каже точці: «PMK уже маю». Збіг — і обидва беруть готовий PMK;\nчотири кроки лишаються, але важка PBKDF2 не повторюється",
                      size=11, fill="#eafaf1", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "handshake.svg"), W, H, *f)


# ── DHCP: холодний чотиритактний проти INIT-REBOOT (REQUEST/ACK) ──────────────
def fig_dhcp():
    W, H = 780, 430
    f = [text(W / 2, 28,
              "DHCP: повний цикл проти перевірки збереженої адреси",
              size=15, bold=True)]

    def column(px, title, steps, note, col):
        cw = 300
        f.append(text(px + cw / 2, 64, title, size=13, bold=True))
        y = 96
        for i, s in enumerate(steps):
            b = fitbox(px + 30, y, cw - 60, 40, s, size=11.5,
                       fill="#f4f6f8", stroke=col)
            f.append(b)
            if i < len(steps) - 1:
                f.append(arrow(px + cw / 2, y + 40, px + cw / 2, y + 56,
                               color=col, sw=1.7))
            y += 56
        f.append(text(px + cw / 2, y + 8, note, size=11, italic=True,
                      color=MUTED))

    column(40, "холодний старт",
           ["DISCOVER  (хто роздає?)",
            "OFFER  (ось адреса)",
            "REQUEST  (беру її)",
            "ACK  (твоя)"],
           "чотири такти, два широкомовні", NEG)

    column(440, "INIT-REBOOT (адреса в кеші)",
           ["REQUEST  (підтвердь 192.168.1.42)",
            "ACK  (твоя)"],
           "два такти; NAK → впасти на повний цикл", FIELD)

    b, _, _ = textbox(W / 2, 386,
                      "Маючи торішню адресу, клієнт одразу шле REQUEST з нею (server-id порожній, ciaddr 0).\nСервер підтверджує — або шле NAK, і тоді повний цикл",
                      size=11, fill="#f4f6f8", stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "dhcp-flow.svg"), W, H, *f)


# ── Машина станів прошивки: холодний шлях зберігає, теплий відновлює й відкочується ─
def fig_state_machine():
    W, H = 860, 620
    f = [text(W / 2, 28,
              "Шлях прошивки: холодний старт записує, теплий пробує кеш і відкочується",
              size=15, bold=True)]

    def node(cx, cy, s, col, fill, w=200, h=52):
        f.append(fitbox(cx - w / 2, cy - h / 2, w, h, s, size=11.5,
                        fill=fill, stroke=col, bold=True))
        return (cx, cy, w, h)

    cold_x, warm_x = 215, 645

    # старт + розгалуження
    node(W / 2, 64, "Старт: читаємо blob з NVS", MUTED, "#f4f6f8", 280)
    f.append(arrow(W / 2, 90, W / 2, 120, color=INK))
    node(W / 2, 148, "blob valid?", INK, "#fff8e1", 150)

    # ── теплий шлях (праворуч, «так») ──
    f.append(arrow(W / 2 + 75, 148, warm_x - 110, 148, color=FIELD))
    f.append(text((W / 2 + 75 + warm_x - 110) / 2, 140, "так", size=11, bold=True, color=FIELD))
    node(warm_x, 148, "channel=N з кешу\nstatic IP / RESTORE_LAST", FIELD, "#eafaf1", 220)
    f.append(arrow(warm_x, 174, warm_x, 222, color=FIELD))
    node(warm_x, 248, "got IP?", INK, "#fff8e1", 130)
    f.append(arrow(warm_x, 274, warm_x, 330, color=FIELD))
    f.append(text(warm_x + 12, 304, "так", size=11, bold=True, color=FIELD, anchor="start"))
    node(warm_x, 356, "працюємо\n(канал/PMK/IP влучили)", FIELD, "#eafaf1", 230)

    # ── холодний шлях (ліворуч, «ні») ──
    f.append(arrow(W / 2 - 75, 148, cold_x + 95, 148, color=NEG))
    f.append(text((W / 2 - 75 + cold_x + 95) / 2, 140, "ні", size=11, bold=True, color=NEG))
    node(cold_x, 148, "channel=0\nповний пошук", NEG, "#eaf0fd", 180)
    f.append(arrow(cold_x, 174, cold_x, 222, color=NEG))
    node(cold_x, 248, "повний handshake\n+ DHCP DISCOVER", NEG, "#eaf0fd", 200)
    f.append(arrow(cold_x, 274, cold_x, 330, color=NEG))
    node(cold_x, 356, "got IP →\nзберегти blob у NVS", FIELD, "#eafaf1", 210)

    # ── відкат: «got IP?» = ні → вниз, ліворуч попід рядом, ліве плече вгору, у верх «channel=0» ──
    rb_y = 416   # рівень нижче третього ряду вузлів
    lb_x = 95    # ліве плече — лівіше за всі холодні вузли (їх лівий край ~110)
    f.append(line(warm_x, 274, warm_x, rb_y, color=POS, sw=1.8))          # вниз від got IP?
    f.append(line(warm_x, rb_y, lb_x, rb_y, color=POS, sw=1.8))           # вліво попід рядом
    f.append(line(lb_x, rb_y, lb_x, 122, color=POS, sw=1.8))              # вгору лівим плечем
    f.append(arrow(lb_x, 122, cold_x - 90, 122, color=POS))               # вправо у верх «channel=0»
    f.append(text(warm_x + 14, 300, "ні", size=11, bold=True, color=POS, anchor="start"))
    bb, _, _ = textbox((lb_x + warm_x) / 2, rb_y,
                       "ні: NO_AP_FOUND (канал змінився) або DHCP NAK → повтор із channel=0",
                       size=10.5, fill="#fdecea", stroke=POS, color=POS, bold=True)
    f.append(bb)

    # ── пастка зі зривом стека — окрема рамка внизу ──
    b, _, _ = textbox(W / 2, 528,
                      "ПАСТКА: esp_wifi_deinit() між сеансами вбиває PMKSA-кеш у RAM.\n"
                      "Канал та IP переживуть (вони в NVS), а живий PMK — НІ: handshake знову платить повну PBKDF2.\n"
                      "Хочеш зберегти PMK — не зривай стек: modem-sleep / light-sleep замість deinit.",
                      size=11, fill="#fdecea", stroke=POS, color=INK)
    f.append(b)
    render(os.path.join(IMG, "state-machine.svg"), W, H, *f)


# ── ВСТАВКА hist: родовід механізмів швидкого захищеного роумінгу ─────────────
def fig_roaming_timeline():
    W, H = 820, 470
    f = [text(W / 2, 28,
              "Родовід швидкого захищеного роумінгу: одна біда, чотири відповіді",
              size=15, bold=True)]

    # вісь років
    ax_y = 250
    x0, x1 = 80, 740
    f.append(line(x0, ax_y, x1, ax_y, color=MUTED, sw=2.0))
    for yr, px in (("2004", 235), ("~сер. 2000-х", 470), ("2008", 660)):
        f.append(line(px, ax_y - 6, px, ax_y + 6, color=MUTED, sw=1.6))
        f.append(text(px, ax_y + 24, yr, size=11.5, bold=True, color=MUTED))

    # 802.11i (2004) — над віссю, з двома дітьми
    bi = fitbox(235 - 115, 70, 230, 46,
                "IEEE 802.11i (24.06.2004)\n= WPA2 / RSN", size=12,
                fill="#eaf0fd", stroke=NEG, bold=True)
    f.append(bi)
    f.append(arrow(235, 116, 235, ax_y - 8, color=NEG))
    # двоє стандартних дітей під «гілкою»
    c1 = fitbox(60, 150, 175, 40, "кешування PMK\n(повернення)", size=10.5,
                fill="#eafaf1", stroke=FIELD, bold=True)
    c2 = fitbox(248, 150, 175, 40, "передплата\n(нова точка)", size=10.5,
                fill="#f4f6f8", stroke=MUTED, bold=True)
    f.append(c1); f.append(c2)
    f.append(line(235, 130, 147, 150, color=MUTED, sw=1.2))
    f.append(line(235, 130, 335, 150, color=MUTED, sw=1.2))

    # OKC — вендорний, нестандартний (між 2004 і 2008), нижче осі
    bo = fitbox(470 - 110, ax_y + 48, 220, 46,
                "OKC (вендорний, поза стандартом)\nключ роздає контролер", size=10.5,
                fill="#fff8e1", stroke=POS, bold=True)
    f.append(bo)
    f.append(arrow(470, ax_y + 8, 470, ax_y + 48, color=POS))

    # 802.11r (2008) — над віссю
    br = fitbox(660 - 110, 70, 220, 46,
                "IEEE 802.11r (15.07.2008)\nFast BSS Transition (FT)", size=11,
                fill="#eaf0fd", stroke=NEG, bold=True)
    f.append(br)
    f.append(arrow(660, 116, 660, ax_y - 8, color=NEG))

    # побічний дарунок — виноска від «кешування PMK» вниз
    f.append(line(147, 190, 147, 366, color=FIELD, sw=1.4, dash="4,4"))
    bg, _, _ = textbox(W / 2, 392,
                       "Побічний дарунок: правило «упізнай станцію з відомим PMK і пропусти важке»\n"
                       "не питає, ЧОМУ станція зникала — через роумінг чи через сон.\n"
                       "Тож пристрій на батарейці отримує прискорення, якого ніхто не проєктував",
                       size=11, fill="#eafaf1", stroke=FIELD)
    f.append(bg)
    render(os.path.join(IMG, "roaming-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_time_budget()
    fig_handshake()
    fig_dhcp()
    fig_state_machine()
    fig_roaming_timeline()
    print("OK: 5 figures ->", IMG)
