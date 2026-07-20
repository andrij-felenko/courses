# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Fig 1: створити всередині (приварено) проти прийняти ззовні (гніздо) ──────
def fig_new_vs_injected():
    W, H = 1100, 560
    frags = []

    frags.append(text(W / 2, 34, "Створити всередині чи прийняти ззовні",
                      size=18, bold=True, color=INK))
    frags.append(line(W / 2, 66, W / 2, 452, color="#d0d5db", sw=1.1, dash="4,6"))

    lx, rx = W * 0.26, W * 0.74

    # ── Ліворуч: приварено ───────────────────────────────────────────────────
    frags.append(text(lx, 88, "СТВОРИТИ ВСЕРЕДИНІ", size=14, bold=True, color=POS))
    # корпус сервісу
    sb_x, sb_y, sb_w, sb_h = lx - 155, 112, 310, 240
    frags.append(rect(sb_x, sb_y, sb_w, sb_h, fill=BG, stroke=LINE, sw=1.8))
    frags.append(text(lx, sb_y + 30, "OrderService", size=14, bold=True, color=INK))
    # приварена деталь усередині
    wb, ww, wh = textbox(lx, sb_y + 150, ["new StripeGateway()", "приварено намертво"],
                         size=13, bold=True, fill="#fdecea", stroke=POS, sw=2.0, min_w=250)
    frags.append(wb)
    frags.append(text(lx, sb_y + 92, "конструктор сам майструє деталь",
                      size=11.5, color=MUTED))
    # підпис-наслідки
    frags.append(text(lx, 388, "не підміниш без правки класу", size=12.5, color=POS))
    frags.append(text(lx, 410, "не протестуєш без мережі", size=12.5, color=POS))

    # ── Праворуч: гніздо + подача ззовні ─────────────────────────────────────
    frags.append(text(rx, 88, "ПРИЙНЯТИ ЗЗОВНІ", size=14, bold=True, color=FIELD))
    # зовнішній збирач
    cr, crw, crh = textbox(rx, 130, "композиційний корінь (main)",
                           size=12, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.6, min_w=250)
    frags.append(cr)
    # корпус сервісу з гніздом
    rb_x, rb_y, rb_w, rb_h = rx - 155, 190, 310, 162
    frags.append(rect(rb_x, rb_y, rb_w, rb_h, fill=BG, stroke=LINE, sw=1.8))
    frags.append(text(rx, rb_y + 30, "OrderService(gateway)", size=14, bold=True, color=INK))
    # гніздо (пунктирне) під обіцянку
    gs_x, gs_y, gs_w, gs_h = rx - 125, rb_y + 60, 250, 62
    frags.append(('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" '
                  'fill="#e8f6ee" stroke="%s" stroke-width="2" stroke-dasharray="6,5"/>'
                  % (gs_x, gs_y, gs_w, gs_h, FIELD)))
    frags.append(mtext(rx, gs_y + gs_h / 2 - 6, ["гніздо: PaymentGateway", "(обіцянка, не продукт)"],
                       size=12, color=INK, bold=True))
    # стрілка згори від кореня у гніздо
    frags.append(arrow(rx, 130 + crh / 2 + 2, rx, rb_y - 2, color=FIELD, sw=1.8))
    frags.append(text(rx + 96, 176, "вкидає ззовні", size=11.5, color=FIELD, anchor="start"))
    # підпис-наслідки
    frags.append(text(rx, 388, "у прод — StripeGateway,", size=12.5, color=FIELD))
    frags.append(text(rx, 410, "у тест — підробку; клас не знає різниці", size=12.5, color=FIELD))

    # ── Нижня плашка ─────────────────────────────────────────────────────────
    frags.append(line(40, 476, W - 40, 476, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, 506,
                      "one рядок new всередині = вибір приварено; прийняти ззовні = вибір роблять на порозі, деталь замінна",
                      size=12.5, bold=True, color=INK))

    render(os.path.join(IMG, 'new-vs-injected.svg'), W, H, *frags)


