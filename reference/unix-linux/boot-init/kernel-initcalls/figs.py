# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#eceff1"
WHITE = "#ffffff"


# ── 1. Шлях одного покажчика: джерело → об'єктний файл → vmlinux ─────────────
def fig_pipeline():
    W, H = 1440, 620
    p = []

    ax, aw = 40, 400
    bx, bw = 512, 380
    cx, cw = 964, 436
    top = 96

    p.append(text(ax + aw / 2, 60, "У джерелі підсистеми", size=16, bold=True))
    p.append(text(bx + bw / 2, 60, "В об'єктному файлі", size=16, bold=True))
    p.append(text(cx + cw / 2, 60, "У зібраному образі ядра", size=16, bold=True))

    # A — код
    p.append(rect(ax, top, aw, 200, fill=WHITE, stroke=MUTED, sw=1.2, rx=10))
    p.append(fitbox(ax + 18, top + 24, aw - 36, 60,
                    "static int __init foo_init(void)\n{ ... }",
                    size=14, fill=GREY_FILL, stroke=MUTED, sw=1.0))
    p.append(fitbox(ax + 18, top + 104, aw - 36, 44,
                    "subsys_initcall(foo_init);",
                    size=14, bold=True, fill=BLUE_FILL, stroke=NEG, sw=1.4))
    p.append(fitbox(ax + 18, top + 158, aw - 36, 30,
                    "жодного центрального списку не правимо",
                    size=12, fill=WHITE, stroke=WHITE, sw=0.0))

    # B — секція в .o
    p.append(rect(bx, top, bw, 200, fill=WHITE, stroke=MUTED, sw=1.2, rx=10))
    p.append(fitbox(bx + 18, top + 24, bw - 36, 40, "секція .initcall4.init",
                    size=14, bold=True, fill=WARM_FILL, stroke=MUTED, sw=1.2))
    p.append(fitbox(bx + 18, top + 76, bw - 36, 76,
                    "один запис завдовжки 4 байти:\nзсув від цього місця до foo_init",
                    size=13, fill=WHITE, stroke=MUTED, sw=1.0))
    p.append(fitbox(bx + 18, top + 160, bw - 36, 28,
                    "де саме — вирішує число 4 в макросі",
                    size=12, fill=WHITE, stroke=WHITE, sw=0.0))

    # C — зібраний масив
    p.append(rect(cx, top, cw, 372, fill=WHITE, stroke=MUTED, sw=1.2, rx=10))
    rows = [
        ("__initcall3_start", "sym", None),
        ("записи рівня arch", "cell", GREY_FILL),
        ("__initcall4_start", "sym", None),
        ("записи рівня subsys, зібрані з усіх .o", "cell", GREY_FILL),
        ("наш запис — foo_init", "cell", BLUE_FILL),
        ("решта записів рівня subsys", "cell", GREY_FILL),
        ("__initcall5_start", "sym", None),
    ]
    y = top + 22
    for label, kind, fill in rows:
        if kind == "sym":
            p.append(fitbox(cx + 20, y, cw - 40, 30, label, size=13, bold=True,
                            fill=GREEN_FILL, stroke=FIELD, sw=1.2))
            y += 38
        else:
            p.append(fitbox(cx + 20, y, cw - 40, 40, label, size=13,
                            fill=fill, stroke=MUTED, sw=1.1))
            y += 48

    # стрілки між панелями
    p.append(arrow(ax + aw + 12, top + 100, bx - 12, top + 100))
    p.append(text((ax + aw + bx) / 2, top + 84, "компілятор", size=13, color=MUTED))
    p.append(arrow(bx + bw + 12, top + 100, cx - 12, top + 100))
    p.append(text((bx + bw + cx) / 2, top + 84, "компонувальник", size=13, color=MUTED))

    p.append(fitbox(40, 516, 1360, 66,
                    "Масив ніхто не оголошував: він виник сам, бо компонувальник зсипає"
                    " однойменні секції всіх об'єктних файлів в одне суцільне місце.\n"
                    "Ядру лишається пройти його від межі до межі — і в цьому весь механізм.",
                    size=14, fill=WARM_FILL, stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'initcall-pipeline.svg'), W, H, *p)


