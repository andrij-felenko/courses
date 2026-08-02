# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COOL = "#eaf0fd"
GREENF = "#eafaf0"
PALE = "#f4f6f8"


# ── 1. Ліміт на процес проти ліміту на групу ───────────────────────────────────
def fig_per_process_vs_group():
    W, H = 1040, 560
    p = []

    def tree(ox, accent):
        out = []
        out.append(fitbox(ox + 130, 126, 170, 44, "make -j4", size=13,
                          fill=SOFT, stroke=accent, sw=1.8, color=INK, bold=True))
        kids = ["cc1", "cc1", "cc1", "ld"]
        for i, k in enumerate(kids):
            kx = ox + 22 + i * 104
            out.append(fitbox(kx, 236, 88, 42, k, size=12,
                              fill=SOFT, stroke=accent, sw=1.5, color=INK))
            out.append(line(ox + 215, 170, kx + 44, 236, color=accent, sw=1.2))
        return out

    # ── ліва половина: ліміт на кожен процес ─────────────────────────────────
    lx = 40
    p.append(fitbox(lx, 62, 440, 34, "Стеля на КОЖЕН процес: 1 ГіБ", size=14,
                    fill=WARM, stroke=POS, sw=1.8, color=POS, bold=True))
    p.extend(tree(lx, POS))
    for i in range(4):
        p.append(text(lx + 66 + i * 104, 300, "1 ГіБ", size=11, color=MUTED))
    p.append(fitbox(lx, 328, 440, 76,
                    "1 + 1 + 1 + 1 + 1 = 5 ГіБ\n"
                    "жодної стелі не порушено — і машина все одно стала",
                    size=12, fill="#fff", stroke=POS, sw=1.4, color=INK))

    # ── права половина: ліміт на групу ───────────────────────────────────────
    rx = 560
    p.append(fitbox(rx, 62, 440, 34, "Стеля на ГРУПУ: 2 ГіБ", size=14,
                    fill=GREENF, stroke=FIELD, sw=1.8, color=FIELD, bold=True))
    p.append(rect(rx + 10, 110, 420, 200, fill="#f7fdf9", stroke=FIELD, sw=1.8, rx=12))
    p.append(text(rx + 24, 128, "cgroup", size=11, color=FIELD, anchor="start", bold=True))
    p.extend(tree(rx, FIELD))
    p.append(fitbox(rx, 328, 440, 76,
                    "рахується СУМА всього піддерева\n"
                    "дійшли до 2 ГіБ — ядро тисне саме на цю роботу",
                    size=12, fill="#fff", stroke=FIELD, sw=1.4, color=INK))

    p.append(line(520, 62, 520, 404, color="#d7dbe0", sw=1.4, dash="6 6"))
    p.append(fitbox(40, 430, 960, 62,
                    "одиниця обмеження мусить збігатися з одиницею роботи:\n"
                    "робота — це не процес, а все дерево процесів, яке з нього виросло",
                    size=12, fill=PALE, stroke=MUTED, sw=1.2, color=INK))
    p.append(text(W / 2, 526,
                  "розмножуючись, робота обходить будь-яку стелю, виставлену поштучно",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "per-process-vs-group.svg"), W, H, *p,
           title="Чому стелі на окремий процес недосить")