# ── Fig 2: три способи впровадити — за моментом у житті об'єкта ───────────────
def fig_three_forms():
    W, H = 1120, 600
    frags = []

    frags.append(text(W / 2, 34, "Три способи впровадити залежність",
                      size=18, bold=True, color=INK))
    frags.append(text(W / 2, 58, "різняться тим, КОЛИ залежність приходить у життя об'єкта",
                      size=12.5, color=MUTED))

    spine_x = 205
    nodes = [
        ("народження", 170, FIELD),
        ("життя об'єкта", 330, LINE),
        ("виклик методу", 490, LINE),
    ]
    # вертикальна вісь життя
    frags.append(line(spine_x, nodes[0][1], spine_x, nodes[-1][1], color=MUTED, sw=2.0))
    for label, y, col in nodes:
        frags.append(circle(spine_x, y, 8, fill=col, stroke=col, sw=1.5))
        frags.append(text(spine_x - 20, y + 4, label, size=12.5, bold=True,
                          color=INK, anchor="end"))

    box_cx = W * 0.60
    box_w = 460
    box_left = box_cx - box_w / 2
    forms = [
        (170, FIELD, "#e8f6ee",
         "Через конструктор",
         "new Service(gateway)",
         "обов'язкова · незмінна · об'єкт завжди повний",
         "✓ типовий вибір"),
        (330, "#adb5bd", FILL,
         "Через встановлювач (сетер)",
         "service.setAuditLog(log)",
         "необов'язкова або змінна на льоту",
         "ризик: поки не встановили — порожнє поле"),
        (490, "#adb5bd", FILL,
         "Через аргумент методу",
         "service.checkout(order, clock)",
         "потрібна лише цьому виклику",
         "і щоразу інша (час, контекст запиту)"),
    ]
    for y, stroke, fill, name, code, note1, note2 in forms:
        b, bw, bh = textbox(box_cx, y, [name, code, note1, note2],
                            size=12.5, bold=False, fill=fill, stroke=stroke,
                            sw=1.8, min_w=box_w)
        # стрілка від вузла осі до лівого краю рамки
        frags.append(arrow(spine_x + 12, y, box_left - 4, y, color=stroke if stroke != "#adb5bd" else MUTED, sw=1.6))
        frags.append(b)
    # перший рядок кожної рамки — назва форми — підсвітимо жирним поверх
    for y, stroke, fill, name, code, note1, note2 in forms:
        col = FIELD if stroke == FIELD else INK
        frags.append(text(box_cx, y - 26, name, size=13, bold=True, color=col))

    # ── Нижня плашка ─────────────────────────────────────────────────────────
    frags.append(line(40, 548, W - 40, 548, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, 576,
                      "тягни до конструктора, поки можеш: обов'язкове — конструктором, необов'язкове — встановлювачем, разове — аргументом",
                      size=12.5, bold=True, color=INK))

    render(os.path.join(IMG, 'three-forms.svg'), W, H, *frags)


