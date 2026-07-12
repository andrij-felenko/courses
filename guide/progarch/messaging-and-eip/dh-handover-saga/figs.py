# -*- coding: utf-8 -*-
"""Фігури до кроку «Сага «сім'я продає дім»».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER   = "#b8860b"
AMBERBG = "#fff8e8"
GREENBG = "#eafaf0"
REDBG   = "#fdecea"
BLUEBG  = "#eaf0fd"
FAINT   = "#f4f6f8"


def xmark(cx, cy, r=8, color=POS, sw=2.6):
    return (line(cx - r, cy - r, cx + r, cy + r, color=color, sw=sw) +
            line(cx - r, cy + r, cx + r, cy - r, color=color, sw=sw))


def check(cx, cy, r=8, color=FIELD, sw=2.8):
    return (line(cx - r, cy, cx - r * 0.2, cy + r * 0.8, color=color, sw=sw) +
            line(cx - r * 0.2, cy + r * 0.8, cx + r, cy - r, color=color, sw=sw))


# ───────── Фіг. 1: хребет саги — зворотні → півот → повторювані ─────────
def fig_spine():
    W, H = 1240, 588
    f = []
    PX = 620                      # вертикаль півота

    # зонні заголовки
    f.append(text(300, 74, "ЗВОРОТНІ  (компенсувальні)", size=14, bold=True, color=FIELD))
    f.append(text(958, 74, "ПОВТОРЮВАНІ", size=14, bold=True, color=AMBER))
    f.append(text(PX, 74, "точка неповороту", size=12.5, bold=True, color=POS))

    # вертикаль півота — двома сегментами, з розривом під рамкою (лінія не перетинає текст)
    f.append(line(PX, 88, PX, 150, color=POS, sw=4))
    f.append(line(PX, 250, PX, 402, color=POS, sw=4))

    # кроки — зворотна зона (зелена)
    left = [
        (60,  "заморозити"),
        (232, "відкликати\nдоступ"),
        (404, "чекати на\nприйняття"),
    ]
    for x, s in left:
        f.append(fitbox(x, 162, 156, 74, s, size=13, bold=True,
                        fill=GREENBG, stroke=FIELD, color=INK, sw=1.8))

    # півот-рамка на вертикалі
    f.append(fitbox(548, 150, 144, 100, "ПІВОТ\nпередати власність\n+ стерти\nперсональне",
                    size=12.5, bold=True, fill=REDBG, stroke=POS, color=INK, sw=2.4))

    # кроки — повторювана зона (бурштин)
    right = [
        (712,  "перевипустити\nсертифікати"),
        (888,  "переоформити\nбілінг"),
        (1064, "привітати"),
    ]
    for x, s in right:
        f.append(fitbox(x, 162, 156, 74, s, size=13, bold=True,
                        fill=AMBERBG, stroke=AMBER, color=INK, sw=1.8))

    # тонкі стрілки поступу вздовж осі
    f.append(arrow(216, 199, 232, 199, color=MUTED, sw=1.6))
    f.append(arrow(388, 199, 404, 199, color=MUTED, sw=1.6))
    f.append(arrow(868, 199, 888, 199, color=MUTED, sw=1.6))
    f.append(arrow(1044, 199, 1064, 199, color=MUTED, sw=1.6))

    # ── динаміка зворотної зони: задкуй, відкоти ──
    f.append(arrow(556, 300, 66, 300, color=FIELD, sw=2.8))
    f.append(fitbox(150, 322, 360, 46,
                    "невдача ДО півота → задкуй, відкоти,\nчисте скасування",
                    size=12.5, bold=True, fill="#ffffff", stroke=FIELD, color=INK, sw=1.6))

    # ── динаміка повторюваної зони: петля повтору ──
    f.append(line(720, 300, 1156, 300, color=AMBER, sw=2.8))
    f.append(line(1156, 300, 1156, 326, color=AMBER, sw=2.8))
    f.append(line(1156, 326, 720, 326, color=AMBER, sw=2.8))
    f.append(arrow(720, 326, 720, 302, color=AMBER, sw=2.8))
    f.append(fitbox(742, 344, 396, 46,
                    "невдача ПІСЛЯ → не скасовуй, повторюй до успіху\n(застрягло → мертва черга, до людини)",
                    size=12, bold=True, fill="#ffffff", stroke=AMBER, color=INK, sw=1.6))

    # підсумкова стрічка
    f.append(fitbox(300, 428, 640, 40,
                    "Уся проєктна робота — знайти, ДЕ поставити вертикаль півота.",
                    size=13.5, bold=True, fill=FILL, stroke=INK, color=INK, sw=1.8))

    render(os.path.join(IMG, "saga-spine.svg"), W, H, *f,
           title="Хребет саги: зворотне ДО півота, обов'язкове ПІСЛЯ, і одна лінія неповороту")


# ───────── Фіг. 2: дві невдачі, дві долі ─────────
def fig_two_failures():
    W, H = 1200, 496
    f = []

    # ── ЛІВА панель: невдача ДО півота ──
    f.append(rect(32, 58, 540, 404, fill="#f3fbf6", stroke=FIELD, sw=1.6, rx=12))
    f.append(text(302, 86, "НЕВДАЧА ДО ПІВОТА: власники не прийняли", size=13.5, bold=True, color=FIELD))

    f.append(fitbox(96, 104, 300, 40, "заморозити", size=12.5, bold=True,
                    fill=GREENBG, stroke=FIELD, color=INK, sw=1.5))
    f.append(check(430, 124))
    f.append(fitbox(96, 152, 300, 40, "відкликати доступ", size=12.5, bold=True,
                    fill=GREENBG, stroke=FIELD, color=INK, sw=1.5))
    f.append(check(430, 172))
    f.append(fitbox(96, 200, 300, 40, "чекати на прийняття", size=12.5, bold=True,
                    fill=REDBG, stroke=POS, color=INK, sw=1.5))
    f.append(xmark(430, 220, r=9))
    f.append(text(300, 260, "витримка вичерпана — ще ДО півота", size=11.5, bold=True, color=POS))

    # задкування
    f.append(arrow(470, 220, 470, 300, color=FIELD, sw=2.6))
    f.append(text(486, 286, "компенсуй: розморозь, поверни доступ",
                  size=11, color=INK, anchor="start"))
    f.append(fitbox(70, 322, 464, 62,
                    "дім повертається старій сім'ї\nчисте скасування · жодного сліду передачі",
                    size=13, bold=True, fill="#ffffff", stroke=FIELD, color=INK, sw=1.8))

    # ── ПРАВА панель: невдача ПІСЛЯ півота ──
    f.append(rect(628, 58, 540, 404, fill="#fdf6ef", stroke=AMBER, sw=1.6, rx=12))
    f.append(text(898, 86, "НЕВДАЧА ПІСЛЯ ПІВОТА: білінг лежить", size=13.5, bold=True, color=AMBER))

    f.append(fitbox(668, 104, 460, 52,
                    "ПІВОТ пройдено: власність передано + персональне стерто",
                    size=12.5, bold=True, fill=REDBG, stroke=POS, color=INK, sw=2))
    f.append(text(898, 176, "незворотно — назад ходу нема", size=11.5, bold=True, color=POS))

    f.append(fitbox(692, 190, 300, 40, "переоформити білінг", size=12.5, bold=True,
                    fill=AMBERBG, stroke=AMBER, color=INK, sw=1.5))
    f.append(xmark(1024, 210, r=9))

    # петля повтору
    f.append(line(1052, 210, 1108, 210, color=AMBER, sw=2.6))
    f.append(line(1108, 210, 1108, 250, color=AMBER, sw=2.6))
    f.append(line(1108, 250, 742, 250, color=AMBER, sw=2.6))
    f.append(arrow(742, 250, 742, 212, color=AMBER, sw=2.6))
    f.append(text(898, 274, "повторюй до успіху", size=11.5, bold=True, color=AMBER))

    f.append(fitbox(666, 322, 464, 62,
                    "НЕ скасовуємо нічого · крутимо повтор\nзастрягло надовго → мертва черга + сигнал людині",
                    size=12.5, bold=True, fill="#ffffff", stroke=AMBER, color=INK, sw=1.8))

    render(os.path.join(IMG, "two-failures.svg"), W, H, *f,
           title="Той самий збій, різні боки півота — різні долі саги")


# ───────── Фіг. 3: outbox — стан + подія в одній транзакції ─────────
def fig_outbox():
    W, H = 1264, 588
    f = []

    # ── ЛІВА панель: наївний подвійний запис ──
    f.append(rect(44, 60, 556, 500, fill="#fbf3f2", stroke=POS, sw=1.6, rx=12))
    f.append(text(322, 92, "НАЇВНИЙ ПОДВІЙНИЙ ЗАПИС", size=14.5, bold=True, color=POS))
    f.append(fitbox(102, 120, 440, 52, "1. коміт: посунути стан саги → крок DONE",
                    size=12.5, bold=True, fill=GREENBG, stroke=FIELD, color=INK, sw=1.6))
    f.append(arrow(322, 176, 322, 206, color=INK, sw=2.4))
    f.append(xmark(322, 222, r=11, color=POS, sw=3))
    f.append(text(350, 226, "крах саме тут", size=12.5, bold=True, color=POS, anchor="start"))
    f.append(arrow(322, 240, 322, 270, color=MUTED, sw=2.2))
    f.append(fitbox(102, 272, 440, 52, "2. публікація події «крок зроблено»",
                    size=12.5, bold=True, fill="#efefef", stroke=MUTED, color=MUTED, sw=1.6))
    f.append(text(322, 350, "не сталося — подія загубилась", size=12, color=MUTED))
    f.append(fitbox(80, 442, 484, 92,
                    "стан саги пішов уперед, а подія кроку\nзагубилась → крок ніколи не поїде далі.\n(Або навпаки: подія без коміту — привид.)",
                    size=12.5, bold=True, fill="#ffffff", stroke=POS, color=INK, sw=1.8))

    # ── ПРАВА панель: outbox — одна транзакція ──
    f.append(rect(664, 60, 556, 500, fill="#f3fbf6", stroke=FIELD, sw=1.6, rx=12))
    f.append(text(942, 92, "OUTBOX: ОДНА ТРАНЗАКЦІЯ", size=14.5, bold=True, color=FIELD))
    f.append(rect(704, 110, 476, 180, fill="#ffffff", stroke=FIELD, sw=2.2, rx=10))
    f.append(text(942, 132, "ОДНА транзакція:", size=12.5, bold=True, color=FIELD))
    f.append(fitbox(720, 142, 444, 38, "діло кроку — напр. відкликати ключі",
                    size=11.5, bold=True, fill=GREENBG, stroke=FIELD, color=INK, sw=1.4))
    f.append(fitbox(720, 186, 444, 38, "нова позиція саги → крок DONE",
                    size=11.5, bold=True, fill=GREENBG, stroke=FIELD, color=INK, sw=1.4))
    f.append(fitbox(720, 230, 444, 38, "рядок outbox: подія «крок зроблено»",
                    size=11.5, bold=True, fill=BLUEBG, stroke=NEG, color=INK, sw=1.4))
    f.append(text(942, 312, "COMMIT — усе або нічого", size=12.5, bold=True, color=INK))
    f.append(arrow(942, 320, 942, 350, color=INK, sw=2.4))
    f.append(fitbox(742, 352, 400, 50, "реле: читає outbox → публікує в брокер",
                    size=12, bold=True, fill=FAINT, stroke=INK, color=INK, sw=1.6))
    f.append(text(942, 424, "крах будь-де — реле по підйому дочитає й опублікує",
                  size=11, color=MUTED))
    f.append(fitbox(700, 442, 484, 92,
                    "подія народжується в ТІЙ САМІЙ транзакції,\nщо й діло: коміт дає обидва,\nкрах — жодного напіврезультату",
                    size=12.5, bold=True, fill="#ffffff", stroke=FIELD, color=INK, sw=1.8))

    render(os.path.join(IMG, "outbox-atomic.svg"), W, H, *f,
           title="Outbox: стан саги й подія кроку — в одній транзакції, тож крах не лишає напіврезультату")


# ───────── Фіг. 4: ключ ідемпотентності знешкоджує дубль ─────────
def fig_idempotency():
    W, H = 1180, 466
    f = []

    f.append(fitbox(40, 92, 184, 46, "доставка 1", size=13, bold=True,
                    fill=BLUEBG, stroke=NEG, color=INK, sw=1.6))
    f.append(fitbox(40, 300, 184, 46, "доставка 2 (дубль)", size=12.5, bold=True,
                    fill=BLUEBG, stroke=NEG, color=INK, sw=1.6))
    f.append(arrow(224, 115, 344, 178, color=NEG, sw=2.2))
    f.append(arrow(224, 323, 344, 262, color=NEG, sw=2.2))

    f.append(fitbox(344, 150, 236, 140, "ВАРТОВИЙ:\nбачив ключ\n(sagaId, revokeAccess)?",
                    size=13, bold=True, fill=AMBERBG, stroke=AMBER, color=INK, sw=2))

    f.append(arrow(580, 184, 676, 150, color=FIELD, sw=2.2))
    f.append(fitbox(676, 116, 456, 66, "ні → виконати revokeOldKeys,\nзаписати ключ + результат",
                    size=12.5, bold=True, fill=GREENBG, stroke=FIELD, color=INK, sw=1.6))
    f.append(arrow(580, 256, 676, 300, color=MUTED, sw=2.2))
    f.append(fitbox(676, 290, 456, 66, "так → повернути збережений\nрезультат, 0 ефекту",
                    size=12.5, bold=True, fill="#efefef", stroke=MUTED, color=MUTED, sw=1.6))

    f.append(fitbox(266, 392, 628, 52,
                    "ефект стався РІВНО раз, попри дві доставки — ключ ідемпотентності знешкодив дубль",
                    size=12.5, bold=True, fill="#ffffff", stroke=INK, color=INK, sw=1.8))

    render(os.path.join(IMG, "idempotency-dedup.svg"), W, H, *f,
           title="Ключ ідемпотентності на крок: доставка «щонайменше раз», а ефект — рівно раз")


# ───── Фіг. 5 (для вставки hist-saga-origin): та сама форма, змінений сенс ─────
def fig_shape_shift():
    W, H = 1220, 680
    f = []

    # ── ЛІВА панель: 1987, одна база ──
    f.append(rect(36, 56, 560, 452, fill=BLUEBG, stroke=NEG, sw=1.8, rx=12))
    f.append(text(316, 88, "1987 · ОДНА БАЗА ДАНИХ", size=15, bold=True, color=NEG))

    # ── ПРАВА панель: 2010-ті, багато сервісів ──
    f.append(rect(624, 56, 560, 452, fill=AMBERBG, stroke=AMBER, sw=1.8, rx=12))
    f.append(text(904, 88, "2010-ті · БАГАТО СЕРВІСІВ", size=15, bold=True, color=AMBER))

    # три смуги-порівняння: ворог / компенсація / мета (спільні підписи по центру кожної панелі)
    for cy, s in [(122, "ВОРОГ"), (232, "КОМПЕНСАЦІЯ — ЦЕ"), (344, "МЕТА Й ПРЕМІСА")]:
        f.append(text(316, cy, s, size=12.5, bold=True, color=MUTED))
        f.append(text(904, cy, s, size=12.5, bold=True, color=MUTED))

    left = [
        (132, 70, "довга транзакція\nтримає замки годинами"),
        (244, 70, "сама транзакція БД —\nзустрічний запис у тій самій базі"),
        (356, 88, "віддати замки, підняти конкурентність;\nусі кроки зворотні за замовчуванням"),
    ]
    for y, h, s in left:
        f.append(fitbox(60, y, 512, h, s, size=13.5, bold=True,
                        fill="#ffffff", stroke=NEG, color=INK, sw=1.6))

    right = [
        (132, 70, "спільної транзакції нема:\n2PC крізь сервіси — глухий кут"),
        (244, 70, "семантична дія в іншому сервісі:\n«поверни кошти», «звільни резерв»"),
        (356, 88, "узгодити те, чого не замкнути разом;\nдехто з кроків — незворотний"),
    ]
    for y, h, s in right:
        f.append(fitbox(648, y, 512, h, s, size=13.5, bold=True,
                        fill="#ffffff", stroke=AMBER, color=INK, sw=1.6))

    # ── нижня стрічка: класика → доробок Річардсона ──
    f.append(fitbox(150, 556, 360, 60, "класика 1987:\nусі кроки компенсовні",
                    size=13.5, bold=True, fill=BLUEBG, stroke=NEG, color=INK, sw=1.8))
    f.append(arrow(518, 586, 684, 586, color=INK, sw=2.8))
    f.append(fitbox(690, 556, 380, 60, "доробок Річардсона:\nзворотні · ПІВОТ · повторювані",
                    size=13.5, bold=True, fill=AMBERBG, stroke=POS, color=INK, sw=2))
    f.append(text(610, 650,
                  "Незворотні кроки розподіленого світу дописали до класики півот.",
                  size=13.5, bold=True, color=INK))

    render(os.path.join(IMG, "saga-shape-shift.svg"), W, H, *f,
           title="Та сама форма саги — інші ворог і сенс компенсації")


if __name__ == "__main__":
    fig_spine()
    fig_two_failures()
    fig_outbox()
    fig_idempotency()
    fig_shape_shift()
    print("OK: saga-spine.svg, two-failures.svg, outbox-atomic.svg, idempotency-dedup.svg, saga-shape-shift.svg")
