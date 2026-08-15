# -*- coding: utf-8 -*-
"""Фігури до теми «Конфігурація й збірка ядра: Kconfig, .config і що потрапляє в образ»."""
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


# ── 1. Три положення перемикача — три долі одного файлу ────────────────────
def fig_tristate():
    W, H = 1120, 560
    f = []

    # спільне джерело
    f.append(fitbox(60, 250, 210, 66, "джерело\nfs/ext4/*.c",
                    size=14, bold=True, fill=BG, stroke=INK))

    rows = [
        (70,  "n", RED_FILL, POS,
         "obj- += ext4.o",
         "файл не компілюється",
         "у системі немає нічого"),
        (250, "y", GREEN_FILL, FIELD,
         "obj-y += ext4.o",
         "об'єктний файл у built-in.a",
         "код в образі /boot/vmlinuz"),
        (430, "m", BLUE_FILL, NEG,
         "obj-m += ext4.o",
         "окремий ext4.ko",
         "файл у /lib/modules, вантажать пізніше"),
    ]

    for y, val, fill, stroke, mk, mid, res in rows:
        f.append(fitbox(330, y, 120, 60, "= " + val if val else "",
                        size=20, bold=True, fill=fill, stroke=stroke))
        f.append(fitbox(480, y, 240, 60, mk, size=13, fill=GREY_FILL, stroke=MUTED))
        f.append(fitbox(750, y, 300, 60, mid, size=13, fill=BG, stroke=stroke))
        f.append(text(750 + 150, y + 88, res, size=12, color=MUTED))
        f.append(arrow(450, y + 30, 476, y + 30))
        f.append(arrow(720, y + 30, 746, y + 30))
        f.append(arrow(272, 283, 326, y + 30))

    f.append(text(390, 40, "значення", size=12, color=MUTED))
    f.append(text(600, 40, "у Makefile", size=12, color=MUTED))
    f.append(text(900, 40, "що виходить зі збірки", size=12, color=MUTED))

    render(os.path.join(IMG, 'tristate.svg'), W, H, *f,
           title="Той самий код і три можливі долі — за значенням перемикача")


# ── 2. Шлях від дерева питань до образу ────────────────────────────────────
def fig_config_flow():
    W, H = 1180, 640
    f = []

    # ряд 1: Kconfig-файли з дерева
    f.append(text(210, 44, "питання оголошено поруч із кодом", size=12, color=MUTED))
    for i, (x, name) in enumerate([(60, "fs/ext4/Kconfig"),
                                   (240, "drivers/net/Kconfig"),
                                   (420, "arch/x86/Kconfig")]):
        f.append(fitbox(x, 60, 170, 46, name, size=12, fill=BG, stroke=MUTED))
        f.append(arrow(x + 85, 106, 300, 142))

    f.append(fitbox(180, 144, 240, 54, "одне дерево питань\n(source ← source ← …)",
                    size=13, fill=GREY_FILL, stroke=MUTED))

    # відповіді людини
    f.append(fitbox(560, 144, 250, 54, "menuconfig · defconfig\nlocalmodconfig · oldconfig",
                    size=12, fill=BG, stroke=MUTED))
    f.append(arrow(420, 171, 556, 171))

    # .config
    f.append(fitbox(300, 246, 330, 62, ".config\nCONFIG_EXT4_FS=y   CONFIG_BTRFS_FS=m",
                    size=13, bold=True, fill=GREEN_FILL, stroke=FIELD))
    f.append(arrow(300, 198, 400, 242))
    f.append(arrow(680, 198, 560, 242))

    # syncconfig — три виходи
    f.append(fitbox(360, 340, 220, 46, "make syncconfig", size=14, bold=True,
                    fill=BLUE_FILL, stroke=NEG))
    f.append(arrow(465, 308, 465, 336))

    outs = [
        (60,  "include/generated/\nautoconf.h", "для компілятора C"),
        (400, "include/config/\nauto.conf", "змінні для make"),
        (740, "include/config/*\nпо позначці на символ", "для fixdep"),
    ]
    for x, name, note in outs:
        f.append(fitbox(x, 420, 300, 56, name, size=12, fill=BG, stroke=NEG))
        f.append(text(x + 150, 498, note, size=12, color=MUTED))
        f.append(arrow(470, 386, x + 150, 416))

    # низ: наслідок
    f.append(fitbox(60, 540, 640, 56,
                    "перезбираються ЛИШЕ ті об'єктні файли, що згадують змінений символ",
                    size=13, fill=GREEN_FILL, stroke=FIELD))
    f.append(arrow(890, 504, 700, 540))

    f.append(fitbox(760, 540, 360, 56, "решта дерева лишається як була",
                    size=13, fill=GREY_FILL, stroke=MUTED))

    render(os.path.join(IMG, 'config-flow.svg'), W, H, *f,
           title="Від дерева питань до збірки: де осідає кожна відповідь")


