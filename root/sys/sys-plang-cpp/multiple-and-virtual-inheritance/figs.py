# -*- coding: utf-8 -*-
"""Фігури до теми «Множинне й віртуальне спадкування: розкладка підобʼєктів»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── 1. Розкладка при множинному невіртуальному спадкуванні ──────────────────
def fig_non_virtual_multiple_layout():
    W, H = 1040, 480
    parts = []

    parts.append(text(W / 2, 36, "Розкладка об'єкта AudioDuplex : public AudioInput, public AudioOutput",
                      size=16, bold=True, color=INK))

    # Стовпчик пам'яті об'єкта
    ox, oy = 210, 75
    bw, bh = 340, 52

    # Блоки пам'яті
    # 0..7: vptr (AudioInput)
    parts.append(rect(ox, oy, bw, bh, fill="#e8f4fd", stroke="#2980b9", sw=1.5))
    parts.append(text(ox + bw / 2, oy + 26, "vptr для AudioInput / AudioDuplex (8 B)", size=13, bold=True, color="#1a5276"))
    parts.append(text(ox - 15, oy + 26, "+0 B", size=12, color=MUTED, anchor="end"))

    # 8..15: AudioInput::sample_rate
    parts.append(rect(ox, oy + bh, bw, bh, fill="#f0f7fc", stroke="#2980b9", sw=1.5))
    parts.append(text(ox + bw / 2, oy + bh + 26, "AudioInput::sample_rate (int32_t + pad, 8 B)", size=13, color=INK))
    parts.append(text(ox - 15, oy + bh + 26, "+8 B", size=12, color=MUTED, anchor="end"))

    # 16..23: vptr (AudioOutput)
    parts.append(rect(ox, oy + 2 * bh, bw, bh, fill="#fef5e7", stroke="#d35400", sw=1.5))
    parts.append(text(ox + bw / 2, oy + 2 * bh + 26, "vptr для AudioOutput (8 B)", size=13, bold=True, color="#935116"))
    parts.append(text(ox - 15, oy + 2 * bh + 26, "+16 B", size=12, color=MUTED, anchor="end"))

    # 24..31: AudioOutput::volume
    parts.append(rect(ox, oy + 3 * bh, bw, bh, fill="#fdfaf6", stroke="#d35400", sw=1.5))
    parts.append(text(ox + bw / 2, oy + 3 * bh + 26, "AudioOutput::volume (float + pad, 8 B)", size=13, color=INK))
    parts.append(text(ox - 15, oy + 3 * bh + 26, "+24 B", size=12, color=MUTED, anchor="end"))

    # 32..39: AudioDuplex::device_id
    parts.append(rect(ox, oy + 4 * bh, bw, bh, fill="#eaeded", stroke="#566573", sw=1.5))
    parts.append(text(ox + bw / 2, oy + 4 * bh + 26, "AudioDuplex::device_id (int64_t, 8 B)", size=13, bold=True, color="#2c3e50"))
    parts.append(text(ox - 15, oy + 4 * bh + 26, "+32 B", size=12, color=MUTED, anchor="end"))

    # Вказівники this ліворуч
    # this (AudioDuplex*) та this (AudioInput*)
    parts.append(arrow(100, oy + 26, ox - 4, oy + 26, color="#2980b9", sw=2))
    parts.append(text(92, oy + 18, "AudioDuplex* ptr", size=12, color=INK, anchor="end", bold=True))
    parts.append(text(92, oy + 36, "AudioInput* in (+0 B)", size=11, color="#2980b9", anchor="end"))

    # this (AudioOutput*)
    parts.append(arrow(100, oy + 2 * bh + 26, ox - 4, oy + 2 * bh + 26, color="#d35400", sw=2))
    parts.append(text(92, oy + 2 * bh + 18, "AudioOutput* out", size=12, color="#d35400", anchor="end", bold=True))
    parts.append(text(92, oy + 2 * bh + 36, "зсув +16 B", size=11, color="#d35400", anchor="end"))

    # Пояснення праворуч у картках
    c1, _, _ = textbox(790, 135, [
        "Статичний upcast:",
        "static_cast<AudioOutput*>(ptr)",
        "компілятор додає +16 байтів до адреси",
        "без звернень до динамічних таблиць."
    ], size=13, fill="#fdfaf6", stroke="#d35400", min_w=390)

    c2, _, _ = textbox(790, 275, [
        "Виклик через AudioOutput*:",
        "out->write(...) очікує this = out (+16).",
        "Реалізація AudioDuplex::write чекає this = ptr (+0).",
        "Компілятор генерує thunk: sub rdi, 16."
    ], size=13, fill="#f4f6f8", stroke="#566573", min_w=390)

    parts += [c1, c2]

    # Підсумковий рядок розміру
    parts.append(line(ox, oy + 5 * bh + 20, ox + bw, oy + 5 * bh + 20, color=MUTED, sw=1, dash="4,4"))
    parts.append(text(ox + bw / 2, oy + 5 * bh + 42, "Загальний розмір об'єкта AudioDuplex: 40 байтів (без virtual)", size=13, color=MUTED, bold=True))

    render(os.path.join(IMG, 'non-virtual-multiple-layout.svg'), W, H, *parts,
           title="Розкладка об'єкта при множинному невіртуальному спадкуванні")


# ── 2. Ромбоподібне спадкування: подвоєння стану ─────────────────────────────
def fig_diamond_duplicate():
    W, H = 1000, 490
    parts = []

    parts.append(text(W / 2, 34, "Ромбоподібне спадкування без virtual: дублювання DeviceNode",
                      size=16, bold=True, color=POS))

    # Схема ієрархії ліворуч
    b_top, _, _ = textbox(190, 85, "DeviceNode (base)\nint32_t node_id", size=13, fill="#fdfefe", stroke=MUTED, min_w=180)
    b_l, _, _ = textbox(95, 175, "AudioInput\nint32_t rate", size=13, fill="#e8f4fd", stroke="#2980b9", min_w=150)
    b_r, _, _ = textbox(285, 175, "AudioOutput\nfloat vol", size=13, fill="#fef5e7", stroke="#d35400", min_w=150)
    b_bot, _, _ = textbox(190, 265, "AudioDuplex\nint64_t dev_id", size=13, fill="#eaeded", stroke="#566573", min_w=180)

    parts += [b_top, b_l, b_r, b_bot]
    parts.append(arrow(150, 115, 110, 145, color=MUTED))
    parts.append(arrow(230, 115, 270, 145, color=MUTED))
    parts.append(arrow(110, 205, 160, 235, color=MUTED))
    parts.append(arrow(270, 205, 220, 235, color=MUTED))

    # Розкладка пам'яті праворуч
    ox, oy = 520, 75
    bw, bh = 420, 46

    # Блок 1: Left -> DeviceNode
    parts.append(rect(ox, oy, bw, bh, fill="#fadbd8", stroke=POS, sw=1.5))
    parts.append(text(ox + bw / 2, oy + 24, "AudioInput :: DeviceNode :: node_id (4 B + pad)", size=12, bold=True, color=POS))
    parts.append(text(ox - 20, oy + 24, "+0 B", size=12, color=MUTED, anchor="end"))

    # Блок 2: Left -> AudioInput
    parts.append(rect(ox, oy + bh, bw, bh, fill="#e8f4fd", stroke="#2980b9", sw=1.5))
    parts.append(text(ox + bw / 2, oy + bh + 24, "AudioInput :: sample_rate (4 B + pad)", size=12, color=INK))
    parts.append(text(ox - 20, oy + bh + 24, "+8 B", size=12, color=MUTED, anchor="end"))

    # Блок 3: Right -> DeviceNode (дублікат!)
    parts.append(rect(ox, oy + 2 * bh, bw, bh, fill="#fadbd8", stroke=POS, sw=2))
    parts.append(text(ox + bw / 2, oy + 2 * bh + 24, "AudioOutput :: DeviceNode :: node_id (ДУБЛІКАТ, 4 B + pad)", size=12, bold=True, color=POS))
    parts.append(text(ox - 20, oy + 2 * bh + 24, "+16 B", size=12, color=MUTED, anchor="end"))

    # Блок 4: Right -> AudioOutput
    parts.append(rect(ox, oy + 3 * bh, bw, bh, fill="#fef5e7", stroke="#d35400", sw=1.5))
    parts.append(text(ox + bw / 2, oy + 3 * bh + 24, "AudioOutput :: volume (4 B + pad)", size=12, color=INK))
    parts.append(text(ox - 20, oy + 3 * bh + 24, "+24 B", size=12, color=MUTED, anchor="end"))

    # Блок 5: AudioDuplex
    parts.append(rect(ox, oy + 4 * bh, bw, bh, fill="#eaeded", stroke="#566573", sw=1.5))
    parts.append(text(ox + bw / 2, oy + 4 * bh + 24, "AudioDuplex :: device_id (8 B)", size=12, bold=True, color="#2c3e50"))
    parts.append(text(ox - 20, oy + 4 * bh + 24, "+32 B", size=12, color=MUTED, anchor="end"))

    # Блок пояснення наслідків
    c_err, _, _ = textbox(W / 2, 405, [
        "Наслідки відсутності virtual:",
        "1. Неоднозначність звернення: ptr->node_id — помилка компіляції (ambiguous base).",
        "2. Розкол стану: ptr->AudioInput::node_id = 1 НЕ змінює ptr->AudioOutput::node_id.",
        "3. Неможливий прямий upcast: static_cast<DeviceNode*>(ptr) не компілюється."
    ], size=13, fill="#fdf2e9", stroke=POS, min_w=900)
    parts.append(c_err)

    render(os.path.join(IMG, 'diamond-problem-duplicate.svg'), W, H, *parts,
           title="Ромбоподібне спадкування: дублювання базового класу")


# ── 3. Розкладка при віртуальному спадкуванні (Itanium ABI) ─────────────────
def fig_virtual_layout():
    W, H = 1000, 520
    parts = []

    parts.append(text(W / 2, 34, "Розкладка пам'яті при virtual public DeviceNode (Itanium C++ ABI)",
                      size=16, bold=True, color=FIELD))

    # Стовпчик пам'яті AudioDuplex
    ox, oy = 80, 75
    bw, bh = 340, 50

    # 1. vptr (AudioInput)
    parts.append(rect(ox, oy, bw, bh, fill="#e8f4fd", stroke="#2980b9", sw=1.5))
    parts.append(text(ox + bw / 2, oy + 25, "vptr для AudioInput (включає vbase offset)", size=12, bold=True, color="#1a5276"))
    parts.append(text(ox - 20, oy + 25, "+0 B", size=12, color=MUTED, anchor="end"))

    # 2. AudioInput fields
    parts.append(rect(ox, oy + bh, bw, bh, fill="#f0f7fc", stroke="#2980b9", sw=1.5))
    parts.append(text(ox + bw / 2, oy + bh + 25, "AudioInput::sample_rate (int32_t + pad, 8 B)", size=12, color=INK))
    parts.append(text(ox - 20, oy + bh + 25, "+8 B", size=12, color=MUTED, anchor="end"))

    # 3. vptr (AudioOutput)
    parts.append(rect(ox, oy + 2 * bh, bw, bh, fill="#fef5e7", stroke="#d35400", sw=1.5))
    parts.append(text(ox + bw / 2, oy + 2 * bh + 25, "vptr для AudioOutput (включає vbase offset)", size=12, bold=True, color="#935116"))
    parts.append(text(ox - 20, oy + 2 * bh + 25, "+16 B", size=12, color=MUTED, anchor="end"))

    # 4. AudioOutput fields
    parts.append(rect(ox, oy + 3 * bh, bw, bh, fill="#fdfaf6", stroke="#d35400", sw=1.5))
    parts.append(text(ox + bw / 2, oy + 3 * bh + 25, "AudioOutput::volume (float + pad, 8 B)", size=12, color=INK))
    parts.append(text(ox - 20, oy + 3 * bh + 25, "+24 B", size=12, color=MUTED, anchor="end"))

    # 5. AudioDuplex fields
    parts.append(rect(ox, oy + 4 * bh, bw, bh, fill="#eaeded", stroke="#566573", sw=1.5))
    parts.append(text(ox + bw / 2, oy + 4 * bh + 25, "AudioDuplex::device_id (int64_t, 8 B)", size=12, bold=True, color="#2c3e50"))
    parts.append(text(ox - 20, oy + 4 * bh + 25, "+32 B", size=12, color=MUTED, anchor="end"))

    # 6. Спільна віртуальна база DeviceNode
    parts.append(rect(ox, oy + 5 * bh, bw, bh + 15, fill="#eafaf1", stroke=FIELD, sw=2))
    parts.append(text(ox + bw / 2, oy + 5 * bh + 25, "Спільний підоб'єкт DeviceNode (Virtual Base)", size=12, bold=True, color=FIELD))
    parts.append(text(ox + bw / 2, oy + 5 * bh + 46, "vptr_DeviceNode + node_id (16 B)", size=11, color=INK))
    parts.append(text(ox - 20, oy + 5 * bh + 32, "+40 B", size=12, color=FIELD, anchor="end", bold=True))

    # Праворуч: Віртуальна таблиця і VBase offset
    tx, ty = 570, 75
    tw, th = 380, 44

    parts.append(text(tx + tw / 2, ty - 12, "Таблиця віртуальних методів (vtable для AudioDuplex)", size=13, bold=True, color=INK))

    parts.append(rect(tx, ty, tw, th, fill="#f9ebea", stroke=POS, sw=1.5))
    parts.append(text(tx + tw / 2, ty + 24, "vbase_offset для DeviceNode: +40", size=12, bold=True, color=POS))
    parts.append(text(tx - 15, ty + 24, "[-3]", size=12, color=MUTED, anchor="end"))

    parts.append(rect(tx, ty + th, tw, th, fill="#f5eef8", stroke="#8e44ad", sw=1.5))
    parts.append(text(tx + tw / 2, ty + th + 24, "offset_to_top: 0", size=12, color=INK))
    parts.append(text(tx - 15, ty + th + 24, "[-2]", size=12, color=MUTED, anchor="end"))

    parts.append(rect(tx, ty + 2 * th, tw, th, fill="#ebf5fb", stroke="#2980b9", sw=1.5))
    parts.append(text(tx + tw / 2, ty + 2 * th + 24, "RTTI typeinfo pointer (&typeinfo for AudioDuplex)", size=11, color=INK))
    parts.append(text(tx - 15, ty + 2 * th + 24, "[-1]", size=12, color=MUTED, anchor="end"))

    parts.append(rect(tx, ty + 3 * th, tw, th, fill="#e8f8f5", stroke=FIELD, sw=2))
    parts.append(text(tx + tw / 2, ty + 3 * th + 24, "Вхідна точка vptr -> AudioDuplex::read()", size=12, bold=True, color=FIELD))
    parts.append(text(tx - 15, ty + 3 * th + 24, "[0]", size=12, color=FIELD, anchor="end", bold=True))

    parts.append(rect(tx, ty + 4 * th, tw, th, fill="#e8f8f5", stroke=FIELD, sw=1.5))
    parts.append(text(tx + tw / 2, ty + 4 * th + 24, "AudioDuplex::write() (override)", size=12, color=INK))
    parts.append(text(tx - 15, ty + 4 * th + 24, "[1]", size=12, color=MUTED, anchor="end"))

    # Стрілка від vptr об'єкта до vtable[0]
    parts.append(arrow(ox + bw, oy + 25, tx - 5, ty + 3 * th + 24, color=FIELD, sw=2))

    # Стрілка від vbase_offset до підоб'єкта DeviceNode
    parts.append(arrow(tx, ty + 24, ox + bw + 10, oy + 5 * bh + 32, color=POS, sw=1.8))

    # Пояснення знизу
    c_info, _, _ = textbox(W / 2, 465, [
        "Непряма адресація: AudioInput звертається до полів DeviceNode за два кроки:",
        "1. Читає vptr[ -3 ], отримує зсув +40;   2. Обчислює адресу: (char*)this + 40.",
        "Завдяки цьому підоб'єкт DeviceNode існує в єдиному екземплярі на весь AudioDuplex."
    ], size=13, fill="#f4f6f8", stroke=LINE, min_w=920)
    parts.append(c_info)

    render(os.path.join(IMG, 'virtual-inheritance-layout.svg'), W, H, *parts,
           title="Розкладка об'єкта при віртуальному спадкуванні")


# ── 4. Механізм VTT під час конструювання ──────────────────────────────────
def fig_vtt_construction():
    W, H = 1000, 480
    parts = []

    parts.append(text(W / 2, 34, "Таблиця віртуальних таблиць (VTT) під час конструювання",
                      size=16, bold=True, color="#8e44ad"))

    # Етапи конструювання ліворуч
    b1, _, _ = textbox(210, 95, [
        "1. Конструювання DeviceNode",
        "Найбільш похідний клас (AudioDuplex)",
        "викликає конструктор віртуальної бази."
    ], size=12, fill="#eafaf1", stroke=FIELD, min_w=340)

    b2, _, _ = textbox(210, 205, [
        "2. Конструювання AudioInput",
        "AudioInput конструюється як підоб'єкт.",
        "Йому потрібен vptr для його методів,",
        "але зсув vbase має вести до AudioDuplex."
    ], size=12, fill="#e8f4fd", stroke="#2980b9", min_w=340)

    b3, _, _ = textbox(210, 315, [
        "3. Фіналізація AudioDuplex",
        "Встановлюється повна vtable",
        "для AudioDuplex з усіма перевизначеннями."
    ], size=12, fill="#eaeded", stroke="#566573", min_w=340)

    parts += [b1, b2, b3]
    parts.append(arrow(210, 135, 210, 165, color=MUTED))
    parts.append(arrow(210, 245, 210, 275, color=MUTED))

    # Схема VTT праворуч
    vx, vy = 550, 80
    vw, vh = 410, 48

    parts.append(text(vx + vw / 2, vy - 12, "Структура VTT (Virtual Table Table) для AudioDuplex", size=13, bold=True, color=INK))

    parts.append(rect(vx, vy, vw, vh, fill="#f4ecf7", stroke="#8e44ad", sw=1.5))
    parts.append(text(vx + vw / 2, vy + 24, "VTT[0]: Головна vtable AudioDuplex", size=12, bold=True, color="#6c3483"))

    parts.append(rect(vx, vy + vh, vw, vh, fill="#ebf5fb", stroke="#2980b9", sw=2))
    parts.append(text(vx + vw / 2, vy + vh + 24, "VTT[1]: Construction vtable для AudioInput-в-AudioDuplex", size=12, bold=True, color="#1b4f72"))

    parts.append(rect(vx, vy + 2 * vh, vw, vh, fill="#fef5e7", stroke="#d35400", sw=2))
    parts.append(text(vx + vw / 2, vy + 2 * vh + 24, "VTT[2]: Construction vtable для AudioOutput-в-AudioDuplex", size=12, bold=True, color="#7e5109"))

    parts.append(rect(vx, vy + 3 * vh, vw, vh, fill="#eafaf1", stroke=FIELD, sw=1.5))
    parts.append(text(vx + vw / 2, vy + 3 * vh + 24, "VTT[3]: Вторинні таблиці віртуальних баз", size=12, color=INK))

    # Стрілка зв'язку між етапом 2 і VTT[1]
    parts.append(arrow(390, 205, vx - 10, vy + vh + 24, color="#2980b9", sw=2))
    parts.append(text(465, vy + vh - 5, "передає VTT[1]", size=11, color="#2980b9", bold=True))

    # Пояснення внизу
    c_why, _, _ = textbox(W / 2, 420, [
        "Навіщо потрібен VTT:",
        "Під час роботи конструктора AudioInput заборонено викликати віртуальні методи ще не створеного AudioDuplex,",
        "але водночас зміщення до віртуальної бази DeviceNode має відповідати геометрії кінцевого AudioDuplex.",
        "Construction vtable з масиву VTT задовольняє обидві вимоги одночасно."
    ], size=12, fill="#fdfefe", stroke=MUTED, min_w=920)
    parts.append(c_why)

    render(os.path.join(IMG, 'vtt-and-construction.svg'), W, H, *parts,
           title="Таблиця віртуальних таблиць (VTT) та етапи конструювання")


def main():
    fig_non_virtual_multiple_layout()
    fig_diamond_duplicate()
    fig_virtual_layout()
    fig_vtt_construction()
    print("Всі 4 фігури згенеровано успішно.")


if __name__ == '__main__':
    main()