# ── 2. Ієрархія cgroup v2 ──────────────────────────────────────────────────────
def fig_hierarchy():
    W, H = 1080, 640
    p = []

    def node(x, y, w, label, accent, fill=SOFT):
        return fitbox(x, y, w, 46, label, size=12, fill=fill, stroke=accent, sw=1.7, color=INK)

    def procs(x, y, w, label):
        return fitbox(x, y, w, 38, label, size=11, fill=COOL, stroke=NEG, sw=1.4, color=NEG)

    # рівні
    p.append(node(440, 70, 200, "/  (корінь cgroup2)", INK, PALE))
    p.append(node(160, 176, 240, "system.slice", NEG))
    p.append(node(680, 176, 240, "user.slice", NEG))
    p.append(node(50, 282, 200, "nginx.service", FIELD))
    p.append(node(280, 282, 200, "postgres.service", FIELD))
    p.append(node(660, 282, 280, "user@1000.service", NEG))
    p.append(node(670, 388, 220, "app.slice", FIELD))

    # ребра
    p.append(line(540, 116, 280, 176, color=INK, sw=1.3))
    p.append(line(540, 116, 800, 176, color=INK, sw=1.3))
    p.append(line(280, 222, 150, 282, color=INK, sw=1.3))
    p.append(line(280, 222, 380, 282, color=INK, sw=1.3))
    p.append(line(800, 222, 800, 282, color=INK, sw=1.3))
    p.append(line(800, 328, 780, 388, color=INK, sw=1.3))

    # листки з процесами
    p.append(procs(50, 452, 200, "процеси: 812, 813"))
    p.append(procs(280, 452, 200, "процеси: 940 … 972"))
    p.append(procs(670, 452, 220, "процеси: 2311, 2404"))
    p.append(line(150, 328, 150, 452, color=NEG, sw=1.2, dash="4 4"))
    p.append(line(380, 328, 380, 452, color=NEG, sw=1.2, dash="4 4"))
    p.append(line(780, 434, 780, 452, color=NEG, sw=1.2, dash="4 4"))

    # пояснення
    p.append(fitbox(40, 524, 480, 74,
                    "процеси живуть ЛИШЕ в листках: вузол, що роздає ресурс дітям,\n"
                    "сам процесів не тримає — інакше його частка й частка його\n"
                    "дитини були б непорівнянні",
                    size=11, fill="#fff", stroke=FIELD, sw=1.4, color=INK))
    p.append(fitbox(560, 524, 480, 74,
                    "cgroup.subtree_control вирішує, які контролери батько\n"
                    "роздає дітям; дитина не бачить більше, ніж їй дали,\n"
                    "і не може вийти за батькову межу",
                    size=11, fill="#fff", stroke=NEG, sw=1.4, color=INK))
    render(os.path.join(OUT, "hierarchy.svg"), W, H, *p,
           title="Єдине дерево: облік і межі накопичуються вгору")


# ── 3. Вага проти стелі ────────────────────────────────────────────────────────
def fig_weight_vs_cap():
    W, H = 1040, 560
    p = []
    x0, bw = 70, 900

    # ── ВАГА ────────────────────────────────────────────────────────────────
    p.append(text(x0, 68, "Вага: ділиться тільки дефіцит", size=14, color=FIELD,
                  anchor="start", bold=True))

    p.append(text(x0, 100, "усі троє просять процесора", size=11, color=MUTED, anchor="start"))
    seg = [(0.25, "A · вага 100\n25 %", GREENF), (0.50, "B · вага 200\n50 %", "#d9f2e4"),
           (0.25, "C · вага 100\n25 %", GREENF)]
    cx = x0
    for frac, lab, fill in seg:
        w = bw * frac
        p.append(fitbox(cx, 112, w, 58, lab, size=12, fill=fill, stroke=FIELD, sw=1.6, color=INK))
        cx += w

    p.append(text(x0, 206, "B заснув — його частка не пропадає", size=11, color=MUTED, anchor="start"))
    cx = x0
    for frac, lab in [(0.5, "A · 50 %"), (0.5, "C · 50 %")]:
        w = bw * frac
        p.append(fitbox(cx, 218, w, 52, lab, size=12, fill=GREENF, stroke=FIELD, sw=1.6, color=INK))
        cx += w

    p.append(line(x0, 300, x0 + bw, 300, color="#d7dbe0", sw=1.4, dash="6 6"))

    # ── СТЕЛЯ ───────────────────────────────────────────────────────────────
    p.append(text(x0, 340, "Стеля: cpu.max = 200000 100000 (200 мс квоти на 100 мс періоду)",
                  size=14, color=POS, anchor="start", bold=True))
    p.append(text(x0, 372, "8 ниток, кожна рахує безперервно", size=11, color=MUTED, anchor="start"))

    run_w = bw * 0.25
    p.append(fitbox(x0, 384, run_w, 58, "виконуються\n0 … 25 мс", size=12,
                    fill=WARM, stroke=POS, sw=1.7, color=INK))
    p.append(fitbox(x0 + run_w, 384, bw - run_w, 58,
                    "заморожено 75 мс — навіть якщо всі ядра машини вільні",
                    size=12, fill="#fff", stroke=POS, sw=1.5, color=MUTED, rx=6))
    p.append(text(x0, 462, "0", size=10, color=MUTED, anchor="start"))
    p.append(text(x0 + run_w, 462, "25 мс", size=10, color=MUTED))
    p.append(text(x0 + bw, 462, "100 мс", size=10, color=MUTED, anchor="end"))

    p.append(fitbox(x0, 482, bw, 46,
                    "у середньому все ті самі 2 процесори — але затримка стрибає на десятки мілісекунд",
                    size=12, fill=PALE, stroke=MUTED, sw=1.2, color=INK))
    render(os.path.join(OUT, "weight-vs-cap.svg"), W, H, *p,
           title="Дві мови обмеження і чому вони не рівносильні")


