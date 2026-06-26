# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── module-anatomy: що ховається під металевим екраном ────────────────────────
# Ідея: голий чіп не працює сам; модуль додає кварц, Flash, RF-узгодження й
# розв'язку, накриває все екраном, а антену виносить у вільну від міді зону.

def fig_module_anatomy():
    W, H = 920, 470
    p = []

    # зовнішня плата модуля
    p.append(rect(70, 90, 780, 300, fill="#f6f4ee", stroke=INK, sw=2.2, rx=10))
    p.append(text(80, 80, "модуль (WROOM / WROVER-клас)", size=11, color=MUTED,
                  anchor="start", bold=True))

    # зона антени (без міді) праворуч
    p.append(rect(690, 90, 160, 300, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=0))
    p.append(text(770, 116, "зона антени", size=11, color=FIELD, bold=True))
    p.append(text(770, 134, "(без міді під нею)", size=10, color=FIELD))
    p.append('<path d="M 708,206 v -38 h 18 v 38 h 18 v -38 h 18 v 38 h 18 v -38 '
             'h 18 v 38 h 18 v -38 h 18" fill="none" stroke="%s" stroke-width="2.4"/>' % FIELD)
    p.append(text(770, 360, "PCB-антена", size=10, color=FIELD))

    # металевий екран над начинкою
    p.append(rect(70, 90, 620, 300, fill="#e9ebf0", stroke=MUTED, sw=1.6, rx=10))
    p.append(text(90, 116, "металевий екран (shield can)", size=11, color=INK,
                  anchor="start", bold=True))
    p.append(text(90, 134, "тримає випромінювання всередині", size=10, color=MUTED,
                  anchor="start"))

    # начинка під екраном
    p.append(rect(150, 210, 120, 120, fill="#2b2b2b", stroke="#000000", sw=1.2, rx=6))
    p.append(text(210, 272, "ESP32", size=12, color="#ffffff", bold=True))
    p.append(text(210, 290, "кристал у QFN", size=10, color="#cfd6e6"))

    p.append(fitbox(310, 210, 130, 52, "Flash (SPI)\nкод", size=11, bold=True,
                    fill="#fdf0e6", stroke="#c07a2e", color="#9a5a1e"))
    p.append(fitbox(310, 278, 130, 52, "кварц 40 МГц", size=11, bold=True,
                    fill="#e9eefb", stroke=NEG, color=NEG))
    p.append(fitbox(470, 210, 150, 52, "RF-узгодження\nдо антени", size=11, bold=True,
                    fill="#eef6ef", stroke=FIELD, color=FIELD))
    p.append(fitbox(470, 278, 150, 52, "розв'язка\nживлення", size=11, bold=True,
                    fill="#e4e4e4", stroke=MUTED, color=INK))

    # крайові напівотвори знизу
    for i in range(11):
        bx = 150 + i * 46
        p.append(rect(bx, 384, 16, 12, fill="#9a9aa0", stroke="#666666", sw=0.8, rx=2))
    p.append(text(W / 2, 430, "напівотвори по краю (castellated) — ними модуль паяють на твою плату",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "module-anatomy.svg"), W, H, *p,
           title="Що ховається під металевим екраном модуля")


# ── certification: готовий модуль успадковує дозвіл, голий чіп — повна процедура ─
# Ідея: будь-який передавач треба сертифікувати; модуль уже має FCC/CE/IC, тож
# виріб успадковує дозвіл, а голий чіп веде на повну процедуру власним коштом.

def fig_certification():
    W, H = 900, 430
    p = []

    # ліва колонка — готовий модуль
    p.append(rect(60, 80, 360, 300, fill="#fbfdfb", stroke=FIELD, sw=2, rx=12))
    p.append(text(240, 110, "Береш готовий модуль", size=14, color=FIELD, bold=True))
    rows_ok = ["модуль уже має FCC / CE / IC",
               "виробник пройшов випроби радіо",
               "твій виріб успадковує дозвіл",
               "на ринок — швидко й дешево"]
    for i, r in enumerate(rows_ok):
        cy = 150 + i * 42
        p.append(plus(86, cy, r=8))
        p.append(text(108, cy + 4, r, size=11, color=INK, anchor="start"))
    p.append(fitbox(86, 332, 308, 32, "FCC ID на корпусі = квиток на ринок",
                    size=11, bold=True, fill="#eef6ef", stroke=FIELD, color=FIELD))

    # права колонка — голий чіп
    p.append(rect(480, 80, 360, 300, fill="#fffafa", stroke=POS, sw=2, rx=12))
    p.append(text(660, 110, "Береш голий чіп + свою антену", size=13, color=POS, bold=True))
    rows_bad = ["сам проєктуєш ВЧ-тракт і антену",
                "сам ідеш на повну сертифікацію",
                "лабораторія, місяці, чималі гроші",
                "ризик не пройти з першого разу"]
    for i, r in enumerate(rows_bad):
        cy = 150 + i * 42
        p.append(minus(508, cy, r=8))
        p.append(text(528, cy + 4, r, size=11, color=INK, anchor="start"))
    p.append(fitbox(506, 332, 308, 32, "виправдано лише на великому масштабі",
                    size=11, bold=True, fill="#fbecec", stroke=POS, color=POS))

    render(os.path.join(OUT, "certification.svg"), W, H, *p,
           title="Головна причина модуля: готова сертифікація радіо")


if __name__ == "__main__":
    fig_module_anatomy()
    fig_certification()
    print("OK: figures written to", OUT)
