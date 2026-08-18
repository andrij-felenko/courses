# -*- coding: utf-8 -*-
"""Фігури до теми «Вибір моделі fan-out сповіщень DH».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREENBG = "#eafaf0"
REDBG   = "#fdecea"
BLUEBG  = "#eaf0fd"
GREY    = "#e5e7eb"

# ───────── Фіг. 1: Порівняння моделей On-Write, On-Read та Hybrid ─────────
def fig_fanout_models():
    W, H = 1100, 520
    f = []

    # Три колонки порівняння
    # Колонка 1: On-Write (Push)
    f.append(fitbox(40, 40, 320, 430,
                    "ON-WRITE (PUSH / MATERIALIZED)\n\n"
                    "• Продюсер дублює запис для кожного з N підписників у момент події.\n"
                    "• Сховище: N записів у БД / чергах.\n"
                    "• Читання: O(1) — миттєво зі скриньки.\n"
                    "• Запис: O(N) — вибух навантаження на спалахах (fan-out amplification).\n"
                    "• Ідеально для: вузької аудиторії (сім'я, 1–10 пристроїв).",
                    size=13, fill=BLUEBG, stroke=FIELD, color=INK, bold=False, sw=1.6))

    # Колонка 2: On-Read (Pull)
    f.append(fitbox(390, 40, 320, 430,
                    "ON-READ (PULL / BROADCAST)\n\n"
                    "• Продюсер пише подійний запис ЛИШЕ ОДИН РАЗ у загальний журнал.\n"
                    "• Сховище: 1 запис у БД.\n"
                    "• Запис: O(1) — миттєво та дешево.\n"
                    "• Читання: O(M) — кожен із M активних підписників фільтрує стрічку при вході.\n"
                    "• Ідеально для: масових подій ЖК та системи (10 000+ мешканців).",
                    size=13, fill=REDBG, stroke=POS, color=INK, bold=False, sw=1.6))

    # Колонка 3: Hybrid
    f.append(fitbox(740, 40, 320, 430,
                    "ГІБРИДНА МОДЕЛЬ (TIERED)\n\n"
                    "• Динамічний роутинг за розміром аудиторії N та критичністю.\n"
                    "• Вузька аудиторія → On-Write.\n"
                    "• Велика аудиторія → On-Read для стрічки + асинхронний push-дайджест.\n"
                    "• Критична тривога → Аварійний обхід (Emergency bypass).\n"
                    "• Ідеально для: Digital Homes.",
                    size=13, fill=GREENBG, stroke=FIELD, color=INK, bold=False, sw=2))

    render(os.path.join(IMG, "fanout-models-comparison.svg"), W, H, *f,
           title="Порівняння моделей масової розсилки сповіщень: On-Write, On-Read та Гібрид")

# ───────── Фіг. 2: Вибух розмноження (Fan-out amplification) ─────────
def fig_fanout_amplification():
    W, H = 1050, 460
    f = []

    # Блок ліворуч: Джерело
    f.append(fitbox(40, 160, 210, 120,
                    "ДЖЕРЕЛО ПОДІЇ\n\n1 оголошення ОСББ:\n«Аварія водопроводу»\n(1 сира подія)",
                    size=13, fill=FILL, stroke=INK, color=INK, bold=True, sw=1.8))

    f.append(arrow(252, 220, 310, 220, color=MUTED, sw=2))

    # Центр: Fan-out Router
    f.append(fitbox(315, 120, 260, 200,
                    "FAN-OUT ROUTER\n\n"
                    "Обчислення аудиторії:\n"
                    "12 000 квартир\n"
                    "× 2.5 мешканця\n"
                    "= 30 000 підписників!\n"
                    "Множник: 30 000×",
                    size=13, fill=REDBG, stroke=POS, color=POS, bold=True, sw=2))

    f.append(arrow(577, 220, 635, 220, color=MUTED, sw=2))
    f.append(text(606, 200, "30 000 задач", size=11, color=POS, bold=True))

    # Правороч: Вибух у черзі та БД
    f.append(fitbox(640, 100, 360, 240,
                    "ВАСЛІДОК НАЇВНОГО ON-WRITE:\n\n"
                    "• 30 000 записів у таблицю inboxes\n"
                    "• 30 000 HTTP-запитів до APNs / FCM\n"
                    "• Черга задач розпухає до гігабайтів\n"
                    "• CPU 100%, Redis OOM-killer\n"
                    "• Затримка критичних сигналів дому!",
                    size=13, fill=REDBG, stroke=POS, color=INK, bold=False, sw=1.8))

    # Банер висновку знизу
    f.append(fitbox(60, 380, 930, 50,
                    "Захист від вибуху: розбиття на пакетні батчі (chunking), throttling та перехід на On-Read для мас",
                    size=14, fill=GREENBG, stroke=FIELD, color=FIELD, bold=True, sw=2))

    render(os.path.join(IMG, "fanout-amplification-pipeline.svg"), W, H, *f,
           title="Вибух розмноження подій (Fan-out amplification) при масовій розсилці")

# ───────── Фіг. 3: Архітектура 3-рівневого Fan-out роутера DH ─────────
def fig_dh_fanout_arch():
    W, H = 1150, 560
    f = []

    # Вхідна подія
    f.append(fitbox(40, 200, 180, 160,
                    "ВХІДНА ПОДІЯ\n(Event Ingress)\n\nТип, Scope, N,\nПріоритет",
                    size=13, fill=FILL, stroke=INK, color=INK, bold=True, sw=1.8))

    f.append(arrow(222, 280, 280, 280, color=MUTED, sw=2))

    # Селектор / Роутер у центрі
    f.append(fitbox(285, 200, 200, 160,
                    "FAN-OUT ROUTER\n(Аналіз аудиторії N\nта SLA доставки)",
                    size=13, fill=BLUEBG, stroke=FIELD, color=FIELD, bold=True, sw=2))

    # Три гілки праворуч
    # Гілка 1: Аварії / Дім (N <= 10)
    f.append(arrow(487, 230, 565, 120, color=POS, sw=2))
    f.append(text(510, 160, "Emergency / N <= 10", size=11, color=POS, bold=True))
    f.append(fitbox(570, 60, 530, 120,
                    "TIER 1: EMERGENCY & HOME SCOPE (On-Write + Fast-Track)\n"
                    "Пряма розсилка по індивідуальних пристроях без злиття (лаг < 500 мс).\n"
                    "Bypass throttling. Пули високого пріоритету.",
                    size=12, fill=REDBG, stroke=POS, color=INK, bold=False, sw=1.8))

    # Гілка 2: Будинок / ЖК (10 < N <= 5000)
    f.append(arrow(487, 280, 565, 280, color=FIELD, sw=2))
    f.append(text(510, 265, "10 < N <= 5000", size=11, color=FIELD, bold=True))
    f.append(fitbox(570, 220, 530, 120,
                    "TIER 2: COMMUNITY SCOPE (Hybrid: On-Read Feed + Batched Push)\n"
                    "Новина в загальний журнал ЖК. Push розсилається батчами (chunking = 500)\n"
                    "із дедуплікацією та throttling.",
                    size=12, fill=GREENBG, stroke=FIELD, color=INK, bold=False, sw=1.8))

    # Гілка 3: Системні анонси (N > 5000)
    f.append(arrow(487, 330, 565, 440, color=MUTED, sw=2))
    f.append(text(510, 395, "N > 5000", size=11, color=MUTED, bold=True))
    f.append(fitbox(570, 380, 530, 120,
                    "TIER 3: SYSTEM BROADCAST (On-Read Only + Topic Push)\n"
                    "1 запис у глобальну стрічку. Жодних записів в inboxes.\n"
                    "Push через broadcast FCM/APNs topics.",
                    size=12, fill=BLUEBG, stroke=FIELD, color=INK, bold=False, sw=1.8))

    render(os.path.join(IMG, "dh-notification-fanout-arch.svg"), W, H, *f,
           title="Архітектура трирівневого Fan-Out роутера Digital Homes")

if __name__ == "__main__":
    fig_fanout_models()
    fig_fanout_amplification()
    fig_dh_fanout_arch()
    print("Figures generated successfully.")
