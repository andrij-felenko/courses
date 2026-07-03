# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def softap_flow():
    # Хореографія SoftAP-провізіонування як стрічка кроків зліва направо:
    # пристрій піднімає AP → телефон під'єднується → перевірка зв'язку через
    # DNS-пастку впирається в пристрій → вискакує форма → введено дані →
    # пристрій гасить AP і йде в домашню мережу як станція.
    W, H = 760, 470
    p = []

    dev_x = 150         # колонка «пристрій»
    ph_x = W - 150      # колонка «телефон»
    rows = [92, 176, 260, 344]   # рівні кроків

    # заголовки колонок
    p.append(circle(dev_x, 54, 22, fill="#eafaf0", stroke=FIELD, sw=2.5))
    p.append(text(dev_x, 58, "ПЛ", size=12, color=FIELD, bold=True))
    p.append(text(dev_x, 90 - 4, "пристрій", size=12, color=FIELD, bold=True))
    p.append(circle(ph_x, 54, 22, fill="#eaf0fd", stroke=NEG, sw=2.5))
    p.append(text(ph_x, 58, "☎", size=15, color=NEG))
    p.append(text(ph_x, 90 - 4, "телефон", size=12, color=NEG, bold=True))

    # вертикальні «доріжки життя»
    p.append(line(dev_x, 78, dev_x, 396, color=FIELD, sw=1, dash="2 5"))
    p.append(line(ph_x, 78, ph_x, 396, color=NEG, sw=1, dash="2 5"))

    def step_label(y, s, col):
        b, bw, bh = textbox((dev_x + ph_x) / 2, y, s, size=12, bold=True,
                            fill="#ffffff", stroke=col, color=col, min_w=150, pad=8)
        return b

    # 1) пристрій піднімає AP
    y = rows[0]
    p.append(arrow(dev_x + 24, y, (dev_x + ph_x) / 2 - 96, y, color=FIELD, sw=1.8))
    p.append(step_label(y, "1 · AP «Thermostat-A3F2»", FIELD))
    p.append(text((dev_x + ph_x) / 2, y - 26, "піднято без жодної зовнішньої мережі",
                  size=11, color=MUTED))

    # 2) телефон під'єднується до AP пристрою
    y = rows[1]
    p.append(arrow(ph_x - 24, y, (dev_x + ph_x) / 2 + 96, y, color=NEG, sw=1.8))
    p.append(step_label(y, "2 · телефон під'єднався", NEG))

    # 3) перевірка зв'язку → DNS-пастка → впирається в пристрій
    y = rows[2]
    # стрілку СПИНЯЄМО біля рамки-підпису (як у кроках 1–2), щоб не різати напис
    p.append(arrow(ph_x - 24, y, (dev_x + ph_x) / 2 + 96, y, color=POS, sw=1.8))
    p.append(step_label(y, "3 · перевірка зв'язку → DNS-пастка", POS))
    p.append(text((dev_x + ph_x) / 2, y + 24,
                  "будь-яке ім'я → 192.168.4.1 (сам пристрій)",
                  size=11, color=MUTED))

    # 4) вискакує форма і користувач вводить дані домашньої мережі
    y = rows[3]
    p.append(arrow(dev_x + 24, y, (dev_x + ph_x) / 2 - 96, y, color=FIELD, sw=1.8))
    p.append(step_label(y, "4 · форма вискакує → SSID + пароль", FIELD))

    # фінал: пристрій гасить AP і йде в домашню мережу як станція
    fy = 424
    p.append(fitbox(dev_x - 92, fy - 20, 184, 40,
                    "AP згас · пристрій → станція\nу домашній мережі", size=12,
                    fill="#eafaf0", stroke=FIELD, bold=True))
    p.append(fitbox(ph_x - 92, fy - 20, 184, 40,
                    "телефон вертається\nв домашній Wi-Fi", size=12,
                    fill="#eaf0fd", stroke=NEG))

    # домашній роутер угорі-центр як ціль
    p.append(text((dev_x + ph_x) / 2, fy - 2, "🏠", size=20))
    p.append(arrow(dev_x + 60, fy + 4, (dev_x + ph_x) / 2 - 14, fy + 2, color=FIELD, sw=1.6))

    render(os.path.join(IMG, 'softap-flow.svg'), W, H, *p,
           title="SoftAP: як пароль долітає в пристрій без клавіатури")


