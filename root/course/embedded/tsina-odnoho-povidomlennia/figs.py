# -*- coding: utf-8 -*-
"""Фігури до теми «Ціна одного повідомлення: байти, мА·год, гроші».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

# Палітра
COL_NAIVE = "#c0392b"    # Червоний (неефективний стек)
COL_MQTT  = "#d35400"    # Помаранчевий (MQTT + TLS)
COL_COAP  = "#2457d6"    # Синій (CoAP + DTLS)
COL_RAW   = "#27ae60"    # Зелений (бінарний кадр / NIDD)
COL_TAIL  = "#e74c3c"    # Червоний для RRC tail
COL_RAI   = "#2ecc71"    # Зелений для швидкого скидання RAI


# ── 1. Накладні витрати транспортного стека ──────────────────────────────────
def fig_protocol_overhead_stack():
    W, H = 820, 480
    f = [text(W / 2, 28, "Накладні витрати передачі 10 байтів корисних даних у різних стеках", 16, INK, "middle", bold=True)]

    stacks = [
        {
            "title": "HTTPS / TLS 1.2 + JSON (нове з'єднання)",
            "total": "~6400 байтів (6.4 КБ)",
            "color": COL_NAIVE,
            "fill": "#fdecea",
            "layers": [
                ("TCP Handshake (SYN, SYN-ACK, ACK)", "120 Б", 45),
                ("TLS 1.2 Handshake + X.509 Сертифікати", "4800 Б", 380),
                ("HTTP POST заголовки + JSON тіло", "380 Б", 60),
                ("TCP ACK, FIN-ACK закриття сесії", "160 Б", 50),
                ("Дані", "10 Б", 15),
            ],
            "note": "Корисне навантаження становить лише 0.15% від переданого радіотрафіку"
        },
        {
            "title": "MQTT + TLS (відновлення сесії Session Ticket)",
            "total": "~480 байтів",
            "color": COL_MQTT,
            "fill": "#fef5e7",
            "layers": [
                ("TCP 3-Way Handshake", "120 Б", 75),
                ("TLS Session Resumption (Client/ServerHello)", "220 Б", 140),
                ("MQTT CONNECT / CONNACK + PUBLISH (JSON)", "110 Б", 90),
                ("Дані", "10 Б", 25),
            ],
            "note": "Потребує підтримання TCP Keep-Alive або повторного TCP-з'єднання"
        },
        {
            "title": "CoAP / UDP + DTLS Connection ID (CID) + CBOR",
            "total": "~68 байтів",
            "color": COL_COAP,
            "fill": "#eaf0fd",
            "layers": [
                ("IPv6/UDP заголовок (зі стиском 6LoWPAN / RoHC)", "28 Б", 140),
                ("DTLS 1.3 Record (CID + MAC)", "16 Б", 90),
                ("CoAP NON POST + CBOR бінарні дані", "14 Б", 80),
                ("Дані", "10 Б", 50),
            ],
            "note": "Без стану з'єднання, без TCP-рукостискання, нульові витрати на закриття"
        },
        {
            "title": "Ультракомпактний бінарний кадр поверх UDP / NB-IoT NIDD",
            "total": "28 байтів",
            "color": COL_RAW,
            "fill": "#eafaf1",
            "layers": [
                ("UDP/IP заголовок або NIDD NAS-інверт", "8 Б", 100),
                ("Заголовок кадру: версія, seq, прапорці", "4 Б", 60),
                ("HMAC-SHA256 / Poly1305 тег автентичності", "8 Б", 100),
                ("Упаковані дані (bit-packed)", "8 Б", 100),
            ],
            "note": "Максимальна ефективність: понад 35% кадру — корисна інформація"
        }
    ]

    y_start = 58
    row_h = 92
    for idx, st in enumerate(stacks):
        y = y_start + idx * (row_h + 10)
        f.append(rect(30, y, W - 60, row_h, fill=st["fill"], stroke=st["color"], sw=1.6, rx=6))
        f.append(text(46, y + 20, st["title"], 13, INK, "start", bold=True))
        f.append(text(W - 46, y + 20, "Разом: " + st["total"], 13, st["color"], "end", bold=True))

        bar_x = 46
        bar_y = y + 30
        bar_w = W - 92
        bar_h = 24
        
        f.append(rect(bar_x, bar_y, bar_w, bar_h, fill="#ffffff", stroke="#bdc3c7", sw=1, rx=3))
        
        cur_x = bar_x
        num_layers = len(st["layers"])
        total_weight = sum(l[2] for l in st["layers"])
        for l_idx, (l_name, l_sz, l_w) in enumerate(st["layers"]):
            seg_w = (l_w / total_weight) * bar_w
            is_data = (l_idx == num_layers - 1)
            seg_fill = st["color"] if is_data else ("#e0e0e0" if l_idx % 2 == 0 else "#d0d0d0")
            txt_col = "#ffffff" if is_data else INK
            
            f.append(rect(cur_x, bar_y, seg_w, bar_h, fill=seg_fill, stroke="#bdc3c7", sw=0.8, rx=0))
            if seg_w > 55:
                label_txt = f"{l_name.split()[0]} ({l_sz})" if seg_w < 130 else f"{l_name}: {l_sz}"
                f.append(text(cur_x + seg_w / 2, bar_y + 16, label_txt, 10, txt_col, "middle", bold=is_data))
            elif seg_w > 20:
                f.append(text(cur_x + seg_w / 2, bar_y + 16, l_sz, 9, txt_col, "middle", bold=is_data))
            cur_x += seg_w
            
        f.append(text(46, y + 74, "• " + st["note"], 11, MUTED, "start"))

    render(os.path.join(IMG, "protocol-overhead-stack.svg"), W, H, *f)


# ── 2. Енергетичний профіль передавача (NB-IoT / LTE-M) ───────────────────────
def fig_cellular_energy_timeline():
    W, H = 820, 480
    f = [text(W / 2, 28, "Хронограма споживання струму модема: пробудження, TX та хвіст RRC", 16, INK, "middle", bold=True)]

    gx, gy = 70, 70
    gw, gh = 700, 260

    f.append(rect(gx, gy, gw, gh, fill="#fafbfc", stroke="#d1d5db", sw=1.2, rx=4))
    
    levels = [
        (gy + 25, "300 мА", "TX на повній потужності (+23 дБм)"),
        (gy + 95, "70 мА", "Синхронізація (Cell Search) та RX вікно"),
        (gy + 165, "25 мА", "Таймер неактивності RRC Connected (Tail)"),
        (gy + 240, "3.5 мкА", "Глибокий сон PSM (Floor current)"),
    ]
    for ly, lval, ldesc in levels:
        f.append(line(gx, ly, gx + gw, ly, color="#e5e7eb", sw=1, dash="3 3"))
        f.append(text(gx - 8, ly + 4, lval, 10, MUTED, "end", bold=True))

    f.append(line(gx, gy + gh, gx + gw + 10, gy + gh, color=LINE, sw=1.5))
    f.append(arrow(gx + gw, gy + gh, gx + gw + 12, gy + gh, color=LINE, sw=1.5))
    f.append(text(gx + gw + 14, gy + gh + 4, "Час (t)", 11, INK, "start", bold=True))

    tail_poly = f"M {gx+220} {gy+165} L {gx+470} {gy+165} L {gx+470} {gy+240} L {gx+220} {gy+240} Z"
    f.append(f'<path d="{tail_poly}" fill="#fadbd8" opacity="0.6"/>')

    work_poly = f"M {gx+40} {gy+240} L {gx+40} {gy+155} L {gx+80} {gy+155} L {gx+80} {gy+90} L {gx+140} {gy+90} L {gx+140} {gy+25} L {gx+190} {gy+25} L {gx+190} {gy+105} L {gx+220} {gy+105} L {gx+220} {gy+240} Z"
    f.append(f'<path d="{work_poly}" fill="#d5f5e3" opacity="0.5"/>')

    path_no_rai = (
        f"M {gx} {gy+240} "
        f"L {gx+40} {gy+240} L {gx+40} {gy+155} L {gx+80} {gy+155} "
        f"L {gx+80} {gy+90} L {gx+140} {gy+90} "
        f"L {gx+140} {gy+25} L {gx+190} {gy+25} "
        f"L {gx+190} {gy+105} L {gx+220} {gy+105} "
        f"L {gx+220} {gy+165} L {gx+470} {gy+165} "
        f"L {gx+470} {gy+240} L {gx+gw} {gy+240}"
    )
    f.append(f'<path d="{path_no_rai}" fill="none" stroke="{COL_NAIVE}" stroke-width="2.4"/>')

    path_rai = (
        f"M {gx+220} {gy+105} "
        f"L {gx+245} {gy+105} L {gx+255} {gy+240} L {gx+470} {gy+240}"
    )
    f.append(f'<path d="{path_rai}" fill="none" stroke="{COL_RAI}" stroke-width="2.6" stroke-dasharray="5 3"/>')

    f.append(text(gx + 60, gy + 140, "Пробудження", 9.5, INK, "middle", bold=True))
    f.append(text(gx + 110, gy + 75, "RRC Setup & Sync", 9.5, INK, "middle", bold=True))
    f.append(text(gx + 165, gy + 15, "TX Data", 10.5, COL_NAIVE, "middle", bold=True))
    f.append(text(gx + 205, gy + 90, "RX ACK", 9.5, INK, "middle", bold=True))

    f.append(rect(gx + 270, gy + 135, 180, 24, fill="#ffffff", stroke=COL_NAIVE, sw=1.2, rx=4))
    f.append(text(gx + 360, gy + 151, "Марний хвіст RRC: 25 мА", 9.5, COL_NAIVE, "middle", bold=True))

    f.append(rect(gx + 270, gy + 205, 190, 24, fill="#e8f8f5", stroke=COL_RAI, sw=1.4, rx=4))
    f.append(text(gx + 365, gy + 221, "З прапорцем RAI: скидання в PSM", 9.5, COL_RAI, "middle", bold=True))

    card_y = gy + gh + 22
    cw = (gw - 20) / 2
    
    f.append(rect(gx, card_y, cw, 100, fill="#fdf2e9", stroke=COL_NAIVE, sw=1.4, rx=6))
    f.append(text(gx + 16, card_y + 20, "Без оптимізації (HTTPS / TCP / без RAI)", 11.5, COL_NAIVE, "start", bold=True))
    f.append(mtext(gx + 16, card_y + 38, [
        "• Енергія на 1 повідомлення: ~0.25–0.40 мА·год",
        "• 90% заряду згорає на встановлення сесії та хвіст таймера",
        "• Батарея LiSOCl2 (2.4 А·год) виснажується за 45–60 днів"
    ], size=10, color=INK, anchor="start"))

    f.append(rect(gx + cw + 20, card_y, cw, 100, fill="#eafaf1", stroke=COL_RAI, sw=1.4, rx=6))
    f.append(text(gx + cw + 36, card_y + 20, "Оптимізовано (CoAP / UDP + RAI + PSM)", 11.5, COL_RAI, "start", bold=True))
    f.append(mtext(gx + cw + 36, card_y + 38, [
        "• Енергія на 1 повідомлення: ~0.008–0.015 мА·год (у 25 разів менше)",
        "• Модем засинає в PSM (3.5 мкА) за 200 мс після прийому ACK",
        "• Автономна робота тієї ж батареї: 6–8 років"
    ], size=10, color=INK, anchor="start"))

    render(os.path.join(IMG, "cellular-energy-timeline.svg"), W, H, *f)


# ── 3. Економіка парку з 10 000 пристроїв ─────────────────────────────────────
def fig_fleet_cost_projection():
    W, H = 820, 440
    f = [text(W / 2, 28, "Економіка парку 10 000 пристроїв на 5 років: трафік проти сервісних виїздів", 16, INK, "middle", bold=True)]

    box_w = 360
    box_h = 330
    y0 = 60

    f.append(rect(40, y0, box_w, box_h, fill="#fdf2e9", stroke=COL_NAIVE, sw=1.8, rx=8))
    f.append(text(40 + box_w / 2, y0 + 26, "Наївний підхід: JSON / HTTPS", 13.5, COL_NAIVE, "middle", bold=True))
    f.append(line(60, y0 + 38, 40 + box_w - 20, y0 + 38, color=COL_NAIVE, sw=1))

    stats_naive = [
        ("Розмір 1 пакету на радіо:", "6.4 КБ (з рукостисканням)"),
        ("Трафік на пристрій/міс:", "18.4 МБ (інтервал 15 хв)"),
        ("Округлення сесії оператором:", "до 10 КБ → 28.8 МБ/міс"),
        ("Трафік парку (10k пристроїв):", "288 ГБ / місяць"),
        ("Витрати на SIM-трафік:", "$1 800 / міс ($108 000 за 5 р.)"),
        ("Строк служби батареї:", "48 днів"),
        ("Замін батарей за 5 років:", "380 000 сервісних операцій"),
        ("Вартість польового сервісу:", "> $3 800 000 (катастрофа)"),
    ]
    for i, (k, v) in enumerate(stats_naive):
        cy = y0 + 64 + i * 29
        f.append(text(56, cy, k, 10, INK, "start"))
        is_bad = "катастрофа" in v or "48 днів" in v or "$108 000" in v
        f.append(text(40 + box_w - 16, cy, v, 10, COL_NAIVE if is_bad else INK, "end", bold=True))

    f.append(rect(420, y0, box_w, box_h, fill="#eafaf1", stroke=COL_RAW, sw=1.8, rx=8))
    f.append(text(420 + box_w / 2, y0 + 26, "Оптимізований: Binary / UDP / PSM", 13.5, COL_RAW, "middle", bold=True))
    f.append(line(440, y0 + 38, 420 + box_w - 20, y0 + 38, color=COL_RAW, sw=1))

    stats_opt = [
        ("Розмір 1 пакету на радіо:", "28 байтів (bit-packed)"),
        ("Трафік на пристрій/міс:", "80.6 КБ (інтервал 15 хв)"),
        ("Округлення сесії (NIDD/UDP):", "без націнки сесії (81 КБ)"),
        ("Трафік парку (10k пристроїв):", "806 МБ / місяць (увесь парк!)"),
        ("Витрати на SIM-трафік:", "$120 / міс ($7 200 за 5 р.)"),
        ("Строк служби батареї:", "6.8 років на одній LiSOCl2"),
        ("Замін батарей за 5 років:", "0 операцій"),
        ("Вартість польового сервісу:", "$0 планових виїздів"),
    ]
    for i, (k, v) in enumerate(stats_opt):
        cy = y0 + 64 + i * 29
        f.append(text(436, cy, k, 10, INK, "start"))
        is_good = "$0" in v or "6.8 років" in v or "$7 200" in v or "806 МБ" in v
        f.append(text(420 + box_w - 16, cy, v, 10, COL_RAW if is_good else INK, "end", bold=True))

    f.append(fitbox(40, y0 + box_h + 12, W - 80, 28,
                    "Різниця між «працює на столі» і «пораховано для поля» — 15-кратна економія трафіку та збереження життєздатності бізнесу.",
                    size=10.5, fill="#f4f6f8", stroke="#d1d5db", color=INK, bold=True))

    render(os.path.join(IMG, "fleet-cost-projection.svg"), W, H, *f)


if __name__ == "__main__":
    fig_protocol_overhead_stack()
    fig_cellular_energy_timeline()
    fig_fleet_cost_projection()
    print("OK: figures generated in", IMG)
