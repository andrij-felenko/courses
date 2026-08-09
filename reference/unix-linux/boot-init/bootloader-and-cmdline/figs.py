# -*- coding: utf-8 -*-
"""Фігури до теми «Завантажувач і командний рядок ядра»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

GREEN_FILL = "#eaf7ef"
RED_FILL = "#fdecea"
BLUE_FILL = "#eaf0fd"
GREY_FILL = "#f4f6f8"


# ── 1. Що саме завантажувач мусить зробити перед стрибком ──────────────────
def fig_handoff():
    W, H = 1400, 520
    f = []

    f.append(text(220, 72, "що кладе в пам'ять", size=13, color=MUTED, bold=True))
    f.append(text(700, 72, "що вписує в заголовок образу", size=13, color=MUTED, bold=True))
    f.append(text(1160, 72, "і лише тоді — передача керування", size=13, color=MUTED, bold=True))

    # ліва колонка: вміст пам'яті
    mem = [
        (100, "образ ядра,\nрозпакований у своє місце", GREEN_FILL, FIELD),
        (220, "initramfs —\nархів так, як лежав на диску", BLUE_FILL, NEG),
        (340, "командний рядок —\nтекст із нулем у кінці", RED_FILL, POS),
    ]
    for y, s, fill, stroke in mem:
        f.append(fitbox(60, y, 320, 80, s, size=13, fill=fill, stroke=stroke))

    # середня колонка: поля заголовка
    hdr = [
        (100, "type_of_loader — хто саме завантажує"),
        (160, "cmdline_size — стеля, яку оголосило ядро"),
        (220, "ramdisk_image — адреса архіву initramfs"),
        (280, "ramdisk_size — довжина того архіву"),
        (340, "cmd_line_ptr — адреса рядка"),
    ]
    for y, s in hdr:
        f.append(fitbox(520, y, 360, 48, s, size=13, fill=GREY_FILL, stroke=MUTED))

    f.append(arrow(516, 244, 388, 258))
    f.append(arrow(516, 364, 388, 378))

    # права колонка: власне передача
    steps = [
        (120, "виставити стан процесора\nтак, як вимагає протокол"),
        (230, "стрибнути в точку входу\nобразу"),
        (340, "далі керує ядро —\nзавантажувача більше немає"),
    ]
    for y, s in steps:
        f.append(fitbox(980, y, 360, 70, s, size=13, fill=BG, stroke=INK))
    f.append(arrow(1160, 194, 1160, 226))
    f.append(arrow(1160, 304, 1160, 336))
    f.append(arrow(888, 265, 972, 265))

    f.append(text(700, 470,
                  "чого немає ні в пам'яті, ні в заголовку — того для ядра не існує",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'handoff.svg'), W, H, *f,
           title="Передача керування: пам'ять, заповнений заголовок і тільки після цього стрибок")


# ── 2. Куди потрапляє кожне слово командного рядка ─────────────────────────
def fig_word_routing():
    W, H = 1300, 700
    f = []

    f.append(fitbox(80, 50, 1140, 56,
                    "root=UUID=6f1c… ro quiet console=ttyS0,115200 i915.enable_psr=0 "
                    "systemd.unit=rescue.target -- verbose",
                    size=14, fill=GREY_FILL, stroke=INK))
    f.append(fitbox(500, 150, 300, 50, "ядро ріже рядок на слова\n(лапки шануються)",
                    size=13, fill=BG, stroke=MUTED))
    f.append(arrow(650, 110, 650, 146))

    rows = [
        (240, "слово стоїть після «--»",
         "потрапляє в argv першого процесу;\nядро його навіть не розглядає", RED_FILL, POS),
        (330, "у ключі є крапка: modname.param=…",
         "параметр модуля: вбудованому — одразу,\nзавантажному — коли той завантажиться", BLUE_FILL, NEG),
        (420, "ключ зареєстровано через early_param()",
         "обробник працює ще до підняття пам'яті:\nearlycon, memmap", GREEN_FILL, FIELD),
        (510, "ключ зареєстровано через __setup()",
         "звичайний обробник підсистеми:\nroot=, init=, quiet", GREEN_FILL, FIELD),
        (600, "ключа не впізнав ніхто",
         "є «=» — в оточення init;\nнемає «=» — у його argv", GREY_FILL, MUTED),
    ]
    for y, cond, out, fill, stroke in rows:
        f.append(fitbox(80, y, 430, 64, cond, size=13, fill=BG, stroke=MUTED))
        f.append(fitbox(620, y, 560, 64, out, size=13, fill=fill, stroke=stroke))
        f.append(arrow(514, y + 32, 616, y + 32))

    f.append(arrow(650, 202, 300, 236))
    for y in (240, 330, 420, 510):
        f.append(arrow(295, y + 66, 295, y + 86))

    f.append(text(650, 690,
                  "порядок перевірки саме такий — тому «--» вимикає всі правила, що нижче",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'word-routing.svg'), W, H, *f,
           title="Кожне слово рядка перевіряють за списком правил, і перше влучання вирішує його долю")


# ── 3. Звідки береться сам рядок ───────────────────────────────────────────
def fig_cmdline_sources():
    W, H = 1300, 520
    f = []

    f.append(text(235, 62, "чотири можливі джерела", size=13, color=MUTED, bold=True))
    f.append(text(1070, 62, "один рядок і його сліди", size=13, color=MUTED, bold=True))

    src = [
        (90, "рядок у записі меню\nзавантажувача"),
        (180, "властивість bootargs\nу дереві пристроїв"),
        (270, "CONFIG_CMDLINE,\nвшитий у сам образ"),
        (360, "секція .cmdline\nусередині UKI"),
    ]
    for y, s in src:
        f.append(fitbox(70, y, 330, 70, s, size=13, fill=BG, stroke=MUTED))

    f.append(fitbox(520, 190, 280, 170,
                    "правило злиття,\nобране при збірці ядра:\n \nбрати від завантажувача ·\nдодати до вшитого ·\nвшите переважає",
                    size=13, fill=GREY_FILL, stroke=INK))

    for y in (125, 215, 305, 395):
        f.append(arrow(404, y, 516, 275))

    res = [
        (150, "boot_command_line —\nрядок, який розбирають"),
        (260, "saved_command_line —\nкопія, збережена назавжди"),
        (370, "/proc/cmdline —\nте, що бачить система"),
    ]
    for y, s in res:
        f.append(fitbox(900, y, 340, 64, s, size=13, fill=GREEN_FILL, stroke=FIELD))
    f.append(arrow(1070, 216, 1070, 256))
    f.append(arrow(1070, 326, 1070, 366))
    f.append(arrow(806, 275, 896, 190))

    f.append(text(650, 480,
                  "лише рядок із UKI прикритий підписом — решту три можна змінити на місці",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'cmdline-sources.svg'), W, H, *f,
           title="Рядок збирають із кількох джерел за правилом, обраним ще при збірці ядра")


# ── 4. Розкладка єдиного образу ядра (вставка proj-uki-by-hand) ────────────
def fig_uki_layout():
    W, H = 1320, 660
    f = []

    f.append(text(235, 62, "що беремо з диска", size=13, color=MUTED, bold=True))
    f.append(text(770, 62, "один PE-файл, секції за зростанням адрес",
                  size=13, color=MUTED, bold=True))

    src = [
        (150, 66, "/usr/lib/os-release", GREEN_FILL, FIELD),
        (250, 76, "cmdline — рядок, записаний\nprintf, без переводу рядка", RED_FILL, POS),
        (370, 76, "vmlinuz — сам собою PE\nз EFI-заглушкою всередині", BLUE_FILL, NEG),
        (490, 76, "initramfs — архів так,\nяк він лежить на диску", BLUE_FILL, NEG),
    ]
    for y, h, s, fill, stroke in src:
        f.append(fitbox(60, y, 350, h, s, size=13, fill=fill, stroke=stroke))

    blocks = [
        (100, 64, ".text · .data · .reloc — код самої заглушки", GREY_FILL, MUTED),
        (190, 56, ".osrel · 0x20000 · 386 Б", GREEN_FILL, FIELD),
        (280, 56, ".cmdline · 0x21000 · 47 Б", RED_FILL, POS),
        (390, 76, ".linux · 0x22000 · 12.5 МіБ", BLUE_FILL, NEG),
        (510, 76, ".initrd · 0xCA2000 · 41.6 МіБ", BLUE_FILL, NEG),
    ]
    for y, h, s, fill, stroke in blocks:
        f.append(fitbox(580, y, 400, h, s, size=13, fill=fill, stroke=stroke))

    f.append(arrow(414, 183, 576, 218))
    f.append(arrow(414, 288, 576, 308))
    f.append(arrow(414, 408, 576, 428))
    f.append(arrow(414, 528, 576, 548))

    f.append(line(1010, 100, 1010, 586, color=MUTED, sw=1.5))
    f.append(line(1010, 100, 996, 100, color=MUTED, sw=1.5))
    f.append(line(1010, 586, 996, 586, color=MUTED, sw=1.5))
    f.append(fitbox(1028, 290, 250, 100,
                    "підпис sbsign накриває\nфайл цілком: підмінити\nодну секцію окремо\nвже неможливо",
                    size=13, fill=BG, stroke=INK))

    f.append(text(660, 630,
                  "проміжки між блоками — вирівнювання: секція починається "
                  "лише з межі, оголошеної в заголовку заглушки",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'uki-layout.svg'), W, H, *f,
           title="Єдиний образ ядра: ті самі чотири файли, покладені секціями за зростанням адрес")


# ── 5. Межі всередині одного слова (вставка api-cmdline-reference) ─────────
def _segrow(x, y, h, segs, size=15, gap=6):
    """Сегменти слова в ряд + короткий підпис під кожним. Повертає (фрагменти, кінець_x)."""
    out = []
    cx = float(x)
    for s, fill, stroke, label in segs:
        w = max(36.0, text_width(s, size, True) + 26)
        out.append(fitbox(cx, y, w, h, s, size=size, fill=fill, stroke=stroke, bold=True))
        if label:
            out.append(text(cx + w / 2, y + h + 22, label, size=12, color=MUTED))
        cx += w + gap
    return out, cx


def fig_word_anatomy():
    W, H = 1360, 620
    f = []

    rows = [
        (92, [("root", GREEN_FILL, FIELD, "ключ"),
              ("=", BG, INK, "перший «=»"),
              ("UUID=6f1c…", BLUE_FILL, NEG, "значення")],
         "Ключ — усе до ПЕРШОГО «=». Другий «=» стоїть уже всередині значення\n"
         "й нічого не ділить: тут ключ — root, значення — увесь рядок UUID=6f1c…"),

        (222, [("i915", GREY_FILL, MUTED, "модуль"),
               (".", BG, INK, "крапка"),
               ("enable_psr", GREEN_FILL, FIELD, "параметр"),
               ("=", BG, INK, ""),
               ("0", BLUE_FILL, NEG, "значення")],
         "Крапка віддає слово модулю. В іменах «-» і «_» рівнозначні\n"
         "(enable-psr — те саме), у значеннях — уже ні."),

        (352, [("dyndbg", GREEN_FILL, FIELD, "ключ"),
               ("=", BG, INK, ""),
               ('"file svc.c +p"', BLUE_FILL, NEG, "значення в лапках")],
         "Усередині лапок пробіл слово не ріже. Крайні лапки знімають,\n"
         "внутрішню лапку екранувати нічим — такої можливості просто немає."),

        (482, [("--", RED_FILL, POS, "не параметр")],
         "Самотнє «--» обриває розбір: усе далі ядро не розглядає взагалі\n"
         "й віддає першому процесу як його власні аргументи."),
    ]

    for y, segs, note in rows:
        frags, _ = _segrow(70, y, 52, segs)
        f.extend(frags)
        f.append(fitbox(430, y - 5, 860, 62, note, size=13, fill=BG, stroke=MUTED))

    f.append(text(680, 580,
                  "роздільник слів — пробіл; усе інше вирішує вже обробник ключа",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'word-anatomy.svg'), W, H, *f,
           title="Межі всередині слова: перший «=», крапка, лапки й самотнє «--»")


# ── 6. Де побачити рядок і його наслідки (вставка api-cmdline-reference) ───
def fig_cmdline_views():
    W, H = 1340, 570
    f = []

    f.append(text(670, 62,
                  "усе з bootconfig стоїть попереду — тому слово з рядка завантажувача "
                  "перекриває його, а не навпаки",
                  size=13, color=MUTED, bold=True))

    chunks = [
        (70, 300, "bootconfig · ключі під kernel", BLUE_FILL, NEG),
        (378, 340, "рядок від завантажувача", GREEN_FILL, FIELD),
        (726, 64, "--", RED_FILL, POS),
        (798, 300, "bootconfig · ключі під init", BLUE_FILL, NEG),
    ]
    for x, w, s, fill, stroke in chunks:
        f.append(fitbox(x, 86, w, 62, s, size=13, fill=fill, stroke=stroke))

    f.append(fitbox(70, 196, 1028, 58,
                    "склеєний рядок: його ядро й розбирає, і зберігає назавжди",
                    size=14, fill=GREY_FILL, stroke=INK))
    f.append(arrow(584, 152, 584, 190))

    cols = [
        (70, "/proc/cmdline",
         "увесь склеєний рядок,\nразом зі словами, які ядро\nвикинуло або передало далі"),
        (386, "/proc/bootconfig",
         "лише те, що прийшло\nз bootconfig, і вже деревом\nключів, а не текстом"),
        (702, "/proc/1/cmdline",
         "argv init: argv[0] — справжній\nшлях, далі слова без «=»\nі все, що стояло після «--»"),
        (1018, "/proc/1/environ",
         "оточення init: HOME=/ і\nTERM=linux плюс невпізнані\nслова, у яких було «=»"),
    ]
    for x, path, body in cols:
        f.append(fitbox(x, 300, 290, 44, path, size=14, fill=BG, stroke=INK, bold=True))
        f.append(fitbox(x, 352, 290, 110, body, size=13, fill=BG, stroke=MUTED))

    for cx in (215, 531, 847, 1163):
        f.append(arrow(584, 258, cx, 294))

    f.append(text(670, 520,
                  "чого не показує жоден: які слова ядро не впізнало — це лише в журналі, "
                  "рядком «Unknown kernel command line parameters»",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'cmdline-views.svg'), W, H, *f,
           title="Чотири різні відповіді на питання «що ця машина отримала при старті»")


if __name__ == '__main__':
    fig_handoff()
    fig_word_routing()
    fig_cmdline_sources()
    fig_uki_layout()
    fig_word_anatomy()
    fig_cmdline_views()
    print("ok")