def softap_vs_ble():
    # Два канали провізіонування пліч-о-пліч. Ліворуч SoftAP: телефон
    # ПЕРЕСКАКУЄ з домашньої мережі на мережу пристрою (розрив інтернету),
    # зате голий браузер. Праворуч BLE: телефон ЛИШАЄТЬСЯ в домашньому Wi-Fi,
    # окреме радіо веде розмову, але потрібен фірмовий застосунок.
    W, H = 760, 450
    p = []
    colL = 205
    colR = 555
    p.append(line(W / 2, 60, W / 2, H - 20, color="#d9d9d9", sw=1))

    # ---- Заголовки ----
    p.append(fitbox(colL - 130, 56, 260, 34, "SoftAP  (Wi-Fi)", size=16,
                    fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))
    p.append(fitbox(colR - 130, 56, 260, 34, "BLE  (Bluetooth LE)", size=16,
                    fill="#eaf0fd", stroke=NEG, color=NEG, bold=True))

    # ---- Ліва колонка: SoftAP ----
    ph_y = 150
    p.append(text(colL, ph_y, "☎", size=26, color=INK))
    # підпис НАД слухавкою — стрілка «перескоку» відходить донизу, тож напису не торкається
    p.append(text(colL, ph_y - 22, "телефон", size=11, color=MUTED))

    # телефон перескакує з дому на мережу пристрою
    home_x = colL - 92
    dev_x = colL + 92
    hy = 240
    p.append(circle(home_x, hy, 30, fill="#f4f6f8", stroke=MUTED, sw=1.6))
    p.append(mtext(home_x, hy - 2, ["дім", "Wi-Fi"], size=11, color=MUTED, bold=True))
    p.append(circle(dev_x, hy, 30, fill="#eafaf0", stroke=FIELD, sw=2.2))
    p.append(mtext(dev_x, hy - 2, ["AP", "пристрою"], size=11, color=FIELD, bold=True))
    # стрілка «перескок»
    p.append(arrow(colL - 18, ph_y + 14, dev_x - 6, hy - 26, color=FIELD, sw=1.8))
    # перекреслений зв'язок телефон↔дім (розрив інтернету)
    p.append(line(colL - 20, ph_y + 14, home_x + 8, hy - 22, color=POS, sw=1.6, dash="4 4"))
    xm = ((colL - 20) + (home_x + 8)) / 2
    ym = ((ph_y + 14) + (hy - 22)) / 2
    p.append(line(xm - 8, ym - 8, xm + 8, ym + 8, color=POS, sw=2.4))
    p.append(line(xm - 8, ym + 8, xm + 8, ym - 8, color=POS, sw=2.4))
    p.append(text(colL, hy + 54, "телефон ПЕРЕСКАКУЄ на мережу пристрою",
                  size=11, color=POS, bold=True))
    p.append(text(colL, hy + 70, "→ інтернет на телефоні на мить зникає",
                  size=11, color=MUTED))

    p.append(fitbox(colL - 132, 356, 264, 34, "✓ вистачає будь-якого браузера",
                    size=12, fill="#ffffff", stroke=FIELD, color=FIELD, bold=True))
    p.append(fitbox(colL - 132, 398, 264, 34, "✗ розрив зв'язку · іноді не вертає Wi-Fi",
                    size=12, fill="#ffffff", stroke=POS, color=POS))

    # ---- Права колонка: BLE ----
    p.append(text(colR, ph_y, "☎", size=26, color=INK))
    p.append(text(colR, ph_y - 22, "телефон", size=11, color=MUTED))

    home_xr = colR - 92
    dev_xr = colR + 92
    p.append(circle(home_xr, hy, 30, fill="#eaf0fd", stroke=NEG, sw=2.2))
    p.append(mtext(home_xr, hy - 2, ["дім", "Wi-Fi"], size=11, color=NEG, bold=True))
    p.append(circle(dev_xr, hy, 30, fill="#eafaf0", stroke=FIELD, sw=2.2))
    p.append(mtext(dev_xr, hy - 2, ["пристрій", "BLE"], size=11, color=FIELD, bold=True))
    # телефон тримає дім (суцільна) і паралельно говорить BLE (окреме радіо)
    p.append(line(colR - 18, ph_y + 14, home_xr + 6, hy - 24, color=NEG, sw=2))
    # підпис ВБІК (над лінією), щоб суцільна лінія «тримає» його не перетинала
    p.append(text((colR + home_xr) / 2 - 12, (ph_y + hy) / 2 - 14, "тримає",
                  size=10, color=NEG, anchor="middle"))
    p.append(arrow(colR + 18, ph_y + 14, dev_xr - 6, hy - 24, color=FIELD, sw=1.8))
    p.append(text((colR + dev_xr) / 2 + 8, (ph_y + hy) / 2 - 6, "BLE",
                  size=10, color=FIELD, anchor="middle"))
    p.append(text(colR, hy + 54, "телефон НЕ покидає домашній Wi-Fi",
                  size=11, color=NEG, bold=True))
    p.append(text(colR, hy + 70, "→ розмова йде окремим радіо, гладко",
                  size=11, color=MUTED))

    p.append(fitbox(colR - 132, 356, 264, 34, "✓ без розриву · рівний досвід",
                    size=12, fill="#ffffff", stroke=FIELD, color=FIELD, bold=True))
    p.append(fitbox(colR - 132, 398, 264, 34, "✗ потрібен фірмовий застосунок",
                    size=12, fill="#ffffff", stroke=POS, color=POS))

    render(os.path.join(IMG, 'softap-vs-ble.svg'), W, H, *p,
           title="Два канали для одного пароля: SoftAP проти BLE")


