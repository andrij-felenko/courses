# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── residues-grid: симетрія квадратичного відображення mod 11 ─────────────────
def fig_residues_grid():
    W, H = 820, 360
    p = []

    gx, gy = 80, 80
    cw, ch = 66, 48

    p.append(text(gx - 15, gy + ch / 2 + 5, "x", size=14, color=INK, bold=True, anchor="end"))
    p.append(text(gx - 15, gy + 1.5 * ch + 5, "x² mod 11", size=13, color=MUTED, anchor="end"))

    # Значення x та квадрати mod 11
    xs = list(range(1, 11))
    sqs = [(x * x) % 11 for x in xs]

    # Кольорова палітра лишків
    qr_colors = {
        1: "#e3f2fd",
        3: "#e8f5e9",
        4: "#fff3e0",
        5: "#f3e5f5",
        9: "#fce4ec"
    }

    qr_borders = {
        1: "#1976d2",
        3: "#388e3c",
        4: "#f57c00",
        5: "#7b1fa2",
        9: "#c2185b"
    }

    for idx, (x, sq) in enumerate(zip(xs, sqs)):
        x_pos = gx + idx * cw
        fill_col = qr_colors[sq]
        border_col = qr_borders[sq]

        # Комірка x
        p.append(rect(x_pos, gy, cw, ch, fill="#f8f9fa", stroke=MUTED, sw=1.2))
        p.append(text(x_pos + cw / 2, gy + ch / 2 + 5, x, size=15, color=INK, bold=True))

        # Комірка x^2 mod 11
        p.append(rect(x_pos, gy + ch, cw, ch, fill=fill_col, stroke=border_col, sw=1.8))
        p.append(text(x_pos + cw / 2, gy + 1.5 * ch + 5, sq, size=15, color=border_col, bold=True))

    # З'єднувальні дуги симетрії (x та 11-x дають однаковий квадрат)
    pairs = [(1, 10), (2, 9), (3, 8), (4, 7), (5, 6)]
    for a, b in pairs:
        x1 = gx + (a - 1) * cw + cw / 2
        x2 = gx + (b - 1) * cw + cw / 2
        y_top = gy - 6
        h_arc = 18 + (5 - a) * 8
        path_d = f"M {x1} {y_top} C {x1} {y_top - h_arc}, {x2} {y_top - h_arc}, {x2} {y_top}"
        p.append(f'<path d="{path_d}" fill="none" stroke="{FIELD}" stroke-width="1.5" stroke-dasharray="4 3" />')

    p.append(text(W / 2, 230, "П'ять квадратичних лишків: {1, 3, 4, 5, 9} (кожен має по 2 квадратні корені)",
                  size=13, color=FIELD, bold=True))
    p.append(text(W / 2, 255, "П'ять квадратичних нелишків: {2, 6, 7, 8, 10} (не мають жодного кореня в Z₁₁)",
                  size=13, color=POS, bold=True))

    p.append(text(W / 2, 310, "Симетрія x² ≡ (11 − x)² (mod 11) згортає 10 елементів групи Z₁₁* у 5 квадратичних лишків",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "residues-grid.svg"), W, H, *p,
           title="Відображення x ↦ x² (mod 11): піднесення до квадрата згортає елементи попарно")


