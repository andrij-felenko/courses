# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: дерево тактик розгортуваності (дві родини) ─────────────────────
def fig_deploy_tree():
    W, H = 900, 470
    frags = []
    # корінь
    root, rw, rh = textbox(W / 2, 66, "Завести зміну легко й безпечно", size=16, bold=True,
                           fill="#eef4ff", stroke=NEG, sw=2, pad=14)
    frags.append(root)

    cols = [
        ("Керувати конвеєром\nдоставки",
         ["Конвеєр доставки", "Малі незалежні одиниці", "Автоматичні тести"], NEG),
        ("Керувати розгорнутими\nсистемами",
         ["Почергове оновлення", "Синьо-зелене", "Канаркове", "Прапорець можливості"], FIELD),
    ]
    n = len(cols)
    colw = W / n
    top_y = 185
    for i, (head, items, col) in enumerate(cols):
        cx = colw * i + colw / 2
        frags.append(line(W / 2, 66 + rh / 2, cx, top_y - 30, color=MUTED, sw=1.4))
        hb, hw, hh = textbox(cx, top_y, head, size=14, bold=True, fill="#fbfbfb",
                             stroke=col, sw=2, pad=12, min_w=colw - 120)
        frags.append(hb)
        yy = top_y + hh / 2 + 26
        for it in items:
            frags.append(fitbox(cx - (colw - 180) / 2, yy, colw - 180, 38, it, size=13,
                                fill=FILL, stroke=col, sw=1.4))
            yy += 48
    render(os.path.join(IMG, 'deploy-tree.svg'), W, H, *frags,
           title="Дві родини тактик розгортуваності")