# ── 2. Сходи рівнів: макрос, секція, що там живе ─────────────────────────────
def fig_levels():
    W, H = 1460, 860
    p = []

    c1x, c1w = 40, 252
    c2x, c2w = 308, 264
    c3x, c3w = 588, 832

    p.append(text(c1x + c1w / 2, 62, "макрос", size=15, bold=True))
    p.append(text(c2x + c2w / 2, 62, "секція", size=15, bold=True))
    p.append(text(c3x + c3w / 2, 62, "що туди кладуть", size=15, bold=True))

    rows = [
        ("early_initcall", ".initcallearly.init",
         "виконується окремим проходом ще до підняття решти процесорів", WARM_FILL),
        ("pure_initcall", ".initcall0.init",
         "не залежить ні від чого: лише задає змінні, яких не задати статично", BLUE_FILL),
        ("core_initcall", ".initcall1.init",
         "серцевина ядра: те, на що спирається геть усе інше", BLUE_FILL),
        ("postcore_initcall", ".initcall2.init",
         "спирається на серцевину, але потрібне ще до архітектурного коду", BLUE_FILL),
        ("arch_initcall", ".initcall3.init",
         "залежне від архітектури: шини платформи, особливості процесора", BLUE_FILL),
        ("subsys_initcall", ".initcall4.init",
         "великі підсистеми: типи шин, мережа, керування живленням", BLUE_FILL),
        ("fs_initcall", ".initcall5.init",
         "файлові системи й те, що реєструється всередині них", BLUE_FILL),
        ("rootfs_initcall", ".initcallrootfs.init",
         "розпакування initramfs; лежить усередині діапазону рівня fs", GREEN_FILL),
        ("device_initcall", ".initcall6.init",
         "драйвери; сюди ж потрапляє module_init вбудованого модуля", BLUE_FILL),
        ("late_initcall", ".initcall7.init",
         "останнє: те, чому потрібна вже готова решта системи", BLUE_FILL),
    ]

    y = 84
    rh, gap = 62, 10
    for macro, sec, what, fill in rows:
        p.append(fitbox(c1x, y, c1w, rh, macro, size=15, bold=True, fill=fill,
                        stroke=MUTED, sw=1.2))
        p.append(fitbox(c2x, y, c2w, rh, sec, size=13, fill=WHITE, stroke=MUTED, sw=1.1))
        p.append(fitbox(c3x, y, c3w, rh, what, size=14, fill=WHITE, stroke=MUTED, sw=1.1))
        y += rh + gap

    p.append(fitbox(c1x, y + 12, c3x + c3w - c1x, 62,
                    "Суфікс _sync дає ту саму назву з літерою s (.initcall4s.init) — другий слот"
                    " у хвості того самого рівня.\nЖодної окремої дії він не виконує: усе, що він"
                    " робить, — стає після решти записів свого рівня.",
                    size=14, fill=WARM_FILL, stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'initcall-levels.svg'), W, H, *p)


