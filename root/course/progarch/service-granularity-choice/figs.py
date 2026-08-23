# -*- coding: utf-8 -*-
"""Фігури до теми «Вибір гранулярності сервісів: nano-services антипатерн» (root/course/progarch/monolith-vs-microservices)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_TINT = "#eafaf0"
RED_TINT   = "#fdecea"
BLUE_TINT  = "#eef2fb"
NEUT       = "#f7f8fa"
AMBER_TINT = "#fff8e6"

def fig_granularity_spectrum():
    """Спектр гранулярності архітектури: від Моноліта до Наносервісів."""
    W, H = 980, 460
    frags = []

    frags.append(text(W / 2, 30, "Спектр гранулярності сервісів: баланс зв'язності та мережевого податку", size=15, bold=True))

    columns = [
        ("Модульний моноліт", "Монолітний процес", "High (у пам'яті)", "0 ms (call)", "Низьке (1 репо)", BLUE_TINT, LINE),
        ("Макросервіс", "Великий bounded context", "Висока", "Низький (2–5 ms)", "Помірне", BLUE_TINT, LINE),
        ("Мікросервіс", "Автономна предметна область", "Оптимальна", "Прийнятний", "Оптимальне (1–3 сервіси)", GREEN_TINT, FIELD),
        ("Наносервіс", "Одна таблиця / 1 CRUD", "Дуже низька", "Критичний (N+1)", "Екстремальне (20+ репо)", RED_TINT, POS),
        ("FaaS / Serverless", "Окрема функція/подія", "Вузька / Event-based", "Cold start + Network", "Специфічне (Cloud ops)", AMBER_TINT, MUTED),
    ]

    for i, (name, scope, cohesion, latency, cog_load, bg, stroke_color) in enumerate(columns):
        cx = 105 + i * 190
        cy = 220
        bw, bh = 175, 300
        frags.append(rect(cx - bw/2, cy - bh/2, bw, bh, fill=bg, stroke=stroke_color, sw=1.8, rx=8))

        # Заголовок блоку
        frags.append(text(cx, cy - 120, name, size=13, bold=True, color=INK))
        frags.append(text(cx, cy - 98, scope, size=10, color=MUTED, italic=True))

        # Лінія-розділювач
        frags.append(line(cx - bw/2 + 10, cy - 85, cx + bw/2 - 10, cy - 85, color=LINE, sw=0.8))

        # Метрики
        frags.append(mtext(cx, cy - 65, [
            "Функціональна зв'язність:",
            cohesion,
            "",
            "Мережевий податок (Latency):",
            latency,
            "",
            "Когнітивне навантаження:",
            cog_load
        ], size=10, anchor="middle", lh=1.35))

    # Зона оптимальної гранулярності
    frags.append(rect(485 - 175, 400, 350, 42, fill=GREEN_TINT, stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(485, 426, "🟢 Зона інженерного балансу: Макросервіси та Мікросервіси", size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, "granularity-spectrum.svg"), W, H, *frags,
           title="Спектр гранулярності сервісів")


def fig_nano_services_pathology():
    """Порівняння патології наносервісів із правильними предметними сервісами."""
    W, H = 960, 480
    frags = []

    frags.append(text(W / 2, 30, "Патологія Наносервісів проти Предметних Сервісів (Domain Services)", size=15, bold=True))

    # Ліва колонка — Наносервіси (Патологія)
    frags.append(rect(30, 60, 435, 390, fill=RED_TINT, stroke=POS, sw=1.8, rx=10))
    frags.append(text(247, 90, "🔴 Патологія: 12 Наносервісів (CRUD / Table per service)", size=13, color=POS, bold=True))

    # Схема наносервісів
    frags.append(rect(50, 115, 395, 230, fill="#ffffff", stroke=POS, sw=1.0, rx=6))
    nano_boxes = [
        ("UserSvc", 90, 145), ("ProfileSvc", 200, 145), ("AddrSvc", 310, 145),
        ("OrderSvc", 90, 200), ("ItemSvc", 200, 200), ("PriceSvc", 310, 200),
        ("PaySvc", 90, 255), ("TokenSvc", 200, 255), ("LogSvc", 310, 255),
    ]
    for nname, nx, ny in nano_boxes:
        frags.append(rect(nx - 40, ny - 16, 80, 32, fill=RED_TINT, stroke=POS, sw=1.0, rx=4))
        frags.append(text(nx, ny + 4, nname, size=10, bold=True, color=POS))

    # Павутина зв'язків
    frags.append(line(130, 145, 160, 145, color=POS, sw=1.2))
    frags.append(line(240, 145, 270, 145, color=POS, sw=1.2))
    frags.append(line(90, 161, 90, 184, color=POS, sw=1.2))
    frags.append(line(200, 161, 200, 184, color=POS, sw=1.2))
    frags.append(line(310, 161, 310, 184, color=POS, sw=1.2))
    frags.append(line(130, 200, 160, 200, color=POS, sw=1.2))
    frags.append(line(240, 200, 270, 200, color=POS, sw=1.2))
    frags.append(line(90, 216, 90, 239, color=POS, sw=1.2))
    frags.append(line(200, 216, 200, 239, color=POS, sw=1.2))
    frags.append(line(310, 216, 310, 239, color=POS, sw=1.2))

    frags.append(mtext(247, 370, [
        "• Синхронні каскади N+1 RPC-викликів (P99 = 1500 ms)",
        "• Синхронні Lockstep-деплої 9 репозиторіїв",
        "• 80% коду — обгортки gRPC/HTTP та Sidecars",
        "• Високе когнітивне навантаження команди"
    ], size=11, color=INK, anchor="middle", lh=1.35))

    # Права колонка — Предметні сервіси
    frags.append(rect(495, 60, 435, 390, fill=GREEN_TINT, stroke=FIELD, sw=1.8, rx=10))
    frags.append(text(712, 90, "🟢 Норма: 2 Зв'язаних Сервіси (Bounded Contexts)", size=13, color=FIELD, bold=True))

    frags.append(rect(515, 115, 395, 230, fill="#ffffff", stroke=FIELD, sw=1.0, rx=6))

    # Двоє сервісів
    frags.append(rect(535, 140, 170, 180, fill=GREEN_TINT, stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(620, 165, "Customer Context", size=12, bold=True, color=FIELD))
    frags.append(text(620, 185, "(User, Profile, Address)", size=10, color=MUTED, italic=True))
    frags.append(rect(550, 205, 140, 95, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    frags.append(text(620, 235, "Модуль у пам'яті", size=10, bold=True, color=INK))
    frags.append(text(620, 255, "ACID DB / call()", size=10, color=MUTED))

    frags.append(rect(725, 140, 170, 180, fill=GREEN_TINT, stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(810, 165, "Order Context", size=12, bold=True, color=FIELD))
    frags.append(text(810, 185, "(Order, Price, Payment)", size=10, color=MUTED, italic=True))
    frags.append(rect(740, 205, 140, 95, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    frags.append(text(810, 235, "Модуль у пам'яті", size=10, bold=True, color=INK))
    frags.append(text(810, 255, "ACID DB / call()", size=10, color=MUTED))

    # Один асинхронний зв'язок
    frags.append(arrow(705, 230, 725, 230, color=FIELD, sw=2.0))
    frags.append(text(715, 215, "Event / RPC", size=9, bold=True, color=FIELD))

    frags.append(mtext(712, 370, [
        "• Одиничний міжсервісний виклик (P99 = 25 ms)",
        "• Незалежний деплой автономних контекстів",
        "• 90% бізнес-логіки / 10% інфраструктури",
        "• Низьке когнітивне навантаження (1 team = 1 context)"
    ], size=11, color=INK, anchor="middle", lh=1.35))

    render(os.path.join(IMG, "nano-services-pathology.svg"), W, H, *frags,
           title="Патологія наносервісів проти предметних сервісів")


def fig_tail_latency_amplification():
    """Мультиплікація хводової затримки P99 при рості кількості міжсервісних викликів K."""
    W, H = 940, 420
    frags = []

    frags.append(text(W / 2, 30, "Мультиплікація хводової затримки P99 при послідовному/паралельному Fan-out", size=15, bold=True))

    # Графічний заголовок/осі
    ox, oy = 90, 350
    gw, gh = 780, 270

    frags.append(rect(ox, oy - gh, gw, gh, fill=FILL, stroke=LINE, sw=1.0, rx=6))

    # Сітка
    for p in [0, 20, 40, 60, 80, 100]:
        y_pos = oy - (p / 100.0) * (gh - 40) - 20
        frags.append(line(ox, y_pos, ox + gw, y_pos, color="#e0e0e0", sw=0.8))
        frags.append(text(ox - 15, y_pos + 4, "%d%%" % p, size=10, color=MUTED, anchor="end"))

    frags.append(text(ox - 50, oy - gh / 2, "Ймовірність затримки P99 на клієнті", size=11, bold=True, color=INK, anchor="middle"))

    # Постійні K точки для p=0.99: P(at least 1 P99) = 1 - 0.99^K
    # K=1 -> 1%, K=5 -> 4.9%, K=10 -> 9.56%, K=20 -> 18.2%, K=30 -> 26.0%, K=50 -> 39.5%
    pts = [(1, 1.0), (5, 4.9), (10, 9.6), (15, 14.0), (20, 18.2), (30, 26.0), (40, 33.1), (50, 39.5)]

    poly_pts = []
    for k, pval in pts:
        x_pos = ox + (k / 50.0) * (gw - 60) + 30
        y_pos = oy - (pval / 100.0) * (gh - 40) - 20
        poly_pts.append((x_pos, y_pos))
        frags.append(circle(x_pos, y_pos, 4, fill=POS, stroke=POS))
        frags.append(text(x_pos, y_pos - 10, "K=%d (%.1f%%)" % (k, pval), size=9, bold=True, color=POS))
        frags.append(text(x_pos, oy + 18, "K=%d" % k, size=10, color=INK))

    frags.append(text(ox + gw/2, oy + 36, "Кількість міжсервісних RPC-викликів на один запит користувача (K)", size=11, bold=True, color=INK))

    # З'єднувальна лінія
    for i in range(len(poly_pts) - 1):
        x1, y1 = poly_pts[i]
        x2, y2 = poly_pts[i+1]
        frags.append(line(x1, y1, x2, y2, color=POS, sw=2.2))

    render(os.path.join(IMG, "tail-latency-amplification-fanout.svg"), W, H, *frags,
           title="Мультиплікація затримки P99")


if __name__ == "__main__":
    fig_granularity_spectrum()
    fig_nano_services_pathology()
    fig_tail_latency_amplification()