# ── euler-criterion-split: розбиття групи та мультиплікативні правила ────────
def fig_euler_criterion_split():
    W, H = 840, 380
    p = []

    # Лівий блок: Квадратичні лишки (QR)
    p.append(rect(60, 70, 330, 160, rx=10, fill="#eafaf0", stroke=FIELD, sw=2.0))
    p.append(text(225, 100, "Квадратичні лишки (QR)", size=15, color=FIELD, bold=True))
    p.append(text(225, 130, "a^((p-1)/2) ≡ +1 (mod p)", size=14, color=INK, bold=True))
    p.append(text(225, 160, "Символ Лежандра (a/p) = +1", size=13, color=FIELD, bold=True))
    p.append(text(225, 195, "Утворюють підгрупу індексу 2 в Zₚ*", size=12, color=MUTED, italic=True))

    # Правий блок: Квадратичні нелишки (QNR)
    p.append(rect(450, 70, 330, 160, rx=10, fill="#fdecea", stroke=POS, sw=2.0))
    p.append(text(615, 100, "Квадратичні нелишки (QNR)", size=15, color=POS, bold=True))
    p.append(text(615, 130, "a^((p-1)/2) ≡ -1 (mod p)", size=14, color=INK, bold=True))
    p.append(text(615, 160, "Символ Лежандра (a/p) = -1", size=13, color=POS, bold=True))
    p.append(text(615, 195, "Суміжний клас підгрупи лишків", size=12, color=MUTED, italic=True))

    # Нижня таблиця мультиплікативних правил
    p.append(rect(180, 255, 480, 85, rx=8, fill="#f8f9fa", stroke=MUTED, sw=1.2))
    p.append(text(420, 278, "Таблиця множення класів (ізоморфізм із групами {+1, -1} ≅ Z₂):",
                  size=12.5, color=INK, bold=True))
    p.append(text(420, 302, "QR · QR = QR  (+1 · +1 = +1)     |     QR · QNR = QNR  (+1 · -1 = -1)",
                  size=12, color=INK))
    p.append(text(420, 324, "QNR · QNR = QR  (-1 · -1 = +1)",
                  size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, "euler-criterion-split.svg"), W, H, *p,
           title="Гомоморфізм критерію Ейлера: a ↦ a^((p-1)/2) (mod p)")


# ── reciprocity-lattice: решітка Айзенштайна для закону взаємності ───────────
def fig_reciprocity_lattice():
    W, H = 840, 440
    p = []

    # Прямокутник (p-1)/2 × (q-1)/2 = 3 × 5
    ox, oy = 180, 340
    step_x, step_y = 70, 50

    p.append(rect(ox, oy - 5 * step_y, 3 * step_x, 5 * step_y, fill="#fbfbff", stroke=INK, sw=1.8))

    # Діагональна лінія y = (q/p) * x => y = (11/7) * x
    x_start, y_start = ox, oy
    x_end, y_end = ox + 3.5 * step_x, oy - 5.5 * step_y
    p.append(line(x_start, y_start, x_end, y_end, color=POS, sw=2.2))

    # Малювання точок решітки
    for x in range(1, 4):
        for y in range(1, 6):
            px = ox + x * step_x
            py = oy - y * step_y
            below = (7 * y < 11 * x)
            dot_col = FIELD if below else POS
            p.append(circle(px, py, 5, fill=dot_col, stroke=dot_col, sw=1))

    # Вісь X
    p.append(line(ox - 20, oy, ox + 3.5 * step_x + 20, oy, color=INK, sw=1.5))
    p.append(text(ox + 3.5 * step_x + 35, oy + 4, "x", size=14, color=INK, bold=True))
    for x in range(1, 4):
        p.append(text(ox + x * step_x, oy + 22, x, size=13, color=INK))

    # Вісь Y
    p.append(line(ox, oy + 20, ox, oy - 5.5 * step_y - 10, color=INK, sw=1.5))
    p.append(text(ox, oy - 5.5 * step_y - 22, "y", size=14, color=INK, bold=True))
    for y in range(1, 6):
        p.append(text(ox - 20, oy - y * step_y + 4, y, size=13, color=INK))

    # Пояснювальний текстовий блок праворуч
    p.append(rect(470, 95, 340, 240, rx=8, fill="#f8f9fa", stroke=MUTED, sw=1.2))
    p.append(text(640, 125, "Розбиття прямокутника 3 × 5:", size=13, color=INK, bold=True))
    p.append(text(640, 155, "● Точок нижче діагоналі (y < 11/7 x):", size=12, color=FIELD, bold=True))
    p.append(text(640, 182, "   Σ ⌊11x/7⌋ = 1 + 3 + 4 = 8 точок", size=12, color=INK))
    p.append(text(640, 215, "● Точок вище діагоналі (y > 11/7 x):", size=12, color=POS, bold=True))
    p.append(text(640, 242, "   Σ ⌊7y/11⌋ = 0 + 1 + 1 + 2 + 3 = 7 точок", size=12, color=INK))
    p.append(text(640, 278, "Усього: 8 + 7 = 15 = ((7-1)/2) · ((11-1)/2)", size=12.5, color=INK, bold=True))
    p.append(text(640, 310, "Символ (7/11)(11/7) = (-1)⁸⁺⁷ = (-1)¹⁵ = -1", size=12, color=MUTED, italic=True))

    p.append(text(W / 2, 415, "Прямокутник розміру ((p-1)/2) × ((q-1)/2) розбивається діагоналлю на два підрахунки точок",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "reciprocity-lattice.svg"), W, H, *p,
           title="Геометричне доведення Айзенштайна для p = 7, q = 11")


