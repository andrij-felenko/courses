# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: латентність ≠ пропускна здатність ───────────────────────────────
# Два різні питання. Латентність: скільки чекати ОДНУ відповідь (час одного
# кадру). Пропускна здатність: скільки відповідей за секунду (потік кадрів).
# Конвеєр дає високий потік, але кожна деталь усе одно йде довго — тому для
# керування важлива саме затримка одного, а не сумарний потік.
def fig_latency_vs_throughput():
    W, H = 760, 300
    p = []
    p.append(text(W / 2, 30, "Дві різні мірки одного інференсу", size=18, bold=True))

    # ЛІВОРУЧ — латентність: одна деталь від входу до виходу
    lx = 40
    p.append(text(lx + 150, 66, "Латентність", size=15, bold=True, color=NEG))
    p.append(text(lx + 150, 86, "час однієї відповіді", size=12, color=MUTED))
    y = 130
    p.append(rect(lx, y, 60, 46, fill="#eef4ff", stroke=NEG, sw=2, rx=8))
    p.append(text(lx + 30, y + 28, "вхід", size=12, color=NEG))
    p.append(arrow(lx + 66, y + 23, lx + 224, y + 23, color=NEG, sw=2.4))
    p.append(rect(lx + 230, y, 70, 46, fill="#eef4ff", stroke=NEG, sw=2, rx=8))
    p.append(text(lx + 265, y + 28, "відповідь", size=11, color=NEG))
    p.append(text(lx + 148, y + 66, "◄─ 33 мс ─►", size=13, color=NEG, bold=True))
    p.append(text(lx + 148, y + 92, "коротша = швидша реакція", size=11, color=MUTED))

    # роздільник
    p.append(line(W / 2, 56, W / 2, H - 20, color="#d0d0d0", sw=1.4, dash="5 5"))

    # ПРАВОРУЧ — пропускна: багато деталей за секунду (конвеєр)
    rx = W / 2 + 40
    p.append(text(rx + 150, 66, "Пропускна здатність", size=15, bold=True, color=FIELD))
    p.append(text(rx + 150, 86, "відповідей за секунду", size=12, color=MUTED))
    yy = 128
    for i in range(5):
        cx = rx + 20 + i * 58
        p.append(rect(cx, yy, 44, 50, fill="#eafbf0", stroke=FIELD, sw=1.8, rx=7))
        p.append(text(cx + 22, yy + 30, "▮", size=15, color=FIELD))
    p.append(text(rx + 150, yy + 70, "багато нараз → 60 за сек", size=12, color=FIELD, bold=True))
    p.append(text(rx + 150, yy + 96, "але кожна все одно чекає своє", size=11, color=MUTED))

    render(os.path.join(OUT, "latency-vs-throughput.svg"), W, H, *p)


# ── Фігура 2: куди тече час — увесь ланцюг, не лише мережа ────────────────────
# Латентність кадру — це не «час forward-проходу», а сума ланок: захоплення,
# підготовка, сам прохід мережі, розбір виходу, дія. Модель — часто НЕ найбільша
# ланка; бюджет 33 мс (30 к/с) ділиться на весь конвеєр.
def fig_where_time_goes():
    W, H = 780, 320
    p = []
    p.append(text(W / 2, 30, "Куди тече час одного кадру (бюджет 33 мс)", size=18, bold=True))

    # смуга-конвеєр, ширина ланки ~ частка часу
    stages = [
        ("захоплення\nкадру", 90, "#f4f6f8", INK),
        ("підготовка\n(масштаб, норм.)", 150, "#eafbf0", FIELD),
        ("прохід мережі\nforward", 300, "#eef4ff", NEG),
        ("розбір\nвиходу (NMS)", 120, "#fdf0e6", "#b9770e"),
        ("дія\n(команда)", 70, "#f4f6f8", INK),
    ]
    x = 30
    y = 90
    h = 78
    total = sum(w for _, w, _, _ in stages)
    for label, w, fill, col in stages:
        p.append(rect(x, y, w, h, fill=fill, stroke=LINE, sw=1.6, rx=8))
        p.append(mtext(x + w / 2, y + h / 2 - 4, label, size=12, color=col, bold=True))
        x += w + 6

    # шкала часу під смугою
    ty = y + h + 34
    p.append(line(30, ty, 30 + total + 24, ty, color=MUTED, sw=1.4))
    p.append(text(30, ty + 22, "0 мс", size=12, color=MUTED, anchor="start"))
    p.append(text(30 + total + 24, ty + 22, "33 мс", size=12, color=MUTED, anchor="end"))
    p.append(text(W / 2, ty + 22, "весь ланцюг мусить влізти в один інтервал", size=12, color=MUTED))

    # висновок
    box = fitbox(90, ty + 44, W - 180, 44,
                 "Затримка = сума ВСІХ ланок. Мережа — лише одна з них; часто\nпідготовка й розбір з’їдають не менше за сам прохід.",
                 size=12.5, fill="#fff9e6", stroke="#b9770e", color=INK)
    p.append(box)

    render(os.path.join(OUT, "where-time-goes.svg"), W, H, *p)