# ── 4. Чотири позначки пам'яті ─────────────────────────────────────────────────
def fig_memory_bands():
    W, H = 1000, 600
    p = []
    bx, bw = 90, 190
    top, band = 96, 96          # верх колонки і висота смуги

    bands = [
        ("#fbe3df", POS,   "high … max",
         "ядро жене посилений відбір сторінок і присипляє нитку\n"
         "на виході з ядра: чим глибше зайшов, тим довша затримка"),
        ("#ffffff", MUTED, "low … high",
         "звичайна робота: ніхто нікого не чіпає"),
        ("#e6f6ec", FIELD, "min … low",
         "м'який захист: сторінки заберуть лише тоді,\n"
         "коли більше нема звідки"),
        ("#cdedd9", FIELD, "0 … min",
         "тверда підлога: відбір сторінок сюди не заходить узагалі"),
    ]

    for i, (fill, accent, name, note) in enumerate(bands):
        y = top + i * band
        p.append(rect(bx, y, bw, band, fill=fill, stroke=accent, sw=1.6, rx=0))
        p.append(text(bx + bw / 2, y + band / 2 + 4, name, size=12, color=accent, bold=True))
        p.append(line(bx + bw, y + band / 2, 330, y + band / 2, color=accent, sw=1.2))
        p.append(fitbox(340, y + 14, 610, band - 28, note, size=11,
                        fill="#fff", stroke=accent, sw=1.3, color=INK))

    # позначки шкали ліворуч
    marks = [(top, "memory.max"), (top + band, "memory.high"),
             (top + 2 * band, "memory.low"), (top + 3 * band, "memory.min"), (top + 4 * band, "0")]
    for y, lab in marks:
        p.append(line(bx - 8, y, bx, y, color=MUTED, sw=1.2))
        p.append(text(bx - 14, y + 4, lab, size=11, color=MUTED, anchor="end"))

    p.append(fitbox(340, 56, 610, 30,
                    "перевищили max: відбір не витяг → OOM усередині цієї групи",
                    size=12, fill=WARM, stroke=POS, sw=1.6, color=POS, bold=True))
    p.append(line(bx + bw / 2, top, bx + bw / 2, 86, color=POS, sw=1.6))

    p.append(fitbox(90, 500, 860, 66,
                    "пам'ять доводиться і обмежувати зверху, і берегти знизу:\n"
                    "відбір сторінок глобальний, тож без підлоги важливий кеш вимиє\n"
                    "будь-яке фонове копіювання файлів у сусідній групі",
                    size=12, fill=PALE, stroke=MUTED, sw=1.2, color=INK))
    render(os.path.join(OUT, "memory-bands.svg"), W, H, *p,
           title="Пам'ять: чотири позначки замість однієї стелі")


