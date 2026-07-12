# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

RED_T   = "#fdecea"
GREEN_T = "#e7f6ec"
BLUE_T  = "#eaf0fd"
AMBER_T = "#fdf0dd"
NEUT    = "#eef2f6"


def fig_ledger():
    """Терези: що віддаєш (важча ліва шалька) проти вузького виграшу (права)."""
    W, H = 1080, 560
    f = []

    # ── балка терезів із нахилом уліво (ліва нижча = важча) ──
    lx, rx = 265, 815
    ly, ry = 92, 72
    f.append(line(lx, ly, rx, ry, color=INK, sw=4))          # балка
    f.append(circle(lx, ly, 5, fill=INK, stroke=INK))
    f.append(circle(rx, ry, 5, fill=INK, stroke=INK))
    # опора-трикутник під центром балки
    f.append('<path d="M540 82 L520 116 L560 116 z" fill="%s" stroke="%s" '
             'stroke-width="1.5"/>' % (FILL, LINE))
    f.append(text(540, 140, "Розмін, а не апгрейд", size=13, color=MUTED, bold=True))
    # підвіси до заголовків
    f.append(line(lx, ly, lx, 158, color=MUTED, sw=1.4))
    f.append(line(rx, ry, rx, 158, color=MUTED, sw=1.4))

    # ── ліва шалька: що ВІДДАЄШ ──
    f.append(fitbox(40, 160, 450, 48, "Що ВІДДАЄШ — реляційне дає задарма",
                    size=15, bold=True, fill=RED_T, stroke=POS, color="#7a231a"))
    give = [
        "Транзакції ACID — усе або нічого",
        "З'єднання — дані без дублів",
        "Запити наздогад — спитати незаплановане",
        "Зрілі інструменти — бекапи, ORM, моніторинг",
    ]
    for i, s in enumerate(give):
        f.append(fitbox(40, 224 + i * 70, 450, 58, s, size=14, fill=BG,
                        stroke="#d98b83", sw=1.8))

    # ── права шалька: що ВИГРАЄШ ──
    f.append(fitbox(590, 160, 450, 48, "Що ВИГРАЄШ — лише для однієї задачі",
                    size=15, bold=True, fill=GREEN_T, stroke=FIELD, color="#1c6b3a"))
    gain = [
        "Запис розкидається по вузлах",
        "Модель лягає на форму доступу",
        "Дешеве зберігання й видалення за строком",
    ]
    for i, s in enumerate(gain):
        f.append(fitbox(590, 224 + i * 70, 450, 58, s, size=14, fill=BG,
                        stroke="#8fce9f", sw=1.4))
    f.append(text(815, 452, "вужча обіцянка", size=12, color=MUTED, italic=True))

    # ── девіз ──
    f.append(fitbox(140, 500, 800, 42,
                    "За замовчуванням ліва шалька важча — тому тягар доказу на тому, "
                    "хто хоче піти", size=14, bold=True, fill=NEUT, stroke=LINE))

    render(os.path.join(OUT, "migration-ledger.svg"), W, H, *f,
           title="Міграція — це розмін, а не сходинка вгору")