def wps_pin_split():
    # ЧОМУ восьмицифровий PIN тримається не на 10⁸, а на ~11 000 спроб.
    # Показуємо роздрібнення: 8-й розряд — контрольна сума (не вгадують),
    # перевірка йде ДВОМА половинами окремо → 10⁴ + 10³, а не 10⁷·10.
    W, H = 760, 470
    p = []

    # ── Верх: сам код із восьми клітинок ──
    cx0 = 120
    cell = 62
    gap = 6
    top = 78
    digits = ["d₁", "d₂", "d₃", "d₄", "d₅", "d₆", "d₇", "C"]
    for i, d in enumerate(digits):
        x = cx0 + i * (cell + gap)
        # перші 4 — перша половина (зелена), 5–7 — друга (синя), 8-й — контр.сума (сіра)
        if i < 4:
            fill, st, col = "#eafaf0", FIELD, FIELD
        elif i < 7:
            fill, st, col = "#eaf0fd", NEG, NEG
        else:
            fill, st, col = "#f1f1f4", MUTED, MUTED
        p.append(rect(x, top, cell, cell, fill=fill, stroke=st, sw=2, rx=8))
        p.append(text(x + cell / 2, top + cell / 2 + 9, d, size=24, color=col, bold=True))

    x_full = cx0
    x_last = cx0 + 7 * (cell + gap)
    right = x_last + cell
    mid = (x_full + right) / 2

    # дужки-підписи над половинами
    p.append(text(cx0 + 2 * (cell + gap) - gap / 2, top - 14,
                  "перша половина", size=12, color=FIELD, bold=True))
    p.append(text(cx0 + 5 * (cell + gap) - gap / 2, top - 14,
                  "друга половина", size=12, color=NEG, bold=True))
    p.append(text(x_last + cell / 2, top + cell + 22,
                  "контрольна сума", size=11, color=MUTED))
    p.append(text(x_last + cell / 2, top + cell + 37,
                  "(рахується сама)", size=10, color=MUTED))

    # ── Ліворуч-центр: наївний підрахунок (перекреслений) ──
    ny = 250
    b, bw, bh = textbox(215, ny, "Наївно: 8 незалежних цифр\n10⁸ = 100 000 000 кодів",
                        size=13, bold=True, fill="#ffffff", stroke=MUTED,
                        color=MUTED, min_w=250, pad=10)
    p.append(b)
    # позначка «хибно» — червоне ✗ у кутку рамки, БЕЗ лінії крізь напис
    p.append(circle(215 + bw / 2 - 4, ny - bh / 2 + 4, 13, fill="#fff4f0", stroke=POS, sw=2))
    p.append(text(215 + bw / 2 - 4, ny - bh / 2 + 9, "✗", size=16, color=POS, bold=True))

    # стрілка «насправді»
    p.append(arrow(215, ny + bh / 2 + 4, 215, ny + bh / 2 + 30, color=POS, sw=2))
    p.append(text(248, ny + bh / 2 + 22, "а перевірка йде половинами →",
                  size=12, color=POS, bold=True, anchor="start"))

    # ── Праворуч: реальний підрахунок по половинах ──
    ry = 250
    b1, w1, h1 = textbox(560, ry - 34,
                         "1-ша половина окремо:  10⁴ = 10 000",
                         size=13, bold=True, fill="#eafaf0", stroke=FIELD,
                         color=FIELD, min_w=300, pad=9)
    p.append(b1)
    b2, w2, h2 = textbox(560, ry + 6,
                         "2-га половина окремо:  10³ = 1 000",
                         size=13, bold=True, fill="#eaf0fd", stroke=NEG,
                         color=NEG, min_w=300, pad=9)
    p.append(b2)
    p.append(text(560, ry + 50, "(7-ма цифра випливає з контрольної суми)",
                  size=10, color=MUTED))

    # ── Низ: підсумок ──
    fb = fitbox(mid - 250, 372, 500, 66,
                "разом ≤ 10 000 + 1 000 = 11 000 спроб  →  години, не тисячоліття",
                size=16, fill="#fff4f0", stroke=POS, color=POS, bold=True)
    p.append(fb)

    render(os.path.join(IMG, 'wps-pin-split.svg'), W, H, *p,
           title="Чому 8-цифровий PIN ламають за години: перевірка двома половинами")


