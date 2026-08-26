# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Рівні захисту від читання (RDP): переходи та механіка стирання ─────────
def fig_rdp_levels():
    W, H = 840, 360
    p = []
    p.append(text(W / 2, 28, "Рівні апаратного захисту RDP: стани та переходи", size=16, bold=True))

    # Три рівні
    # L0
    x0, y0, bw, bh = 40, 70, 220, 150
    p.append(rect(x0, y0, bw, bh, fill="#eafaf0", stroke=FIELD, sw=2.0))
    p.append(text(x0 + bw / 2, y0 + 26, "RDP Рівень 0", size=14, color=FIELD, bold=True))
    p.append(text(x0 + bw / 2, y0 + 46, "0xAA (відкрито)", size=11, color=MUTED))
    p.append(line(x0 + 15, y0 + 58, x0 + bw - 15, y0 + 58, color=FIELD, sw=1.0))
    p.append(text(x0 + bw / 2, y0 + 80, "• SWD/JTAG повністю відкритий", size=10.5, color=INK))
    p.append(text(x0 + bw / 2, y0 + 100, "• Читання/запис Flash і RAM", size=10.5, color=INK))
    p.append(text(x0 + bw / 2, y0 + 120, "• Режим розробки та налагодження", size=10.5, color=INK))
    p.append(text(x0 + bw / 2, y0 + 140, "• Вільний доступ через DAP", size=10.5, color=INK))

    # L1
    x1 = 310
    p.append(rect(x1, y0, bw, bh, fill="#eef2fb", stroke=NEG, sw=2.0))
    p.append(text(x1 + bw / 2, y0 + 26, "RDP Рівень 1", size=14, color=NEG, bold=True))
    p.append(text(x1 + bw / 2, y0 + 46, "будь-яке значення, крім 0xAA/0xCC", size=10, color=MUTED))
    p.append(line(x1 + 15, y0 + 58, x1 + bw - 15, y0 + 58, color=NEG, sw=1.0))
    p.append(text(x1 + bw / 2, y0 + 80, "• Дебагер відрізано від Flash/RAM", size=10.5, color=INK))
    p.append(text(x1 + bw / 2, y0 + 100, "• Код у Flash працює штатно", size=10.5, color=INK))
    p.append(text(x1 + bw / 2, y0 + 120, "• Звернення з DAP → Bus Error", size=10.5, color=INK))
    p.append(text(x1 + bw / 2, y0 + 140, "• Можливий відкат у Рівень 0", size=10.5, color=INK))

    # L2
    x2 = 580
    p.append(rect(x2, y0, bw, bh, fill="#fff7f5", stroke=POS, sw=2.0))
    p.append(text(x2 + bw / 2, y0 + 26, "RDP Рівень 2", size=14, color=POS, bold=True))
    p.append(text(x2 + bw / 2, y0 + 46, "0xCC (замок назавжди)", size=11, color=POS, bold=True))
    p.append(line(x2 + 15, y0 + 58, x2 + bw - 15, y0 + 58, color=POS, sw=1.0))
    p.append(text(x2 + bw / 2, y0 + 80, "• SWD/JTAG вимкнено фізично", size=10.5, color=INK))
    p.append(text(x2 + bw / 2, y0 + 100, "• Завантаження з RAM заборонено", size=10.5, color=INK))
    p.append(text(x2 + bw / 2, y0 + 120, "• Option Bytes заблоковано", size=10.5, color=INK))
    p.append(text(x2 + bw / 2, y0 + 140, "• Незворотний апаратний лок", size=10.5, color=POS, bold=True))

    # Стрілка 0 -> 1
    p.append(arrow(x0 + bw + 4, y0 + 40, x1 - 4, y0 + 40, color=NEG, sw=2.0))
    p.append(text((x0 + bw + x1) / 2, y0 + 30, "запис OB", size=10, color=NEG, bold=True))

    # Стрілка 1 -> 0 (відкат зі стиранням)
    p.append(arrow(x1 - 4, y0 + 110, x0 + bw + 4, y0 + 110, color=POS, sw=2.0))
    p.append(text((x0 + bw + x1) / 2, y0 + 98, "відкат 1→0", size=10, color=POS, bold=True))
    p.append(text((x0 + bw + x1) / 2, y0 + 124, "Mass Erase\nFlash + RAM", size=9, color=POS))

    # Стрілка 1 -> 2
    p.append(arrow(x1 + bw + 4, y0 + 40, x2 - 4, y0 + 40, color=POS, sw=2.0))
    p.append(text((x1 + bw + x2) / 2, y0 + 30, "запис 0xCC", size=10, color=POS, bold=True))

    # Заборона 2 -> 1 / 0
    p.append(line(x2 - 4, y0 + 110, x1 + bw + 4, y0 + 110, color=MUTED, sw=1.6, dash="4 4"))
    p.append(text((x1 + bw + x2) / 2, y0 + 100, "відкат неможливий", size=10, color=POS, bold=True))
    p.append(text((x1 + bw + x2) / 2, y0 + 120, "DAP відрізано", size=9, color=MUTED))

    # Нижній блок висновку
    p.append(fitbox(40, 245, W - 80, 85,
                    "Механіка RDP захищає від звичайного зчитування через дебагер.\n"
                    "При зниженні захисту з Рівня 1 до Рівня 0 апаратура стирає весь Flash до нуля.\n"
                    "Рівень 2 замикає кристал незворотно: порт налагодження фізично відключається від внутрішньої шини.",
                    size=12, fill="#f4f6f8", stroke=LINE, sw=1.5))

    return render(os.path.join(OUT, "rdp-levels.svg"), W, H, *p)