# ── 3. Статичний порядок проти графа, відомого лише на машині ────────────────
def fig_static_vs_graph():
    W, H = 1440, 800
    p = []

    lx, lw = 40, 600
    rx, rw = 700, 700
    top = 92

    p.append(text(lx + lw / 2, 58, "Що рівні впорядковують добре", size=16, bold=True))
    p.append(text(rx + rw / 2, 58, "Чого вони впорядкувати не можуть", size=16, bold=True))

    p.append(rect(lx, top, lw, 420, fill=WHITE, stroke=MUTED, sw=1.2, rx=10))
    chain = [
        ("розподільник пам'яті", "core"),
        ("тип шини як поняття", "subsys"),
        ("драйвер контролера шини", "device"),
        ("драйвер пристрою на шині", "device"),
    ]
    y = top + 28
    for what, lvl in chain:
        p.append(fitbox(lx + 30, y, 400, 52, what, size=14, fill=BLUE_FILL,
                        stroke=NEG, sw=1.2))
        p.append(text(lx + 486, y + 32, lvl, size=13, color=MUTED))
        if lvl != "device" or what != "драйвер пристрою на шині":
            p.append(arrow(lx + 230, y + 54, lx + 230, y + 86))
        y += 92
    p.append(fitbox(lx + 24, top + 372, lw - 48, 34,
                    "Це відношення однакове на всіх машинах світу",
                    size=13, fill=WHITE, stroke=WHITE, sw=0.0))

    p.append(rect(rx, top, rw, 420, fill=WHITE, stroke=MUTED, sw=1.2, rx=10))
    gx = rx + 40
    p.append(fitbox(gx, top + 26, 250, 52, "тактовий генератор", size=14,
                    fill=GREY_FILL, stroke=MUTED, sw=1.2))
    p.append(fitbox(gx + 366, top + 26, 250, 52, "регулятор живлення", size=14,
                    fill=GREY_FILL, stroke=MUTED, sw=1.2))
    p.append(fitbox(gx, top + 148, 250, 52, "контролер I²C", size=14,
                    fill=GREY_FILL, stroke=MUTED, sw=1.2))
    p.append(fitbox(gx + 120, top + 270, 250, 52, "сенсор на шині", size=14,
                    fill=RED_FILL, stroke=POS, sw=1.4))

    p.append(arrow(gx + 125, top + 80, gx + 125, top + 144))
    p.append(arrow(gx + 125, top + 202, gx + 200, top + 266))
    p.append(arrow(gx + 491, top + 80, gx + 300, top + 266))

    p.append(fitbox(rx + 24, top + 348, rw - 48, 58,
                    "Цей граф описує прошивка конкретної плати.\n"
                    "У сирцях ядра його немає й бути не може.",
                    size=13, fill=WHITE, stroke=WHITE, sw=0.0))

    # нижня смуга — цикл повторних спроб
    by = 570
    p.append(text(W / 2, by - 16, "Тому порядок замінили повторною спробою", size=16, bold=True))
    cells = [
        ("драйвер бачить,\nщо ресурсу ще немає", GREY_FILL),
        ("повертає -EPROBE_DEFER", WARM_FILL),
        ("пристрій лягає\nв список відкладених", GREY_FILL),
        ("будь-яка вдала прив'язка\nбудить увесь список", GREEN_FILL),
    ]
    cw2, gap2 = 300, 44
    x = (W - (len(cells) * cw2 + (len(cells) - 1) * gap2)) / 2
    for label, fill in cells:
        p.append(fitbox(x, by + 8, cw2, 78, label, size=14, fill=fill,
                        stroke=MUTED, sw=1.2))
        x += cw2 + gap2
    for i in range(len(cells) - 1):
        ax0 = (W - (len(cells) * cw2 + (len(cells) - 1) * gap2)) / 2 + (i + 1) * cw2 + i * gap2
        p.append(arrow(ax0 + 6, by + 47, ax0 + gap2 - 6, by + 47))

    p.append(fitbox(120, by + 118, W - 240, 34,
                    "Коло замикається: остання клітинка повертає до першої, аж поки"
                    " не лишиться жодного відкладеного або не збіжить час очікування",
                    size=13, fill=WHITE, stroke=WHITE, sw=0.0))

    render(os.path.join(IMG, 'static-order-vs-graph.svg'), W, H, *p)