# ── 3. Куди що лягає після встановлення ────────────────────────────────────
def fig_where_it_lands():
    W, H = 1120, 600
    f = []

    f.append(fitbox(430, 60, 260, 54, "збірка ядра", size=15, bold=True,
                    fill=GREY_FILL, stroke=INK))

    # ліва гілка — образ
    f.append(arrow(490, 114, 260, 168))
    f.append(fitbox(60, 172, 400, 50, "/boot/vmlinuz-6.16.0-mykernel",
                    size=13, bold=True, fill=GREEN_FILL, stroke=FIELD))
    f.append(fitbox(60, 240, 400, 50, "/boot/config-6.16.0-mykernel",
                    size=13, fill=BG, stroke=FIELD))
    f.append(text(260, 314, "усе, що було = y: код уже в образі", size=12, color=MUTED))

    # права гілка — модулі
    f.append(arrow(630, 114, 860, 168))
    f.append(fitbox(660, 172, 400, 50, "/lib/modules/6.16.0-mykernel/kernel/**.ko",
                    size=12, bold=True, fill=BLUE_FILL, stroke=NEG))
    f.append(fitbox(660, 240, 400, 50, "modules.dep · modules.alias  (depmod)",
                    size=12, fill=BG, stroke=NEG))
    f.append(text(860, 314, "усе, що було = m: чекає на modprobe", size=12, color=MUTED))

    # initramfs — місток
    f.append(fitbox(330, 372, 460, 60,
                    "/boot/initrd.img-6.16.0-mykernel\nкопії модулів, без яких не дістатися кореня",
                    size=13, fill=RED_FILL, stroke=POS))
    f.append(arrow(860, 292, 700, 368))
    f.append(line(560, 332, 560, 368, color=MUTED, sw=1.2, dash="4 4"))

    f.append(fitbox(330, 480, 460, 56,
                    "завантажувач подає ядру образ і initramfs",
                    size=13, fill=GREY_FILL, stroke=MUTED))
    f.append(arrow(560, 432, 560, 476))

    render(os.path.join(IMG, 'where-it-lands.svg'), W, H, *f,
           title="Два продукти однієї збірки й місток між ними")


# ── 4. Три мови конфігурації і їхня доля (вставка hist-config-wars) ─────────
def fig_config_wars():
    W, H = 1240, 620
    f = []

    f.append(text(230, 52, "мова", size=13, bold=True, color=MUTED))
    f.append(text(660, 52, "як зроблено", size=13, bold=True, color=MUTED))
    f.append(text(1060, 52, "доля", size=13, bold=True, color=MUTED))

    rows = [
        (100, GREY_FILL, MUTED,
         "стара система («CML1»)\nдо 2002",
         "Config.in синтаксисом shell, обхід дерева скриптом Configure;\n"
         "меню й Tk-фронтенд читають ті самі файли кожен по-своєму;\n"
         "довідка окремо, у Documentation/Configure.help",
         "виріс за межі\nвласної мови"),
        (250, RED_FILL, POS,
         "CML2\n2000 – 2002",
         "цілком нова мова з розв'язувачем обмежень усередині;\n"
         "дві програми на Python: cmlcompile і cmlconfigure;\n"
         "сумісності з Config.in немає — база правил переписана",
         "у дерево\nне взяли"),
        (400, GREEN_FILL, FIELD,
         "Kconfig\nз 2.5.45, жовтень 2002",
         "мова, впізнавана для того, хто знав Config.in;\n"
         "парсер і фронтенди на C, знайомий вигляд menuconfig;\n"
         "довідка переїхала до самої опції, нових залежностей нема",
         "у дереві\nдосі"),
    ]

    for y, fill, stroke, name, how, fate in rows:
        f.append(fitbox(70, y, 320, 110, name, size=15, bold=True, fill=fill, stroke=stroke))
        f.append(fitbox(430, y, 460, 110, how, size=12, fill=BG, stroke=MUTED))
        f.append(fitbox(940, y, 230, 110, fate, size=13, bold=True, fill=fill, stroke=stroke))

    # стрілки заміни: хто кого приходив міняти
    f.append(arrow(230, 214, 230, 246))
    f.append(arrow(230, 364, 230, 396))

    f.append(fitbox(70, 540, 1100, 56,
                    "вигране не найкращим дизайном, а найменшою ціною переходу для тих, "
                    "хто щодня правив ці файли",
                    size=13, bold=True, fill=BLUE_FILL, stroke=NEG))

    render(os.path.join(IMG, 'config-wars.svg'), W, H, *f,
           title="Дві заміни старої мови конфігурації: одну відхилили, другу прийняли")


