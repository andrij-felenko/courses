import sys
import os
import math

# Add scripts directory to path (4 levels up from book/math/number-theory/baker-method)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, mtext, circle, fitbox, POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
except ImportError:
    print("WARNING: svgkit not found.")
    sys.exit(1)

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')


def generate_baker_bound_principle():
    """Малює графік перетину верхньої експоненціальної та нижньої логарифмічної меж."""
    width, height = 740, 440
    frags = []

    # Заливка фону
    frags.append(rect(0, 0, width, height, fill=BG, stroke="none"))

    # Заголовок
    frags.append(text(width / 2, 24, "Принцип двосторонньої пастки Бейкера для межі B₀", size=15, bold=True, color=INK))

    # Вісь X та Y
    ox, oy = 80, 360
    w_axis, h_axis = 610, 300

    # Сітка
    for i in range(1, 6):
        px = ox + i * (w_axis / 6)
        frags.append(line(px, oy - h_axis, px, oy, color="#e5e7eb", sw=1))

    for j in range(1, 6):
        py = oy - j * (h_axis / 6)
        frags.append(line(ox, py, ox + w_axis, py, color="#e5e7eb", sw=1))

    # Осі
    frags.append(line(ox, oy, ox + w_axis, oy, color=LINE, sw=1.5))
    frags.append(line(ox, oy, ox, oy - h_axis, color=LINE, sw=1.5))

    frags.append(text(ox + w_axis + 10, oy + 4, "B", size=11, bold=True, color=INK))
    frags.append(text(ox - 10, oy - h_axis - 10, "ln |Λ|", size=11, bold=True, color=INK, anchor="end"))

    # Знаходимо точний перетин B0 (приблизно t = 0.46)
    b0_t = 0.46
    b0_x = ox + b0_t * (w_axis - 40)
    b0_val = 1.0 + b0_t * 99.0
    b0_y = oy - (-45.0 * math.log(b0_val) + 280)

    # Зафарбування зони до B0 (зеленуватий прямокутник)
    frags.append(rect(ox, oy - h_axis, b0_x - ox, h_axis, fill="#f0fdf4", stroke="none", rx=0))
    # Зафарбування неможливої зони після B0 (червонуватий прямокутник)
    frags.append(rect(b0_x, oy - h_axis, ox + w_axis - b0_x, h_axis, fill="#fef2f2", stroke="none", rx=0))

    # Крива 1: Нижня межа Бейкера ln |Λ| ≥ - C3 * ln(B) (синя лінія)
    pts_baker = []
    for step in range(0, 201):
        t = step / 200.0
        bx = t * (w_axis - 40)
        b_val = 1.0 + t * 99.0
        val_baker = -45.0 * math.log(b_val)
        by = oy - (val_baker + 280)
        pts_baker.append((ox + bx, by))

    # Крива 2: Верхня межа з рівняння ln |Λ| ≤ ln C1 - C2 * B (червона лінія)
    pts_upper = []
    for step in range(0, 201):
        t = step / 200.0
        bx = t * (w_axis - 40)
        b_val = 1.0 + t * 99.0
        val_upper = 20.0 - 2.8 * b_val
        by = oy - (val_upper + 280)
        pts_upper.append((ox + bx, by))

    # Малювання кривих полілініями
    for i in range(len(pts_baker) - 1):
        x1, y1 = pts_baker[i]
        x2, y2 = pts_baker[i + 1]
        if oy - h_axis <= y1 <= oy and oy - h_axis <= y2 <= oy:
            frags.append(line(x1, y1, x2, y2, color="#2563eb", sw=2.5))

    for i in range(len(pts_upper) - 1):
        x1, y1 = pts_upper[i]
        x2, y2 = pts_upper[i + 1]
        if oy - h_axis <= y1 <= oy and oy - h_axis <= y2 <= oy:
            frags.append(line(x1, y1, x2, y2, color="#dc2626", sw=2.5))

    # Вертикальна пунктирна лінія для B0
    frags.append(line(b0_x, oy, b0_x, oy - h_axis, color=LINE, sw=1.5, dash="4,4"))
    frags.append(circle(b0_x, b0_y, 5, fill="#7c3aed", stroke="#ffffff", sw=1.5))

    # Підпис B0 на осі X
    frags.append(fitbox(b0_x - 45, oy + 8, 90, 24, "B₀ (межа)", size=11, fill="#f3e8ff", border="#7c3aed", color="#6b21a8", bold=True))

    # Пояснювальні картки / плашки в чистих зонах
    frags.append(fitbox(ox + 10, oy - h_axis + 10, 180, 50, "Область розв'язків:\nB ≤ B₀ (Скінченна)", fill="#dcfce7", border="#16a34a", color="#15803d", size=10, bold=True))

    # Зону суперечності розміщуємо в правому верхньому кутку (x=450..700, y=70..120), де криві вже опустилися нижче y=180
    frags.append(fitbox(450, oy - h_axis + 10, 230, 50, "Зона суперечності B > B₀:\nВерхня межа < Нижня межа\n(Розв'язки відсутні)", fill="#fee2e2", border="#dc2626", color="#b91c1c", size=10, bold=True))

    # Легенда для ліній в лівому нижньому кутку
    frags.append(line(ox + 20, oy - 55, ox + 50, oy - 55, color="#dc2626", sw=2.5))
    frags.append(text(ox + 55, oy - 51, "Верхня оцінка з геометрії: ln C₁ - C₂·B", size=11, color=INK, anchor="start"))

    frags.append(line(ox + 20, oy - 30, ox + 50, oy - 30, color="#2563eb", sw=2.5))
    frags.append(text(ox + 55, oy - 26, "Нижня оцінка Бейкера: -C₃·ln B", size=11, color=INK, anchor="start"))

    os.makedirs(IMG_DIR, exist_ok=True)
    out_path = os.path.join(IMG_DIR, 'baker-bound-principle.svg')
    render(out_path, width, height, *frags)
    print("Generated baker-bound-principle.svg")