def fig_gates():
    """Воронка з чотирьох воріт: усі «так» → мігрувати задачу; будь-яке «ні» → лишитися."""
    W, H = 1020, 740
    f = []

    cx = 380
    gates = [
        ("1 · Біль реальний\nі ВИМІРЯНИЙ?", 640,
         "ні → уявний масштаб\nлишаємося"),
        ("2 · Реляційне ВИЧЕРПАНО?\nіндекси · секції · JSONB · репліки · кеш", 580,
         "ні → спершу налаштуй\nлишаємося"),
        ("3 · Форма доступу пасує іншій моделі,\nа втрачених гарантій цим даним не треба?", 520,
         "ні → втрата дорожча\nза виграш · лишаємося"),
        ("4 · Переселяємо ЛИШЕ\nзадачу-невдаху, не всю систему?", 460,
         "ні → переписати все?\nстоп, звузь до задачі"),
    ]
    ys = [64, 202, 340, 478]
    gh = 92
    for (label, w, branch), y in zip(gates, ys):
        x = cx - w / 2
        f.append(fitbox(x, y, w, gh, label, size=15, bold=True, fill=BLUE_T,
                        stroke=NEG, sw=1.8))
        # відгалуження «ні» праворуч
        bx, by, bw, bh = 720, y + gh / 2 - 27, 268, 54
        f.append(arrow(x + w, y + gh / 2, bx, by + bh / 2, color=POS, sw=1.8))
        f.append(fitbox(bx, by, bw, bh, branch, size=12.5, fill=RED_T,
                        stroke="#d98b83", color="#7a231a"))

    # стрілки-воронка вниз між воротами
    for i in range(len(ys) - 1):
        f.append(arrow(cx, ys[i] + gh, cx, ys[i + 1], color=INK, sw=2))
        f.append(text(cx + 14, (ys[i] + gh + ys[i + 1]) / 2 + 4, "так", size=12,
                      color=FIELD, anchor="start", bold=True))

    # фінал: мігрувати задачу
    f.append(arrow(cx, ys[-1] + gh, cx, 616, color=FIELD, sw=2.4))
    f.append(text(cx + 14, (ys[-1] + gh + 616) / 2 + 4, "так", size=12,
                  color=FIELD, anchor="start", bold=True))
    f.append(fitbox(cx - 230, 616, 460, 58, "МІГРУВАТИ ЦЮ ЗАДАЧУ\n(поліглотне зберігання)",
                    size=16, bold=True, fill=GREEN_T, stroke=FIELD, sw=2.2,
                    color="#1c6b3a"))
    f.append(text(W / 2, 706, "провал на будь-яких воротах → лишаємося на нудному за замовчуванням",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, "migration-gates.svg"), W, H, *f,
           title="Виправдана міграція — це чотири «так» поспіль")


def fig_split():
    """DH до/після: телеметрія відчіпляється в своє сховище, ядро лишається реляційним."""
    W, H = 1100, 560
    f = []

    # ── ЛІВОРУЧ: одна база — до ──
    f.append(rect(40, 66, 380, 384, fill="#fbfcfd", stroke=LINE, sw=1.8))
    f.append(text(230, 92, "Одна реляційна база — до", size=15, bold=True))
    f.append(fitbox(66, 112, 328, 62, "ядро — домівки, люди,\nпристрої, рахунки, правила",
                    size=12.5, fill=NEUT, stroke=LINE))
    f.append(fitbox(66, 190, 328, 210, "телеметрія\n\n260 млрд рядків",
                    size=17, bold=True, fill=RED_T, stroke=POS, sw=2, color="#7a231a"))
    f.append(text(230, 428, "одна таблиця душить решту", size=12.5, color=POS, italic=True))

    # ── стрілка «розділити» ──
    f.append(arrow(430, 250, 522, 250, color=INK, sw=2.6))
    f.append(text(476, 236, "розділити", size=13, bold=True))

    # ── ПРАВОРУЧ, згори: реляційне ядро лишається ──
    f.append(rect(560, 78, 500, 150, fill=GREEN_T, stroke=FIELD, sw=1.8))
    f.append(text(810, 104, "Реляційна база (лишається)", size=14, bold=True,
                  color="#1c6b3a"))
    f.append(fitbox(586, 120, 448, 52, "ядро — з'єднання + транзакції ACID",
                    size=14, bold=True, fill=BG, stroke=FIELD))
    f.append(text(810, 210, "те, за що платимо, — тут потрібне", size=12.5,
                  color="#1c6b3a", italic=True))

    # ── ПРАВОРУЧ, знизу: нове сховище часових рядів ──
    f.append(rect(560, 258, 500, 178, fill=BLUE_T, stroke=NEG, sw=1.8))
    f.append(text(810, 284, "Ширококолонкове сховище часових рядів (нове)",
                  size=13.5, bold=True, color="#1c3a8a"))
    f.append(fitbox(586, 300, 448, 62, "телеметрія — дописуй ·\nчитай за вікном · видаляй за строком",
                    size=13.5, bold=True, fill=BG, stroke=NEG))
    f.append(text(810, 416, "нічого реляційного не треба; запис розкидається по вузлах",
                  size=12, color="#1c3a8a", italic=True))

    # стрілки від «розділити» до двох правих рамок
    f.append(arrow(522, 240, 560, 150, color=MUTED, sw=1.6))
    f.append(arrow(522, 262, 560, 330, color=MUTED, sw=1.6))

    # ── девіз ──
    f.append(fitbox(210, 486, 680, 46,
                    "Поліглотне зберігання: мігрує ЗАДАЧА, а не компанія",
                    size=15, bold=True, fill=NEUT, stroke=LINE))

    render(os.path.join(OUT, "dh-telemetry-split.svg"), W, H, *f)