def provisioning_fsm():
    # Скінченний автомат прошивки: BOOT → розвилка за NVS → або одразу STA,
    # або підняти портал → прийняти дані → СПРОБУВАТИ реальне STA-підключення
    # (окремий стан!) → успіх фіксує в NVS і лишається STA; невдача вертає в
    # портал з повідомленням помилки. Плюс жест скидання довгою кнопкою.
    W, H = 780, 610
    p = []

    def state(cx, cy, w, h, title, sub, col, fillc):
        b = rect(cx - w / 2, cy - h / 2, w, h, fill=fillc, stroke=col, sw=2.2, rx=10)
        if sub:
            b += text(cx, cy - 4, title, size=13, color=col, bold=True)
            b += text(cx, cy + 15, sub, size=10.5, color=MUTED)
        else:
            b += text(cx, cy + 4, title, size=13, color=col, bold=True)
        return b

    boot_y = 66
    forky = 148
    ap_x, ap_y = 250, 250
    rcv_x, rcv_y = 250, 348
    prv_x, prv_y = 250, 452
    con_x, con_y = 588, 452

    # BOOT
    p.append(state(W / 2, boot_y, 210, 44, "BOOT / скидання", "живлення або жест reset",
                   INK, "#f4f6f8"))
    # розвилка-ромб за NVS
    p.append(line(W / 2, boot_y + 22, W / 2, forky - 22, color=INK, sw=1.8))
    d = 26
    p.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f L%.0f %.0f Z" fill="#fff8e6" stroke="%s" stroke-width="2"/>'
             % (W / 2 - d, forky, W / 2, forky - 22, W / 2 + d, forky, W / 2, forky + 22, "#b8860b"))
    p.append(text(W / 2, forky + 40, "у NVS є мережа?", size=11, color="#8a6d0b", bold=True))

    # ГІЛКА «так» → одразу CONNECTED (STA)
    p.append(line(W / 2 + d, forky, con_x, forky, color=FIELD, sw=1.9))
    p.append(text((W / 2 + d + con_x) / 2, forky - 9, "так", size=11, color=FIELD, bold=True))
    p.append(arrow(con_x, forky, con_x, con_y - 34, color=FIELD, sw=1.9))

    # ГІЛКА «ні» → PROVISION_AP
    p.append(line(W / 2 - d, forky, ap_x, forky, color=POS, sw=1.9))
    p.append(text((W / 2 - d + ap_x) / 2, forky - 9, "ні", size=11, color=POS, bold=True))
    p.append(arrow(ap_x, forky, ap_x, ap_y - 32, color=POS, sw=1.9))

    # PROVISION_AP
    p.append(state(ap_x, ap_y, 236, 58, "PROVISION_AP", "AP + DNS-пастка + форма",
                   POS, "#fdecea"))
    # прийшла форма → RECEIVED
    p.append(arrow(ap_x, ap_y + 29, rcv_x, rcv_y - 22, color=INK, sw=1.8))
    p.append(text(ap_x - 96, (ap_y + rcv_y) / 2 + 2, "POST", size=10.5, color=INK, bold=True))

    # RECEIVED
    p.append(state(rcv_x, rcv_y, 236, 44, "RECEIVED", "SSID/пароль прийнято й провалідовано",
                   NEG, "#eaf0fd"))
    p.append(arrow(rcv_x, rcv_y + 22, prv_x, prv_y - 34, color=NEG, sw=1.8))

    # PROVING — серце автомата
    p.append(state(prv_x, prv_y, 256, 68, "", None, "#7a1fb0", "#f3e8ff"))
    p.append(text(prv_x, prv_y - 12, "PROVING  (APSTA)", size=13, color="#7a1fb0", bold=True))
    p.append(text(prv_x, prv_y + 6, "реально під'єднуємось як STA", size=10, color=MUTED))
    p.append(text(prv_x, prv_y + 22, "тайм-аут ~15 с · портал ще живий", size=10, color=MUTED))

    # PROVING → успіх → CONNECTED
    p.append(arrow(prv_x + 128, prv_y - 6, con_x - 106, con_y - 6, color=FIELD, sw=2.2))
    p.append(text((prv_x + con_x) / 2, con_y - 22, "GOT_IP ✓", size=11, color=FIELD, bold=True))
    p.append(mtext((prv_x + con_x) / 2, con_y + 8, ["зберегти в NVS,", "погасити AP"],
                   size=9.5, color=MUTED))

    # PROVING → невдача → назад у PROVISION_AP (петля ліворуч)
    p.append('<path d="M%.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
             % (prv_x - 128, prv_y - 8, 74, prv_y - 44, 74, ap_y + 8, ap_x - 120, ap_y + 4, POS))
    p.append(text(98, (ap_y + prv_y) / 2 + 8, "невдача", size=10.5, color=POS, bold=True))
    p.append(text(98, (ap_y + prv_y) / 2 + 24, "201 / 202", size=9.5, color=MUTED))

    # CONNECTED
    p.append(state(con_x, con_y, 214, 58, "CONNECTED (STA)", "у домашній мережі, AP згас",
                   FIELD, "#eafaf0"))

    # жест reset: CONNECTED → стерти NVS → BOOT (пунктир)
    p.append('<path d="M%.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5 4" marker-end="url(#arrow)"/>'
             % (con_x + 107, con_y - 18, 762, 300, 704, 84, W / 2 + 106, boot_y + 4, "#8a6d0b"))
    p.append(fitbox(566, 542, 208, 40,
                    "довге утримання кнопки\n→ nvs_erase → BOOT", size=10.5,
                    fill="#fff8e6", stroke="#b8860b", color="#8a6d0b", bold=True))

    render(os.path.join(IMG, 'provisioning-fsm.svg'), W, H, *p,
           title="Провізіонування як скінченний автомат прошивки")


# ═══════════════════════════════════════════════════════════════════════════
#  ФІГУРИ ДЕТАЛЬНОЇ ВЕРСІЇ (device-provisioning-d.md)
# ═══════════════════════════════════════════════════════════════════════════