# ── Фігура 2: три стратегії підміни версії ──────────────────────────────────
def fig_deploy_strategies():
    W, H = 960, 430
    frags = []
    panelw = W / 3
    old_c = MUTED     # стара версія — сіра
    new_c = FIELD     # нова версія — зелена

    def node(cx, cy, label, col):
        return circle(cx, cy, 17, fill="#f6faf7" if col == FIELD else "#f3f4f6",
                      stroke=col, sw=2) + text(cx, cy + 5, label, size=13, bold=True, color=col)

    # ── Панель 1: почергове оновлення ──
    p1 = panelw * 0 + panelw / 2
    frags.append(text(p1, 62, "Почергове оновлення", size=14, bold=True))
    frags.append(text(p1, 84, "вузли заміняють по одному", size=11, color=MUTED))
    row_y = 150
    xs1 = [p1 - 70, p1 - 24, p1 + 22, p1 + 68]
    states = [new_c, new_c, old_c, old_c]  # два вже нові, два ще старі
    labs = ["v2", "v2", "v1", "v1"]
    for x, col, lb in zip(xs1, states, labs):
        frags.append(node(x, row_y, lb, col))
    frags.append(text(p1, 210, "живі завжди; ще й сумісність", size=11, color=INK))
    frags.append(text(p1, 232, "двох версій разом", size=11, color=INK))
    frags.append(fitbox(p1 - 100, 262, 200, 34, "ощадливо; відкіт поступовий",
                        size=11, fill="#f6faf7", stroke=new_c, sw=1.3))

    # роздільники
    frags.append(line(panelw, 46, panelw, H - 20, color="#d0d5db", sw=1.2, dash="5,5"))
    frags.append(line(panelw * 2, 46, panelw * 2, H - 20, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── Панель 2: синьо-зелене ──
    p2 = panelw * 1 + panelw / 2
    frags.append(text(p2, 62, "Синьо-зелене", size=14, bold=True))
    frags.append(text(p2, 84, "два повні середовища", size=11, color=MUTED))
    # маршрутизатор
    rt, rtw, rth = textbox(p2, 128, "маршрут", size=12, bold=True, fill="#eef4ff",
                           stroke=NEG, sw=1.8, pad=8)
    frags.append(rt)
    envg = fitbox(p2 - 96, 186, 82, 46, "зелене\nv1 (живе)", size=11,
                  fill="#f3f4f6", stroke=old_c, sw=1.6)
    envb = fitbox(p2 + 14, 186, 82, 46, "синє\nv2 (нове)", size=11,
                  fill="#f6faf7", stroke=new_c, sw=1.6)
    frags.append(envg)
    frags.append(envb)
    frags.append(line(p2, 128 + rth / 2, p2 - 55, 186, color=MUTED, sw=1.6))
    frags.append(arrow(p2, 128 + rth / 2, p2 + 55, 186, color=new_c, sw=1.8))
    frags.append(fitbox(p2 - 96, 262, 192, 34, "відкіт миттєвий; ×2 ресурси",
                        size=11, fill="#f6faf7", stroke=new_c, sw=1.3))

    # ── Панель 3: канаркове ──
    p3 = panelw * 2 + panelw / 2
    frags.append(text(p3, 62, "Канаркове", size=14, bold=True))
    frags.append(text(p3, 84, "спершу мала частка людей", size=11, color=MUTED))
    frags.append(fitbox(p3 - 40, 118, 80, 34, "1%\nкористувачів", size=11,
                        fill="#f6faf7", stroke=new_c, sw=1.4))
    frags.append(arrow(p3, 154, p3 - 46, 190, color=new_c, sw=1.8))
    frags.append(arrow(p3, 154, p3 + 46, 190, color=old_c, sw=1.6))
    frags.append(node(p3 - 46, 208, "v2", new_c))
    frags.append(node(p3 + 46, 208, "v1", old_c))
    frags.append(text(p3, 244, "збій б'є по 1%, не по всіх", size=11, color=INK))
    frags.append(fitbox(p3 - 104, 262, 208, 34, "найобережніше; складна маршрутизація",
                        size=11, fill="#f6faf7", stroke=new_c, sw=1.3))

    render(os.path.join(IMG, 'deploy-strategies.svg'), W, H, *frags,
           title="Три стратегії підміни версії без простою")


# ── Фігура 3: дві родини експлуатованості (бачу → втручаюсь) ─────────────────
def fig_operability_families():
    W, H = 940, 430
    frags = []
    box_w = 320
    rung_h = 54

    # ЛІВА колонка: спостережуваність
    lx = 50
    frags.append(text(lx + box_w / 2, 60, "Спостережуваність", size=15, bold=True))
    frags.append(text(lx + box_w / 2, 82, "зробити стан ВИДИМИМ", size=11, color=MUTED))
    obs = [
        ("Логи", "події з часом і контекстом", NEG),
        ("Метрики", "числа-пульс: помилки, затримка", NEG),
        ("Перевірка здоров'я", "«ти справді обслуговуєш?»", NEG),
        ("Наскрізне трасування", "де саме застряг запит", NEG),
    ]
    top = 108
    for i, (nm, desc, col) in enumerate(obs):
        yy = top + i * (rung_h + 12)
        frags.append(rect(lx, yy, box_w, rung_h, fill="#eef4ff", stroke=col, sw=1.6, rx=7))
        frags.append(text(lx + 16, yy + 23, nm, size=13, bold=True, color=INK, anchor="start"))
        frags.append(text(lx + 16, yy + 42, desc, size=11, color=MUTED, anchor="start"))

    # ПРАВА колонка: керованість
    rx = W - box_w - 50
    frags.append(text(rx + box_w / 2, 60, "Керованість", size=15, bold=True))
    frags.append(text(rx + box_w / 2, 82, "дати ВАЖЕЛІ впливу", size=11, color=MUTED))
    ctl = [
        ("Зовнішня конфігурація", "пороги й адреси поза кодом", FIELD),
        ("Прапорці можливостей", "вимкнути функцію на ходу", FIELD),
        ("Плавна деградація", "лишити головне, згасити другорядне", FIELD),
        ("Керовані команди", "«прибери вузол», «злий кеш»", FIELD),
    ]
    for i, (nm, desc, col) in enumerate(ctl):
        yy = top + i * (rung_h + 12)
        frags.append(rect(rx, yy, box_w, rung_h, fill="#f6faf7", stroke=col, sw=1.6, rx=7))
        frags.append(text(rx + 16, yy + 23, nm, size=13, bold=True, color=INK, anchor="start"))
        frags.append(text(rx + 16, yy + 42, desc, size=11, color=MUTED, anchor="start"))

    # стрілка «бачу → втручаюсь» посередині, у вільному коридорі між колонками
    mid_x = (lx + box_w + rx) / 2
    mid_y = top + 2 * (rung_h + 12)
    frags.append(arrow(lx + box_w + 12, mid_y, rx - 12, mid_y, color=INK, sw=2.2))
    frags.append(text(mid_x, mid_y - 16, "бачу →", size=12, bold=True, color=INK))
    frags.append(text(mid_x, mid_y + 26, "втручаюсь", size=12, bold=True, color=INK))

    render(os.path.join(IMG, 'operability-families.svg'), W, H, *frags,
           title="Дві половини експлуатованості")


# ── Фігура 4 (вставка hist): часова смуга шляху розгортуваності в канон ──────
def fig_deployability_timeline():
    W, H = 940, 760
    frags = []
    spine_x = 250          # вертикальний хребет із роками
    top = 96
    gap = 104              # відстань між віхами

    milestones = [
        ("1998", "Класичний перелік «-ilities»",
         "продуктивність, доступність, змінюваність…\nрозгортуваності НЕМАЄ — софт возять коробкою", MUTED),
        ("2001", "Agile-маніфест",
         "перший принцип: «рання й БЕЗПЕРЕРВНА\nпоставка» — попит на часті релізи", NEG),
        ("2004", "Конвеєр доставки",
         "Фарлі й Рікмаєр (ThoughtWorks); публічно —\nдопис Ньюмена 2005: техніка автоматизації", NEG),
        ("2009", "DevOps",
         "«10+ Deploys per Day» Оллспо й Гаммонда;\nDevOpsDays Дебуа — культура зруйнувала стіну", FIELD),
        ("2010", "«Continuous Delivery»",
         "Гамбл і Фарлі: конвеєр у центрі; час від\nкоміту до продакшену стає головним числом", FIELD),
        ("2018", "«Accelerate»",
         "Форсґрен, Гамбл, Кім: 4 показники;\nдоведено — швидкість і надійність союзники", POS),
        ("2021", "Окремий розділ «Deployability»",
         "4-те вид. Software Architecture in Practice:\nатрибут визнано — поряд з energy, safety", POS),
    ]

    # хребет
    y_first = top
    y_last = top + (len(milestones) - 1) * gap
    frags.append(line(spine_x, y_first - 30, spine_x, y_last + 30, color="#c9ced6", sw=3))

    for i, (yr, head, desc, col) in enumerate(milestones):
        cy = top + i * gap
        # вузол-рік на хребті
        frags.append(circle(spine_x, cy, 30, fill="#f6faf7" if col == FIELD else
                            ("#fdecea" if col == POS else ("#eef4ff" if col == NEG else "#f3f4f6")),
                            stroke=col, sw=2.4))
        frags.append(text(spine_x, cy + 5, yr, size=14, bold=True, color=col))
        # картка праворуч — заголовок + опис, у рамці textbox (текст ніколи не вилазить)
        card_x = spine_x + 60
        frags.append(line(spine_x + 30, cy, card_x, cy, color=col, sw=1.8))
        hb, hw, hh = textbox(card_x + 305, cy - 16, head, size=14, bold=True,
                             fill="#fbfbfb", stroke=col, sw=1.8, pad=9, min_w=560)
        frags.append(hb)
        frags.append(text(card_x + 305, cy + 16, desc.split("\n")[0], size=11.5, color=INK))
        frags.append(text(card_x + 305, cy + 33, desc.split("\n")[1], size=11.5, color=MUTED))

    render(os.path.join(IMG, 'deployability-timeline.svg'), W, H, *frags,
           title="Шлях розгортуваності: від мовчанки до окремого атрибута")


if __name__ == "__main__":
    fig_deploy_tree()
    fig_deploy_strategies()
    fig_operability_families()
    fig_deployability_timeline()
    print("figures written to", IMG)