def fig_medicine():
    """Ліки від чужої хвороби: рідкісна хвороба → чесні ліки → тисячі здорових, що їх випили."""
    W, H = 1160, 490
    f = []

    # ── ЛІВОРУЧ: хвороба (рідкісна) ──
    f.append(rect(36, 64, 256, 300, fill=RED_T, stroke=POS, sw=1.6))
    f.append(text(164, 92, "ХВОРОБА", size=15, bold=True, color="#7a231a"))
    f.append(fitbox(52, 106, 224, 82,
                    "Google\nувесь веб —\nтисячі машин під одною таблицею",
                    size=12, fill=BG, stroke="#d98b83"))
    f.append(fitbox(52, 200, 224, 92,
                    "Amazon\nкошик не сміє впасти,\nколи падають цілі стійки",
                    size=12, fill=BG, stroke="#d98b83"))
    f.append(text(164, 330, "мали лічені компанії на планеті", size=11.5,
                  color="#7a231a", italic=True))

    # ── стрілка до ліків ──
    f.append(arrow(292, 214, 326, 214, color=INK, sw=2.2))

    # ── ПОСЕРЕДИНІ: ліки (чесний рецепт) ──
    f.append(rect(330, 64, 246, 300, fill=AMBER_T, stroke="#caa46a", sw=1.6))
    f.append(text(453, 92, "ЛІКИ", size=15, bold=True, color="#7a5a1a"))
    f.append(fitbox(346, 106, 214, 48, "Bigtable — Google, 2006",
                    size=12, fill=BG, stroke="#caa46a"))
    f.append(fitbox(346, 162, 214, 48, "Dynamo — Amazon, 2007",
                    size=12, fill=BG, stroke="#caa46a"))
    f.append(fitbox(346, 220, 214, 122,
                    "чесний рецепт:\nвіддай з'єднання,\nтранзакції, сильну\nузгодженість —\nдістань планетарний\nмасштаб",
                    size=11, fill=NEUT, stroke=LINE))

    # ── стрілка до пацієнтів ──
    f.append(arrow(576, 214, 620, 214, color=INK, sw=2.2))

    # ── ПРАВОРУЧ: хто випив ліки (натовп здорових) ──
    f.append(rect(624, 64, 500, 300, fill=NEUT, stroke=LINE, sw=1.6))
    f.append(text(874, 92, "ХТО ВИПИВ ЛІКИ", size=15, bold=True))
    for r in range(3):
        for c in range(6):
            gx = 648 + c * 74
            gy = 106 + r * 44
            f.append(rect(gx, gy, 62, 34, fill="#e2e8f0", stroke=MUTED, sw=1.0, rx=4))
    f.append(fitbox(648, 240, 452, 108,
                    "тисячі ЗДОРОВИХ команд —\nоплатили побічку: втрату з'єднань і транзакцій,\nа хвороби Google так і не мали",
                    size=12.5, fill=BG, stroke=MUTED))

    # ── девіз ──
    f.append(fitbox(230, 398, 700, 58,
                    "Успадкувати ліки, не успадкувавши хвороби, — "
                    "купити пігулку від чужої болячки.",
                    size=14, bold=True, fill="#fdecea", stroke=POS, sw=1.8,
                    color="#7a231a"))

    render(os.path.join(OUT, "nosql-medicine.svg"), W, H, *f,
           title="Рух NoSQL: точні ліки, що відірвалися від своєї хвороби")