def dns_wire_trap():
    # Байтова анатомія DNS-пастки: запит телефона (QNAME=connectivitycheck…)
    # і наша відповідь, у якій RDATA ЗАВЖДИ 192.168.4.1, хоч що спитали.
    # Показуємо два пакети один під одним як стрічки полів + ключ фокуса.
    W, H = 900, 560
    p = []

    # ── Запит (згори) ──
    qy = 96
    p.append(text(W / 2, 58, "Запит телефона (UDP → порт 53)", size=15, color=NEG, bold=True))
    # поля заголовка + питання; ширини пропорційні змісту
    qfields = [
        ("ID", "0x8f2a", 78, "#eaf0fd", NEG),
        ("Flags", "QUERY", 88, "#eaf0fd", NEG),
        ("QD=1", "AN=0", 78, "#f4f6f8", MUTED),
        ("QNAME", "connectivitycheck.gstatic.com", 320, "#fff8e6", "#8a6d0b"),
        ("QTYPE", "A", 78, "#eaf0fd", NEG),
        ("QCLASS", "IN", 78, "#f4f6f8", MUTED),
    ]
    x = 60
    for name, val, w, fill, col in qfields:
        p.append(rect(x, qy, w, 52, fill=fill, stroke=col, sw=1.8, rx=6))
        p.append(text(x + w / 2, qy + 21, name, size=11, color=col, bold=True))
        p.append(text(x + w / 2, qy + 40, val, size=11, color=INK))
        x += w + 4

    # стрілка вниз ліворуч від рамки: «на будь-яке ім'я — та сама відповідь»
    ax = W / 2 - 250
    p.append(arrow(ax, qy + 60, ax, qy + 128, color=POS, sw=2.4))
    p.append(fitbox(W / 2 - 200, qy + 74, 400, 44,
                    "хоч що стоїть у QNAME — відповідаємо ОДНАКОВО", size=13,
                    fill="#fff4f0", stroke=POS, color=POS, bold=True))

    # ── Відповідь (знизу) ──
    ry = qy + 200
    p.append(text(W / 2, ry - 22, "Відповідь пристрою", size=15, color=FIELD, bold=True))
    afields = [
        ("ID", "0x8f2a", 78, "#f4f6f8", MUTED, "той самий ID"),
        ("Flags", "RESP·AA", 92, "#eafaf0", FIELD, "прапор «відповідь»"),
        ("AN=1", "", 66, "#f4f6f8", MUTED, "1 запис"),
        ("NAME", "→ вказ. на QNAME", 176, "#f4f6f8", MUTED, "стиснено (0xC00C)"),
        ("TYPE", "A", 62, "#eafaf0", FIELD, ""),
        ("TTL", "0", 62, "#eafaf0", FIELD, "не кешуй"),
        ("RDATA", "192.168.4.1", 168, "#fff4f0", POS, "= сам пристрій"),
    ]
    x = 44
    for name, val, w, fill, col, note in afields:
        p.append(rect(x, ry, w, 52, fill=fill, stroke=col, sw=1.8, rx=6))
        p.append(text(x + w / 2, ry + 20, name, size=11, color=col, bold=True))
        if val:
            p.append(text(x + w / 2, ry + 39, val, size=10.5, color=INK))
        if note:
            p.append(text(x + w / 2, ry + 70, note, size=9.5, color=MUTED))
        x += w + 4

    # підсумок унизу (два рядки, щоб не тиснути шрифт)
    p.append(fitbox(W / 2 - 320, ry + 106, 640, 56,
                    "RDATA завжди 192.168.4.1 · TTL=0 (щоб телефон не кешував і перепитував)\n"
                    "→ будь-який стук телефона впирається в наш веб-сервер",
                    size=13, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))

    render(os.path.join(IMG, 'dns-wire-trap.svg'), W, H, *p,
           title="DNS-пастка по байтах: одна адреса на будь-яке ім'я")


def portal_detectors():
    # Три детектори капітивного порталу пліч-о-пліч: Apple CNA, Android 204,
    # Windows NCSI — усі впираються в DNS-пастку, а HTTPS-стіна лишається.
    W, H = 900, 520
    p = []

    cols = [
        (170, "Apple  (iOS/macOS)", NEG, "#eaf0fd",
         "captive.apple.com/", "hotspot-detect.html",
         "чекає слово", "«Success»"),
        (450, "Android", FIELD, "#eafaf0",
         "connectivitycheck.", "gstatic.com/generate_204",
         "чекає код", "204 No Content"),
        (730, "Windows  (NCSI)", "#8a6d0b", "#fff8e6",
         "www.msftconnecttest.", "com/connecttest.txt",
         "чекає текст", "«Microsoft Connect Test»"),
    ]
    # телефон/ОС згори кожної колонки
    for cx, name, col, fill, host, path, waitw, waitv in cols:
        p.append(fitbox(cx - 128, 52, 256, 34, name, size=13,
                        fill=fill, stroke=col, color=col, bold=True))
        # службовий запит
        p.append(fitbox(cx - 128, 100, 256, 46, host + "\n" + path, size=10.5,
                        fill="#ffffff", stroke=MUTED, color=INK))
        p.append(text(cx, 168, waitw, size=10.5, color=MUTED))
        p.append(fitbox(cx - 118, 176, 236, 30, waitv, size=11,
                        fill="#ffffff", stroke=col, color=col, bold=True))
        # стрілка вниз у пастку
        p.append(arrow(cx, 210, cx, 250, color=POS, sw=2))

    # спільна DNS-пастка
    p.append(fitbox(W / 2 - 250, 256, 500, 52,
                    "DNS-пастка пристрою: будь-яке ім'я → 192.168.4.1",
                    size=14, fill="#fff4f0", stroke=POS, color=POS, bold=True))
    p.append(arrow(W / 2, 310, W / 2, 348, color=FIELD, sw=2.2))
    p.append(fitbox(W / 2 - 250, 354, 500, 46,
                    "пристрій замість очікуваного віддає 302 → своя форма\n"
                    "ОС бачить «тут портал» і сама розгортає її на весь екран",
                    size=12, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))

    # HTTPS-стіна збоку
    p.append(rect(60, 440, W - 120, 56, fill="#fdecea", stroke=POS, sw=2, rx=8))
    p.append(text(W / 2, 462, "СТІНА HTTPS", size=13, color=POS, bold=True))
    p.append(text(W / 2, 482,
                  "полізе телефон на https://… — підмінити не вийде: чужий сертифікат ми не підпишемо, "
                  "рукостискання TLS тихо впаде",
                  size=11, color=INK))

    render(os.path.join(IMG, 'portal-detectors.svg'), W, H, *p,
           title="Три детектори порталу — одна пастка, одна стіна")


