# -*- coding: utf-8 -*-
"""Фігури до теми «Відтворювані збірки»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

DIRTY = "#fdecea"
CLEAN = "#eaf7ef"
PANEL = "#f8fafc"


# ── 1. Герметичність проти бінарної відтворюваності ─────────────────────────
def fig_hermetic_vs_reproducible():
    W, H = 1000, 480
    p = []

    # Лівий блок: Герметичне середовище (ізоляція входів)
    p.append(rect(40, 40, 420, 400, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(250, 75, "Герметичність середовища", size=16, bold=True, color=NEG))
    p.append(fitbox(70, 100, 360, 45, "Ізольоване середовище збірки", size=13.5, bold=True, fill=BG))

    p.append(fitbox(70, 160, 170, 45, "Зафіксовані входи", size=12.5, fill=BG))
    p.append(fitbox(260, 160, 170, 45, "Фіксований sysroot", size=12.5, fill=BG))
    p.append(fitbox(70, 220, 170, 45, "Без доступу до мережі", size=12.5, fill=BG))
    p.append(fitbox(260, 220, 170, 45, "Очищене середовище", size=12.5, fill=BG))

    p.append(fitbox(70, 290, 360, 65, "Властивість процесу збірки:\nусі залежності та тулчейн задекларовані,\nзовнішній світ не впливає на запуск", size=12.5, fill=BG, stroke=MUTED))
    p.append(fitbox(70, 370, 360, 45, "Умова для детермінізму, але не гарантія", size=12.5, bold=True, fill="#fff3cd", stroke="#e0a800"))

    # Центральна стрілка зв'язку
    p.append(arrow(470, 240, 520, 240, color=LINE, sw=2))
    p.append(text(495, 225, "дає", size=12, italic=True, color=MUTED))

    # Правий блок: Бінарна відтворюваність (детермінізм бінарного результату)
    p.append(rect(530, 40, 430, 400, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(745, 75, "Бінарна відтворюваність", size=16, bold=True, color=FIELD))
    p.append(fitbox(565, 100, 360, 45, "Побайтова ідентичність артефакту", size=13.5, bold=True, fill=BG))

    p.append(fitbox(565, 160, 170, 45, "Збірка А: SHA-256", size=12.5, fill=CLEAN, stroke=FIELD))
    p.append(fitbox(755, 160, 170, 45, "Збірка Б: SHA-256", size=12.5, fill=CLEAN, stroke=FIELD))

    p.append(text(745, 235, "SHA256(A) ≡ SHA256(Б)", size=15, bold=True, color=FIELD))

    p.append(fitbox(565, 270, 360, 85, "Властивість результату:\nнезалежно від часу, шляху чи машини,\nоднакові вихідні файли дають ідентичний\nдвійковий образ біт-у-біт", size=12.5, fill=BG, stroke=MUTED))
    p.append(fitbox(565, 370, 360, 45, "Незалежна перевірка автентичності коду", size=12.5, bold=True, fill="#e8f8f0", stroke=FIELD))

    render(os.path.join(IMG, "hermetic-vs-reproducible.svg"), W, H, *p,
           title="Герметичність проти бінарної відтворюваності")


# ── 2. Джерела недетермінізму під час компіляції та лінкування ───────────────
def fig_sources_of_nondeterminism():
    W, H = 1040, 540
    p = []

    p.append(text(520, 35, "Канали проникнення недетермінізму в бінарний артефакт", size=17, bold=True))

    cols = [
        ("Час і годинник", ["__DATE__, __TIME__", "mtime в архівах .a", "PE TimeDateStamp", "mtime у tar/zip/gz"], 60, POS),
        ("Шляхи до файлів", ["__FILE__, assert()", "DWARF comp_dir", ".debug_line шляхи", "Шляхи до PDB у PE"], 290, POS),
        ("Порядок файлів", ["readdir() / dirent", "ext4 dir_index htree", "file(GLOB) без sort", "Порядок секцій у ld"], 520, POS),
        ("Оточення й структури", ["Локалі LC_ALL, sort", "umask і UID/GID", "ASLR / pointer hash", "Паралельні гонитви LTO"], 750, POS)
    ]

    for title, items, x, col_c in cols:
        p.append(rect(x, 65, 230, 280, fill=PANEL, stroke=MUTED, sw=1.3))
        p.append(fitbox(x + 15, 80, 200, 40, title, size=13.5, bold=True, fill=BG, stroke=col_c))
        y = 135
        for it in items:
            p.append(fitbox(x + 15, y, 200, 38, it, size=12, fill=BG))
            y += 46

        p.append(arrow(x + 115, 350, x + 115, 410, color=col_c, sw=1.8))

    p.append(rect(180, 415, 680, 95, fill=DIRTY, stroke=POS, sw=1.8))
    p.append(text(520, 445, "Недетерміністичний виконуваний файл або бібліотека", size=15, bold=True, color=POS))
    p.append(text(520, 475, "Різні криптографічні геші при повторній компіляції того самого вихідного коду", size=13, color=INK))
    p.append(text(520, 495, "Неможливо довести відсутність стороннього шкідливого втручання", size=12, italic=True, color=MUTED))

    render(os.path.join(IMG, "sources-of-nondeterminism.svg"), W, H, *p,
           title="Джерела недетермінізму під час компіляції та лінкування")


# ── 3. Нормалізація: SOURCE_DATE_EPOCH і Prefix Mapping ────────────────────
def fig_prefix_map_and_epoch():
    W, H = 1000, 520
    p = []

    p.append(text(500, 35, "Механізми нейтралізації недетермінізму тулчейном", size=17, bold=True))

    # Верхня половина: SOURCE_DATE_EPOCH
    p.append(rect(50, 65, 900, 190, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(220, 95, "1. Фіксація часу через SOURCE_DATE_EPOCH", size=14.5, bold=True, color=FIELD))

    p.append(fitbox(70, 115, 230, 60, "Системний годинник:\n19-Aug-2026 19:44:52\n(щоразу інший)", size=12, fill=DIRTY, stroke=POS))
    p.append(fitbox(340, 115, 280, 60, "SOURCE_DATE_EPOCH=1700000000\n(час останнього коміту в git)", size=12.5, bold=True, fill=CLEAN, stroke=FIELD))
    p.append(fitbox(660, 115, 260, 60, "Детерміністичні макроси:\n__DATE__ → 'Nov 14 2023'\n__TIME__ → '22:13:20'", size=12, fill=BG))

    p.append(arrow(305, 145, 335, 145, color=MUTED, sw=1.5))
    p.append(arrow(625, 145, 655, 145, color=FIELD, sw=1.8))

    p.append(fitbox(70, 190, 850, 45, "ar D (детерміністичний архів): mtime = 0, UID = 0, GID = 0, mode = 0644 у заголовках .a", size=12.5, fill=BG, stroke=FIELD))

    # Нижня половина: Prefix Mapping
    p.append(rect(50, 275, 900, 215, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(240, 305, "2. Канонізація шляхів через -ffile-prefix-map", size=14.5, bold=True, color=FIELD))

    p.append(fitbox(70, 325, 250, 65, "Абсолютний шлях розробника:\n/home/alice/dev/proj/main.c\n/builds/runner-42/src/main.c", size=12, fill=DIRTY, stroke=POS))
    p.append(fitbox(360, 325, 260, 65, "-ffile-prefix-map=$PWD=.\n-fdebug-prefix-map=$PWD=/src\nПравило заміни префікса", size=12.5, bold=True, fill=CLEAN, stroke=FIELD))
    p.append(fitbox(660, 325, 260, 65, "Канонічний вихід у DWARF / __FILE__:\n./main.c\n/src/main.c", size=12, fill=BG))

    p.append(arrow(325, 357, 355, 357, color=MUTED, sw=1.5))
    p.append(arrow(625, 357, 655, 357, color=FIELD, sw=1.8))

    p.append(fitbox(70, 410, 850, 60, "DWARF секції (.debug_info, .debug_line) отримують однакові відносні шляхи\nнезалежно від того, у якому каталозі на диску відбувалася збірка", size=12.5, fill=BG, stroke=FIELD))

    render(os.path.join(IMG, "prefix-map-and-epoch.svg"), W, H, *p,
           title="SOURCE_DATE_EPOCH і канонізація шляхів")


# ── 4. Пайплайн верифікації подвійною збіркою та diffoscope ─────────────────
def fig_verification_pipeline():
    W, H = 1020, 500
    p = []

    p.append(text(510, 35, "Верифікація відтворюваності: подвійна збірка в мутованому середовищі", size=17, bold=True))

    # Середовище 1
    p.append(rect(50, 65, 380, 200, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(240, 95, "Збірка 1 (Еталонне середовище)", size=14, bold=True, color=NEG))
    p.append(fitbox(70, 115, 340, 35, "Шлях: /build/env1 · Час: Т1", size=12, fill=BG))
    p.append(fitbox(70, 155, 340, 35, "Користувач: build1 (UID 1001) · TZ=UTC-5", size=12, fill=BG))
    p.append(fitbox(70, 195, 340, 50, "Результат: binary_v1.tar.gz\nSHA256: e3b0c44298fc1c149afbf4c8...", size=12, bold=True, fill=CLEAN, stroke=FIELD))

    # Середовище 2
    p.append(rect(590, 65, 380, 200, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(780, 95, "Збірка 2 (Мутоване середовище)", size=14, bold=True, color=POS))
    p.append(fitbox(610, 115, 340, 35, "Шлях: /opt/other/env2 · Час: Т2 (+2 роки)", size=12, fill=BG))
    p.append(fitbox(610, 155, 340, 35, "Користувач: user99 (UID 2002) · TZ=UTC+9", size=12, fill=BG))
    p.append(fitbox(610, 195, 340, 50, "Результат: binary_v2.tar.gz\nSHA256: e3b0c44298fc1c149afbf4c8...", size=12, bold=True, fill=CLEAN, stroke=FIELD))

    # Стрілки до блоку перевірки
    p.append(arrow(240, 270, 430, 330, color=NEG, sw=1.8))
    p.append(arrow(780, 270, 590, 330, color=POS, sw=1.8))

    # Блок порівняння
    p.append(rect(340, 310, 340, 65, fill=BG, stroke=LINE, sw=2))
    p.append(text(510, 335, "Порівняння контрольних сум", size=14, bold=True))
    p.append(text(510, 358, "SHA256(v1) == SHA256(v2) ?", size=13.5, bold=True, color=FIELD))

    # Розгалуження: Так / Ні
    p.append(arrow(340, 345, 180, 420, color=FIELD, sw=2))
    p.append(text(235, 370, "Так (100% збіг)", size=13, bold=True, color=FIELD))

    p.append(arrow(680, 345, 840, 420, color=POS, sw=2))
    p.append(text(785, 370, "Ні (є розбіжність)", size=13, bold=True, color=POS))

    # Результат ТАК
    p.append(fitbox(50, 420, 280, 60, "ВІДТВОРЮВАНО!\nБінарний артефакт детерміністичний", size=13, bold=True, fill=CLEAN, stroke=FIELD))

    # Результат НІ
    p.append(fitbox(690, 420, 280, 60, "diffoscope v1 v2\nПосекційний розбір ELF / DWARF / tar\nПошук витоку недетермінізму", size=12, bold=True, fill=DIRTY, stroke=POS))

    render(os.path.join(IMG, "verification-pipeline.svg"), W, H, *p,
           title="Верифікація відтворюваності подвійною збіркою")


if __name__ == "__main__":
    fig_hermetic_vs_reproducible()
    fig_sources_of_nondeterminism()
    fig_prefix_map_and_epoch()
    fig_verification_pipeline()
    print("готово:", IMG)