def fig_false_binary():
    """Хибний вибір «SQL або NoSQL» розчиняється: NewSQL, Spanner, всотані документи."""
    W, H = 1080, 490
    f = []

    f.append(text(540, 52, "Гасло: «SQL мертвий» — мовляв, обирай одне",
                  size=14, color=MUTED, italic=True))

    # ── хибна двійка ──
    f.append(fitbox(150, 72, 300, 92, "SQL\nа масштаб?", size=16, bold=True,
                    fill=BLUE_T, stroke=NEG, color="#1c3a8a"))
    f.append(text(540, 132, "АБО", size=24, bold=True, color=POS))
    f.append(fitbox(630, 72, 300, 92, "NoSQL\nа транзакції?", size=16, bold=True,
                    fill=RED_T, stroke=POS, color="#7a231a"))

    # ── розворот ──
    f.append(arrow(540, 176, 540, 234, color=INK, sw=2.4))
    f.append(text(556, 210, "а виявилося — не «або»", size=12.5, bold=True,
                  color=INK, anchor="start"))

    # ── три способи, якими двійку зшили назад ──
    f.append(arrow(540, 238, 210, 250, color=MUTED, sw=1.6))
    f.append(arrow(540, 240, 540, 250, color=MUTED, sw=1.6))
    f.append(arrow(540, 238, 872, 250, color=MUTED, sw=1.6))
    f.append(fitbox(48, 252, 315, 128,
                    "NewSQL — Метью Аслетт,\n451 Group, 2011\n\n"
                    "масштаб NoSQL + гарантії\nACID разом",
                    size=12.5, fill=GREEN_T, stroke=FIELD, color="#1c6b3a"))
    f.append(fitbox(383, 252, 315, 128,
                    "Spanner — Google, 2012\n\n"
                    "планетарний масштаб І SQL\nІ транзакції — від тих самих,\n"
                    "хто написав Bigtable",
                    size=12.5, fill=GREEN_T, stroke=FIELD, color="#1c6b3a"))
    f.append(fitbox(718, 252, 315, 128,
                    "Реляційні всотали NoSQL\n\n"
                    "JSONB: документ\nу реляційній колонці",
                    size=12.5, fill=GREEN_T, stroke=FIELD, color="#1c6b3a"))

    # ── девіз ──
    f.append(fitbox(150, 404, 780, 58,
                    "Двійкового вибору не було: винахідники самі зшили половинки назад.",
                    size=14, bold=True, fill=GREEN_T, stroke=FIELD, color="#1c6b3a"))

    render(os.path.join(OUT, "nosql-false-binary.svg"), W, H, *f,
           title="Хибний вибір, якого не було: «SQL або NoSQL»")