def x25519_handshake():
    # Рукостискання X25519 з уплетеним доказом володіння (PoP): що бачить
    # підслуховувач (публічні ключі — шум) vs що лишається таємним (спільний
    # секрет + PoP). Дві доріжки-життя (телефон / пристрій) + канал ефіру.
    W, H = 900, 620
    p = []
    ph_x = 190          # телефон
    dev_x = W - 190     # пристрій
    top = 92

    p.append(circle(ph_x, 58, 24, fill="#eaf0fd", stroke=NEG, sw=2.4))
    p.append(text(ph_x, 63, "☎", size=17, color=NEG))
    p.append(text(ph_x, 96, "телефон (застосунок)", size=12, color=NEG, bold=True))
    p.append(circle(dev_x, 58, 24, fill="#eafaf0", stroke=FIELD, sw=2.4))
    p.append(text(dev_x, 62, "ПЛ", size=12, color=FIELD, bold=True))
    p.append(text(dev_x, 96, "пристрій", size=12, color=FIELD, bold=True))

    p.append(line(ph_x, 108, ph_x, 560, color=NEG, sw=1, dash="2 6"))
    p.append(line(dev_x, 108, dev_x, 560, color=FIELD, sw=1, dash="2 6"))

    # смуга «ефір» посередині — те, що чути всім
    ear_x = W / 2
    p.append(text(ear_x, 122, "◂ що чути в ефірі ▸", size=11, color=POS, bold=True))

    def msg(y, x1, x2, label, col):
        p.append(arrow(x1, y, x2, y, color=col, sw=2))
        mx = (x1 + x2) / 2
        b, bw, bh = textbox(mx, y - 20, label, size=11, bold=True,
                            fill="#ffffff", stroke=col, color=col, pad=7, min_w=150)
        p.append(b)

    # 1) телефон → пристрій: відкритий ключ телефона
    msg(168, ph_x + 28, dev_x - 28, "публічний ключ P_ph", NEG)
    # 2) пристрій → телефон: відкритий ключ пристрою
    msg(232, dev_x - 28, ph_x + 28, "публічний ключ P_dev", FIELD)

    # обидва рахують спільний секрет (X25519) — окремо, локально
    p.append(fitbox(ph_x - 128, 268, 256, 42,
                    "s = X25519(k_ph, P_dev)", size=12,
                    fill="#eaf0fd", stroke=NEG, color=NEG, bold=True))
    p.append(fitbox(dev_x - 128, 268, 256, 42,
                    "s = X25519(k_dev, P_ph)", size=12,
                    fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))
    p.append(text(ear_x, 292, "=", size=22, color=INK, bold=True))
    p.append(text(ear_x, 326, "той самий s — але в ефір НЕ летів", size=11, color=MUTED))

    # PoP уплітається у ключ сеансу
    p.append(fitbox(ear_x - 210, 348, 420, 44,
                    "ключ сеансу  K = HKDF( s ‖ PoP-секрет із наклейки )",
                    size=12, fill="#fff8e6", stroke="#8a6d0b", color="#8a6d0b", bold=True))
    p.append(text(ear_x, 408, "хто не тримав пристрій у руках — PoP не знає → K не збереться",
                  size=11, color=MUTED))

    # 3) далі — усе шифроване K (пароль летить тут)
    msg(452, ph_x + 28, dev_x - 28, "AES-GCM{ SSID + пароль }", POS)
    p.append(text(ear_x, 480, "пароль їде тут — але вже під шифром K", size=10.5, color=MUTED))

    # що бачить підслуховувач — рамка внизу
    p.append(rect(60, 512, W - 120, 74, fill="#f4f6f8", stroke=MUTED, sw=1.6, rx=8))
    p.append(text(W / 2, 534, "Підслуховувач в ефірі бачить:", size=12, color=INK, bold=True))
    p.append(text(W / 2, 556,
                  "два публічні ключі (з них секрет не відновити) + шифротекст. "
                  "Ні s, ні PoP, ні пароля — самий шум.",
                  size=11, color=MUTED))

    render(os.path.join(IMG, 'x25519-handshake.svg'), W, H, *p,
           title="Захищений канал: X25519 + доказ володіння")