# ── 5. Глухий кут роздільних ієрархій (v1) ────────────────────────────────────
def fig_v1_crossing():
    W, H = 1060, 570
    p = []

    p.append(fitbox(50, 54, 440, 32, "ієрархія контролера memory", size=12,
                    fill=COOL, stroke=NEG, sw=1.6, color=NEG, bold=True))
    p.append(fitbox(570, 54, 440, 32, "ієрархія контролера blkio", size=12,
                    fill=GREENF, stroke=FIELD, sw=1.6, color=FIELD, bold=True))

    def tree(ox, accent, root, k1, k2):
        out = [fitbox(ox + 170, 104, 130, 38, root, size=12,
                      fill=PALE, stroke=accent, sw=1.6, color=INK, bold=True),
               fitbox(ox + 20, 180, 180, 42, k1, size=12,
                      fill=SOFT, stroke=accent, sw=1.5, color=INK),
               fitbox(ox + 250, 180, 180, 42, k2, size=12,
                      fill=SOFT, stroke=accent, sw=1.5, color=INK),
               line(ox + 235, 142, ox + 110, 180, color=accent, sw=1.2),
               line(ox + 235, 142, ox + 340, 180, color=accent, sw=1.2)]
        return out

    p.extend(tree(50, NEG, "/", "prod", "batch"))
    p.extend(tree(570, FIELD, "/", "fast", "slow"))

    p.append(fitbox(390, 268, 280, 44, "та сама задача 1234", size=12,
                    fill="#fff", stroke=INK, sw=1.8, color=INK, bold=True))
    p.append(line(390, 286, 200, 224, color=NEG, sw=1.3, dash="5 4"))
    p.append(line(670, 286, 860, 224, color=FIELD, sw=1.3, dash="5 4"))
    p.append(text(286, 306, "у memory/prod", size=10, color=NEG))
    p.append(text(774, 306, "у blkio/slow", size=10, color=FIELD))

    p.append(fitbox(300, 342, 460, 44,
                    "фонова нитка ядра несе на диск брудну сторінку", size=12,
                    fill=WARM, stroke=POS, sw=1.7, color=INK))
    p.append(line(530, 312, 530, 342, color=POS, sw=1.5))

    p.append(fitbox(90, 414, 880, 84,
                    "сторінку записали на memory/prod — але дерево blkio про вузол «prod» нічого не знає,\n"
                    "і спільної відповіді «чия ця сторінка і чий це диск» просто не існує:\n"
                    "увесь відкладений запис лягав на фонову нитку, повз будь-яку стелю",
                    size=12, fill="#fff", stroke=POS, sw=1.5, color=INK))
    p.append(text(W / 2, 534,
                  "полагодити це в межах роздільних дерев не було чим — звідси й друга версія",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "v1-crossing.svg"), W, H, *p,
           title="Чому роздільні ієрархії першої версії зайшли в глухий кут")