def fig_cutover_timeline():
    """Шість фаз перевезення: де запис, де читання, який крок назад на кожній."""
    W, H = 1200, 668
    f = []
    cL, wL = 24, 214     # фаза
    cW, wW = 250, 244    # запис
    cR, wR = 506, 320    # читання
    cB, wB = 838, 338    # крок назад

    hy = 60
    f.append(text(cL + wL / 2, hy, "фаза", size=14, bold=True))
    f.append(text(cW + wW / 2, hy, "запис іде в", size=14, bold=True))
    f.append(text(cR + wR / 2, hy, "читання йде з", size=14, bold=True))
    f.append(text(cB + wB / 2, hy, "крок назад", size=14, bold=True))

    AMB_S = "#caa24a"
    rows = [
        ("0 · базовий стан", "старе", BLUE_T, "старе", BLUE_T,
         "— (нема потреби)", NEUT),
        ("1 · подвійний запис", "старе  +  НОВЕ", GREEN_T, "старе", BLUE_T,
         "вимкнути подвійний запис", GREEN_T),
        ("2 · беквіл історії", "старе  +  нове", GREEN_T, "старе", BLUE_T,
         "спинити / перезапустити\n(беквіл ідемпотентний)", GREEN_T),
        ("3 · звірка паритету", "старе  +  нове", GREEN_T, "старе", BLUE_T,
         "розбіжність невидима —\nчитання ще на старому", GREEN_T),
        ("4 · перемикання читань\n(поетапно)", "старе  +  нове", GREEN_T,
         "нове ⟵ %-трафіку ⟶ старе", AMBER_T,
         "вернути rollout = 0\n(миттєво, без бекапа)", AMBER_T),
        ("5 · стоп запису в старе", "лише НОВЕ", GREEN_T, "нове", GREEN_T,
         "старе ще ціле — soak-вікно\nперш ніж рушати далі", RED_T),
        ("6 · скидання партицій", "нове", GREEN_T, "нове", GREEN_T,
         "DETACH оборотний;\nDROP — вже ні", RED_T),
    ]
    y0, rh, gap = 82, 62, 12
    for i, (lab, wtxt, wc, rtxt, rc, btxt, bc) in enumerate(rows):
        y = y0 + i * (rh + gap)
        f.append(fitbox(cL, y, wL, rh, lab, size=13, bold=True, fill=NEUT, stroke=LINE))
        f.append(fitbox(cW, y, wW, rh, wtxt, size=13, bold=True, fill=wc,
                        stroke=(FIELD if wc == GREEN_T else NEG)))
        rst = FIELD if rc == GREEN_T else (NEG if rc == BLUE_T else AMB_S)
        f.append(fitbox(cR, y, wR, rh, rtxt, size=13, bold=True, fill=rc, stroke=rst))
        bst = POS if bc == RED_T else (FIELD if bc == GREEN_T else LINE)
        f.append(fitbox(cB, y, wB, rh, btxt, size=12.5, fill=bc, stroke=bst))
    render(os.path.join(OUT, "cutover-timeline.svg"), W, H, *f,
           title="Перевезення телеметрії: шість оборотних фаз")


def fig_backfill_overlap():
    """Рухома межа беквілу: історія ліворуч T₀, живий край праворуч, ідемпотентний шов."""
    W, H = 1140, 470
    f = []
    axy = 300
    x0, x1 = 70, 1060
    t0x = 770

    # вісь часу
    f.append(arrow(x0, axy, x1, axy, color=INK, sw=2))
    f.append(text(x1, axy + 26, "час події (ts) →", size=13, color=MUTED, anchor="end"))
    f.append(text(x0 - 8, axy + 26, "минуле", size=12, color=MUTED, anchor="start"))

    # виносок про запізнілий запис + ідемпотентність (угорі, ліворуч від мітки T₀)
    f.append(fitbox(300, 28, 470, 60,
                    "запізніле показання (ts < T₀) прилітає ПІСЛЯ беквілу →\n"
                    "подвійний запис кладе його за event-ts; повтор упсертом безпечний",
                    size=12, fill=AMBER_T, stroke="#caa24a"))
    f.append(arrow(600, 90, 662, 205, color="#caa24a", sw=1.8))

    # T₀ — мітку ведемо праворуч від лінії, щоб не перетнути виносок і стрілку
    f.append(line(t0x, 150, t0x, axy + 8, color=POS, sw=2, dash="6 5"))
    f.append(text(t0x + 8, 142, "T₀ — увімкнули подвійний запис", size=12.5,
                  color=POS, bold=True, anchor="start"))

    # історичні партиції (ліворуч T₀)
    f.append(text((90 + t0x) / 2, 196, "історичні партиції (ts < T₀)", size=12.5,
                  color=MUTED, italic=True))
    labels = ["…", "квіт", "трав", "черв", "лип"]
    pw = (t0x - 90) / len(labels)
    for i, lb in enumerate(labels):
        px = 90 + i * pw
        f.append(fitbox(px + 4, 210, pw - 8, 56, lb, size=13, fill=NEUT, stroke=LINE))

    # беквіл-стрілка під історією
    f.append(arrow(110, 340, t0x - 16, 340, color=FIELD, sw=2.4))
    f.append(text((110 + t0x) / 2, 362, "беквіл: від найстарішої партиції до T₀, пачками",
                  size=12.5, color="#1c6b3a"))

    # живий край (праворуч T₀)
    f.append(fitbox(t0x + 16, 210, x1 - t0x - 20, 56,
                    "живий край\nподвійний запис, ts ≥ T₀",
                    size=12.5, bold=True, fill=GREEN_T, stroke=FIELD))

    render(os.path.join(OUT, "backfill-overlap.svg"), W, H, *f,
           title="Беквіл історії й живий край не б'ються — шов тримає ідемпотентність")