# ── Fig 3: штовхнути ззовні (DI) проти сам тягне з глобала (локатор) ──────────
def fig_push_vs_pull():
    W, H = 1160, 600
    frags = []

    frags.append(text(W / 2, 34, "Дві доставки залежності: подати проти витягти",
                      size=18, bold=True, color=INK))
    frags.append(text(W / 2, 58, "той самий результат у руках — різний напрямок і різна чесність",
                      size=12.5, color=MUTED))
    frags.append(line(W / 2, 74, W / 2, 496, color="#d0d5db", sw=1.1, dash="4,6"))

    lx, rx = W * 0.26, W * 0.74

    # ── Ліворуч: DI — штовхнути ззовні ───────────────────────────────────────
    frags.append(text(lx, 96, "ВПРОВАДЖЕННЯ — штовхнути ззовні", size=13.5, bold=True, color=FIELD))
    cr, crw, crh = textbox(lx, 150, "композиційний корінь", size=12, bold=True,
                           fill="#eaf0fd", stroke=NEG, sw=1.6, min_w=230)
    frags.append(cr)
    sv, svw, svh = textbox(lx, 300, ["OrderService(gateway)", "конструктор просить gateway"],
                           size=12.5, bold=True, fill="#e8f6ee", stroke=FIELD, sw=1.9, min_w=280)
    frags.append(sv)
    frags.append(arrow(lx, 150 + crh / 2 + 2, lx, 300 - svh / 2 - 2, color=FIELD, sw=1.9))
    frags.append(text(lx + 96, 228, "подає ззовні", size=11.5, color=FIELD, anchor="start"))
    frags.append(text(lx, 300 + svh / 2 + 30, "✓ залежність видно в сигнатурі",
                      size=12.5, bold=True, color=FIELD))
    frags.append(text(lx, 300 + svh / 2 + 52, "тест підставляє підробку в конструктор",
                      size=11.5, color=MUTED))

    # ── Праворуч: локатор — сам тягне з глобала ──────────────────────────────
    frags.append(text(rx, 96, "ЛОКАТОР — сам тягне з глобала", size=13.5, bold=True, color=POS))
    loc, locw, loch = textbox(rx, 150, "глобальний Locator (реєстр)", size=12, bold=True,
                              fill="#fdecea", stroke=POS, sw=1.7, min_w=250)
    frags.append(loc)
    sv2, sv2w, sv2h = textbox(rx, 300, ["OrderService()", "конструктор порожній — бреше"],
                              size=12.5, bold=True, fill=FILL, stroke=LINE, sw=1.6, min_w=280)
    frags.append(sv2)
    # смик угору (запит) і повернення вниз — чорний хід до глобала
    frags.append(arrow(rx - 22, 300 - sv2h / 2 - 2, rx - 22, 150 + loch / 2 + 2, color=POS, sw=1.8))
    frags.append(arrow(rx + 22, 150 + loch / 2 + 2, rx + 22, 300 - sv2h / 2 - 2, color=MUTED, sw=1.5))
    frags.append(text(rx - 30, 230, "смикає", size=11, color=POS, anchor="end"))
    frags.append(text(rx - 30, 246, "get()", size=11, color=POS, anchor="end"))
    frags.append(text(rx + 30, 236, "служба", size=11, color=MUTED, anchor="start"))
    frags.append(text(rx, 300 + sv2h / 2 + 30, "✗ залежність схована в тілі",
                      size=12.5, bold=True, color=POS))
    frags.append(text(rx, 300 + sv2h / 2 + 52, "тест мусить готувати глобал; збій у рантаймі",
                      size=11.5, color=MUTED))

    # ── Нижня плашка ─────────────────────────────────────────────────────────
    frags.append(line(40, 520, W - 40, 520, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, 550, "штовхнули ззовні — видно в сигнатурі;  сам смикнув із глобала — сховано",
                      size=13, bold=True, color=INK))
    frags.append(text(W / 2, 574, "обидва дають об'єктові залежність — тому двійники; чесність доставки й розводить їх",
                      size=11.5, color=MUTED))

    render(os.path.join(IMG, 'push-vs-pull.svg'), W, H, *frags)