# ── Фігура 3: пам'ять чи лічба — що тримає forward-прохід ─────────────────────
# Для одного входу (batch=1) прохід часто впирається не в кількість множень,
# а в ЧАС ПРОЧИТАТИ ВАГИ з пам'яті. Дві межі: лічильна (FLOPs/швидкість) і
# пам'ятева (байти ваг/пропускна). Реальний час = більша з двох. Малий вхід →
# лічильники простоюють, чекаючи ваги; менші ваги (квантування) б'ють прямо в межу.
def fig_memory_vs_compute():
    W, H = 780, 330
    p = []
    p.append(text(W / 2, 30, "Що тримає прохід: лічба множень чи читання ваг", size=18, bold=True))

    # дві вертикальні межі-стовпчики
    baseX = 120
    y0 = 250      # низ
    # компонент 1: лічба (менша) — стовпчик коротший
    c1x = baseX
    p.append(rect(c1x, y0 - 70, 130, 70, fill="#eef4ff", stroke=NEG, sw=2, rx=8))
    p.append(mtext(c1x + 65, y0 - 42, "лічба множень\n(FLOPs ÷ швидкість)", size=12, color=NEG, bold=True))
    p.append(text(c1x + 65, y0 + 22, "≈ 5 мс", size=13, color=NEG, bold=True))

    # компонент 2: читання ваг (більша) — стовпчик вищий, він і диктує
    c2x = baseX + 330
    p.append(rect(c2x, y0 - 150, 130, 150, fill="#fdecea", stroke=POS, sw=2.4, rx=8))
    p.append(mtext(c2x + 65, y0 - 95, "читання ваг\n(байти ÷ пропускна)", size=12, color=POS, bold=True))
    p.append(text(c2x + 65, y0 + 22, "≈ 12 мс", size=13, color=POS, bold=True))

    # стрілка «час = більша з двох»
    p.append(line(c1x, y0 + 44, c2x + 130, y0 + 44, color=MUTED, sw=1.2, dash="4 4"))
    p.append(text(W / 2, y0 + 66, "реальний час ≈ БІЛЬША з двох = 12 мс (впертися в пам'ять)",
                  size=13, color=INK, bold=True))

    # підказка збоку
    box = fitbox(W / 2 - 150, 58, 300, 40,
                 "batch = 1: лічильники простоюють,\nчекаючи, поки приїдуть ваги",
                 size=12, fill="#f4f6f8", stroke=LINE, color=MUTED)
    p.append(box)

    render(os.path.join(OUT, "memory-vs-compute.svg"), W, H, *p)


# ── Фігура 4 (вставка hist): переселення інференсу з хмари на борт ────────────
# Дуга історії: спершу все рахували в хмарі (важке залізо — GPU-ферми), тоді
# з'явилися спеціалізовані прискорювачі інференсу, і врешті модель переїхала на
# сам апарат. Дві сили тягли її туди: латентність (немає часу на мережу) і
# приватність (дані не покидають пристрій).
def fig_cloud_to_edge():
    W, H = 820, 360
    p = []
    p.append(text(W / 2, 30, "Куди переїхав інференс: хмара → прискорювач → борт", size=18, bold=True))

    # три стани зліва направо, кожен — рамка з роком і суттю
    y = 92
    h = 96
    # 1) ХМАРА — важке залізо
    x1 = 30
    w1 = 230
    p.append(rect(x1, y, w1, h, fill="#eef4ff", stroke=NEG, sw=2, rx=10))
    p.append(mtext(x1 + w1 / 2, y + 30, "ХМАРА\n(дата-центр)", size=13, color=NEG, bold=True))
    p.append(mtext(x1 + w1 / 2, y + 66, "GPU-ферми, кіловати\nкадр летить туди й назад", size=11, color=MUTED))

    # 2) ПРИСКОРЮВАЧ — окремий чип під інференс
    x2 = x1 + w1 + 40
    w2 = 230
    p.append(rect(x2, y, w2, h, fill="#eafbf0", stroke=FIELD, sw=2, rx=10))
    p.append(mtext(x2 + w2 / 2, y + 30, "ПРИСКОРЮВАЧ\nінференсу", size=13, color=FIELD, bold=True))
    p.append(mtext(x2 + w2 / 2, y + 66, "спец-ASIC / модуль\nвати, не кіловати", size=11, color=MUTED))

    # 3) БОРТ — на самому апараті
    x3 = x2 + w2 + 40
    w3 = 220
    p.append(rect(x3, y, w3, h, fill="#fdf0e6", stroke=POS, sw=2.2, rx=10))
    p.append(mtext(x3 + w3 / 2, y + 30, "БОРТ\n(on-device)", size=13, color=POS, bold=True))
    p.append(mtext(x3 + w3 / 2, y + 66, "чип у самому апараті\nмілівати, batch = 1", size=11, color=MUTED))

    # стрілки переходу
    p.append(arrow(x1 + w1, y + h / 2, x2, y + h / 2, color=INK, sw=2.4))
    p.append(arrow(x2 + w2, y + h / 2, x3, y + h / 2, color=INK, sw=2.4))

    # дві сили, що тягнуть праворуч (на борт)
    fy = y + h + 46
    box = fitbox(30, fy, W - 60, 52,
                 "Дві сили тягнуть інференс на борт: ЛАТЕНТНІСТЬ (немає часу гнати кадр у хмару\nй чекати відповідь) і ПРИВАТНІСТЬ (сирі дані не покидають пристрій).",
                 size=13, fill="#fff9e6", stroke="#b9770e", color=INK)
    p.append(box)

    # підпис-шкала часу під дугою
    ly = fy + 74
    p.append(line(30, ly, W - 30, ly, color=MUTED, sw=1.3))
    p.append(text(x1 + w1 / 2, ly + 20, "2012 — AlexNet на 2 GPU", size=11, color=MUTED))
    p.append(text(x2 + w2 / 2, ly + 20, "2015 TPU · 2015 Jetson TX1", size=11, color=MUTED))
    p.append(text(x3 + w3 / 2, ly + 20, "2018–19 Edge TPU, on-device", size=11, color=MUTED))

    render(os.path.join(OUT, "cloud-to-edge.svg"), W, H, *p)


if __name__ == "__main__":
    fig_latency_vs_throughput()
    fig_where_time_goes()
    fig_memory_vs_compute()
    fig_cloud_to_edge()
    print("ok")
