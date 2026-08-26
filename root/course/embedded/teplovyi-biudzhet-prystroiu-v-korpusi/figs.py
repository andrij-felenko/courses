# -*- coding: utf-8 -*-
"""Фігури до теми «Тепловий бюджет пристрою в корпусі».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

HOT  = POS        # гаряче — червоне (#c0392b)
COOL = NEG        # холодне — синє (#2457d6)
OK   = FIELD      # зелене виділення (#27ae60)
WARN = "#d35400"   # помаранчевий попереджувальний


# ── 1. Еквівалентна теплова схема пристрою в корпусі ────────────────────────
def fig_thermal_network():
    """Еквівалентна схема теплового ланцюга: від кристала Tj через плату,
    термоміст або внутрішнє повітря, опір стінки корпусу до зовнішньої конвекції та випромінювання."""
    W, H = 840, 440
    f = [text(W / 2, 28, "Еквівалентна схема теплових опорів пристрою в корпусі", size=16, bold=True)]

    # Ліва частина — кристал і корпус компонента
    f.append(rect(30, 70, 150, 110, fill="#fdecea", stroke=HOT, sw=2, rx=8))
    f.append(text(105, 96, "Кристал (Junction)", size=13, color=HOT, bold=True))
    f.append(text(105, 122, "P_тепло = Σ P_втрат", size=13, color=INK, bold=True))
    f.append(text(105, 146, "T_j (найвища)", size=12, color=HOT))
    f.append(text(105, 168, "Межа: 105..125 °C", size=11, color=MUTED))

    # Стрілка тепла від кристала
    f.append(arrow(180, 125, 235, 125, color=HOT, sw=2.5))
    f.append(text(208, 112, "Q = P", size=11, color=HOT, bold=True))

    # Вузол корпусу компонента / теплового поду
    f.append(circle(245, 125, 7, fill=HOT, stroke=LINE, sw=1.5))
    f.append(text(245, 152, "T_case", size=12, color=INK, bold=True))

    # Розгалуження на два шляхи: Прямий термоміст (вгору) та Внутрішнє повітря (вниз)
    f.append(line(245, 125, 245, 80, color=LINE, sw=2))
    f.append(line(245, 125, 245, 240, color=LINE, sw=2))

    # Верхня гілка: Термопрокладка (Gap Pad) на стінку корпусу
    f.append(arrow(245, 80, 295, 80, color=OK, sw=2))
    f.append(rect(295, 55, 140, 50, fill="#eafaf0", stroke=OK, sw=1.8))
    f.append(text(365, 76, "Термоміст (Gap Pad)", size=11, color=OK, bold=True))
    f.append(text(365, 94, "R_th_gap (1..3 °C/Вт)", size=10.5, color=INK))

    # Нижня гілка: Внутрішнє повітря (конвекція + випромінювання на стінку)
    f.append(arrow(245, 240, 295, 240, color=WARN, sw=2))
    f.append(rect(295, 215, 140, 50, fill="#fef5e7", stroke=WARN, sw=1.8))
    f.append(text(365, 235, "Внутрішнє повітря", size=11, color=WARN, bold=True))
    f.append(text(365, 254, "R_th_air (15..50 °C/Вт)", size=10.5, color=INK))

    # Зведення гілок у вузол внутрішньої стінки корпусу
    f.append(line(435, 80, 485, 80, color=LINE, sw=2))
    f.append(line(435, 240, 485, 240, color=LINE, sw=2))
    f.append(line(485, 80, 485, 160, color=LINE, sw=2))
    f.append(line(485, 240, 485, 160, color=LINE, sw=2))
    f.append(circle(485, 160, 7, fill="#d5dbdb", stroke=LINE, sw=1.5))
    f.append(text(485, 142, "T_enc_in", size=12, color=INK, bold=True))

    # Ланка стінки корпусу (кондукція крізь матеріал стінки)
    f.append(arrow(485, 160, 525, 160, color=LINE, sw=2))
    f.append(rect(525, 135, 130, 50, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(590, 155, "Стінка корпусу", size=11, color=INK, bold=True))
    f.append(text(590, 174, "R_th_wall = d/(k·A)", size=10.5, color=MUTED))

    # Вузол зовнішньої поверхні корпусу
    f.append(arrow(655, 160, 695, 160, color=LINE, sw=2))
    f.append(circle(695, 160, 7, fill=COOL, stroke=LINE, sw=1.5))
    f.append(text(695, 142, "T_enc_out", size=12, color=COOL, bold=True))

    # Розгалуження на зовнішній скид: Конвекція та Випромінювання
    f.append(line(695, 160, 695, 105, color=LINE, sw=1.8))
    f.append(line(695, 160, 695, 215, color=LINE, sw=1.8))

    f.append(arrow(695, 105, 735, 105, color=COOL, sw=1.8))
    f.append(rect(735, 85, 90, 40, fill="#eaf0fd", stroke=COOL, sw=1.5))
    f.append(text(780, 102, "Конвекція", size=10.5, color=COOL, bold=True))
    f.append(text(780, 118, "1/(h_c·A)", size=10, color=MUTED))

    f.append(arrow(695, 215, 735, 215, color=COOL, sw=1.8))
    f.append(rect(735, 195, 90, 40, fill="#eaf0fd", stroke=COOL, sw=1.5))
    f.append(text(780, 212, "Радіація", size=10.5, color=COOL, bold=True))
    f.append(text(780, 228, "1/(h_r·A)", size=10, color=MUTED))

    # Кінцевий резервуар — довкілля
    f.append(line(825, 105, 835, 105, color=LINE, sw=1.5))
    f.append(line(825, 215, 835, 215, color=LINE, sw=1.5))
    f.append(line(835, 105, 835, 215, color=LINE, sw=1.5))
    f.append(circle(835, 160, 5, fill=COOL, stroke=LINE, sw=1.5))
    f.append(text(785, 275, "Довкілля T_amb", size=12, color=COOL, bold=True))

    # Нижній висновок-панель
    f.append(fitbox(30, 320, W - 60, 95,
                    "Послідовно-паралельний закон: повний опір системи визначає найслабша ланка.\n"
                    "Без термопрокладки тепло йде через повітря (R_th_air ≈ 20..50 °C/Вт) — пристрій перегрівається.\n"
                    "Прямий контакт через Gap Pad зменшує внутрішній перепад у 10–20 разів, скидаючи тепло на стінку.",
                    size=11, fill="#f4f6f8", stroke=LINE, sw=1.3))

    render(os.path.join(IMG, "enclosure-thermal-network.svg"), W, H, *f)


# ── 2. Пластиковий герметичний корпус проти алюмінієвого з термомостом ──────
def fig_plastic_vs_metal():
    """Порівняння теплових полів:
    (А) Пластиковий бокс IP67 (теплова пастка, гаряче внутрішнє повітря, локальний hotspot);
    (Б) Алюмінієвий корпус з Gap Pad (прямий відвід на стінку, ізотермічний радіатор)."""
    W, H = 840, 500
    f = [text(W / 2, 26, "Порівняння теплових режимів: пластиковий бокс проти алюмінієвого", size=16, bold=True)]

    # ── Варіант А: Пластик (ліворуч) ──
    ax, ay, aw, ah = 35, 55, 370, 310
    f.append(rect(ax, ay, aw, ah, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    f.append(text(ax + aw / 2, ay + 24, "А. Герметичний пластиковий корпус (IP67)", size=13, color=HOT, bold=True))
    f.append(text(ax + aw / 2, ay + 42, "k_пластику ≈ 0.2 Вт/(м·К) • Немає термомосту", size=10.5, color=MUTED))

    # Стінка пластикового корпусу (помаранчевий товстий прямокутник)
    f.append(rect(ax + 20, ay + 55, aw - 40, ah - 85, fill="#fdf2e9", stroke="#d35400", sw=3, rx=6))

    # Гаряче застійне повітря всередині
    f.append(text(ax + aw / 2, ay + 80, "Гаряча кишеня: повітря T_in ≈ 75..85 °C", size=11, color=HOT, bold=True))

    # Плата всередині
    f.append(rect(ax + 50, ay + 185, aw - 100, 10, fill="#27ae60", stroke="#1e8449", sw=1.5))
    f.append(text(ax + 90, ay + 215, "PCB (FR4)", size=10, color=INK))

    # Гарячий чіп (SoC / DC-DC)
    f.append(rect(ax + 135, ay + 155, 100, 30, fill=HOT, stroke=LINE, sw=1.5))
    f.append(text(ax + 185, ay + 174, "Чіп Tj ≈ 120 °C", size=11, color="#ffffff", bold=True))

    # Тепловий бар'єр у повітрі
    f.append(text(ax + 185, ay + 120, "♨  ♨  ♨", size=16, color=HOT))
    f.append(text(ax + 185, ay + 140, "Повітря k=0.026 ізолює", size=9.5, color=HOT))

    # Зовнішня поверхня — висновки
    f.append(text(ax + aw / 2, ay + ah - 22, "✖ Тепло замкнене всередині (перегрів!)", size=11, color=HOT, bold=True))

    # ── Варіант Б: Алюміній з термомостом (праворуч) ──
    bx, by, bw, bh = 435, 55, 370, 310
    f.append(rect(bx, by, bw, bh, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    f.append(text(bx + bw / 2, by + 24, "Б. Алюмінієвий корпус з термопрокладкою", size=13, color=OK, bold=True))
    f.append(text(bx + bw / 2, by + 42, "k_алюмінію ≈ 180 Вт/(м·К) • Прямий контакт", size=10.5, color=MUTED))

    # Стінка алюмінієвого корпусу
    f.append(rect(bx + 20, by + 65, bw - 40, bh - 95, fill="#ebf5fb", stroke="#2980b9", sw=3, rx=6))

    # Ребра охолодження зверху (поза текстом)
    for rx_pos in range(int(bx + 60), int(bx + bw - 60), 28):
        f.append(rect(rx_pos, by + 50, 10, 15, fill="#2980b9", stroke=LINE, sw=1))

    # Плата всередині
    f.append(rect(bx + 50, by + 185, bw - 100, 10, fill="#27ae60", stroke="#1e8449", sw=1.5))
    f.append(text(bx + 90, by + 215, "PCB (FR4)", size=10, color=INK))

    # Чіп
    f.append(rect(bx + 135, by + 155, 100, 30, fill="#e74c3c", stroke=LINE, sw=1.5))
    f.append(text(bx + 185, by + 174, "Чіп Tj ≈ 68 °C", size=11, color="#ffffff", bold=True))

    # Термопрокладка (Gap Pad) між чіпом і верхньою стінкою
    f.append(rect(bx + 140, by + 75, 90, 80, fill="#a2d9ce", stroke=OK, sw=1.5))
    f.append(text(bx + 185, by + 110, "Gap Pad", size=11, color="#0e6251", bold=True))
    f.append(text(bx + 185, by + 128, "3 Вт/(м·К)", size=10, color="#0e6251"))

    # Стрілки швидкого відведення тепла
    f.append(arrow(bx + 185, by + 150, bx + 185, by + 85, color=OK, sw=2.5))
    f.append(arrow(bx + 110, by + 60, bx + 110, by + 35, color=COOL, sw=2))
    f.append(arrow(bx + 185, by + 45, bx + 185, by + 22, color=COOL, sw=2))
    f.append(arrow(bx + 260, by + 60, bx + 260, by + 35, color=COOL, sw=2))

    # Внутрішнє повітря помірне
    f.append(text(bx + 85, by + 115, "T_in ≈ 45 °C", size=10, color=COOL))

    # Зовнішня поверхня
    f.append(text(bx + bw / 2, by + bh - 22, "✔ Корпус-радіатор: ΔT_кристал-корпус < 18 °C", size=11, color=OK, bold=True))

    # Нижній підсумок
    f.append(fitbox(35, 380, W - 70, 95,
                    "Головний висновок теплового проектування: пластиковий корпус вимагає жорсткого обмеження потужності (< 1–2 Вт).\n"
                    "Якщо плата розсіює понад 3–5 Вт у герметичному об'ємі, єдиний надійний шлях — алюмінієве шасі\n"
                    "із теплопровідним силіконовим заповнювачем (Gap Pad / Putty) безпосередньо на металеву кришку.",
                    size=11, fill="#f4f6f8", stroke=LINE, sw=1.3))

    render(os.path.join(IMG, "plastic-vs-metal-enclosure.svg"), W, H, *f)


# ── 3. Зовнішня природна конвекція та випромінювання з поверхні корпусу ──────
def fig_convection_radiation():
    """Фізика зовнішнього розсіювання: пристінний шар конвекції вздовж вертикальних стінок
    та просторове теплове випромінювання (радіація) за законом Стефана-Больцмана."""
    W, H = 820, 440
    f = [text(W / 2, 26, "Механіка тепловіддачі зовнішньої поверхні: конвекція та випромінювання", size=16, bold=True)]

    # Центральний об'єкт — металевий корпус
    cx, cy, cw, ch = 280, 80, 260, 220
    f.append(rect(cx, cy, cw, ch, fill="#eaeded", stroke=LINE, sw=2, rx=8))
    f.append(text(cx + cw / 2, cy + 30, "Зовнішня стінка корпусу", size=13, color=INK, bold=True))
    f.append(text(cx + cw / 2, cy + 55, "Температура поверхні: T_s", size=12, color=HOT, bold=True))
    f.append(text(cx + cw / 2, cy + 85, "Q_заг = Q_conv + Q_rad", size=13, color=INK, bold=True))

    # Конвекція ліворуч (вертикальний рух повітря вгору)
    f.append(rect(50, 75, 190, 230, fill="#eaf0fd", stroke=COOL, sw=1.5, rx=6))
    f.append(text(145, 100, "1. Природна конвекція", size=12.5, color=COOL, bold=True))
    f.append(text(145, 122, "Q_c = h_c · A · (T_s − T_amb)", size=11, color=INK))
    f.append(text(145, 148, "Рушій: сила Архімеда", size=10.5, color=MUTED))
    f.append(text(145, 168, "(гаряче повітря легше)", size=10, color=MUTED))

    # Стрілочки конвективного пристінного шару
    for py in [260, 220, 180]:
        f.append(arrow(210, py, 210, py - 30, color=COOL, sw=2))
    f.append(text(210, 140, "↑ потік", size=10, color=COOL, bold=True))
    f.append(text(145, 275, "h_c ≈ 3..8 Вт/(м²·К)", size=11, color=COOL, bold=True))

    # Випромінювання праворуч (радіальні промені випромінювання)
    f.append(rect(580, 75, 190, 230, fill="#fdf2e9", stroke=WARN, sw=1.5, rx=6))
    f.append(text(675, 100, "2. Теплове випромінювання", size=12.5, color=WARN, bold=True))
    f.append(text(675, 122, "Q_r = ε · σ · A · (T_s⁴ − T_amb⁴)", size=11, color=INK))
    f.append(text(675, 148, "Закон Стефана-Больцмана", size=10.5, color=MUTED))

    # Промені радіації
    f.append(arrow(545, 130, 575, 115, color=WARN, sw=2))
    f.append(arrow(545, 160, 580, 160, color=WARN, sw=2))
    f.append(arrow(545, 190, 575, 205, color=WARN, sw=2))

    f.append(text(675, 180, "Чорне анодування: ε ≈ 0.9", size=10.5, color=OK, bold=True))
    f.append(text(675, 202, "Чистий алюміній: ε ≈ 0.05", size=10.5, color=HOT))
    f.append(text(675, 224, "(у 18 разів гірша радіація!)", size=9.5, color=HOT))
    f.append(text(675, 275, "h_r ≈ 5..7 Вт/(м²·К)", size=11, color=WARN, bold=True))

    # Пояснення ролі орієнтації
    f.append(fitbox(50, 325, W - 100, 95,
                    "Співвідношення часток: при природному охолодженні на відкритому повітрі радіація дає 40–55% тепловіддачі,\n"
                    "а конвекція — решту 45–60%. Тому фарбування чи анодування металевого корпусу подвоює його ефективність!\n"
                    "Орієнтація ребер має бути вертикальною: горизонтальні ребра перекривають природний висхідний потік повітря.",
                    size=11, fill="#f4f6f8", stroke=LINE, sw=1.3))

    render(os.path.join(IMG, "natural-convection-radiation.svg"), W, H, *f)


if __name__ == "__main__":
    fig_thermal_network()
    fig_plastic_vs_metal()
    fig_convection_radiation()
    print("OK: generated 3 figures in", IMG)
