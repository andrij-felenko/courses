# -*- coding: utf-8 -*-
"""Фігури до теми «MTU і фрагментація IP: механіка, Path MTU та вразливості».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Поля фрагментації в заголовку IPv4 ───────────────────────────────────
def fig_ipv4_frag_header():
    """32-бітний рядок заголовка IPv4: Identification (16 біт),
    Flags (3 біти: Res, DF, MF) та Fragment Offset (13 біт)."""
    W, H = 820, 390
    f = [text(W / 2, 28, "Поля керування фрагментацією в заголовку IPv4 (32-бітний рядок)", size=16, bold=True)]

    # Смуга бітів від 0 до 31
    bx, by = 50, 70
    total_w = 720
    row_h = 56

    # Шкала бітів зверху
    f.append(text(bx + 5, by - 8, "біт 0", size=11, color=MUTED, anchor="start"))
    f.append(text(bx + total_w * 0.5 - 5, by - 8, "біт 15", size=11, color=MUTED, anchor="end"))
    f.append(text(bx + total_w * 0.5 + 5, by - 8, "біт 16", size=11, color=MUTED, anchor="start"))
    f.append(text(bx + total_w * 0.59375, by - 8, "18", size=11, color=MUTED))
    f.append(text(bx + total_w * 0.59375 + 5, by - 8, "19", size=11, color=MUTED, anchor="start"))
    f.append(text(bx + total_w - 5, by - 8, "біт 31", size=11, color=MUTED, anchor="end"))

    # Блок 1: Identification (16 біт)
    w_id = total_w * 0.5
    f.append(rect(bx, by, w_id, row_h, fill="#eef3ff", stroke=NEG, sw=1.8, rx=4))
    f.append(text(bx + w_id / 2, by + 24, "Identification (16 біт)", size=13, bold=True, color=NEG))
    f.append(text(bx + w_id / 2, by + 44, "Унікальний ID дейтаграми джерела", size=10, color=MUTED))

    # Блок 2: Flags (3 біти)
    w_flags = total_w * (3.0 / 32.0)
    x_flags = bx + w_id
    f.append(rect(x_flags, by, w_flags, row_h, fill="#fff7e6", stroke=POS, sw=1.8, rx=4))
    f.append(text(x_flags + w_flags / 2, by + 24, "Flags", size=12, bold=True, color=POS))
    f.append(text(x_flags + w_flags / 2, by + 44, "3 біти", size=10, color=MUTED))

    # Блок 3: Fragment Offset (13 біт)
    w_off = total_w * (13.0 / 32.0)
    x_off = x_flags + w_flags
    f.append(rect(x_off, by, w_off, row_h, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=4))
    f.append(text(x_off + w_off / 2, by + 24, "Fragment Offset (13 біт)", size=13, bold=True, color=FIELD))
    f.append(text(x_off + w_off / 2, by + 44, "Зміщення навантаження в блоках по 8 байтів", size=10, color=MUTED))

    # Деталізація Flags унизу ліворуч
    fy = by + row_h + 35
    f.append(rect(bx, fy, 320, 155, fill="#fffdf9", stroke=POS, sw=1.3, rx=6))
    f.append(text(bx + 160, fy + 22, "Розшифровка прапорців (Flags)", size=12, bold=True, color=POS))
    f.append(line(bx + 15, fy + 32, bx + 305, fy + 32, color="#fed7aa", sw=1))

    f.append(text(bx + 20, fy + 52, "• Біт 0: Reserved (мусить бути 0)", size=11, anchor="start"))
    f.append(text(bx + 20, fy + 78, "• Біт 1: DF (Don't Fragment)", size=11, bold=True, color=NEG, anchor="start"))
    f.append(text(bx + 35, fy + 95, "1 = заборона ділити пакет (роутер відкидає)", size=10, color=MUTED, anchor="start"))
    f.append(text(bx + 20, fy + 120, "• Біт 2: MF (More Fragments)", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(text(bx + 35, fy + 137, "1 = є наступні фрагменти; 0 = останній", size=10, color=MUTED, anchor="start"))

    # Деталізація Offset унизу праворуч
    f.append(rect(bx + 350, fy, 370, 155, fill="#f6fcf8", stroke=FIELD, sw=1.3, rx=6))
    f.append(text(bx + 535, fy + 22, "Масштабування зміщення (Крок 8 байтів)", size=12, bold=True, color=FIELD))
    f.append(line(bx + 365, fy + 32, bx + 705, fy + 32, color="#bbf7d0", sw=1))

    f.append(text(bx + 370, fy + 52, "• 13 біт задають максимум 2¹³ = 8192 позиції.", size=11, anchor="start"))
    f.append(text(bx + 370, fy + 76, "• Одиниця виміру — 8 октетів (64 біти):", size=11, anchor="start"))
    f.append(text(bx + 385, fy + 98, "Байтове зміщення = Fragment Offset × 8", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(bx + 370, fy + 122, "• 8192 × 8 = 65 536 байтів — максимальна дейтаграма IPv4.", size=10, color=MUTED, anchor="start"))
    f.append(text(bx + 370, fy + 142, "• Кожен нефінальний фрагмент МУСИТЬ бути кратним 8 байтам.", size=10, bold=True, color=POS, anchor="start"))

    render(os.path.join(IMG, "ipv4-frag-header.svg"), W, H, *f)


# ── 2. Процес фрагментації пакета роутером ─────────────────────────────────
def fig_fragmentation_process():
    """Розрізання великого пакета (4000 байтів) при переході на канал MTU 1500."""
    W, H = 840, 440
    f = [text(W / 2, 28, "Процес фрагментації дейтаграми IPv4 на проміжному маршрутизаторі", size=16, bold=True)]

    # Вихідний пакет зверху
    ox, oy = 70, 60
    f.append(text(W / 2, oy - 8, "Вихідна дейтаграма: Total Length = 4000 байтів (ID=0x4A12, DF=0, MF=0, Offset=0)", size=11, bold=True))
    f.append(rect(ox, oy, 110, 44, fill="#eef3ff", stroke=NEG, sw=1.5, rx=4))
    f.append(text(ox + 55, oy + 22, "IP Hdr (20 B)", size=11, bold=True, color=NEG))
    f.append(text(ox + 55, oy + 36, "Len=4000", size=9, color=MUTED))

    f.append(rect(ox + 110, oy, 590, 44, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=4))
    f.append(text(ox + 405, oy + 27, "Корисне навантаження TCP/UDP (3980 байтів даних)", size=12, bold=True))

    # Стрілка переходу через роутер з MTU 1500
    ry = oy + 70
    f.append(line(W / 2, oy + 46, W / 2, ry + 15, color=LINE, sw=1.8))
    f.append(rect(W / 2 - 190, ry - 14, 380, 36, fill="#fff7e6", stroke=POS, sw=1.4, rx=6))
    f.append(text(W / 2, ry + 9, "Вихідний інтерфейс має MTU = 1500 байтів  →  Max Data = 1480 B", size=11, bold=True, color=POS))
    f.append(arrow(W / 2, ry + 24, W / 2, ry + 52, color=POS, sw=1.8))

    # Три фрагменти знизу
    fy = ry + 65
    frags = [
        ("Фрагмент 1", 1480, "0 .. 1479", "0 (0 B)", "1", "1500 B", 0),
        ("Фрагмент 2", 1480, "1480 .. 2959", "185 (1480 B)", "1", "1500 B", 1),
        ("Фрагмент 3", 1020, "2960 .. 3979", "370 (2960 B)", "0", "1040 B", 2)
    ]

    for title, dlen, span, off_str, mf_val, tot_len, idx in frags:
        cury = fy + idx * 72
        # Заголовок фрагмента
        f.append(rect(ox, cury, 110, 52, fill="#eef3ff", stroke=NEG, sw=1.5, rx=4))
        f.append(text(ox + 55, cury + 18, "IP Hdr (20 B)", size=10, bold=True, color=NEG))
        f.append(text(ox + 55, cury + 32, "ID=0x4A12", size=9, color=MUTED))
        f.append(text(ox + 55, cury + 45, "Len=" + tot_len, size=9, bold=True, color=INK))

        # Тіло фрагмента
        w_body = 230 if dlen == 1480 else 165
        f.append(rect(ox + 115, cury, w_body, 52, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=4))
        f.append(text(ox + 115 + w_body / 2, cury + 22, title + " (" + str(dlen) + " B)", size=11, bold=True, color=FIELD))
        f.append(text(ox + 115 + w_body / 2, cury + 40, "Байти навантаження: " + span, size=9, color=MUTED))

        # Пояснення параметрів праворуч
        f.append(rect(ox + 125 + w_body, cury, 355, 52, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
        f.append(text(ox + 135 + w_body, cury + 20, "Offset = " + off_str + " (кратне 8)", size=10, bold=True, anchor="start"))
        mf_color = FIELD if mf_val == "1" else POS
        f.append(text(ox + 135 + w_body, cury + 38, "MF = " + mf_val + (" (ще будуть фрагменти)" if mf_val == "1" else " (останній фрагмент дейтаграми)"), size=10, color=mf_color, bold=True, anchor="start"))

    render(os.path.join(IMG, "fragmentation-process.svg"), W, H, *f)


# ── 3. PMTUD і проблема Black Hole ─────────────────────────────────────────
def fig_pmtud_and_blackhole():
    """Порівняння: коректна робота PMTUD (RFC 1191) проти PMTUD Black Hole."""
    W, H = 840, 420
    f = [text(W / 2, 28, "Path MTU Discovery (PMTUD) та проблема «чорних дір» (Black Hole)", size=16, bold=True)]

    # Ліва колонка: Успішний PMTUD
    lx = 45
    col_w = 360
    f.append(rect(lx, 55, col_w, 345, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(lx + col_w / 2, 80, "Штатний PMTUD (ICMP діє)", size=13, bold=True, color=FIELD))

    # Схема взаємодії зліва
    f.append(rect(lx + 20, 105, 80, 36, fill="#eef3ff", stroke=NEG, sw=1.3, rx=4))
    f.append(text(lx + 60, 127, "Хост A", size=11, bold=True))

    f.append(rect(lx + 140, 105, 80, 36, fill="#fff7e6", stroke=POS, sw=1.3, rx=4))
    f.append(text(lx + 180, 127, "Роутер R", size=11, bold=True))

    f.append(rect(lx + 260, 105, 80, 36, fill="#eafaf0", stroke=FIELD, sw=1.3, rx=4))
    f.append(text(lx + 300, 127, "Хост B", size=11, bold=True))

    # Крок 1: Пакет 1500 B DF=1
    f.append(arrow(lx + 60, 160, lx + 180, 160, color=NEG, sw=1.8))
    f.append(text(lx + 120, 152, "Пакет 1500 B (DF=1)", size=9, bold=True, color=NEG))

    # R відкидає (MTU=1400)
    f.append(text(lx + 180, 185, "MTU=1400 → Drop!", size=10, bold=True, color=POS))

    # Крок 2: ICMP Type 3 Code 4
    f.append(arrow(lx + 180, 215, lx + 60, 215, color=POS, sw=1.8))
    f.append(text(lx + 120, 207, "ICMP T3 C4 (Next MTU=1400)", size=9, bold=True, color=POS))

    # Крок 3: Хост A оновлює кеш і надсилає 1400 B
    f.append(arrow(lx + 60, 255, lx + 300, 255, color=FIELD, sw=1.8))
    f.append(text(lx + 180, 247, "Пакет 1400 B (DF=1) → Доставлено!", size=9, bold=True, color=FIELD))

    f.append(fitbox(lx + 15, 290, col_w - 30, 95,
                    "Результат: Хост A кешує PMTU = 1400 B.\nУсі наступні сегменти надсилаються без\nфрагментації та втрат даних.",
                    size=10, fill="#ffffff", stroke=FIELD, sw=1.2))

    # Права колонка: PMTUD Black Hole
    rx = 435
    f.append(rect(rx, 55, col_w, 345, fill="#fdfaf9", stroke=POS, sw=1.5, rx=8))
    f.append(text(rx + col_w / 2, 80, "PMTUD Black Hole (ICMP заблоковано)", size=13, bold=True, color=POS))

    f.append(rect(rx + 20, 105, 75, 36, fill="#eef3ff", stroke=NEG, sw=1.3, rx=4))
    f.append(text(rx + 57, 127, "Хост A", size=11, bold=True))

    f.append(rect(rx + 115, 105, 75, 36, fill="#fff7e6", stroke=POS, sw=1.3, rx=4))
    f.append(text(rx + 152, 127, "Роутер R", size=11, bold=True))

    f.append(rect(rx + 205, 105, 65, 36, fill="#fee2e2", stroke=POS, sw=1.3, rx=4))
    f.append(text(rx + 237, 127, "Фаєрвол", size=10, bold=True, color=POS))

    f.append(rect(rx + 285, 105, 60, 36, fill="#eafaf0", stroke=FIELD, sw=1.3, rx=4))
    f.append(text(rx + 315, 127, "Хост B", size=10, bold=True))

    # Крок 1: Пакет 1500 B DF=1
    f.append(arrow(rx + 57, 160, rx + 152, 160, color=NEG, sw=1.8))
    f.append(text(rx + 105, 152, "Пакет 1500 B (DF=1)", size=9, bold=True, color=NEG))
    f.append(text(rx + 152, 185, "MTU=1400 → Drop!", size=10, bold=True, color=POS))

    # Крок 2: ICMP блокується
    f.append(line(rx + 152, 215, rx + 220, 215, color=POS, sw=1.8, dash="4,3"))
    f.append(text(rx + 237, 219, "✖ Блок ICMP", size=10, bold=True, color=POS))

    # Крок 3: Хост A зависає в таймаутах
    f.append(text(rx + col_w / 2, 255, "Хост A НЕ знає причини й нескінченно ретранслює...", size=9, italic=True, color=POS))

    f.append(fitbox(rx + 15, 280, col_w - 30, 105,
                    "Наслідок: TCP-рукостискання проходить (малі SYN),\nале щойно йде повний кадр із даними (TLS/HTTP) —\nз'єднання «зависає наглухо» (Black Hole).\nЛікування: TCP MSS Clamping або PLPMTUD.",
                    size=10, fill="#ffffff", stroke=POS, sw=1.2))

    render(os.path.join(IMG, "pmtud-and-blackhole.svg"), W, H, *f)


# ── 4. Фрагментація в IPv6: Fragment Extension Header ──────────────────────
def fig_ipv6_fragment_header():
    """Заголовок розширення фрагментації в IPv6 (RFC 8200)."""
    W, H = 820, 390
    f = [text(W / 2, 28, "Фрагментація в IPv6: базовий заголовок і Fragment Extension Header", size=16, bold=True)]

    bx, by = 60, 60
    total_w = 700

    # 1. Базовий заголовок IPv6 (40 байтів)
    f.append(rect(bx, by, 320, 56, fill="#eef3ff", stroke=NEG, sw=1.8, rx=4))
    f.append(text(bx + 160, by + 24, "Базовий заголовок IPv6 (40 байтів)", size=12, bold=True, color=NEG))
    f.append(text(bx + 160, by + 44, "Next Header = 44 (Fragment Header)", size=10, bold=True, color=POS))

    f.append(arrow(bx + 320, by + 28, bx + 370, by + 28, color=LINE, sw=1.8))

    # 2. Fragment Extension Header (8 байтів)
    f.append(rect(bx + 370, by, 330, 56, fill="#fff7e6", stroke=POS, sw=1.8, rx=4))
    f.append(text(bx + 535, by + 24, "Fragment Header (8 байтів / 64 біти)", size=12, bold=True, color=POS))
    f.append(text(bx + 535, by + 44, "Додається ТІЛЬКИ хостом-відправником", size=10, color=MUTED))

    # Детальна структура Fragment Extension Header (32 біти на рядок, 2 рядки)
    sy = by + 80
    row_w = 640
    sx = (W - row_w) / 2

    # Рядок 1: Next Header (8b), Reserved (8b), Offset (13b), Res (2b), M flag (1b)
    f.append(text(W / 2, sy - 8, "Структура Fragment Extension Header (RFC 8200):", size=11, bold=True))

    w_nh = row_w * (8.0 / 32.0)
    w_res = row_w * (8.0 / 32.0)
    w_off = row_w * (13.0 / 32.0)
    w_r2 = row_w * (2.0 / 32.0)
    w_m = row_w * (1.0 / 32.0)

    f.append(rect(sx, sy, w_nh, 44, fill="#f4f6f8", stroke=LINE, sw=1.4, rx=3))
    f.append(text(sx + w_nh / 2, sy + 20, "Next Hdr", size=10, bold=True))
    f.append(text(sx + w_nh / 2, sy + 35, "8 бітів", size=9.5, color=MUTED))

    f.append(rect(sx + w_nh, sy, w_res, 44, fill="#ffffff", stroke=LINE, sw=1.4, rx=3))
    f.append(text(sx + w_nh + w_res / 2, sy + 20, "Reserved", size=10))
    f.append(text(sx + w_nh + w_res / 2, sy + 35, "8 бітів", size=9.5, color=MUTED))

    f.append(rect(sx + w_nh + w_res, sy, w_off, 44, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=3))
    f.append(text(sx + w_nh + w_res + w_off / 2, sy + 20, "Fragment Offset", size=10, bold=True, color=FIELD))
    f.append(text(sx + w_nh + w_res + w_off / 2, sy + 35, "13 бітів (блок 8 B)", size=9.5, color=MUTED))

    f.append(rect(sx + w_nh + w_res + w_off, sy, w_r2, 44, fill="#ffffff", stroke=LINE, sw=1.4, rx=3))
    f.append(text(sx + w_nh + w_res + w_off + w_r2 / 2, sy + 27, "Res", size=9.5))

    f.append(rect(sx + w_nh + w_res + w_off + w_r2, sy, w_m, 44, fill="#fee2e2", stroke=POS, sw=1.4, rx=3))
    f.append(text(sx + w_nh + w_res + w_off + w_r2 + w_m / 2, sy + 27, "M", size=9.5, bold=True, color=POS))

    # Рядок 2: Identification (32 біти)
    sy2 = sy + 48
    f.append(rect(sx, sy2, row_w, 44, fill="#eef3ff", stroke=NEG, sw=1.8, rx=3))
    f.append(text(sx + row_w / 2, sy2 + 22, "Identification (32 біти — розширено з 16 біт IPv4!)", size=12, bold=True, color=NEG))
    f.append(text(sx + row_w / 2, sy2 + 37, "Запобігає колізіям ID на швидкостях 100+ Гбіт/с", size=9, color=MUTED))

    # Порівняльні акценти IPv6 унизу
    f.append(rect(sx, sy2 + 58, row_w, 75, fill="#f8fafc", stroke=FIELD, sw=1.3, rx=6))
    f.append(text(sx + 15, sy2 + 78, "🔑 Ключові відмінності IPv6:", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(text(sx + 15, sy2 + 98, "1. Маршрутизатори НІКОЛИ не фрагментують: пакет > MTU → відкидання + ICMPv6 Packet Too Big.", size=10, anchor="start"))
    f.append(text(sx + 15, sy2 + 118, "2. Мінімальний гарантований MTU для будь-якої мережі IPv6 = 1280 байтів (проти 576 B у IPv4).", size=10, anchor="start"))

    render(os.path.join(IMG, "ipv6-fragment-header.svg"), W, H, *f)


# ── 5. Атаки на основі фрагментації IP ─────────────────────────────────────
def fig_fragment_attacks():
    """Типові атаки: Teardrop (overlapping offset), Ping of Death (>65535), Tiny Fragment."""
    W, H = 840, 430
    f = [text(W / 2, 28, "Атаки на основі фрагментації IP: механізми порушення меж", size=16, bold=True)]

    card_w = 240
    card_h = 345
    cy = 60

    # 1. Teardrop Attack
    x1 = 35
    f.append(rect(x1, cy, card_w, card_h, fill="#fffaf9", stroke=POS, sw=1.5, rx=8))
    f.append(text(x1 + card_w / 2, cy + 26, "1. Атака Teardrop", size=13, bold=True, color=POS))
    f.append(text(x1 + card_w / 2, cy + 44, "Перекриття зміщень (Overlap)", size=10, color=MUTED))
    f.append(line(x1 + 15, cy + 54, x1 + card_w - 15, cy + 54, color="#fecaca", sw=1))

    # Схема фрагментів Teardrop
    f.append(rect(x1 + 15, cy + 70, 140, 30, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(x1 + 85, cy + 89, "Frag 1: [0 .. 599]", size=10, bold=True))

    f.append(rect(x1 + 85, cy + 108, 140, 30, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
    f.append(text(x1 + 155, cy + 127, "Frag 2: [300 .. 700]", size=10, bold=True, color=POS))

    # Зона накладення позначена прямокутником/підписом знизу
    f.append(text(x1 + card_w / 2, cy + 158, "Зона накладення: [300 .. 599]", size=10, bold=True, color=POS))

    f.append(fitbox(x1 + 12, cy + 180, card_w - 24, 145,
                    "Механіка: Розрахунок розміру:\nlen = end - start < 0.\nПри виклику memcpy(..., len)\nвід'ємне число як unsigned\nстає 4 ГБ → аварійне падіння\nядра системи (BSOD / Kernel Panic).",
                    size=9.5, fill="#ffffff", stroke=POS, sw=1.1))

    # 2. Ping of Death
    x2 = x1 + card_w + 25
    f.append(rect(x2, cy, card_w, card_h, fill="#fffdf8", stroke=NEG, sw=1.5, rx=8))
    f.append(text(x2 + card_w / 2, cy + 26, "2. Ping of Death", size=13, bold=True, color=NEG))
    f.append(text(x2 + card_w / 2, cy + 44, "Переповнення ліміту 65 535 B", size=10, color=MUTED))
    f.append(line(x2 + 15, cy + 54, x2 + card_w - 15, cy + 54, color="#bfdbfe", sw=1))

    # Схема Ping of Death
    f.append(rect(x2 + 15, cy + 70, 130, 32, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(x2 + 80, cy + 90, "Frag 1: Offset = 0", size=10))

    f.append(text(x2 + card_w / 2, cy + 115, "• • •", size=14, color=MUTED))

    f.append(rect(x2 + 75, cy + 125, 150, 32, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
    f.append(text(x2 + 150, cy + 145, "Frag N: Off=65528, Len=100", size=9.5, bold=True, color=POS))

    f.append(text(x2 + card_w / 2, cy + 172, "Total: 65528 + 100 = 65628 B", size=10, bold=True, color=POS))

    f.append(fitbox(x2 + 12, cy + 190, card_w - 24, 135,
                    "Механіка: Буфер виділявся\nстрого під 65 535 байтів.\nСума Offset × 8 + PayloadLen\nперевищує 64 КБ → запис\nза межі виділеної пам'яті\nта крах мережевого стека.",
                    size=9.5, fill="#ffffff", stroke=NEG, sw=1.1))

    # 3. Tiny Fragment Attack
    x3 = x2 + card_w + 25
    f.append(rect(x3, cy, card_w, card_h, fill="#faf5ff", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(x3 + card_w / 2, cy + 26, "3. Tiny Fragment", size=13, bold=True, color=FIELD))
    f.append(text(x3 + card_w / 2, cy + 44, "Обхід фаєрволів (NIDS Bypass)", size=10, color=MUTED))
    f.append(line(x3 + 15, cy + 54, x3 + card_w - 15, cy + 54, color="#e9d5ff", sw=1))

    # Схема Tiny Fragment
    f.append(rect(x3 + 15, cy + 70, 210, 32, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
    f.append(text(x3 + 120, cy + 90, "Frag 1: IP (20B) + TCP Port (8B)", size=9.5, bold=True, color=POS))

    f.append(rect(x3 + 15, cy + 112, 210, 32, fill="#fff7e6", stroke=POS, sw=1.2, rx=3))
    f.append(text(x3 + 120, cy + 132, "Frag 2: Offset=1 → TCP Flags (SYN)", size=9.5, bold=True, color=INK))

    f.append(fitbox(x3 + 12, cy + 160, card_w - 24, 165,
                    "Механіка: Фаєрвол перевіряє\nправило «блокувати нові SYN».\nУ Frag 1 прапорці відсутні (він вміщує\nлише порти), тому фаєрвол його пропускає.\nFrag 2 не має портів (offset > 0) і теж проходить.\nЦіль збирає повний SYN-пакет.",
                    size=9.5, fill="#ffffff", stroke=FIELD, sw=1.1))

    render(os.path.join(IMG, "fragment-attacks.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ipv4_frag_header()
    fig_fragmentation_process()
    fig_pmtud_and_blackhole()
    fig_ipv6_fragment_header()
    fig_fragment_attacks()
    print("All figures generated successfully.")