# ── 4. Символи-межі й те, який прохід бере який шматок ───────────────────────
def fig_boundaries():
    W, H = 1500, 1000
    p = []

    sx, sw_ = 60, 470
    px, pw = 576, 336
    kx, kw = 984, 456

    p.append(text(sx + sw_ / 2, 58, "Один масив у зібраному образі", size=16, bold=True))
    p.append(text(px + pw / 2, 58, "Хто його проходить", size=16, bold=True))
    p.append(text(kx + kw / 2, 58, "Окремий масив — консолі", size=16, bold=True))

    rows = [
        ("sym", "__initcall_start"),
        ("sec", ".initcallearly.init"),
        ("sym", "__initcall0_start"),
        ("sec", ".initcall0.init"),
        ("sym", "__initcall1_start"),
        ("sec", ".initcall1.init · .initcall1s.init"),
        ("sym", "__initcall2_start"),
        ("sec", ".initcall2.init · .initcall2s.init"),
        ("sym", "__initcall3_start"),
        ("sec", ".initcall3.init · .initcall3s.init"),
        ("sym", "__initcall4_start"),
        ("sec", ".initcall4.init · .initcall4s.init"),
        ("sym", "__initcall5_start"),
        ("sec", ".initcall5.init · .initcall5s.init"),
        ("sym", "__initcallrootfs_start"),
        ("sec", ".initcallrootfs.init"),
        ("sym", "__initcall6_start"),
        ("sec", ".initcall6.init · .initcall6s.init"),
        ("sym", "__initcall7_start"),
        ("sec", ".initcall7.init · .initcall7s.init"),
        ("sym", "__initcall_end"),
    ]

    ys = []
    y = 84
    for kind, label in rows:
        h = 28 if kind == "sym" else 42
        ys.append((y, h))
        if kind == "sym":
            p.append(fitbox(sx, y, sw_, h, label, size=13, bold=True,
                            fill=GREEN_FILL, stroke=FIELD, sw=1.2))
        else:
            fill = WARM_FILL if ("early" in label or "rootfs" in label) else WHITE
            p.append(fitbox(sx, y, sw_, h, label, size=13, fill=fill,
                            stroke=MUTED, sw=1.1))
        y += h + 6

    passes = [
        (1, 1, "прохід «early»"),
        (3, 3, "прохід «pure»"),
        (5, 5, "прохід «core»"),
        (7, 7, "прохід «postcore»"),
        (9, 9, "прохід «arch»"),
        (11, 11, "прохід «subsys»"),
        (13, 15, "прохід «fs»\nмежа шостого рівня\nстоїть після rootfs —\nтож rootfs тут"),
        (17, 17, "прохід «device»"),
        (19, 19, "прохід «late»"),
    ]
    for i0, i1, label in passes:
        y0 = ys[i0][0]
        y1 = ys[i1][0] + ys[i1][1]
        p.append(fitbox(px, y0, pw, y1 - y0, label, size=13, fill=BLUE_FILL,
                        stroke=NEG, sw=1.2))

    ky = 84
    for kind, label in [("sym", "__con_initcall_start"),
                        ("sec", ".con_initcall.init"),
                        ("sym", "__con_initcall_end")]:
        h = 28 if kind == "sym" else 42
        if kind == "sym":
            p.append(fitbox(kx, ky, kw, h, label, size=13, bold=True,
                            fill=GREEN_FILL, stroke=FIELD, sw=1.2))
        else:
            p.append(fitbox(kx, ky, kw, h, label, size=13, fill=WHITE,
                            stroke=MUTED, sw=1.1))
        ky += h + 6

    p.append(fitbox(kx, ky + 24, kw, 132,
                    "console_init() проходить його рано й окремо,\n"
                    "щоб було куди друкувати журнал.\n"
                    "Записи викликаються прямо, не через\n"
                    "do_one_initcall() — тож initcall_blacklist=\n"
                    "їх не бачить.",
                    size=14, fill=WARM_FILL, stroke=MUTED, sw=1.2))

    p.append(fitbox(kx, ky + 192, kw, 132,
                    "Ім'я проходу — не прикраса. Тим самим\n"
                    "рядком ядро розбирає параметри\n"
                    "командного рядка саме перед цим\n"
                    "проходом і ним же помічає точку\n"
                    "трасування initcall_level.",
                    size=14, fill=BLUE_FILL, stroke=NEG, sw=1.2))

    p.append(fitbox(kx, ky + 360, kw, 132,
                    "Суфікс _sync дає другу секцію того\n"
                    "самого рівня — з літерою s на кінці.\n"
                    "Компонувальник ставить її одразу після\n"
                    "основної, тож ці виклики йдуть у хвості\n"
                    "свого проходу.",
                    size=14, fill=GREY_FILL, stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'initcall-boundaries.svg'), W, H, *p)