def fig_bigbang_vs_phased():
    """Ризик big-bang в одну незворотну мить проти шести оборотних воріт без простою."""
    W, H = 1160, 520
    f = []

    # ── Big-bang (верх) ──
    f.append(text(W / 2, 44, "Big-bang: увесь ризик в одну незворотну мить",
                  size=15, bold=True, color=POS))
    f.append(fitbox(80, 66, 620, 92,
                    "ВІКНО ПРОСТОЮ\nзупинити запис → dump → restore → перемкнути",
                    size=14, bold=True, fill=RED_T, stroke=POS, sw=2, color="#7a231a"))
    f.append(arrow(700, 112, 744, 112, color=POS, sw=2))
    f.append(fitbox(744, 66, 336, 92,
                    "крок назад =\nвідновлення з бекапа\n(години, усе або нічого)",
                    size=12.5, fill=RED_T, stroke=POS, color="#7a231a"))
    f.append(text(W / 2, 190, "простій вимірюється годинами-добою; відкату «на крок» немає",
                  size=12.5, color=MUTED, italic=True))

    # роздільник
    f.append(line(60, 228, W - 60, 228, color=LINE, sw=1, dash="4 5"))

    # ── Поетапно (низ) ──
    f.append(text(W / 2, 268, "Поетапно: шість дрібних оборотних воріт, 0 простою",
                  size=15, bold=True, color="#1c6b3a"))
    gates = ["1 подв.\nзапис", "2 беквіл", "3 звірка", "4 читання\n%-трафіку",
             "5 стоп\nстарого", "6 DROP\nстарого"]
    gw, gh, gy = 150, 76, 300
    gap = (W - 120 - 6 * gw) / 5
    for i, g in enumerate(gates):
        gx = 60 + i * (gw + gap)
        last = (i == 5)
        f.append(fitbox(gx, gy, gw, gh, g, size=13, bold=True,
                        fill=(RED_T if last else GREEN_T),
                        stroke=(POS if last else FIELD), sw=1.8))
        if last:
            f.append(text(gx + gw / 2, gy + gh + 22, "незворотно", size=12,
                          color=POS, bold=True))
        else:
            f.append(text(gx + gw / 2, gy + gh + 22, "↩ оборотно", size=12, color="#1c6b3a"))
        if i < 5:
            ax = gx + gw
            f.append(arrow(ax + 4, gy + gh / 2, ax + gap - 4, gy + gh / 2, color=INK, sw=1.6))
    f.append(text(W / 2, 470,
                  "ризик розсипано на дрібні кроки; кожен, крім останнього, вертається флагом",
                  size=12.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "bigbang-vs-phased.svg"), W, H, *f,
           title="Чому поетапно безпечніше за big-bang")


if __name__ == "__main__":
    fig_ledger()
    fig_gates()
    fig_split()
    fig_medicine()
    fig_false_binary()
    fig_cutover_timeline()
    fig_backfill_overlap()
    fig_bigbang_vs_phased()
    print("ok:", os.listdir(OUT))