# ── tonelli-shanks-tree: конвеєр алгоритму Тонеллі-Шенкса ─────────────────────
def fig_tonelli_shanks_tree():
    W, H = 840, 420
    p = []

    # Крок 1: Факторизація
    p.append(rect(40, 70, 230, 80, rx=8, fill="#e3f2fd", stroke="#1976d2", sw=1.6))
    p.append(text(155, 95, "1. Факторизація", size=13, color="#1976d2", bold=True))
    p.append(text(155, 122, "p − 1 = 2ˢ · q (q непарне)", size=12, color=INK))

    p.append(line(270, 110, 310, 110, color=INK, sw=1.5))
    p.append(f'<path d="M 305 105 L 315 110 L 305 115 Z" fill="{INK}" />')

    # Крок 2: Ініціалізація
    p.append(rect(315, 70, 230, 80, rx=8, fill="#e8f5e9", stroke="#388e3c", sw=1.6))
    p.append(text(430, 95, "2. Ініціалізація", size=13, color="#388e3c", bold=True))
    p.append(text(430, 122, "R = a^((q+1)/2), t = a^q (mod p)", size=12, color=INK))

    p.append(line(545, 110, 585, 110, color=INK, sw=1.5))
    p.append(f'<path d="M 580 105 L 590 110 L 580 115 Z" fill="{INK}" />')

    # Крок 3: Нелишок z
    p.append(rect(590, 70, 210, 80, rx=8, fill="#fff3e0", stroke="#f57c00", sw=1.6))
    p.append(text(695, 95, "3. Генератор нелишку", size=13, color="#f57c00", bold=True))
    p.append(text(695, 122, "Знайти z: (z/p) = −1", size=12, color=INK))
    p.append(text(695, 138, "c = z^q (mod p)", size=11, color=MUTED))

    # Перехід до циклу
    p.append(line(430, 150, 430, 185, color=INK, sw=1.5))
    p.append(f'<path d="M 425 180 L 430 190 L 435 180 Z" fill="{INK}" />')

    # Основний цикл
    p.append(rect(180, 190, 500, 135, rx=10, fill="#f8f9fa", stroke=FIELD, sw=2.0))
    p.append(text(430, 215, "4. Основний цикл коригування інваріанта R² ≡ a · t (mod p)", size=13, color=FIELD, bold=True))
    p.append(text(430, 242, "Якщо t ≡ 1 (mod p) ──► Повернути R (розв'язок знайдено!)", size=12.5, color="#388e3c", bold=True))
    p.append(text(430, 268, "Інакше: знайти найменше m таке, що t^(2ᵐ) ≡ 1 (mod p)", size=12, color=INK))
    p.append(text(430, 295, "Оновити: b = c^(2ˢ⁻ᵐ⁻¹), R ⟵ R·b, t ⟵ t·b², c ⟵ b², s ⟵ m", size=12, color="#d35400", bold=True))

    p.append(text(W / 2, 385, "На кожній ітерації порядок елемента t у 2-групі суворо зменшується (m < s), що гарантує збіжність за ≤ s кроків",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "tonelli-shanks-tree.svg"), W, H, *p,
           title="Алгоритм Тонеллі-Шенкса: зменшення 2-порядку інваріанта t")


def main():
    fig_residues_grid()
    fig_euler_criterion_split()
    fig_reciprocity_lattice()
    fig_tonelli_shanks_tree()

if __name__ == "__main__":
    main()
