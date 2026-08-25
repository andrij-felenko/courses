# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_scatter_vs_layer():
    """Ліворуч: три входи дублюють оркестрацію. Праворуч: єдиний шар операцій."""
    W, H = 900, 470
    frags = []
    frags.append(text(W / 2, 30, "Без шару операції розповзаються; із шаром — сходяться в одну точку",
                      size=16, bold=True))

    # ── ЛІВОРУЧ: без сервісного шару ──
    entries = ["веб-\nконтролер", "REST-\nендпойнт", "нічне\nзавдання"]
    lx = 120
    for i, e in enumerate(entries):
        yy = 110 + i * 96
        b, _, _ = textbox(lx, yy, e, size=12, min_w=120, fill="#f4f6f8", stroke=LINE)
        frags.append(b)
        # кожен веде власну стрілку до бази — дубльована оркестрація
        frags.append(arrow(lx + 66, yy, 300, yy, color=POS, sw=1.8))
    dbL, _, _ = textbox(360, 206, "домен + база", size=12, min_w=130, fill="#eafaf1", stroke=FIELD)
    frags.append(dbL)
    frags.append(text(230, 400, "правило «розмісти замовлення»\nповторене тричі, розходиться",
                      size=12, color=POS, bold=True))

    # роздільник
    frags.append(line(W / 2, 60, W / 2, 430, color=LINE, sw=1, dash="2 4"))

    # ── ПРАВОРУЧ: із сервісним шаром ──
    rx = 560
    for i, e in enumerate(entries):
        yy = 110 + i * 96
        b, _, _ = textbox(rx, yy, e, size=12, min_w=120, fill="#f4f6f8", stroke=LINE)
        frags.append(b)
        frags.append(arrow(rx + 66, yy, 720, 206, color=MUTED, sw=1.6))
    svc, _, _ = textbox(775, 206, "сервісний шар\nplaceOrder()", size=13, bold=True,
                        min_w=150, fill="#fff7e6", stroke="#d68910")
    frags.append(svc)
    frags.append(arrow(775, 246, 775, 316, color=INK, sw=2))
    dbR, _, _ = textbox(775, 350, "домен + база", size=12, min_w=130, fill="#eafaf1", stroke=FIELD)
    frags.append(dbR)
    frags.append(text(700, 420, "правило живе в одному місці,\nусі входи кличуть його",
                      size=12, color="#b9770e", bold=True))

    render(os.path.join(IMG, "scatter-vs-layer.svg"), W, H, *frags)


def fig_two_logics():
    """Сервіс тримає ЛОГІКУ ЗАСТОСУНКУ (оркестрацію), домен — ЛОГІКУ ПРЕДМЕТА (правила)."""
    W, H = 860, 430
    frags = []
    frags.append(text(W / 2, 30, "Дві різні логіки: сервіс диригує, домен вирішує",
                      size=16, bold=True))

    # верхня рамка — логіка застосунку (сервіс)
    svc, _, _ = textbox(W / 2, 130, "Сервісний шар — логіка ЗАСТОСУНКУ", size=14, bold=True,
                        min_w=560, fill="#fff7e6", stroke="#d68910")
    frags.append(svc)
    steps = ["відкрити транзакцію", "завантажити дані", "спитати домен", "зберегти", "сповістити"]
    sx0 = 150
    for i, s in enumerate(steps):
        xx = sx0 + i * 140
        c, _, _ = textbox(xx, 210, s, size=11, min_w=120, fill="#fffaf0", stroke="#e0b060")
        frags.append(c)
        if i < len(steps) - 1:
            frags.append(arrow(xx + 62, 210, xx + 78, 210, color="#b9770e", sw=1.6))

    # стрілка «спитай домен» униз
    frags.append(arrow(430, 236, 430, 300, color=INK, sw=2))
    frags.append(text(500, 270, "делегує правила →", size=12, color=INK))

    # нижня рамка — логіка предмета (домен)
    dom, _, _ = textbox(W / 2, 350, "Модель домену — логіка ПРЕДМЕТА\n"
                        "чи додатна сума · чи можна скасувати · як рахувати знижку",
                        size=13, min_w=560, fill="#eafaf1", stroke=FIELD)
    frags.append(dom)

    render(os.path.join(IMG, "two-logics.svg"), W, H, *frags)


def fig_transaction():
    """Один сценарій = одна одиниця роботи: кілька кроків усередині однієї межі."""
    W, H = 820, 340
    frags = []
    frags.append(text(W / 2, 30, "Одна операція сервісу — одна транзакція на всі кроки",
                      size=16, bold=True))

    # рамка транзакції охоплює кроки
    frags.append(rect(70, 95, 680, 150, fill="#f7fbff", stroke=NEG, sw=2, rx=10))
    frags.append(text(90, 116, "placeOrder(): одна транзакція", size=13, bold=True,
                      color=NEG, anchor="start"))

    steps = ["списати\nтовар зі\nскладу", "створити\nзамовлення", "зняти\nоплату"]
    sx0 = 190
    for i, s in enumerate(steps):
        xx = sx0 + i * 190
        b, _, _ = textbox(xx, 180, s, size=12, min_w=140, fill=BG, stroke=INK)
        frags.append(b)
        if i < len(steps) - 1:
            frags.append(arrow(xx + 72, 180, xx + 118, 180, color=INK, sw=1.8))

    frags.append(text(W / 2, 285,
                      "усе трьома кроками закріплюється разом — або жоден не лишається",
                      size=13, color=NEG, bold=True))
    frags.append(text(W / 2, 312,
                      "оплата впала на кроці 3 → склад і замовлення відкочуються назад",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "transaction.svg"), W, H, *frags)