def generate_baker_davenport_pipeline():
    """Малює блок-схему етапів розв'язання діофантового рівняння методом Бейкера та редукцією."""
    width, height = 760, 320
    frags = []

    # Заливка фону
    frags.append(rect(0, 0, width, height, fill=BG, stroke="none"))

    # Заголовок
    frags.append(text(width / 2, 22, "Конвеєр розв'язання діофантового рівняння методом Бейкера", size=15, bold=True, color=INK))

    # Блоки конвеєра
    boxes_data = [
        ("1. Рівняння", "Рівняння Тюе / Морделла\nF(x,y) = m або y² = x³ + k", "#dcfce7", "#16a34a"),
        ("2. Форма логарифмів", "Одиниці алгебр. поля\nΛ = ∑ bᵢ ln αᵢ ≈ 0", "#dbeafe", "#2563eb"),
        ("3. Теорема Бейкера", "Нижня межа |Λ|\nТеоретична межа B ≤ 10³⁰", "#fee2e2", "#dc2626"),
        ("4. Редукція LLL", "Лема Бейкера-Давенпорта\nЗниження межі до B ≤ 50", "#f3e8ff", "#7c3aed"),
        ("5. Перебір", "Перевірка діапазону\n→ Усі цілі розв'язки", "#dcfce7", "#15803d"),
    ]

    box_w, box_h = 130, 80
    start_x = 20
    gap = 20
    y_pos = 65

    for idx, (title, desc, fill_col, border_col) in enumerate(boxes_data):
        bx = start_x + idx * (box_w + gap)
        frags.append(fitbox(bx, y_pos, box_w, box_h, f"{title}\n{desc}", fill=fill_col, border=border_col, color=INK, size=10, bold=False))

        # Стрілка до наступного блоку
        if idx < len(boxes_data) - 1:
            ax1 = bx + box_w
            ax2 = ax1 + gap
            ay = y_pos + box_h / 2
            frags.append(line(ax1, ay, ax2, ay, color=LINE, sw=2.0))
            frags.append(line(ax2 - 5, ay - 4, ax2, ay, color=LINE, sw=2.0))
            frags.append(line(ax2 - 5, ay + 4, ax2, ay, color=LINE, sw=2.0))

    # Додаткова пояснювальна шкала знизу
    frags.append(rect(start_x, y_pos + box_h + 25, width - 40, 110, fill="#f8fafc", stroke="#cbd5e1", rx=6))
    frags.append(text(width / 2, y_pos + box_h + 45, "Ключовий ефект: Перехід від неефективності до практичного обчислення", size=12, bold=True, color=INK))

    frags.append(fitbox(start_x + 20, y_pos + box_h + 60, 340, 55, "Класична теорема Тюе (1909):\nСкінченність доведена, але B₀ = ∞ (необчислювана)", fill="#fee2e2", border="#ef4444", color="#991b1b", size=10))
    frags.append(fitbox(start_x + 380, y_pos + box_h + 60, 340, 55, "Метод Бейкера + Редукція (1966–1969):\nB₀ ≈ 10³⁰ → B₀' ≈ 50 (повна алгоритмічна розв'язність)", fill="#dcfce7", border="#22c55e", color="#166534", size=10))

    os.makedirs(IMG_DIR, exist_ok=True)
    out_path = os.path.join(IMG_DIR, 'baker-davenport-pipeline.svg')
    render(out_path, width, height, *frags)
    print("Generated baker-davenport-pipeline.svg")


if __name__ == '__main__':
    generate_baker_bound_principle()
    generate_baker_davenport_pipeline()