# ── 2. Механізм обходу перевірки через збій живлення (Voltage Glitch) ─────────
def fig_glitch_bypass():
    W, H = 840, 370
    p = []
    p.append(text(W / 2, 26, "Атака збоєм живлення (Voltage Glitching) на перевірку RDP", size=16, bold=True))

    # Часова діаграма напруги живлення
    gx, gy, gw, gh = 40, 60, 430, 160
    p.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(gx + 16, gy + 20, "Напруга живлення ядра VCORE", size=11, color=MUTED, anchor="start"))

    # Осі
    p.append(line(gx + 40, gy + gh - 30, gx + gw - 20, gy + gh - 30, color=LINE, sw=1.2)) # t
    p.append(line(gx + 40, gy + gh - 30, gx + 40, gy + 30, color=LINE, sw=1.2))           # V
    p.append(text(gx + gw - 15, gy + gh - 26, "t", size=11, color=LINE))
    p.append(text(gx + 30, gy + 34, "V", size=11, color=LINE))

    # Рівні
    p.append(text(gx + 32, gy + 55, "3.3V", size=9.5, color=MUTED, anchor="end"))
    p.append(line(gx + 36, gy + 55, gx + gw - 30, gy + 55, color="#e0e0e0", sw=1.0, dash="2 2"))
    p.append(text(gx + 32, gy + gh - 45, "0.6V", size=9.5, color=POS, anchor="end"))

    # Графік напруги з глітчем
    # Норма 3.3V -> короткий провал на 30 нс -> повернення до 3.3V
    p.append(line(gx + 40, gy + 55, gx + 180, gy + 55, color=NEG, sw=2.2))
    p.append(line(gx + 180, gy + 55, gx + 195, gy + gh - 45, color=POS, sw=2.4))
    p.append(line(gx + 195, gy + gh - 45, gx + 215, gy + gh - 45, color=POS, sw=2.4))
    p.append(line(gx + 215, gy + gh - 45, gx + 230, gy + 55, color=NEG, sw=2.2))
    p.append(line(gx + 230, gy + 55, gx + gw - 30, gy + 55, color=NEG, sw=2.2))

    # Текст над глітчем
    p.append(text(gx + 205, gy + 42, "глітч 30 нс", size=10, color=POS, bold=True))

    # Праворуч: що відбувається в мікроконтролері
    rx, ry, rw, rh = 490, 60, 310, 160
    p.append(rect(rx, ry, rw, rh, fill="#fcfcfd", stroke=LINE, sw=1.5))
    p.append(text(rx + rw / 2, ry + 22, "Стан процесора та шини", size=13, color=INK, bold=True))

    p.append(fitbox(rx + 15, ry + 36, rw - 30, 48,
                    "1. Зчитування Option Bytes:\nтранзистори не встигають закритися",
                    size=10.5, fill="#fff7f5", stroke=POS, sw=1.4))
    p.append(fitbox(rx + 15, ry + 92, rw - 30, 56,
                    "2. Інструкція перевірки (CMP / BNE)\nвиконується як NOP або дає 0xAA;\nшину DAP не заблоковано!",
                    size=10.5, fill="#fdecea", stroke=POS, sw=1.6, bold=True))

    # Нижній пояснювальний блок
    p.append(fitbox(40, 240, W - 80, 105,
                    "Як працює збій: короткочасний провал напруги під час читання Option Bytes порушує логічні рівні.\n"
                    "Процесор пропускає умовний перехід блокування або зчитує байт захисту як 0xAA (Рівень 0).\n"
                    "Результат: програматор/дебагер отримує повний доступ до Flash без запуску апаратного стирання пам'яті.",
                    size=11.5, fill="#f4f6f8", stroke=LINE, sw=1.5))

    return render(os.path.join(OUT, "glitch-bypass.svg"), W, H, *p)