# ── Fig 4 (вставка proj): чотири стани класу під час розплутування ───────────
def fig_untangle_arc():
    W, H = 1340, 620
    frags = []
    frags.append(text(W / 2, 32, "Один клас, чотири стани: як смики їдуть із тіла в сигнатуру",
                      size=18, bold=True))

    centers = [185, 510, 835, 1160]
    half = 135

    # композиційний корінь — з'являється аж на стадіях 3–4
    frags.append(rect(700, 58, 595, 38, fill="#eaf7ef", stroke=FIELD, sw=1.6))
    frags.append(text(997, 82, "композиційний корінь: створює й ПОДАЄ ззовні",
                      size=12.5, color=FIELD, bold=True))

    stages = ["1 · як є", "2 · смики зібрано", "3 · двері відчинено", "4 · чесно"]
    for cx, st in zip(centers, stages):
        frags.append(text(cx, 122, st, size=13, bold=True, color=INK))
        frags.append(rect(cx - half, 142, 2 * half, 226, fill=BG, stroke=LINE, sw=1.8))
        frags.append(text(cx, 166, "OrderService", size=13, bold=True))

    # ── 1 · як є: конструктор порожній, смики розсипані по тілу ──────────────
    c = centers[0]
    frags.append(rect(c - 120, 178, 240, 68, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(mtext(c, 202, ["конструктор ()", "порожній — і бреше"],
                       size=11.5, color=POS, lh=1.35))
    frags.append(rect(c - 120, 256, 240, 102, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(mtext(c, 282, ['checkout() → get("gateway")', 'checkout() → get("clock")',
                                '_audit()   → get("audit")'], size=11, color=INK, lh=1.5))
    for x in (155, 185, 215):
        frags.append(arrow(x, 370, x, 436, color=POS, sw=1.6))
    frags.append(text(243, 408, "3 смики", size=11, color=POS, anchor="start"))

    # ── 2 · смики зібрано в конструктор ─────────────────────────────────────
    c = centers[1]
    frags.append(rect(c - 120, 178, 240, 68, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(mtext(c, 198, ['ctor: get("gateway")', '      get("clock")', '      get("audit")'],
                       size=11, color=POS, lh=1.45))
    frags.append(rect(c - 120, 256, 240, 102, fill=FILL, stroke=LINE, sw=1.5))
    frags.append(mtext(c, 296, ["checkout()  — чисто", "_audit()    — чисто"],
                       size=11, color=MUTED, lh=1.6))
    for x in (480, 510, 540):
        frags.append(arrow(x, 370, x, 436, color=POS, sw=1.6))
    frags.append(text(568, 408, "з конструктора", size=11, color=POS, anchor="start"))

    # ── 3 · двері відчинено: типове значення = смик ──────────────────────────
    c = centers[2]
    frags.append(rect(c - 120, 178, 240, 68, fill="#fff8e1", stroke="#b8860b", sw=1.6))
    frags.append(mtext(c, 198, ["ctor(gateway = get(…),", "     clock   = get(…),", "     …)"],
                       size=11, color=INK, lh=1.45))
    frags.append(rect(c - 120, 256, 240, 102, fill=FILL, stroke=LINE, sw=1.5))
    frags.append(mtext(c, 296, ["старий виклик — живий", "новий — уже подає"],
                       size=11, color=MUTED, lh=1.6))
    frags.append(line(835, 370, 835, 436, color=POS, sw=1.5, dash="5,4"))
    frags.append(text(862, 408, "запасний хід", size=11, color=POS, anchor="start"))
    frags.append(arrow(930, 98, 930, 176, color=FIELD, sw=1.8))

    # ── 4 · чесно: сигнатура = список залежностей ────────────────────────────
    c = centers[3]
    frags.append(rect(c - 120, 178, 240, 68, fill="#eaf7ef", stroke=FIELD, sw=1.8))
    frags.append(mtext(c, 202, ["ctor(gateway, clock,", "     log, receipts)"],
                       size=11, color=INK, lh=1.45))
    frags.append(rect(c - 120, 256, 240, 102, fill=FILL, stroke=LINE, sw=1.5))
    frags.append(mtext(c, 296, ["import Locator", "— видалено"], size=11, color=FIELD, lh=1.6))
    frags.append(arrow(1255, 98, 1255, 176, color=FIELD, sw=1.8))

    # переходи між станами
    for x1, x2 in ((328, 367), (653, 692), (978, 1017)):
        frags.append(arrow(x1, 250, x2, 250, color=MUTED, sw=1.6))

    # глобальний реєстр — і його відсутність під стадією 4
    frags.append(rect(50, 438, 920, 46, fill="#f3f4f6", stroke=POS, sw=1.6))
    frags.append(text(510, 466, "Locator — глобальний реєстр", size=13, bold=True, color=POS))
    frags.append(rect(1025, 438, 270, 46, fill=BG, stroke="#c9ced6", sw=1.4))
    frags.append(text(1160, 466, "локатора тут уже нема", size=12, color=MUTED))

    frags.append(line(50, 520, W - 50, 520, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, 548, "На кожному кроці застосунок збирається, а тести зелені — тому крок їде окремим комітом",
                      size=13, bold=True))
    frags.append(text(W / 2, 574, "смики не зникають раптом: вони переїжджають із тіла в конструктор, тоді в типове значення, тоді геть — у корінь",
                      size=11.5, color=MUTED))

    render(os.path.join(IMG, 'untangle-arc.svg'), W, H, *frags)


# ── Fig 5 (вставка proj): чому листя першим ──────────────────────────────────
def fig_leaf_first():
    W, H = 1200, 580
    frags = []
    frags.append(text(W / 2, 32, "Батько не буває чесним, поки бреше дитина",
                      size=18, bold=True))

    # ── Рядок А: згори вниз — глухий кут ────────────────────────────────────
    frags.append(text(60, 78, "ЗГОРИ ВНИЗ — глухий кут", size=14, bold=True, color=POS, anchor="start"))

    b1, w1, _ = textbox(230, 160, ["OrderService", "ctor(gateway, clock, log)", "✓ прийняв своє"],
                        size=11.5, fill="#eaf7ef", stroke=FIELD, sw=1.6)
    frags.append(b1)
    b2, w2, _ = textbox(620, 160, ["ReceiptBuilder", "ctor() — порожній", 'get("templates")'],
                        size=11.5, fill="#fdecea", stroke=POS, sw=1.6)
    frags.append(b2)
    b3, w3, _ = textbox(990, 160, ["Locator", "глобал"], size=11.5, fill="#f3f4f6", stroke=POS, sw=1.6)
    frags.append(b3)
    frags.append(arrow(230 + w1 / 2 + 10, 160, 620 - w2 / 2 - 10, 160, color=MUTED, sw=1.7))
    frags.append(text((230 + w1 / 2 + 620 - w2 / 2) / 2, 142, "створює всередині", size=11, color=MUTED))
    frags.append(arrow(620 + w2 / 2 + 10, 160, 990 - w3 / 2 - 10, 160, color=POS, sw=1.7))
    frags.append(text((620 + w2 / 2 + 990 - w3 / 2) / 2, 142, "смикає", size=11, color=POS))

    frags.append(text(W / 2, 248, "Батько вже приймає свої три залежності — але сам майструє дитину, а та смикає з глобала.",
                      size=12.5, color=INK))
    frags.append(text(W / 2, 272, "Справжній список залежностей батька досі неповний, і тест усе ще мусить готувати глобал.",
                      size=12.5, color=MUTED))

    frags.append(line(60, 306, W - 60, 306, color="#d0d5db", sw=1.1))

    # ── Рядок Б: від листя вгору ────────────────────────────────────────────
    frags.append(text(60, 344, "ВІД ЛИСТЯ ВГОРУ — працює", size=14, bold=True, color=FIELD, anchor="start"))

    d1, v1, _ = textbox(230, 428, ["① ReceiptBuilder", "ctor(templates)", "✓ чесний"],
                        size=11.5, fill="#eaf7ef", stroke=FIELD, sw=1.6)
    frags.append(d1)
    d2, v2, _ = textbox(620, 428, ["② OrderService", "ctor(…, receipts)", "✓ повний список"],
                        size=11.5, fill="#eaf7ef", stroke=FIELD, sw=1.6)
    frags.append(d2)
    d3, v3, _ = textbox(990, 428, ["③ композиційний корінь", "тут усе й створюють"],
                        size=11.5, fill="#eaf7ef", stroke=FIELD, sw=1.8)
    frags.append(d3)
    frags.append(arrow(230 + v1 / 2 + 10, 428, 620 - v2 / 2 - 10, 428, color=FIELD, sw=1.7))
    frags.append(text((230 + v1 / 2 + 620 - v2 / 2) / 2, 410, "потреба виринає вгору", size=11, color=FIELD))
    frags.append(arrow(620 + v2 / 2 + 10, 428, 990 - v3 / 2 - 10, 428, color=FIELD, sw=1.7))
    frags.append(text((620 + v2 / 2 + 990 - v3 / 2) / 2, 410, "і далі — в корінь", size=11, color=FIELD))

    frags.append(text(W / 2, 512, "Листок чесний → батько мусить його зібрати → його власна потреба стає видимою → піднімаємо до кореня.",
                      size=12.5, color=INK))
    frags.append(text(W / 2, 540, "На кожному кроці клас, який чіпаєш, тримає ПОВНИЙ свій список — і жоден предок за нього не бреше.",
                      size=12.5, bold=True, color=INK))

    render(os.path.join(IMG, 'leaf-first.svg'), W, H, *frags)


# ── Fig 6 (вставка proj): цикл, який локатор ховав ───────────────────────────
def fig_cycle_topo():
    W, H = 1200, 620
    frags = []
    frags.append(text(W / 2, 32, "Цикл, який локатор ховав, а конструктор показує",
                      size=18, bold=True))
    frags.append(line(W / 2, 60, W / 2, 400, color="#d0d5db", sw=1.1, dash="4,6"))

    # ── Ліворуч: під локатором цикл живий ───────────────────────────────────
    lx = 300
    frags.append(text(lx, 88, "ПІД ЛОКАТОРОМ — цикл живий", size=14, bold=True, color=POS))
    a1, aw1, ah1 = textbox(lx, 150, ["Billing", 'charge() → get("notify")'],
                           size=11.5, fill="#fdecea", stroke=POS, sw=1.6)
    frags.append(a1)
    a2, aw2, ah2 = textbox(lx, 290, ["Notifier", 'send() → get("billing")'],
                           size=11.5, fill="#fdecea", stroke=POS, sw=1.6)
    frags.append(a2)
    frags.append(arrow(lx - 55, 150 + ah1 / 2 + 6, lx - 55, 290 - ah2 / 2 - 6, color=POS, sw=1.6))
    frags.append(arrow(lx + 55, 290 - ah2 / 2 - 6, lx + 55, 150 + ah1 / 2 + 6, color=POS, sw=1.6))
    frags.append(text(lx, 224, "смик", size=11, color=POS))
    frags.append(text(lx, 340, "обидва вже створені порожніми —", size=11.5, color=MUTED))
    frags.append(text(lx, 362, "смик стається аж під час виклику", size=11.5, color=MUTED))
    frags.append(text(lx, 386, "✓ працює, і цикл ніхто не бачить", size=12, bold=True, color=POS))

    # ── Праворуч: конструкторами зібрати нема як ────────────────────────────
    rx = 900
    frags.append(text(rx, 88, "КОНСТРУКТОРАМИ — зібрати нема як", size=14, bold=True, color=NEG))
    c1, cw1, ch1 = textbox(rx, 150, ["Billing", "ctor(notify: Notifier)"],
                           size=11.5, fill="#eaf0fd", stroke=NEG, sw=1.6)
    frags.append(c1)
    c2, cw2, ch2 = textbox(rx, 290, ["Notifier", "ctor(billing: Billing)"],
                           size=11.5, fill="#eaf0fd", stroke=NEG, sw=1.6)
    frags.append(c2)
    frags.append(arrow(rx - 78, 150 + ch1 / 2 + 6, rx - 78, 290 - ch2 / 2 - 6, color=NEG, sw=1.6))
    frags.append(arrow(rx + 78, 290 - ch2 / 2 - 6, rx + 78, 150 + ch1 / 2 + 6, color=NEG, sw=1.6))
    frags.append(mtext(rx, 214, ["щоб створити одного —", "треба вже мати другого"],
                       size=11, color=NEG, lh=1.35))
    frags.append(text(rx, 340, "топологічного порядку не існує:", size=11.5, color=MUTED))
    frags.append(text(rx, 362, "граф із циклом не збирається взагалі", size=11.5, color=MUTED))
    frags.append(text(rx, 386, "✗ падає ще на складанні", size=12, bold=True, color=NEG))

    # ── Два виходи ──────────────────────────────────────────────────────────
    frags.append(line(60, 424, W - 60, 424, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, 456, "Два чесні виходи", size=14, bold=True))

    e1 = fitbox(90, 476, 480, 100, ["① РОЗІРВАТИ ЦИКЛ — краще",
                                    "витягти спільне третє або пустити подію назустріч;",
                                    "цикл був справжньою вадою будови, а не дрібницею"],
                size=12, fill="#eaf7ef", stroke=FIELD, sw=1.7)
    frags.append(e1)
    e2 = fitbox(630, 476, 480, 100, ["② ПОСТАЧАЛЬНИК — коли інакше ніяк",
                                     "ctor(notify: () => Notifier) — виклик відкладено,",
                                     "але залежність ЗАДЕКЛАРОВАНА в сигнатурі"],
                size=12, fill="#fff8e1", stroke="#b8860b", sw=1.7)
    frags.append(e2)

    render(os.path.join(IMG, 'cycle-topo.svg'), W, H, *frags)


# ── Fig 7 (вставка proj): скільки екземплярів було насправді ─────────────────
def fig_lifetime_count():
    W, H = 1240, 520
    frags = []
    frags.append(text(W / 2, 32, "Скільки екземплярів роздавав локатор — і скільки вийде після правки",
                      size=18, bold=True))

    cols = [210, 620, 1030]
    heads = [("БУЛО: смик із локатора", POS), ("НЕДБАЛО: кожен майструє свій", NEG),
             ("У КОРЕНІ: створити один і подати", FIELD)]
    for cx, (h, col) in zip(cols, heads):
        frags.append(text(cx, 80, h, size=13, bold=True, color=col))
        for i, dx in enumerate((-105, 0, 105)):
            frags.append(rect(cx + dx - 47, 108, 94, 40, fill=FILL, stroke=LINE, sw=1.4))
            frags.append(text(cx + dx, 133, "сервіс %d" % (i + 1), size=11, color=INK))

    # колонка 1: три смики в один спільний кеш
    cx = cols[0]
    frags.append(rect(cx - 75, 258, 150, 42, fill="#fdecea", stroke=POS, sw=1.7))
    frags.append(text(cx, 284, "RateCache #1", size=12, bold=True, color=INK))
    for dx in (-105, 0, 105):
        frags.append(arrow(cx + dx, 152, cx + dx * 0.35, 254, color=POS, sw=1.5))
    frags.append(text(cx, 330, "кеш один на всіх", size=12, bold=True, color=INK))
    frags.append(text(cx, 354, "записав сервіс 1 — бачать усі ✓", size=11.5, color=MUTED))

    # колонка 2: кожен зі своїм
    cx = cols[1]
    for i, dx in enumerate((-105, 0, 105)):
        frags.append(rect(cx + dx - 47, 258, 94, 42, fill="#eaf0fd", stroke=NEG, sw=1.6))
        frags.append(text(cx + dx, 284, "#%d" % (i + 1), size=12, bold=True, color=INK))
        frags.append(arrow(cx + dx, 152, cx + dx, 254, color=NEG, sw=1.5))
    frags.append(text(cx, 330, "кеш розсипався на три", size=12, bold=True, color=NEG))
    frags.append(text(cx, 354, "записав сервіс 1 — не бачить ніхто ✗", size=11.5, color=MUTED))

    # колонка 3: корінь створює один і подає всім
    cx = cols[2]
    frags.append(rect(cx - 75, 258, 150, 42, fill="#eaf7ef", stroke=FIELD, sw=1.7))
    frags.append(text(cx, 284, "RateCache #1", size=12, bold=True, color=INK))
    for dx in (-105, 0, 105):
        frags.append(arrow(cx + dx * 0.35, 254, cx + dx, 152, color=FIELD, sw=1.5))
    frags.append(text(cx, 330, "кількість відтворено свідомо", size=12, bold=True, color=INK))
    frags.append(text(cx, 354, "записав сервіс 1 — бачать усі ✓", size=11.5, color=MUTED))

    frags.append(line(60, 396, W - 60, 396, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, 428, "Локатор мовчки роздавав ОДИН об'єкт на ключ — і ніде цього не писав",
                      size=13, bold=True))
    frags.append(text(W / 2, 454, "тож перед правкою полічи, скільки екземплярів було насправді, і свідомо відтвори це число в корені",
                      size=11.5, color=MUTED))
    frags.append(text(W / 2, 478, "інакше кеш, пул з'єднань чи лічильник тихо роздвоїться — код збереться, тести пройдуть, а поведінка зміниться",
                      size=11.5, color=MUTED))

    render(os.path.join(IMG, 'lifetime-count.svg'), W, H, *frags)


# ── Fig (hist): одне слово на три роботи — і скибка, названа точно ───────────
def fig_one_word_three_jobs():
    W, H = 1180, 600
    frags = []

    frags.append(text(W / 2, 34, "Одне слово на три роботи", size=18, bold=True, color=INK))

    # ── Парасолька старої назви ──────────────────────────────────────────────
    frags.append(rect(60, 70, 1060, 290, fill="#f7f8fa", stroke=MUTED, sw=1.8))
    frags.append(text(590, 106, "ІНВЕРСІЯ КЕРУВАННЯ — як її вживав Авалон", size=15, bold=True, color=INK))
    frags.append(text(590, 132, "компонентом завжди керують ззовні — і кожній із трьох робіт назва пасує однаково добре",
                      size=12, color=MUTED))

    jobs = [
        (270, ["СКЛАДАННЯ", "хто дає компонентові", "інші компоненти"], FIELD, "#eaf7ef"),
        (590, ["НАЛАШТУВАННЯ", "хто дає числа, шляхи,", "ключі й таймаути"], MUTED, BG),
        (910, ["ЖИТТЄВИЙ ЦИКЛ", "хто вирішує, коли створити,", "запустити й знищити"], MUTED, BG),
    ]
    for cx, lines, col, fill in jobs:
        b, _, _ = textbox(cx, 250, lines, size=12.5, fill=fill, stroke=col, sw=1.7, min_w=290)
        frags.append(b)

    # ── Скибка вниз: точне ім'я — лише для складання ─────────────────────────
    frags.append(arrow(270, 362, 270, 442, color=FIELD, sw=2.2))
    frags.append(arrow(590, 362, 660, 442, color=MUTED, sw=1.5))
    frags.append(arrow(910, 362, 840, 442, color=MUTED, sw=1.5))

    b, _, _ = textbox(270, 480, ["ВПРОВАДЖЕННЯ ЗАЛЕЖНОСТЕЙ", "точне ім'я — лише для ЦІЄЇ роботи"],
                      size=12.5, fill="#eaf7ef", stroke=FIELD, sw=2.0, min_w=300)
    frags.append(b)
    b, _, _ = textbox(750, 480, ["лишилися під старим прапором", "власних імен так і не дістали"],
                      size=12.5, fill="#f3f4f6", stroke=MUTED, sw=1.5, min_w=300)
    frags.append(b)

    frags.append(text(590, 552, "DI не перейменувало IoC — воно відкололо від нього ОДНУ роботу з трьох",
                      size=13, bold=True, color=INK))
    frags.append(text(590, 576, "налаштування й життєвий цикл лишилися під старою назвою",
                      size=11.5, color=MUTED))

    render(os.path.join(IMG, 'one-word-three-jobs.svg'), W, H, *frags)


# ── Fig (hist): четверта форма впорскує локатор, а не залежність ─────────────
def fig_fourth_form_lookup():
    W, H = 1240, 580
    frags = []

    frags.append(text(W / 2, 34, "Що саме доставляє четверта форма", size=18, bold=True, color=INK))
    frags.append(line(620, 64, 620, 500, color="#d0d5db", sw=1.1, dash="4,6"))

    # ── Ліворуч: через конструктор ───────────────────────────────────────────
    frags.append(text(330, 92, "ЧЕРЕЗ КОНСТРУКТОР", size=14, bold=True, color=FIELD))
    b, _, _ = textbox(330, 146, "контейнер", size=12.5, fill="#eaf0fd", stroke=NEG, sw=1.6, min_w=240)
    frags.append(b)
    frags.append(arrow(330, 166, 330, 240, color=FIELD, sw=2.0))
    frags.append(text(448, 198, "подає САМ шлюз", size=11.5, color=FIELD))
    b, _, _ = textbox(330, 270, ["OrderService", "ctor(PaymentGateway gateway)"],
                      size=12.5, fill="#eaf7ef", stroke=FIELD, sw=1.8, min_w=260)
    frags.append(b)
    frags.append(text(330, 340, "прийшла САМА залежність", size=13, bold=True, color=FIELD))
    frags.append(text(330, 366, "потребу видно в сигнатурі", size=11.5, color=MUTED))
    frags.append(text(330, 390, "шлях закінчено", size=11.5, color=MUTED))

    # ── Праворуч: через інтерфейс (Авалон) ───────────────────────────────────
    frags.append(text(910, 92, "ЧЕРЕЗ ІНТЕРФЕЙС — тип 1 (Авалон)", size=14, bold=True, color=POS))
    b, _, _ = textbox(910, 146, "контейнер", size=12.5, fill="#eaf0fd", stroke=NEG, sw=1.6, min_w=240)
    frags.append(b)
    frags.append(arrow(910, 166, 910, 240, color=POS, sw=2.0))
    frags.append(text(1064, 198, "впорскує МЕНЕДЖЕР", size=11.5, color=POS))
    b, _, _ = textbox(910, 282, ["OrderService implements Serviceable", "service(ServiceManager manager)"],
                      size=12, fill="#fdecea", stroke=POS, sw=1.8, min_w=260)
    frags.append(b)
    frags.append(arrow(910, 308, 910, 380, color=POS, sw=2.0))
    frags.append(text(1060, 348, 'manager.lookup("gateway")', size=11.5, color=POS))
    b, _, _ = textbox(910, 410, ["реєстр служб", "ключ → служба"],
                      size=12, fill="#f3f4f6", stroke=POS, sw=1.6, min_w=240)
    frags.append(b)
    frags.append(text(910, 470, "останній крок компонент долає САМ", size=13, bold=True, color=POS))
    frags.append(text(910, 496, "рядковим ключем, усередині свого методу", size=11.5, color=MUTED))

    frags.append(line(60, 518, W - 60, 518, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, 548, "Впорснули не залежність, а локатор — тому тип 1 і перейменували на «пошук»",
                      size=13, bold=True, color=INK))
    frags.append(text(W / 2, 570, "contextualized dependency lookup — не впровадження", size=11.5, color=MUTED))

    render(os.path.join(IMG, 'fourth-form-lookup.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_new_vs_injected()
    fig_three_forms()
    fig_push_vs_pull()
    fig_untangle_arc()
    fig_leaf_first()
    fig_cycle_topo()
    fig_lifetime_count()
    fig_one_word_three_jobs()
    fig_fourth_form_lookup()
    print("figs done")