def fig_orchestration_flow():
    """placeOrder(): порядок кроків усередині транзакції; збій оплати відкочує все."""
    W, H = 900, 430
    frags = []
    frags.append(text(W / 2, 30, "placeOrder(): порядок кроків у межах однієї транзакції",
                      size=16, bold=True))

    # рамка транзакції охоплює всі кроки оркестрації
    frags.append(rect(60, 70, 660, 250, fill="#f7fbff", stroke=NEG, sw=2, rx=10))
    frags.append(text(80, 92, "одна одиниця роботи — BEGIN … COMMIT", size=12, bold=True,
                      color=NEG, anchor="start"))

    steps = [
        "дістати кошик\nзі сховища",
        "checkout():\nдомен рахує суму",
        "зняти оплату\nчерез шлюз",
        "зберегти\nзамовлення",
    ]
    sx0 = 175
    for i, s in enumerate(steps):
        yy = 150 + i * 42
        b, _, _ = textbox(300, yy, s, size=11, min_w=230, fill=BG, stroke=INK)
        frags.append(b)
        if i < len(steps) - 1:
            frags.append(arrow(300, yy + 16, 300, yy + 26, color=INK, sw=1.6))

    # гілка збою оплати — відкіт (виходить від кроку «зняти оплату», y≈234)
    frags.append(arrow(418, 234, 545, 234, color=POS, sw=2))
    fail, _, _ = textbox(605, 234, "оплата впала", size=12, color=POS, bold=True,
                         min_w=120, fill=BG, stroke=POS)
    frags.append(fail)
    frags.append(arrow(605, 251, 605, 288, color=POS, sw=2))
    rb, _, _ = textbox(605, 305, "ROLLBACK усіх кроків", size=12, bold=True,
                       min_w=170, fill="#fdecea", stroke=POS, color=POS)
    frags.append(rb)

    # після успіху — поза транзакцією
    frags.append(arrow(300, 320, 300, 356, color=MUTED, sw=1.8))
    ok, _, _ = textbox(300, 380, "COMMIT → лист-підтвердження\n(уже ПОЗА транзакцією)",
                       size=11, min_w=300, fill="#eafaf1", stroke=FIELD)
    frags.append(ok)

    render(os.path.join(IMG, "orchestration-flow.svg"), W, H, *frags)


def fig_idempotency():
    """Ключ ідемпотентності: перший запит працює, повтор віддає збережений результат."""
    W, H = 880, 360
    frags = []
    frags.append(text(W / 2, 30, "Ключ ідемпотентності: перевір ПЕРЕД записом",
                      size=16, bold=True))

    # вхід
    inb, _, _ = textbox(120, 120, "запит + key\nab-12-cd", size=12, min_w=130,
                        fill="#f4f6f8", stroke=LINE)
    frags.append(inb)
    frags.append(arrow(186, 120, 250, 120, color=INK, sw=1.8))

    # розвилка
    q, _, _ = textbox(330, 120, "цей key\nуже бачили?", size=12, min_w=140,
                      fill="#fff7e6", stroke="#d68910", bold=True)
    frags.append(q)

    # НІ → виконати, зберегти під ключем
    frags.append(arrow(400, 120, 500, 120, color=FIELD, sw=2))
    frags.append(text(450, 104, "ні", size=12, color=FIELD, bold=True))
    no, _, _ = textbox(600, 120, "виконати placeOrder,\nзберегти результат\nпід ключем",
                       size=11, min_w=210, fill="#eafaf1", stroke=FIELD)
    frags.append(no)

    # ТАК → віддати збережене, нічого не роблячи
    frags.append(arrow(330, 152, 330, 230, color=NEG, sw=2))
    frags.append(text(360, 195, "так (подвійний клік)", size=12, color=NEG, bold=True,
                      anchor="start"))
    yes, _, _ = textbox(600, 250, "віддати ТОЙ САМИЙ результат,\nоплату НЕ знімати вдруге",
                        size=11, min_w=280, fill="#eaf0fd", stroke=NEG)
    frags.append(yes)
    frags.append(arrow(430, 250, 458, 250, color=NEG, sw=2))
    dup, _, _ = textbox(360, 250, "збережене\nпід ab-12-cd", size=11, min_w=130,
                        fill=BG, stroke=NEG)
    frags.append(dup)

    render(os.path.join(IMG, "idempotency.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_scatter_vs_layer()
    fig_two_logics()
    fig_transaction()
    fig_orchestration_flow()
    fig_idempotency()
    print("ok")