# ── 3. Ешелонований захист: апаратний, криптографічний, алгоритмічний ──────────
def fig_defense_in_depth():
    W, H = 840, 370
    p = []
    p.append(text(W / 2, 26, "Ешелонований захист (Defense in Depth) для закритого чипа", size=16, bold=True))

    layers = [
        ("1. Фізичний рівень",
         "• Супервізор живлення (BOD)\n"
         "• Фільтри низьких частот на NRST\n"
         "• Блокувальні конденсатори\n"
         "• Заливка плати компаундом",
         "#eafaf0", FIELD),
        ("2. Апаратний та крипто-рівень",
         "• RDP Рівень 2 (апаратний лок)\n"
         "• Secure Boot: підпис RSA/ECDSA\n"
         "• Encrypted Flash / XIP шифрування\n"
         "• Ключі в OTP eFuse без читання",
         "#eef2fb", NEG),
        ("3. Програмний рівень",
         "• Комплементарна перевірка прапорців\n"
         "• Рандомізація затримок (джиттер)\n"
         "• Контроль потоку виконання (CFI)\n"
         "• Занулення RAM при розкритті",
         "#fff7f5", POS)
    ]

    bx, by, bw, bh = 40, 60, 240, 205
    gap = 20
    for i, (title, body, fill, stroke) in enumerate(layers):
        x = bx + i * (bw + gap)
        p.append(rect(x, by, bw, bh, fill=fill, stroke=stroke, sw=2.0))
        p.append(text(x + bw / 2, by + 22, title, size=11.5, color=stroke, bold=True))
        p.append(line(x + 10, by + 34, x + bw - 10, by + 34, color=stroke, sw=1.0))
        
        lines = body.split("\n")
        for j, l in enumerate(lines):
            p.append(text(x + 12, by + 56 + j * 34, l, size=10, color=INK, anchor="start"))

    p.append(fitbox(40, 280, W - 80, 70,
                    "Жоден окремий механізм не дає 100% захисту. Безпека досягається поєднанням шарів:\n"
                    "схемотехніка стримує фізичні глітчі, апаратний RDP2 і Secure Boot закривають шини,\n"
                    "а шифрування та подвійні перевірки роблять прочитані дампи марними.",
                    size=11.5, fill="#f4f6f8", stroke=LINE, sw=1.5))

    return render(os.path.join(OUT, "defense-in-depth.svg"), W, H, *p)


if __name__ == "__main__":
    fig_rdp_levels()
    fig_glitch_bypass()
    fig_defense_in_depth()
    print("Figures generated successfully in", OUT)