# ── Той самий рядок джерела: дві дороги (вставка proj-initcall-lab) ─────────
def fig_two_paths():
    W, H = 1420, 800
    p = []

    lx, lw = 30, 210          # стовпчик підписів рядків
    ax, aw = 268, 552         # ліворуч — зібрано в образ
    bx, bw = 848, 552         # праворуч — зібрано модулем

    p.append(fitbox(ax, 34, bx + bw - ax, 60,
                    "module_init(lab_init);   — ОДИН рядок у джерелі",
                    size=17, bold=True, fill=WARM_FILL, stroke=MUTED, sw=1.4))
    p.append(arrow(ax + aw / 2, 100, ax + aw / 2, 142))
    p.append(arrow(bx + bw / 2, 100, bx + bw / 2, 142))

    p.append(fitbox(ax, 148, aw, 48, "зібрано в образ  (obj-y)",
                    size=16, bold=True, fill=BLUE_FILL, stroke=NEG, sw=1.4))
    p.append(fitbox(bx, 148, bw, 48, "зібрано модулем  (obj-m)",
                    size=16, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.4))

    rows = [
        ("що це\nнасправді",
         "розгортається в device_initcall(lab_init)",
         "стає псевдонімом init_module у lab.ko",
         WHITE),
        ("де живе\nзапис",
         "зсув до функції в секції .initcall6.init,\n"
         "між __initcall6_start і __initcall7_start",
         "функція в .init.text файла lab.ko;\n"
         "жодного запису в таблиці ядра немає",
         WHITE),
        ("хто й коли\nвикликає",
         "цикл do_initcall_level(6) у потоці pid 1,\n"
         "до першої програми простору користувача",
         "завантажувач модулів у мить insmod,\n"
         "у контексті процесу, що вантажить",
         WHITE),
        ("що видно\nв журналі",
         "calling  lab_init+0x0/0x18 @ 1",
         "calling  lab_init+0x0/0x18 [lab] @ 1423",
         WARM_FILL),
        ("коли тіло\nзникає",
         "free_initmem() наприкінці завантаження —\n"
         "разом з усією секцією ініціалізації",
         "одразу після вдалого insmod —\n"
         "звільняють init-пам'ять самого модуля",
         GREY_FILL),
    ]

    y, rh, gap = 218, 96, 14
    for label, left, right, fill in rows:
        p.append(fitbox(lx, y, lw, rh, label, size=14, bold=True,
                        fill=GREY_FILL, stroke=MUTED, sw=1.2))
        p.append(fitbox(ax, y, aw, rh, left, size=14, fill=fill,
                        stroke=NEG, sw=1.2))
        p.append(fitbox(bx, y, bw, rh, right, size=14, fill=fill,
                        stroke=FIELD, sw=1.2))
        y += rh + gap

    p.append(fitbox(lx, y + 12, bx + bw - lx, 62,
                    "Дороги різні від початку до кінця, а сходяться рівно в одній функції — "
                    "do_one_initcall().\n"
                    "Тому пара рядків у журналі однакова, і лише номер процесу та суфікс "
                    "[lab] кажуть, якою дорогою прийшов виклик.",
                    size=14, fill=BLUE_FILL, stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'two-paths-of-module-init.svg'), W, H, *p)


if __name__ == '__main__':
    fig_pipeline()
    fig_levels()
    fig_static_vs_graph()
    fig_boundaries()
    fig_two_paths()
    print("ok")