# ── 6. Хронологія ─────────────────────────────────────────────────────────────
def fig_timeline():
    rows = [
        ("2004–2005", NEG, "cpusets: прив'язка до ядер і вузлів пам'яті. Каркас, з якого потім виросло все"),
        ("2006", NEG, "Google: «process containers» — узагальнення cpusets до довільних контролерів"),
        ("кін. 2007", MUTED, "перейменування на «control groups»: слово «container» уже зайняте"),
        ("січень 2008", NEG, "2.6.24: cgroups у ядрі. Кожен контролер — власна ієрархія"),
        ("2008–2012", NEG, "контролери множаться: пам'ять, blkio, квота процесора, freezer, PIDs"),
        ("березень 2012", POS, "публічне «так далі не можна»: роздільні дерева не дають списати відкладений запис"),
        ("серпень 2014", FIELD, "3.16: єдине дерево під прапорцем __DEVEL__sane_behavior"),
        ("2015", FIELD, "4.2: облік відкладеного запису — та сама поломка, заради якої все й починалося"),
        ("березень 2016", FIELD, "4.5: тип ФС cgroup2, інтерфейс оголошено стабільним — але без процесора"),
        ("2016–2017", POS, "суперечка з планувальником: заборона процесів у вузлах і облік на процес, не на нитку"),
        ("січень 2018", FIELD, "4.15: контролер процесора у v2 разом із «нитковим» режимом"),
        ("2018", FIELD, "4.20: PSI — не «скільки взяв», а «скільки простояв»"),
        ("2019–2022", FIELD, "дистрибутиви перемикаються за замовчуванням: Fedora 31 → Debian 11 → RHEL 9"),
    ]
    W = 1080
    top, rh = 74, 54
    H = top + len(rows) * rh + 66
    p = [text(W / 2, 50, "від латки для машин з нерівномірною пам'яттю "
                         "до одиниці обліку всієї машини", size=12, color=MUTED, italic=True)]
    p.append(line(212, top, 212, top + len(rows) * rh - 12, color="#d7dbe0", sw=2))
    for i, (year, accent, what) in enumerate(rows):
        y = top + i * rh
        p.append(fitbox(60, y, 140, 40, year, size=11,
                        fill="#fff", stroke=accent, sw=1.5, color=accent, bold=True))
        p.append(circle(212, y + 20, 5, fill=accent, stroke=accent, sw=1))
        p.append(fitbox(232, y, 788, 40, what, size=11,
                        fill=SOFT, stroke=accent, sw=1.2, color=INK))
    p.append(text(W / 2, H - 30,
                  "шістнадцять років між першою латкою й типовою машиною, де все це ввімкнено з коробки",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Хронологія cgroups")


if __name__ == "__main__":
    fig_per_process_vs_group()
    fig_hierarchy()
    fig_weight_vs_cap()
    fig_memory_bands()
    fig_v1_crossing()
    fig_timeline()
    print("ok")


# ── 7. Звідки в каталозі беруться файли (вставка api-) ─────────────────────────
def fig_file_origin():
    W, H = 1080, 600
    p = []
    LX, LW = 60, 460
    RX, RW = 560, 460

    # ── батько ───────────────────────────────────────────────────────────────
    p.append(fitbox(LX, 60, LW, 34, "БАТЬКО   /sys/fs/cgroup/build", size=13,
                    fill=PALE, stroke=INK, sw=1.7, color=INK, bold=True))
    p.append(fitbox(LX, 104, LW, 56,
                    "cgroup.controllers   (лише читання)\n"
                    "cpu   io   memory   pids",
                    size=12, fill=SOFT, stroke=NEG, sw=1.5, color=INK))
    p.append(fitbox(LX, 172, LW, 56,
                    "cgroup.subtree_control   (запис)\n"
                    "+cpu +memory",
                    size=12, fill=GREENF, stroke=FIELD, sw=1.8, color=INK))
    p.append(arrow(LX + LW / 2, 236, LX + LW / 2, 284, color=FIELD, sw=2))

    # ── дитина ───────────────────────────────────────────────────────────────
    p.append(fitbox(LX, 292, LW, 34, "ДИТИНА   /sys/fs/cgroup/build/job1", size=13,
                    fill=PALE, stroke=INK, sw=1.7, color=INK, bold=True))
    p.append(fitbox(LX, 336, LW, 56,
                    "cgroup.controllers   (лише читання)\n"
                    "cpu   memory   — рівно те, що дав батько",
                    size=12, fill=SOFT, stroke=NEG, sw=1.5, color=INK))

    # ── наслідки праворуч ────────────────────────────────────────────────────
    p.append(fitbox(RX, 104, RW, 150,
                    "у каталозі дитини З'ЯВИЛИСЯ:\n"
                    "cpu.weight   cpu.weight.nice   cpu.max\n"
                    "cpu.max.burst   cpu.idle   cpu.uclamp.min\n"
                    "memory.max   memory.high   memory.low\n"
                    "memory.min   memory.events   memory.stat",
                    size=12, fill="#f7fdf9", stroke=FIELD, sw=1.6, color=INK))
    p.append(fitbox(RX, 292, RW, 100,
                    "і НЕ з'явилися:\n"
                    "io.max   io.weight   io.latency   pids.max\n"
                    "— батько не ввімкнув io й pids",
                    size=12, fill=WARM, stroke=POS, sw=1.6, color=INK))

    p.append(arrow(LX + LW + 8, 196, RX - 8, 174, color=FIELD, sw=1.8))
    p.append(arrow(LX + LW + 8, 212, RX - 8, 332, color=POS, sw=1.8))

    # ── ядрові файли ─────────────────────────────────────────────────────────
    p.append(fitbox(60, 428, 960, 88,
                    "ядрові файли є в КОЖНОМУ каталозі незалежно від контролерів:\n"
                    "cgroup.type   cgroup.procs   cgroup.threads   cgroup.controllers\n"
                    "cgroup.subtree_control   cgroup.events   cgroup.stat   cgroup.freeze   cgroup.kill\n"
                    "cpu.stat   cpu.pressure   memory.pressure   io.pressure",
                    size=12, fill="#ffffff", stroke=MUTED, sw=1.4, color=INK))
    p.append(fitbox(60, 530, 960, 42,
                    "у самого кореня /sys/fs/cgroup файлів обмежень немає: його ліміти нема кому ввімкнути",
                    size=12, fill=PALE, stroke=MUTED, sw=1.2, color=INK))

    render(os.path.join(OUT, "file-origin.svg"), W, H, *p,
           title="Файл у каталозі створює не сама група, а її батько")


if __name__ == "__main__":
    fig_file_origin()


# ── 8. Межа делегування: де саме нам можна копати (вставка proj-) ──────────────
def fig_delegation():
    W, H = 1120, 660
    p = []

    chain = [
        (60, "/sys/fs/cgroup   —   корінь", PALE, MUTED),
        (122, "user.slice", SOFT, MUTED),
        (184, "user@1000.service", SOFT, MUTED),
        (246, "run-cglab.scope   ·   Delegate=yes", COOL, NEG),
    ]
    for y, lab, fill, accent in chain:
        p.append(fitbox(60, y, 400, 46, lab, size=12, fill=fill, stroke=accent,
                        sw=1.6, color=INK))
    for y in (106, 168, 230):
        p.append(line(150, y, 150, y + 16, color=MUTED, sw=1.3))

    p.append(line(30, 322, 600, 322, color=POS, sw=2.4, dash="9 6"))
    p.append(text(34, 314, "межа делегування", size=11, color=POS,
                  anchor="start", bold=True))

    p.append(fitbox(60, 352, 230, 56, "leaf\nсюди зсунули оболонку",
                    size=12, fill=GREENF, stroke=FIELD, sw=1.7, color=INK))
    p.append(fitbox(330, 352, 230, 56, "lab\nдослід", size=12,
                    fill=GREENF, stroke=FIELD, sw=1.7, color=INK))
    p.append(line(150, 292, 150, 352, color=FIELD, sw=1.4))
    p.append(line(240, 292, 430, 352, color=FIELD, sw=1.4))

    p.append(fitbox(330, 446, 108, 44, "lab/a", size=12,
                    fill="#f7fdf9", stroke=FIELD, sw=1.4, color=INK))
    p.append(fitbox(452, 446, 108, 44, "lab/b", size=12,
                    fill="#f7fdf9", stroke=FIELD, sw=1.4, color=INK))
    p.append(line(384, 408, 384, 446, color=FIELD, sw=1.2, dash="4 4"))
    p.append(line(506, 408, 506, 446, color=FIELD, sw=1.2, dash="4 4"))

    p.append(fitbox(60, 526, 500, 96,
                    "щоб увімкнути контролери в scope, спершу заберіть\n"
                    "з нього всі процеси: вузол, який роздає ресурс дітям,\n"
                    "сам процесів не тримає — інакше запис у\n"
                    "cgroup.subtree_control поверне EBUSY",
                    size=11, fill=PALE, stroke=MUTED, sw=1.2, color=INK))

    notes = [
        (60, 92, GREENF, FIELD,
         "НИЖЧЕ межі — ваше\nmkdir і rmdir; у створеній вами теці\n"
         "всі файли одразу належать вам"),
        (168, 92, GREENF, FIELD,
         "у самому зрізі віддано в оренду три файли:\n"
         "cgroup.procs · cgroup.threads\ncgroup.subtree_control"),
        (276, 92, WARM, POS,
         "ВИЩЕ межі — systemd\nйого дерево перезбирається на кожному\n"
         "daemon-reload; ваші зміни зникнуть"),
        (384, 74, PALE, MUTED,
         "cpu.max і memory.max самого зрізу\n"
         "виставляє systemd — властивостями юніта"),
        (476, 146, COOL, NEG,
         "перевірка перед стартом:\n"
         "stat -fc %T /sys/fs/cgroup  →  cgroup2fs\n"
         "cat cgroup.controllers  →  що вам справді дали\n"
         "(у сеансі часто лише memory pids —\n"
         "cpu долучають окремо)"),
    ]
    for y, h, fill, accent, s in notes:
        p.append(fitbox(640, y, 440, h, s, size=11, fill=fill, stroke=accent,
                        sw=1.4, color=INK))

    render(os.path.join(OUT, "delegation.svg"), W, H, *p,
           title="Де саме нам можна копати, не воюючи з systemd")


# ── 9. Вікно між народженням і переведенням (вставка proj-) ────────────────────
def fig_spawn_race():
    W, H = 1080, 480
    p = []

    p.append(fitbox(40, 70, 250, 62, "fork()\n+ запис PID у cgroup.procs",
                    size=12, fill=WARM, stroke=POS, sw=1.7, color=INK, bold=True))
    steps1 = [(310, 130, "fork", SOFT, MUTED),
              (450, 300, "дитина вже біжить\nі списується на СТАРУ групу", WARM, POS),
              (760, 170, "запис PID", SOFT, MUTED),
              (940, 100, "у групі", GREENF, FIELD)]
    for x, w, lab, fill, accent in steps1:
        p.append(fitbox(x, 76, w, 50, lab, size=11, fill=fill, stroke=accent,
                        sw=1.6, color=INK))
    p.append(text(600, 148, "вікно перегонів", size=11, color=POS, bold=True))

    p.append(line(40, 176, 1040, 176, color="#d7dbe0", sw=1.3, dash="6 6"))

    p.append(fitbox(40, 208, 250, 62, "clone3()\nз CLONE_INTO_CGROUP",
                    size=12, fill=GREENF, stroke=FIELD, sw=1.7, color=INK, bold=True))
    p.append(fitbox(310, 214, 130, 50, "clone3", size=11, fill=SOFT,
                    stroke=MUTED, sw=1.6, color=INK))
    p.append(fitbox(450, 214, 590, 50,
                    "перша ж інструкція дитини виконується вже всередині",
                    size=11, fill=GREENF, stroke=FIELD, sw=1.6, color=INK))
    p.append(text(745, 288, "вікна немає", size=11, color=FIELD, bold=True))

    p.append(fitbox(40, 318, 1000, 76,
                    "у вікні дитина встигає виділити пам'ять — і та спишеться сусідній групі,\n"
                    "де й залишиться; встигає розгалузитися далі; встигає навіть померти,\n"
                    "і тоді ваша група не побачить її взагалі",
                    size=12, fill="#ffffff", stroke=POS, sw=1.4, color=INK))
    p.append(fitbox(40, 410, 1000, 46,
                    "плата: цільова тека мусить бути листком — clone3 поверне EBUSY, "
                    "якщо в ній самій увімкнено контролери",
                    size=11, fill=PALE, stroke=MUTED, sw=1.2, color=INK))

    render(os.path.join(OUT, "spawn-race.svg"), W, H, *p,
           title="Народити всередині групи проти «народити й перевести»")


if __name__ == "__main__":
    fig_delegation()
    fig_spawn_race()
