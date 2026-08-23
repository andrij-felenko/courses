# -*- coding: utf-8 -*-
"""Фігури до кроку «Вибір: центр, сервіс — і гібрид» (progarch / nodes-identity-access).
Три фігури:
  1) three-placements  — «центр чи сервіс» = три незалежні важелі (політика/рішення/дані);
  2) hybrid-dataflow   — потік гібрида: центр роздає, сервіс оцінює локально, вікно застарілості;
  3) sensitivity-map   — площина двох фактів: локальність даних × свіжість відкликання.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_TINT = "#eaf7ef"
BLUE_TINT = "#eaf0fd"
GOLD_TINT = "#fbf1dc"
RED_TINT = "#fdecea"


# ── Фігура 1: три важелі, а не один ──────────────────────────────────────────
def fig_three_placements():
    W, H = 1000, 452
    p = []
    xlab, wlab = 24, 170
    xa, wa = 206, 232
    xb, wb = 448, 232
    xh, wh = 690, 286
    # підсвітка стовпця «Гібрид» (за ним — відповідь кроку)
    p.append(rect(xh - 5, 44, wh + 10, 368, fill="#f2fbf5", stroke=FIELD, sw=2.6))
    # ── шапка ──
    yh, hh = 48, 46
    p.append(fitbox(xlab, yh, wlab, hh, "важіль ↓ / варіант →", size=11, fill="#eef2f7", color=MUTED))
    p.append(fitbox(xa, yh, wa, hh, "Варіант А\nусе в сервісі", size=12.5, bold=True, fill="#eef2f7"))
    p.append(fitbox(xb, yh, wb, hh, "Варіант Б\nусе в центрі", size=12.5, bold=True, fill="#eef2f7"))
    p.append(fitbox(xh, yh, wh, hh, "Гібрид\nкожен важіль окремо", size=12.5, bold=True, fill="#e7f6ec"))
    # ── рядки ──
    rows = [
        (104, 92, "Політика\n(текст правила)",
         ("у сервісі\n(N копій)", BLUE_TINT),
         ("у центрі", GOLD_TINT),
         ("у центрі\n(одне джерело)", GOLD_TINT)),
        (204, 92, "Рішення\n(оцінка вердикту)",
         ("у сервісі\n(виклик функції)", BLUE_TINT),
         ("у центрі\n(стрибок мережею)", GOLD_TINT),
         ("у сервісі\n(локально, без стрибка)", BLUE_TINT)),
        (304, 106, "Дані\n(факти для рішення)",
         ("локальні\n(поруч)", BLUE_TINT),
         ("стягнуті в центр", GOLD_TINT),
         ("розділено:\nлокальні — тут,\nнаскрізні — в центрі", GREEN_TINT)),
    ]
    for y, h, lab, (ta, ca), (tb, cb), (th, ch) in rows:
        p.append(fitbox(xlab, y, wlab, h, lab, size=12, bold=True, fill="#f7f9fb"))
        p.append(fitbox(xa, y, wa, h, ta, size=12, fill=ca))
        p.append(fitbox(xb, y, wb, h, tb, size=12, fill=cb))
        p.append(fitbox(xh, y, wh, h, th, size=12, fill=ch, stroke=FIELD, sw=1.6))
    # ── мораль унизу ──
    p.append(text(W / 2, 434,
                  "А жене всі три важелі в один бік, Б — в інший; гібрид садить кожен на своє місце.",
                  size=12.5, color=MUTED))
    render(os.path.join(IMG, "three-placements.svg"), W, H, *p,
           title="«Центр чи сервіс» — це не один важіль, а три")


# ── Фігура 2: потік гібрида й вікно застарілості ─────────────────────────────
def fig_hybrid_dataflow():
    W, H = 1000, 560
    p = []
    # ── два центральні сховища ──
    p.append(rect(150, 62, 300, 84, fill=GOLD_TINT, stroke=INK, sw=1.8))
    p.append(text(300, 88, "ЦЕНТР ПОЛІТИКИ", size=13, bold=True))
    p.append(mtext(300, 110, ["одне правило (підписаний бандл)", "роздається в кожен сервіс"],
                   size=11, color=INK))
    p.append(rect(560, 62, 300, 84, fill=GOLD_TINT, stroke=INK, sw=1.8))
    p.append(text(710, 88, "ЦЕНТР ЗВ'ЯЗКІВ", size=13, bold=True))
    p.append(mtext(710, 110, ["наскрізне членство, ролі поза сервісом", "(Богдан ∈ дім 7)"],
                   size=11, color=INK))
    # ── подія відкликання (праворуч над центром зв'язків) ──
    p.append(fitbox(878, 58, 110, 78, "подія\n«виключити\nБогдана»", size=11,
                    fill=RED_TINT, stroke=POS, sw=1.6))
    p.append(arrow(876, 98, 862, 98, color=POS, sw=1.9))
    p.append(text(870, 50, "revoke", size=10.5, color=POS, bold=True, anchor="end"))
    # ── сервіс пристроїв (один процес) ──
    sx, sy, sw_, sh_ = 250, 326, 470, 168
    p.append(rect(sx, sy, sw_, sh_, fill=BG, stroke=INK, sw=2))
    p.append(text(sx + sw_ / 2, sy + 26, "Сервіс пристроїв — один процес", size=13, bold=True))
    p.append(fitbox(sx + 24, sy + 44, 252, 60,
                    "локальний оцінювач\ncan() — вердикт У ПРОЦЕСІ", size=12,
                    fill=GREEN_TINT, stroke=FIELD, sw=2))
    p.append(fitbox(sx + 298, sy + 44, 148, 60, "кеш\nчленства", size=12,
                    fill=BLUE_TINT, stroke=NEG, sw=1.6))
    p.append(text(sx + sw_ / 2, sy + 138, "рішення тут: allow ✓ — без стрибка на кожне натискання",
                  size=11, color=FIELD, bold=True))
    # ── привид «інші сервіси» (нижній правий кут) ──
    p.append(rect(792, 392, 152, 104, fill="#f7f9fb", stroke=MUTED, sw=1.4, rx=6))
    p.append(mtext(868, 432, ["· · ·", "інші сервіси —", "роздача та сама"], size=11.5, color=MUTED))
    # ── роздача правил (ліва стрілка, з центру політики) ──
    p.append(arrow(320, 148, 372, 322, color=LINE, sw=1.8))
    p.append(mtext(300, 232, ["роздача", "правил"], size=10.5, color=MUTED, anchor="end"))
    # ── факт членства + кеш (з центру зв'язків, у кеш) ──
    p.append(arrow(660, 148, 610, 322, color=NEG, sw=1.8))
    p.append(mtext(690, 232, ["факт", "+ кеш"], size=10.5, color=NEG, anchor="start"))
    # ── гарячий шлях: запит «відчинити» → оцінювач, у процесі ──
    p.append(fitbox(28, 356, 126, 74, "запит\n«відчинити\nзамок #42»", size=12, fill=FILL))
    p.append(arrow(156, 393, 272, 393, color=FIELD, sw=2.4))
    p.append(mtext(212, 356, ["у процесі,", "без стрибка"], size=10, color=FIELD))
    # ── revoke: пунктир по правому боці у кеш, із затримкою ──
    p.append(line(834, 148, 834, 300, color=POS, sw=2, dash="7 5"))
    p.append(line(834, 300, 700, 360, color=POS, sw=2, dash="7 5"))
    p.append(arrow(712, 354, 698, 362, color=POS, sw=2))
    p.append(mtext(846, 214, ["затримка", "роздачі"], size=10.5, color=POS, anchor="start"))
    # ── банер: вікно застарілості ──
    p.append(fitbox(220, 512, 560, 34,
                    "поки подія в дорозі — кеш ще каже «можна»: ВІКНО ЗАСТАРІЛОСТІ на відкликанні",
                    size=11.5, color=POS, fill=RED_TINT, stroke=POS, sw=1.4))
    render(os.path.join(IMG, "hybrid-dataflow.svg"), W, H, *p,
           title="Гібрид: центр роздає правило, сервіс оцінює локально — а ціна в затримці")


# ── Фігура 3: площина двох фактів ────────────────────────────────────────────
def fig_sensitivity_map():
    W, H = 940, 560
    p = []
    x0, x1 = 150, 866      # межі поля по X
    y0, y1 = 96, 470       # верх/низ поля по Y
    xm = (x0 + x1) / 2
    ym = (y0 + y1) / 2
    # поле й поділ на чверті
    p.append(rect(x0, y0, x1 - x0, y1 - y0, fill=BG, stroke=MUTED, sw=1.4))
    p.append(line(xm, y0, xm, y1, color=MUTED, sw=1.3, dash="6 5"))
    p.append(line(x0, ym, x1, ym, color=MUTED, sw=1.3, dash="6 5"))
    # ── підписи чвертей ──
    p.append(fitbox(x0 + 30, y0 + 26, 250, 52, "Варіант А\nвистачає", size=13, bold=True,
                    fill=GREEN_TINT, stroke=FIELD, sw=1.6))
    p.append(fitbox(x1 - 288, y0 + 20, 258, 64,
                    "найдорожчий кут:\nгібрид з push-інвалідацією\nабо синхронний центр (Б)",
                    size=12, fill=GOLD_TINT, stroke=POS, sw=1.6))
    p.append(fitbox(x0 + 24, ym + 22, 262, 52, "А з інвалідацією\nна подію (локально)",
                    size=12.5, fill=BLUE_TINT, stroke=NEG, sw=1.4))
    p.append(fitbox(x1 - 292, ym + 18, 262, 64,
                    "Гібрид:\nцентр зв'язків\n+ локальний кеш", size=12.5, bold=True,
                    fill=GREEN_TINT, stroke=FIELD, sw=1.8))
    # ── осі (підписи поза полем) ──
    # X
    p.append(text(xm, y1 + 42, "де лежать дані для рішення", size=12.5, bold=True, color=INK))
    p.append(mtext(x0 + 4, y1 + 30, ["локальні", "(у сервісі)"], size=11, color=MUTED, anchor="start"))
    p.append(mtext(x1 - 4, y1 + 30, ["наскрізні", "(кілька сервісів)"], size=11, color=MUTED, anchor="end"))
    # Y
    p.append(mtext(x0 - 96, y0 + 22, ["свіжість", "відкликання ↑"], size=12.5, bold=True,
                   color=INK, anchor="start"))
    p.append(mtext(x0 - 96, y0 + 4, ["має діяти", "миттєво"], size=11, color=MUTED, anchor="start"))
    p.append(mtext(x0 - 96, y1 - 22, ["секунди", "застарілості — ок"], size=11, color=MUTED, anchor="start"))
    # ── приклади DH (крапка + підпис) ──
    dots = [
        (x0 + 96, y1 - 40, ["ліміт запитів", "(свій лічильник)"], "below"),
        (x1 - 150, ym + 118, ["«відчинити»: членство", "наскрізне, кеш терпить"], "above"),
        (xm + 150, y0 + 116, ["виключити гостя", "негайно"], "right"),
    ]
    for dx, dy, lines, pos in dots:
        p.append(circle(dx, dy, 6, fill=INK, stroke=INK))
        if pos == "below":
            p.append(mtext(dx, dy + 20, lines, size=11, color=INK))
        elif pos == "above":
            p.append(mtext(dx, dy - 30, lines, size=11, color=INK))
        else:
            p.append(mtext(dx + 12, dy + 4, lines, size=11, color=INK, anchor="start"))
    render(os.path.join(IMG, "sensitivity-map.svg"), W, H, *p,
           title="Два факти обирають авторизацію: локальність даних × свіжість відкликання")


# ── Фігура 4: матриця fail-closed кеша членства (до вставки proj-гібрида) ─────
def fig_failclosed_matrix():
    W, H = 960, 486
    p = []
    # колонки
    c1x, c1w = 28, 226
    c2x, c2w = 262, 196
    c3x, c3w = 466, 182
    c4x, c4w = 656, 276     # правий край 932
    # ── шапка ──
    yh, hh = 48, 48
    p.append(fitbox(c1x, yh, c1w, hh, "стан кеша членства", size=12.5, bold=True, fill="#eef2f7"))
    p.append(fitbox(c2x, yh, c2w, hh, "що каже центр зв'язків", size=12.5, bold=True, fill="#eef2f7"))
    p.append(fitbox(c3x, yh, c3w, hh, "isMemberOf →", size=12.5, bold=True, fill="#eef2f7"))
    p.append(fitbox(c4x, yh, c4w, hh, "вердикт can()", size=12.5, bold=True, fill="#eef2f7"))
    # ── рядки: (кеш, центр, isMember, вердикт, заливка_вердикту, [зелений акцент]) ──
    rows = [
        ("свіжий ПОЗИТИВ\n(hit: член)", "не питаємо\n(є свіжий кеш)", "true",
         "за політикою\n(allow, якщо роль і вікно)", GREEN_TINT, False),
        ("свіжий НЕГАТИВ\n(hit: не член)", "не питаємо", "false",
         "DENY", BLUE_TINT, False),
        ("промах", "«член»", "true\n(кешуємо +, довше)",
         "за політикою", GREEN_TINT, False),
        ("промах", "«не член»", "false\n(кешуємо −, коротко)",
         "DENY", BLUE_TINT, False),
        ("промах", "НЕДОСТУПНИЙ\nабо таймаут", "false\n(НЕ кешуємо)",
         "DENY — fail-closed", BLUE_TINT, True),
    ]
    y, rh = 100, 56
    for kesh, centr, ism, verd, vfill, accent in rows:
        p.append(fitbox(c1x, y, c1w, rh, kesh, size=11.5, fill=BG))
        p.append(fitbox(c2x, y, c2w, rh, centr, size=11.5, fill=BG))
        p.append(fitbox(c3x, y, c3w, rh, ism, size=11.5, fill="#f7f9fb"))
        p.append(fitbox(c4x, y, c4w, rh, verd, size=11.5, bold=accent, fill=vfill,
                        stroke=(FIELD if accent else LINE), sw=(2.6 if accent else 1.5)))
        y += rh
    # ── мораль: тільки підтверджений «+» веде в політику; усе інше — deny ──
    p.append(text(W / 2, y + 24,
                  "Лише позитивне підтвердження членства веде до політики; негатив, промах-у-збій — усе в deny.",
                  size=12, color=MUTED))
    # ── антипатерн: наївне «пустити на збій» ──
    p.append(fitbox(28, y + 38, 904, 62,
                    "❌ Наївно: промах чи збій центру → «щоб не блокувати — пустити» (allow).\n"
                    "Мить недоступності — і кожен чужий проходить. Правило: підтвердь членство або відмов.",
                    size=12.5, color=POS, fill=RED_TINT, stroke=POS, sw=1.5))
    render(os.path.join(IMG, "failclosed-matrix.svg"), W, H, *p,
           title="Кеш членства: allow лише на підтверджений «+», решта — deny (fail-closed)")


# ── Фігура 5: трасування тесту поширення відкликання (TTL проти push) ─────────
def fig_revocation_test():
    W, H = 1000, 452
    p = []
    x0, x1 = 150, 908           # межі часової осі
    # часові мітки (позиції по X) та підписи
    t_warm, t_rev, t_5s, t_ttl = 208, 366, 486, 760
    # ── вісь часу вгорі з підписами подій ──
    p.append(line(x0, 96, x1, 96, color=MUTED, sw=1.4))
    marks = [
        (t_warm, "t0 = 09:00", "can()=true — тепло", INK),
        (t_rev, "revoke()", "центр правди оновлено", POS),
        (t_5s, "+5 c", "advance(5s)", MUTED),
        (t_ttl, "+60 c", "TTL сплив", MUTED),
    ]
    for x, top, bot, col in marks:
        p.append(line(x, 90, x, 102, color=col, sw=1.6))
        p.append(text(x, 82, top, size=11.5, bold=True, color=col))
        p.append(text(x, 116, bot, size=10.5, color=MUTED))
    # вертикаль події revoke — червона, наскрізь
    p.append(line(t_rev, 96, t_rev, 386, color=POS, sw=1.8, dash="6 5"))

    def lane(y, title, segs, badges):
        p.append(text(x0 - 8, y - 30, title, size=13, bold=True, anchor="end"))
        for xa, xb, fill, stroke in segs:
            p.append(rect(xa, y - 22, xb - xa, 44, fill=fill, stroke=stroke, sw=1.6, rx=5))
        for bx, txt, col in badges:
            p.append(text(bx, y + 5, txt, size=11.5, bold=True, color=col))

    # смуга «лише TTL»: зелено до revoke, ЧЕРВОНО від revoke до TTL (застарілий allow), синьо далі
    lane(170, "лише TTL",
         [(x0, t_rev, GREEN_TINT, FIELD),
          (t_rev, t_ttl, RED_TINT, POS),
          (t_ttl, x1, BLUE_TINT, NEG)],
         [((x0 + t_rev) / 2, "allow ✓", FIELD),
          ((t_rev + t_ttl) / 2, "can()=true ✗ ЗАСТАРІЛО", POS),
          ((t_ttl + x1) / 2, "deny ✓", NEG)])
    # смуга «push на revoke»: зелено до revoke, одразу синьо (вікно ≈ 0)
    lane(320, "push на revoke",
         [(x0, t_rev, GREEN_TINT, FIELD),
          (t_rev, t_rev + 14, RED_TINT, POS),
          (t_rev + 14, x1, BLUE_TINT, NEG)],
         [((x0 + t_rev) / 2, "allow ✓", FIELD),
          ((t_rev + 40 + x1) / 2, "can()=false ✓ — deny ОДРАЗУ (вікно ≈ 0)", NEG)])
    # підпис червоної зони
    p.append(text((t_rev + t_ttl) / 2, 214, "виключений гість ще відчиняє", size=10.5, color=POS))
    # мораль унизу
    p.append(text(W / 2, 424,
                  "Той самий revoke: лише-TTL лишає дозвіл на весь TTL; подія на revoke стискає вікно до ≈0.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "revocation-test.svg"), W, H, *p,
           title="Тест поширення відкликання: вікно застарілості — TTL проти push-інвалідації")


# ── Фігура 6: зв'язок = кортеж; перевірка = прохід графом (вставка Zanzibar) ──
def fig_zanzibar_tuples():
    W, H = 1000, 500
    p = []
    # питання перевірки
    p.append(fitbox(40, 56, 320, 46, "перевірка:  can(ann, view, doc:plan)?",
                    size=13, bold=True, fill=FILL, stroke=NEG, sw=1.6))
    # ── ланцюг угорі: ann → group → folder → doc ──
    ny = 150
    nodes = [(150, "ann\nкористувач", BLUE_TINT),
             (390, "group:eng\nгрупа", "#eef2f7"),
             (630, "folder:q3\nтека", "#eef2f7"),
             (858, "doc:plan\nдокумент", GREEN_TINT)]
    for x, name, col in nodes:
        p.append(fitbox(x - 84, ny, 168, 60, name, size=12.5, bold=True,
                        fill=col, stroke=INK, sw=1.6))
    xs = [150, 390, 630, 858]
    for i in range(3):
        p.append(arrow(xs[i] + 88, ny + 30, xs[i + 1] - 88, ny + 30, color=FIELD, sw=2.2))
    for lx, lab in [(270, "member"), (510, "viewer"), (744, "parent")]:
        p.append(text(lx, ny - 6, lab, size=11.5, color=FIELD, bold=True))
    p.append(fitbox(788, ny + 90, 168, 40, "✓ можна — ланцюг є", size=12, bold=True,
                    fill=GREEN_TINT, stroke=FIELD, sw=1.8))
    # ── центральне сховище кортежів ──
    sx, sy, sw_, sh_ = 60, 300, 880, 150
    p.append(rect(sx, sy, sw_, sh_, fill="#fbfcfe", stroke=INK, sw=2))
    p.append(text(sx + sw_ / 2, sy + 28,
                  "ЦЕНТРАЛЬНЕ СХОВИЩЕ ЗВ'ЯЗКІВ  —  кортежі object#relation@user (у Spanner)",
                  size=13, bold=True))
    for px, t in [(210, "group:eng\n#member@ann"),
                  (500, "folder:q3#viewer\n@group:eng#member"),
                  (790, "doc:plan#parent\n@folder:q3")]:
        p.append(fitbox(px - 140, sy + 62, 280, 56, t, size=12, fill=GOLD_TINT, stroke=MUTED, sw=1.4))
    p.append(text(sx + sw_ / 2, sy + sh_ - 14,
                  "жоден сервіс не має всього ланцюга — тому зв'язки лежать в ОДНОМУ центрі, а не в кожному сервісі",
                  size=11.5, color=MUTED))
    render(os.path.join(IMG, "zanzibar-tuples.svg"), W, H, *p,
           title="Зв'язок — це кортеж; перевірка — прохід графом зв'язків")


# ── Фігура 7: «новий ворог» і як zookie його закриває ────────────────────────
def fig_new_enemy_zookie():
    W, H = 1020, 470
    p = []
    bw, bh, gap = 210, 68, 46

    def lane(y, header, hcolor, stages, tag, tagcol):
        p.append(text(56, y - 16, header, size=13, bold=True, anchor="start", color=hcolor))
        cx = 56
        for i, (t, fill, st, bold) in enumerate(stages):
            p.append(fitbox(cx, y, bw, bh, t, size=12.5, bold=bold, fill=fill, stroke=st, sw=1.6))
            if i < len(stages) - 1:
                p.append(arrow(cx + bw + 6, y + bh / 2, cx + bw + gap - 6, y + bh / 2, color=MUTED, sw=2))
            cx += bw + gap
        p.append(arrow(cx - gap + 6, y + bh / 2, cx - 6, y + bh / 2, color=tagcol, sw=2))
        p.append(fitbox(cx, y + 8, 150, 52, tag, size=12, bold=True, fill=BG, stroke=tagcol, sw=2))

    lane(96, "Без маркера свіжості", POS,
         [("t₁ · відкликали\nБогдана", RED_TINT, POS, False),
          ("t₂ · перевірка читає\nнесвіжий знімок", "#eef2f7", MUTED, False),
          ("allow — доступ\nне зник", RED_TINT, POS, True)],
         "→ «НОВИЙ\nВОРОГ»", POS)
    lane(226, "Із zookie (обмежена свіжість)", FIELD,
         [("збереження контенту\nвидає zookie@t", GOLD_TINT, MUTED, False),
          ("перевірка несе zookie:\nзнімок ≥ t", BLUE_TINT, NEG, False),
          ("deny — відкликання\nвидно", GREEN_TINT, FIELD, True)],
         "→ вікно\nзакрите", FIELD)
    p.append(fitbox(56, 318, 918, 40,
                    "знімок ≥ zookie.час   ⇒   усе, що сталося до видачі zookie (і відкликання теж), вже в цьому знімку",
                    size=12, fill=FILL, stroke=NEG, sw=1.4))
    p.append(fitbox(56, 386, 452, 60, "несвіже «не можна» по ВИДАЧІ\n= незручність: почекав і повторив",
                    size=12, fill=BLUE_TINT, stroke=NEG, sw=1.6))
    p.append(fitbox(522, 386, 452, 60, "несвіже «можна» по ВІДКЛИКАННІ\n= діра: відкликаний ще відчиняє двері",
                    size=12, fill=RED_TINT, stroke=POS, sw=1.6))
    render(os.path.join(IMG, "new-enemy-zookie.svg"), W, H, *p,
           title="«Новий ворог»: несвіже „можна\" по відкликанні — і як zookie його закриває")


# ── Фігура 8: рід Zanzibar — цілий клас продуктів ────────────────────────────
def fig_zanzibar_lineage():
    W, H = 1020, 524
    p = []
    p.append(fitbox(60, 66, 280, 56, "Zanzibar · Google\nUSENIX ATC 2019", size=13, bold=True,
                    fill=GOLD_TINT, stroke=INK, sw=2))
    spine_x = 200
    p.append(line(spine_x, 122, spine_x, 438, color=MUTED, sw=1.8))
    rows = [
        (150, "rebac", 330, "Ory Keto — перша відкрита\nреалізація Zanzibar · ~2021"),
        (222, "rebac", 330, "SpiceDB · AuthZed\nвідкрито 2021"),
        (294, "internal", 330, "Airbnb Himeji\nвнутрішня · ~2021"),
        (366, "rebac", 330, "OpenFGA · Auth0 / Okta\nвідкрито 2022 → CNCF"),
        (438, "adjacent", 430, "AWS Cedar · Verified Permissions · 2023\nінша гілка: мова політик, не кортежі"),
    ]
    for cy, kind, w, t in rows:
        if kind == "rebac":
            fill, st, sw = GREEN_TINT, FIELD, 1.8
        elif kind == "internal":
            fill, st, sw = FILL, MUTED, 1.5
        else:
            fill, st, sw = GOLD_TINT, POS, 1.6
        p.append(line(spine_x, cy, 384, cy, color=MUTED, sw=1.5))
        p.append(fitbox(384, cy - 27, w, 54, t, size=12, bold=(kind == "rebac"),
                        fill=fill, stroke=st, sw=sw))
    ly = 490
    p.append(rect(60, ly - 12, 18, 18, fill=GREEN_TINT, stroke=FIELD, sw=1.8))
    p.append(text(86, ly + 3, "сховище кортежів (ReBAC)", size=11.5, color=INK, anchor="start"))
    p.append(rect(360, ly - 12, 18, 18, fill=FILL, stroke=MUTED, sw=1.5))
    p.append(text(386, ly + 3, "внутрішня система", size=11.5, color=INK, anchor="start"))
    p.append(rect(560, ly - 12, 18, 18, fill=GOLD_TINT, stroke=POS, sw=1.6))
    p.append(text(586, ly + 3, "суміжна гілка: мова політик", size=11.5, color=INK, anchor="start"))
    render(os.path.join(IMG, "zanzibar-lineage.svg"), W, H, *p,
           title="Рід Zanzibar: з одного паперу (2019) — цілий клас авторизаційних сервісів")


if __name__ == "__main__":
    fig_three_placements()
    fig_hybrid_dataflow()
    fig_sensitivity_map()
    fig_failclosed_matrix()
    fig_revocation_test()
    fig_zanzibar_tuples()
    fig_new_enemy_zookie()
    fig_zanzibar_lineage()
    print("OK: 8 SVG ->", IMG)