# ── 5. Чотири способи зв'язати два символи (вставка api-kconfig-language) ───
def fig_dependency_kinds():
    W, H = 1200, 700
    f = []

    f.append(text(170, 48, "конструкція", size=13, bold=True, color=MUTED))
    f.append(text(470, 48, "напрям і межа", size=13, bold=True, color=MUTED))
    f.append(text(900, 48, "наслідки", size=13, bold=True, color=MUTED))

    rows = [
        (76, "depends on B", GREEN_FILL, FIELD,
         "A не може бути\nбільшим за B",
         "питання A зникає з меню, доки B = n\n"
         "власні залежності B шануються\n"
         "найбезпечніша з чотирьох форм"),
        (206, "select B  [if E]", RED_FILL, POS,
         "A мовчки піднімає B\nдо свого значення",
         "залежності B НЕ перевіряються\n"
         "звідси попередження про незадоволену залежність\n"
         "вимкнути B вручну неможливо\n"
         "лише для невидимих символів без залежностей"),
        (336, "imply B  [if E]", BLUE_FILL, NEG,
         "A піднімає лише\nтипове значення B",
         "людина може лишити B = n\n"
         "власні залежності B шануються\n"
         "м'який родич select"),
        (466, "visible if E\nлише для menu", GREY_FILL, MUTED,
         "ховає підказки\nвсього блоку",
         "значення символів усередині не міняються\n"
         "їх усе одно може підняти чужий select\n"
         "це не те саме, що depends on"),
    ]

    for y, kw, fill, stroke, direction, effect in rows:
        f.append(fitbox(60, y, 220, 100, kw, size=14, bold=True, fill=fill, stroke=stroke))
        f.append(fitbox(320, y, 300, 100, direction, size=13, fill=GREY_FILL, stroke=MUTED))
        f.append(fitbox(660, y, 480, 100, effect, size=12, fill=BG, stroke=stroke))
        f.append(arrow(282, y + 50, 316, y + 50))
        f.append(arrow(622, y + 50, 656, y + 50))

    f.append(fitbox(60, 608, 1080, 66,
                    "усі умови обчислюються в наборі n < m < y:   "
                    "&& дає менше,   || дає більше,   ! дзеркалить (n у y, m лишається m)",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    render(os.path.join(IMG, 'dependency-kinds.svg'), W, H, *f,
           title="Чотири конструкції, якими Kconfig зв'язує два символи")


# ── 4. Три причини перезбирання (до вставки proj-trace-one-option) ─────────
def fig_rebuild_reasons():
    W, H = 1200, 600
    f = []

    f.append(text(600, 34, "три різні причини, чому make береться щось перезбирати",
                  size=14, bold=True))

    cols = [
        (40, GREEN_FILL, FIELD, "символ живе тільки в Makefile",
         ["CONFIG_DUMMY: n → y",
          "оновлено\ninclude/config/auto.conf",
          "obj-$(CONFIG_DUMMY) += dummy.o\nтепер потрапляє в obj-y"],
         "CC dummy.o\nі перелінковка vmlinux"),
        (430, RED_FILL, POS, "символ згадано в коді",
         ["CONFIG_SMP: y → n",
          "оновлено позначку\ninclude/config/SMP",
          "на неї посилаються\nтисячі .o.cmd — це робота fixdep"],
         "перекомпілюється\nмайже все дерево"),
        (820, RED_FILL, POS, "символ змінює прапорці компілятора",
         ["CONFIG_CC_OPTIMIZE_FOR_SIZE: n → y",
          "у кожному .cmd\nінший рядок savedcmd_",
          "позначки тут ні до чого:\nзмінилася сама команда"],
         "перекомпілюється\nусе дерево"),
    ]

    for x, fill, stroke, head, rows, res in cols:
        f.append(fitbox(x, 56, 340, 48, head, size=13, bold=True,
                        fill=GREY_FILL, stroke=MUTED))
        ys = [136, 222, 316]
        hs = [52, 58, 58]
        prev_bottom = 104
        for y, h, s in zip(ys, hs, rows):
            f.append(arrow(x + 170, prev_bottom, x + 170, y - 4))
            f.append(fitbox(x, y, 340, h, s, size=13, fill=BG, stroke=MUTED))
            prev_bottom = y + h
        f.append(arrow(x + 170, prev_bottom, x + 170, 410))
        f.append(fitbox(x, 414, 340, 62, res, size=13, bold=True,
                        fill=fill, stroke=stroke))

    f.append(fitbox(40, 512, 1120, 54,
                    "порахувати наперед: grep -rlF 'include/config/СИМВОЛ)' --include='*.cmd' . | wc -l",
                    size=13, fill=GREY_FILL, stroke=MUTED))

    render(os.path.join(IMG, 'rebuild-reasons.svg'), W, H, *f,
           title="Три механізми, через які зміна одного символу веде до перезбирання")


if __name__ == '__main__':
    fig_tristate()
    fig_config_flow()
    fig_where_it_lands()
    fig_rebuild_reasons()
    fig_config_wars()
    fig_dependency_kinds()
    print("готово:", os.listdir(IMG))
