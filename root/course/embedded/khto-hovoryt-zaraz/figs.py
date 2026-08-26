# -*- coding: utf-8 -*-
"""Фігури до теми «Хто говорить зараз: множинний доступ і CSMA/CA» (khto-hovoryt-zaraz).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Напівдуплекс у радіо проти дротового Ethernet ────────────────────────
def fig_half_duplex_rf():
    W, H = 760, 380
    f = [text(W / 2, 26, "Чому CSMA/CD не працює в радіо: напівдуплекс і динамічний діапазон", 15, INK, "middle", bold=True)]

    # Ліва колонка: Ethernet CSMA/CD
    f.append(rect(20, 50, 345, 310, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(192, 75, "Дротовий Ethernet (CSMA/CD)", 13.5, INK, "middle", bold=True))

    # Дріт
    f.append(line(50, 150, 335, 150, color=LINE, sw=3))
    f.append(text(192, 138, "спільний мідний коаксіал / вита пара", 10.5, MUTED, "middle"))

    # Вузол A
    f.append(rect(50, 175, 105, 55, fill="#eef6ef", stroke=FIELD, sw=1.5))
    f.append(text(102, 195, "Вузол A (TX)", 11, INK, "middle", bold=True))
    f.append(text(102, 212, "+2.5 V на шину", 10, FIELD, "middle", bold=True))
    f.append(arrow(102, 175, 102, 153, color=FIELD, sw=1.8))

    # Вузол B
    f.append(rect(230, 175, 105, 55, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(282, 195, "Вузол B (TX)", 11, INK, "middle", bold=True))
    f.append(text(282, 212, "+2.5 V на шину", 10, POS, "middle", bold=True))
    f.append(arrow(282, 175, 282, 153, color=POS, sw=1.8))

    # Компаратор колізії
    f.append(fitbox(50, 245, 285, 98,
                    "Напруга подвоюється: U = 2.5V + 2.5V = 5.0V\n"
                    "Компаратор на вході бачить аномальний рівень прямо під час TX!\n"
                    "Результат: миттєве виявлення колізії (CD),\n"
                    "переривання передачі та скидання jam-сигналу.",
                    size=11, fill="#ffffff", stroke=LINE, color=INK))

    # Права колонка: Радіотракт CSMA/CA
    f.append(rect(395, 50, 345, 310, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(567, 75, "Радіоефір (CSMA/CA)", 13.5, INK, "middle", bold=True))

    # Локальний передавач
    f.append(rect(415, 100, 140, 60, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(485, 120, "Локальний TX", 11, INK, "middle", bold=True))
    f.append(text(485, 138, "+20 dBm (100 мВт)", 10.5, POS, "middle", bold=True))

    # Перемикач антени
    f.append(circle(630, 130, 14, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(630, 134, "RF", 9, INK, "middle", bold=True))
    f.append(line(555, 130, 616, 130, color=POS, sw=2))
    f.append(line(644, 130, 680, 130, color=LINE, sw=2))

    # Антена
    f.append(line(680, 130, 705, 130, color=LINE, sw=2))
    f.append(line(705, 110, 705, 150, color=LINE, sw=2))
    f.append(line(705, 130, 720, 110, color=LINE, sw=1.5))
    f.append(line(705, 130, 720, 150, color=LINE, sw=1.5))

    # Слабкий вхідний сигнал
    f.append(text(685, 95, "чужий RX: -85 dBm (3 пВт)", 9.5, MUTED, "middle"))
    f.append(arrow(670, 100, 640, 118, color=MUTED, sw=1.2))

    # Локальний приймач (вимкнений/ізольований)
    f.append(rect(415, 175, 140, 55, fill="#f1f5f9", stroke=MUTED, sw=1.2, rx=4))
    f.append(text(485, 195, "Локальний LNA / RX", 10.5, MUTED, "middle"))
    f.append(text(485, 212, "від'єднаний (ізоляція 25 dB)", 9, POS, "middle"))
    f.append(line(555, 202, 620, 142, color=MUTED, sw=1.2, dash="3,3"))

    # Пояснення різниці
    f.append(fitbox(415, 245, 305, 98,
                    "Різниця потужностей: 105 dB (у 30 мільярдів разів!)\n"
                    "Власний передавач миттєво спалив би чутливий LNA.\n"
                    "ВЧ-ключ відмикає вхід RX під час передачі.\n"
                    "Станція принципово глуха під час власного мовлення!",
                    size=11, fill="#ffffff", stroke=POS, color=INK))

    render(os.path.join(IMG, "half-duplex-rf.svg"), W, H, *f)


# ── 2. Часова діаграма CSMA/CA ──────────────────────────────────────────────
def fig_csma_ca_timeline():
    W, H = 760, 370
    f = [text(W / 2, 24, "Часова шкала CSMA/CA: інтервали DIFS/SIFS, відкат і підтвердження", 15, INK, "middle", bold=True)]

    # Вісь часу
    y_axis = 140
    f.append(arrow(30, y_axis, 730, y_axis, color=LINE, sw=1.8))
    f.append(text(725, y_axis + 18, "час t", 11, INK, "middle", italic=True))

    # 1. Попередній зайнятий ефір
    f.append(rect(40, 85, 100, 45, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    f.append(text(90, 112, "Ефір зайнятий", 10.5, POS, "middle", bold=True))

    # Лінія спаду зайнятості
    f.append(line(140, 70, 140, y_axis + 30, color=MUTED, sw=1, dash="2,2"))

    # 2. DIFS
    f.append(rect(140, 95, 75, 35, fill="#e0f2fe", stroke=NEG, sw=1.5, rx=3))
    f.append(text(177, 117, "DIFS", 11, NEG, "middle", bold=True))

    # Лінія кінця DIFS
    f.append(line(215, 70, 215, y_axis + 30, color=MUTED, sw=1, dash="2,2"))

    # 3. Слоти випадкового відкату (Backoff slots)
    slots = 5
    slot_w = 24
    for i in range(slots):
        sx = 215 + i * slot_w
        f.append(rect(sx, 100, slot_w, 30, fill="#fef3c7", stroke=LINE, sw=1, rx=2))
        f.append(text(sx + slot_w / 2, 120, str(slots - i), 10, INK, "middle"))

    f.append(text(215 + (slots * slot_w) / 2, 85, "Слоти відкату (Backoff)", 10.5, INK, "middle", bold=True))

    # Лінія початку передачі
    tx_start = 215 + slots * slot_w
    f.append(line(tx_start, 70, tx_start, y_axis + 30, color=MUTED, sw=1, dash="2,2"))

    # 4. Кадр даних (DATA)
    data_w = 175
    f.append(rect(tx_start, 80, data_w, 50, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=4))
    f.append(text(tx_start + data_w / 2, 105, "Кадр даних (DATA Frame)", 11, INK, "middle", bold=True))
    f.append(text(tx_start + data_w / 2, 122, "передавач мовить усім", 9.5, FIELD, "middle"))

    # 5. SIFS
    sifs_start = tx_start + data_w
    sifs_w = 40
    f.append(rect(sifs_start, 98, sifs_w, 32, fill="#e0e7ff", stroke=NEG, sw=1.4, rx=3))
    f.append(text(sifs_start + sifs_w / 2, 118, "SIFS", 10, NEG, "middle", bold=True))

    # 6. ACK
    ack_start = sifs_start + sifs_w
    ack_w = 65
    f.append(rect(ack_start, 88, ack_w, 42, fill="#dbeafe", stroke=NEG, sw=1.6, rx=4))
    f.append(text(ack_start + ack_w / 2, 114, "ACK", 11, NEG, "middle", bold=True))

    # 7. Наступний DIFS
    next_difs_start = ack_start + ack_w
    f.append(rect(next_difs_start, 95, 60, 35, fill="#e0f2fe", stroke=NEG, sw=1.2, rx=3))
    f.append(text(next_difs_start + 30, 117, "DIFS", 10, NEG, "middle"))

    # Друга шкала знизу: Заморожування таймера у сусіда
    y_sub = 220
    f.append(text(30, y_sub - 10, "Вузол 2 (конкурент):", 11, INK, "left", bold=True))
    f.append(arrow(30, y_sub + 15, 730, y_sub + 15, color=MUTED, sw=1.2))

    # Вузол 2 рахував відкат
    f.append(rect(215, y_sub, slot_w * 3, 26, fill="#fef3c7", stroke=LINE, sw=1, rx=2))
    f.append(text(215 + slot_w * 1.5, y_sub + 17, "відлік 8...7...6", 9.5, INK, "middle"))

    # Вузол 2 бачить зайнятість від Вузла 1 -> Заморожування!
    f.append(rect(tx_start, y_sub, data_w + sifs_w + ack_w, 26, fill="#fee2e2", stroke=POS, sw=1.2, rx=2))
    f.append(text(tx_start + (data_w + sifs_w + ack_w) / 2, y_sub + 17, "ЗАМОРОЖЕННЯ ВІДЛІКУ (ефір зайнятий, лічильник = 5)", 10, POS, "middle", bold=True))

    # Вузол 2 відновлює відлік після DIFS
    f.append(rect(next_difs_start + 60, y_sub, slot_w * 2, 26, fill="#fef3c7", stroke=LINE, sw=1, rx=2))
    f.append(text(next_difs_start + 60 + slot_w, y_sub + 17, "5...4...", 9.5, INK, "middle"))

    # Підсумкова плашка внизу
    f.append(fitbox(30, 275, 700, 80,
                    "Правила пріоритетів і арбітражу:\n"
                    "1. SIFS < DIFS: відповідь ACK має абсолютний пріоритет над будь-яким новим кадром.\n"
                    "2. Випадковий відкат (Backoff = rand(0, CW) · SlotTime) розводить вузли, що чекали одночасно.\n"
                    "3. Замороження: вузол не скидає лічильник, а зупиняє його, зберігаючи чесну чергу.",
                    size=11, fill="#f8fafc", stroke=LINE, color=INK))

    render(os.path.join(IMG, "csma-ca-timeline.svg"), W, H, *f)


# ── 3. Прихований та засвічений вузли (Hidden & Exposed Terminal) ───────────
def fig_hidden_exposed():
    W, H = 760, 420
    f = [text(W / 2, 24, "Просторові пастки радіоефіру: прихований і засвічений вузли", 15, INK, "middle", bold=True)]

    # Верхня половина: Прихований вузол (Hidden Node)
    f.append(rect(20, 45, 720, 175, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(35, 68, "1. Проблема прихованого вузла (Hidden Terminal)", 12.5, INK, "left", bold=True))

    # Вузли A, B, C
    ax, ay = 130, 125
    bx, by = 380, 125
    cx, cy = 630, 125

    # Радіуси досяжності
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="4,4"/>' % (ax, ay, 160, FIELD))
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="4,4"/>' % (cx, cy, 160, POS))

    # Вузол A
    f.append(circle(ax, ay, 24, fill="#eef6ef", stroke=FIELD, sw=2))
    f.append(text(ax, ay + 5, "Вузол A", 10.5, INK, "middle", bold=True))

    # Вузол B
    f.append(circle(bx, by, 26, fill="#e0f2fe", stroke=NEG, sw=2))
    f.append(text(bx, by + 5, "Вузол B", 11, INK, "middle", bold=True))
    f.append(text(bx, by - 33, "(приймач)", 10, MUTED, "middle"))

    # Вузол C
    f.append(circle(cx, cy, 24, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(cx, cy + 5, "Вузол C", 10.5, INK, "middle", bold=True))

    # Стрілки передачі від A і C до B
    f.append(arrow(ax + 28, ay, bx - 30, by, color=FIELD, sw=2))
    f.append(text((ax + bx)/2, ay - 10, "DATA A→B", 9.5, FIELD, "middle", bold=True))

    f.append(arrow(cx - 28, cy, bx + 30, by, color=POS, sw=2))
    f.append(text((cx + bx)/2, cy - 10, "DATA C→B", 9.5, POS, "middle", bold=True))

    # Позначка колізії на B
    f.append(text(bx, by + 45, "КОЛІЗІЯ на B! (A і C не чують один одного)", 10.5, POS, "middle", bold=True))
    f.append(text(W / 2, 205, "Рішення: 4-етапний обмін RTS/CTS. Вузол B надсилає CTS, який чує C і виставляє NAV (мовчить).", 10, INK, "middle", italic=True))

    # Нижня половина: Засвічений вузол (Exposed Node)
    f.append(rect(20, 230, 720, 175, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(35, 253, "2. Проблема засвіченого вузла (Exposed Terminal)", 12.5, INK, "left", bold=True))

    # 4 Вузли: A, B, C, D
    n_ay, n_by, n_cy, n_dy = 310, 310, 310, 310
    n_ax, n_bx, n_cx, n_dx = 110, 290, 470, 650

    # Вузол A
    f.append(circle(n_ax, n_ay, 22, fill="#f1f5f9", stroke=LINE, sw=1.5))
    f.append(text(n_ax, n_ay + 4, "A", 11, INK, "middle", bold=True))

    # Вузол B
    f.append(circle(n_bx, n_by, 24, fill="#eef6ef", stroke=FIELD, sw=2))
    f.append(text(n_bx, n_by + 5, "B (TX)", 10.5, INK, "middle", bold=True))

    # Вузол C
    f.append(circle(n_cx, n_cy, 24, fill="#fef3c7", stroke="#d97706", sw=2))
    f.append(text(n_cx, n_cy + 5, "C (TX)", 10.5, INK, "middle", bold=True))

    # Вузол D
    f.append(circle(n_dx, n_dy, 22, fill="#f1f5f9", stroke=LINE, sw=1.5))
    f.append(text(n_dx, n_dy + 4, "D", 11, INK, "middle", bold=True))

    # Передача B -> A
    f.append(arrow(n_bx - 28, n_by, n_ax + 26, n_ay, color=FIELD, sw=2))
    f.append(text((n_ax + n_bx)/2, n_ay - 12, "B передає на A", 10, FIELD, "middle", bold=True))

    # C хоче передати на D
    f.append(arrow(n_cx + 28, n_cy, n_dx - 26, n_dy, color="#d97706", sw=2))
    f.append(text((n_cx + n_dx)/2, n_cy - 12, "C хоче передати на D", 10, "#d97706", "middle", bold=True))

    # C чує B
    f.append(line(n_bx + 26, n_by, n_cx - 26, n_cy, color=POS, sw=1.5, dash="2,2"))
    f.append(text((n_bx + n_cx)/2, n_by + 16, "C чує носій від B", 9.5, POS, "middle"))

    f.append(text(W / 2, 360, "Хибне блокування: C чує B і помилково мовчить, хоча його передача на D не завадить прийому A!", 10.5, POS, "middle", bold=True))
    f.append(text(W / 2, 388, "Наслідок: штучна недоутилізація радіоефіру та затримка передачі незалежних потоків.", 10, MUTED, "middle", italic=True))

    render(os.path.join(IMG, "hidden-exposed-node.svg"), W, H, *f)


# ── 4. Порівняння пропускної здатності методів доступу ───────────────────────
def fig_access_comparison():
    W, H = 760, 390
    f = [text(W / 2, 24, "Пропускна здатність методів множинного доступу від навантаження", 15, INK, "middle", bold=True)]

    # Графік
    gx, gy = 90, 60
    gw, gh = 420, 260

    f.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke=LINE, sw=1.2))

    # Сітка та мітки осей
    for v in [0.2, 0.4, 0.6, 0.8, 1.0]:
        y_pos = gy + gh - int(v * gh)
        f.append(line(gx, y_pos, gx + gw, y_pos, color="#e2e8f0", sw=1))
        f.append(text(gx - 10, y_pos + 4, "%.1f" % v, 10, MUTED, "end"))

    for g_val in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        x_pos = gx + int((g_val / 3.0) * gw)
        f.append(line(x_pos, gy, x_pos, gy + gh, color="#e2e8f0", sw=1))
        f.append(text(x_pos, gy + gh + 16, "%.1f" % g_val, 10, MUTED, "middle"))

    f.append(text(gx + gw / 2, gy + gh + 35, "Запропоноване навантаження ефіру G (кадрів / час кадру)", 11, INK, "middle", bold=True))
    f.append(text(gx - 45, gy + gh / 2, "Пропускна здатність S", 11, INK, "middle", bold=True))

    # Крива 1: Pure ALOHA: S = G * exp(-2G)
    pts_aloha = []
    for step in range(120):
        g = step * 3.0 / 120.0
        s = g * math.exp(-2.0 * g)
        px = gx + (g / 3.0) * gw
        py = gy + gh - (s / 1.0) * gh
        pts_aloha.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts_aloha), MUTED))

    # Крива 2: Slotted ALOHA: S = G * exp(-G)
    pts_slotted = []
    for step in range(120):
        g = step * 3.0 / 120.0
        s = g * math.exp(-g)
        px = gx + (g / 3.0) * gw
        py = gy + gh - (s / 1.0) * gh
        pts_slotted.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts_slotted), NEG))

    # Крива 3: CSMA/CA (1-persistent / non-persistent наближення з відкатом)
    # S(G) = G*exp(-a*G) / (G*(1+2a) + exp(-a*G)), a = 0.05
    a = 0.05
    pts_csma = []
    for step in range(120):
        g = step * 3.0 / 120.0
        if g == 0:
            s = 0
        else:
            s = (g * math.exp(-a * g)) / (g * (1.0 + 2.0 * a) + math.exp(-a * g))
        px = gx + (g / 3.0) * gw
        py = gy + gh - (min(s, 0.95) / 1.0) * gh
        pts_csma.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts_csma), FIELD))

    # Крива 4: TDMA (детермінований розподіл слотів)
    pts_tdma = []
    for step in range(120):
        g = step * 3.0 / 120.0
        s = min(g, 0.92) # ~92% утилізація з урахуванням захисних інтервалів
        px = gx + (g / 3.0) * gw
        py = gy + gh - (s / 1.0) * gh
        pts_tdma.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5,4"/>' % (" ".join(pts_tdma), POS))

    # Легенда праворуч
    lx, ly = 530, 80
    f.append(rect(lx, ly, 210, 220, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(lx + 105, ly + 22, "Порівняння протоколів", 11.5, INK, "middle", bold=True))

    # 1. TDMA
    f.append(line(lx + 15, ly + 50, lx + 45, ly + 50, color=POS, sw=2.2, dash="4,3"))
    f.append(text(lx + 55, ly + 54, "TDMA (до ~92%)", 10.5, POS, "left", bold=True))
    f.append(text(lx + 55, ly + 68, "детермінований, без колізій", 9, MUTED, "left"))

    # 2. CSMA/CA
    f.append(line(lx + 15, ly + 95, lx + 45, ly + 95, color=FIELD, sw=2.6))
    f.append(text(lx + 55, ly + 99, "CSMA/CA (пік ~75-80%)", 10.5, FIELD, "left", bold=True))
    f.append(text(lx + 55, ly + 113, "асинхронний, слухає ефір", 9, MUTED, "left"))

    # 3. Slotted ALOHA
    f.append(line(lx + 15, ly + 140, lx + 45, ly + 140, color=NEG, sw=2.2))
    f.append(text(lx + 55, ly + 144, "Slotted ALOHA (36.8%)", 10.5, NEG, "left", bold=True))
    f.append(text(lx + 55, ly + 158, "S = 1/e при G = 1.0", 9, MUTED, "left"))

    # 4. Pure ALOHA
    f.append(line(lx + 15, ly + 185, lx + 45, ly + 185, color=MUTED, sw=2.2))
    f.append(text(lx + 55, ly + 189, "Pure ALOHA (18.4%)", 10.5, INK, "left", bold=True))
    f.append(text(lx + 55, ly + 203, "S = 1/(2e) при G = 0.5", 9, MUTED, "left"))

    render(os.path.join(IMG, "access-comparison.svg"), W, H, *f)


if __name__ == "__main__":
    fig_half_duplex_rf()
    fig_csma_ca_timeline()
    fig_hidden_exposed()
    fig_access_comparison()
    print("All figures generated successfully.")