def ble_gatt_frag():
    # Розкладка GATT-сервісу провізіонування + фрагментація облікових даних
    # по кількох Write, бо один запис обмежений MTU (типово ~20 байт корисних).
    W, H = 900, 560
    p = []

    # ── Ліворуч: дерево сервісу GATT ──
    sx = 60
    p.append(text(sx + 150, 58, "GATT-сервіс провізіонування", size=14, color=NEG, bold=True))
    svc_y = 84
    p.append(rect(sx, svc_y, 300, 40, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    p.append(text(sx + 150, svc_y + 25, "Service: Provisioning", size=12, color=NEG, bold=True))

    chars = [
        ("scan-list", "READ / NOTIFY", "мережі поблизу", FIELD, "#eafaf0"),
        ("config", "WRITE", "сюди SSID + пароль", POS, "#fff4f0"),
        ("ctrl / status", "WRITE / NOTIFY", "команда й вирок", NEG, "#eaf0fd"),
    ]
    cy = svc_y + 66
    for name, props, note, col, fill in chars:
        p.append(line(sx + 24, svc_y + 40, sx + 24, cy + 22, color=MUTED, sw=1.4))
        p.append(line(sx + 24, cy + 22, sx + 46, cy + 22, color=MUTED, sw=1.4))
        p.append(rect(sx + 46, cy, 274, 46, fill=fill, stroke=col, sw=1.8, rx=7))
        p.append(text(sx + 46 + 137, cy + 19, "Char: " + name, size=11.5, color=col, bold=True))
        p.append(text(sx + 46 + 137, cy + 37, props + "  ·  " + note, size=9.5, color=MUTED))
        cy += 66

    # ── Праворуч: фрагментація по MTU ──
    fx = 520
    p.append(text(fx + 170, 58, "Пароль не влазить в один запис", size=14, color=POS, bold=True))
    # довгий рядок даних
    p.append(fitbox(fx, 84, 340, 34, "SSID + пароль ≈ 90 байтів (зашифровано)",
                    size=11, fill="#ffffff", stroke=INK, color=INK, bold=True))
    p.append(text(fx + 170, 138, "MTU за замовчуванням: 23 байти (корисних ~20)",
                  size=11, color=MUTED))
    p.append(arrow(fx + 170, 150, fx + 170, 186, color=POS, sw=2))

    # ланцюжок фрагментів-записів
    frag_y = 196
    labels = ["Write #1", "Write #2", "Write #3", "…", "Write #5"]
    fw = 62
    fxx = fx
    for i, lab in enumerate(labels):
        col = MUTED if lab == "…" else NEG
        fill = "#f4f6f8" if lab == "…" else "#eaf0fd"
        p.append(rect(fxx, frag_y, fw, 40, fill=fill, stroke=col, sw=1.6, rx=6))
        p.append(text(fxx + fw / 2, frag_y + 24, lab, size=10, color=col, bold=True))
        if i < len(labels) - 1:
            p.append(arrow(fxx + fw, frag_y + 20, fxx + fw + 8, frag_y + 20, color=MUTED, sw=1.4))
        fxx += fw + 12

    p.append(fitbox(fx, frag_y + 66, 340, 62,
                    "пристрій збирає фрагменти в буфер,\nпоки не прийде повний кадр —\n"
                    "аж тоді розшифровує й читає дані",
                    size=11, fill="#eafaf0", stroke=FIELD, color=FIELD))

    # порада внизу
    p.append(fitbox(fx, frag_y + 138, 340, 46,
                    "домовитись про більший MTU (до 517) —\nменше записів, швидше",
                    size=11, fill="#fff8e6", stroke="#8a6d0b", color="#8a6d0b", bold=True))

    render(os.path.join(IMG, 'ble-gatt-frag.svg'), W, H, *p,
           title="BLE-провізіонування: сервіс GATT і фрагментація даних")


# ═══════════════════════════════════════════════════════════════════════════
#  ФІГУРИ ВСТАВКИ math-ecdh-pop.md (математика X25519 + доказ володіння)
# ═══════════════════════════════════════════════════════════════════════════

def ecdlp_oneway():
    # Однобічність множення точки на скаляр: уперед k·G рахується миттєво
    # (сходами Монтгомері, ~256 подвоєнь), назад — знайти k з G і P — задача
    # дискретного логарифма, на яку способу немає. Тому P можна показувати всім.
    W, H = 820, 470
    p = []

    gx, px = 165, W - 165
    my = 210

    # два кінці: базова точка G і публічна точка P
    p.append(circle(gx, my, 42, fill="#eafaf0", stroke=FIELD, sw=2.6))
    p.append(text(gx, my - 4, "G", size=26, color=FIELD, bold=True))
    p.append(text(gx, my + 18, "базова точка", size=11, color=MUTED))
    p.append(text(gx, my + 74, "(u = 9, фіксована,", size=11, color=MUTED))
    p.append(text(gx, my + 90, "однакова для всіх)", size=11, color=MUTED))

    p.append(circle(px, my, 42, fill="#eaf0fd", stroke=NEG, sw=2.6))
    p.append(text(px, my - 4, "P", size=26, color=NEG, bold=True))
    p.append(text(px, my + 18, "відкритий ключ", size=11, color=MUTED))
    p.append(text(px, my + 74, "P = k · G", size=12, color=NEG, bold=True))
    p.append(text(px, my + 90, "(можна показувати всім)", size=11, color=MUTED))

    # ВПЕРЕД — легко: широка зелена стрілка згори
    p.append(arrow(gx + 46, my - 40, px - 46, my - 40, color=FIELD, sw=3))
    b, bw, bh = textbox((gx + px) / 2, my - 66, "k · G  —  легко: ~256 подвоєнь (сходи Монтгомері)",
                        size=13, bold=True, fill="#eafaf0", stroke=FIELD, color=FIELD,
                        min_w=440, pad=9)
    p.append(b)

    # НАЗАД — неможливо: перекреслена червона стрілка знизу
    p.append(arrow(px - 46, my + 40, gx + 46, my + 40, color=POS, sw=3))
    b2, bw2, bh2 = textbox((gx + px) / 2, my + 66,
                           "знайти k з G і P  —  задача дискретного логарифма (ECDLP)",
                           size=13, bold=True, fill="#fdecea", stroke=POS, color=POS,
                           min_w=440, pad=9)
    p.append(b2)
    # хрест на «назад»
    mx = (gx + px) / 2
    p.append(line(mx - 12, my + 40 - 12, mx + 12, my + 40 + 12, color=POS, sw=3))
    p.append(line(mx - 12, my + 40 + 12, mx + 12, my + 40 - 12, color=POS, sw=3))

    # низ: масштаб задачі
    p.append(fitbox(W / 2 - 350, 388, 700, 56,
                    "секрет k живе серед ≈ 2²⁵² можливостей · найшвидший відомий напад ≈ 2¹²⁸ кроків\n"
                    "більше, ніж атомів у Землі — тому «назад» рахувати нікому",
                    size=13, fill="#fff8e6", stroke="#8a6d0b", color="#8a6d0b", bold=True))

    render(os.path.join(IMG, 'ecdlp-oneway.svg'), W, H, *p,
           title="Однобічні двері: k·G легко вперед, ECDLP — назад ні")


def secret_pipeline():
    # Конвеєр згладжування секрету: сирий X25519-секрет s (32 байти, з ухилом,
    # не рівномірний) → змішати з PoP → протягти через хеш/HKDF → рівний ключ
    # сеансу K → AES-GCM бере K + одноразове число (nonce). Показуємо ТОЧНЕ
    # місце, куди входить PoP і nonce. Головний конвеєр — ліва вертикаль;
    # бічні вкидання (PoP, nonce) стоять праворуч, стрілки не перетинають текст.
    W, H = 900, 560
    p = []

    cx = 330                    # вісь головного конвеєра (зсунута вліво)
    side_x = 700                # колонка бічних вкидань
    ys = [86, 208, 330, 468]

    # 1) сирий спільний секрет
    p.append(fitbox(cx - 250, ys[0] - 34, 500, 68,
                    "сирий спільний секрет   s = X25519(k_свій, P_чужий)\n"
                    "32 байти — але з ухилом: НЕ рівномірний шум,\nу молодших бітах лишається структура",
                    size=12.5, fill="#f4f6f8", stroke=MUTED, color=INK, bold=True))

    # PoP входить збоку саме на етапі згладжування
    p.append(fitbox(side_x - 145, ys[1] - 58, 290, 46,
                    "PoP-секрет із наклейки\nвплітається ОСЬ ТУТ", size=12,
                    fill="#fff8e6", stroke="#8a6d0b", color="#8a6d0b", bold=True))
    p.append(arrow(side_x - 145, ys[1] - 35, cx + 254, ys[1] - 18, color="#8a6d0b", sw=2))

    p.append(arrow(cx, ys[0] + 34, cx, ys[1] - 40, color=INK, sw=2.2))

    # 2) змішати + протягти через хеш/HKDF
    p.append(fitbox(cx - 252, ys[1] - 40, 504, 80,
                    "згладжування (KDF)\n"
                    "ESP-IDF security1:  K = SHA-256( s ⊕ SHA-256(PoP) )\n"
                    "загальний спосіб:  K = HKDF(s, salt, info)\n"
                    "— спершу витягти ентропію, тоді розтягти в ключ",
                    size=12, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))

    p.append(arrow(cx, ys[1] + 40, cx, ys[2] - 26, color=INK, sw=2.2))

    # 3) рівний ключ сеансу
    p.append(fitbox(cx - 210, ys[2] - 26, 420, 52,
                    "ключ сеансу K — 256 бітів рівного шуму,\n"
                    "не вгадати, не відрізнити від випадкового",
                    size=12.5, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True))

    # nonce входить збоку на вході в шифр
    p.append(fitbox(side_x - 150, ys[3] - 52, 300, 46,
                    "одноразове число (nonce)\nнове на КОЖЕН кадр — проти повторів",
                    size=11.5, fill="#fff4f0", stroke=POS, color=POS, bold=True))
    p.append(arrow(side_x - 150, ys[3] - 29, cx + 234, ys[3] - 14, color=POS, sw=2))

    p.append(arrow(cx, ys[2] + 26, cx, ys[3] - 34, color=INK, sw=2.2))

    # 4) AES-GCM
    p.append(fitbox(cx - 234, ys[3] - 34, 468, 68,
                    "AES-GCM( ключ K, nonce, дані )\n"
                    "шифрує (конфіденційність) +\nпломба-тег (цілісність) заразом",
                    size=13, fill="#fdecea", stroke=POS, color=POS, bold=True))

    render(os.path.join(IMG, 'secret-pipeline.svg'), W, H, *p,
           title="Від сирого секрету до ключа сеансу: де входять PoP і nonce")


if __name__ == '__main__':
    softap_flow()
    softap_vs_ble()
    wps_pin_split()
    provisioning_fsm()
    dns_wire_trap()
    portal_detectors()
    x25519_handshake()
    ble_gatt_frag()
    ecdlp_oneway()
    secret_pipeline()
    print("ok")
