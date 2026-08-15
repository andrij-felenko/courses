import sys
import os

# Add scripts directory to import svgkit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import (
    render, rect, line, text, circle, arrow, mtext,
    INK, MUTED, FIELD, POS, NEG, FILL, BG, FONT
)

def draw_roots_unity(out_path):
    w, h = 800, 420
    frags = []

    # Background rect (svgkit adds background, but let's keep clean canvas)
    frags.append(rect(0, 0, w, h, fill=BG, stroke="#cbd5e1", sw=1))

    # Header
    frags.append(text(w / 2, 32, "Значення характерів Діріхле як корені з одиниці на комплексній площині", size=16, bold=True, color="#0f172a", anchor="middle"))
    frags.append(text(w / 2, 54, "Група (ℤ/5ℤ)* з первісним коренем g = 2; φ(5) = 4 корені 4-го степеня", size=12, color=MUTED, anchor="middle"))

    # Circle center and radius
    cx, cy = 230, 240
    r = 120

    # Axes
    frags.append(line(cx - r - 30, cy, cx + r + 40, cy, color="#94a3b8", sw=1.5))
    frags.append(line(cx, cy + r + 30, cx, cy - r - 30, color="#94a3b8", sw=1.5))
    frags.append(text(cx + r + 45, cy + 5, "Re", size=12, bold=True, color="#475569", anchor="start"))
    frags.append(text(cx + 5, cy - r - 35, "Im", size=12, bold=True, color="#475569", anchor="start"))

    # Main unit circle
    frags.append(circle(cx, cy, r, fill="none", stroke="#2563eb", sw=2))

    # Roots of unity points: 1 (0 deg), i (90 deg), -1 (180 deg), -i (270 deg)
    pts = [
        (cx + r, cy, "1", "χ(1) = 1", "#16a34a", "start", 15, 5),
        (cx, cy - r, "i", "χ₂(2) = i", "#2563eb", "middle", 0, -15),
        (cx - r, cy, "-1", "χ₁(2) = -1", "#dc2626", "end", -15, 5),
        (cx, cy + r, "-i", "χ₃(2) = -i", "#9333ea", "middle", 0, 22)
    ]

    for px, py, label, sub, col, anch, dx, dy in pts:
        frags.append(line(cx, cy, px, py, color=col, sw=1.5, dash="4,4"))
        frags.append(circle(px, py, 6, fill=col, stroke=BG, sw=1.5))
        frags.append(text(px + dx, py + dy, sub, size=12, bold=True, color=col, anchor=anch))

    # Right side: Panel with character mapping explanation
    px, py = 430, 85
    pw, ph = 340, 305
    frags.append(rect(px, py, pw, ph, fill=FILL, stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(px + pw / 2, py + 26, "Значення характерів для q = 5", size=13, bold=True, color="#1e293b", anchor="middle"))

    mapping_text = [
        ("χ₀ (головний):", "1 → 1,  2 → 1,  3 → 1,  4 → 1", "#15803d"),
        ("χ₁ (знаковий):", "1 → 1,  2 → -1, 3 → -1, 4 → 1", "#b91c1c"),
        ("χ₂ (комплексний):", "1 → 1,  2 → i,  3 → -i, 4 → -1", "#1d4ed8"),
        ("χ₃ (комплексний):", "1 → 1,  2 → -i, 3 → i,  4 → -1", "#7e22ce")
    ]

    for idx, (title_str, val_str, c_col) in enumerate(mapping_text):
        y_pos = py + 60 + idx * 60
        frags.append(rect(px + 12, y_pos - 15, pw - 24, 50, fill=BG, stroke="#e2e8f0", sw=1, rx=4))
        frags.append(text(px + 22, y_pos + 4, title_str, size=12, bold=True, color=c_col, anchor="start"))
        frags.append(text(px + 22, y_pos + 24, val_str, size=11, color="#334155", anchor="start"))

    return render(out_path, w, h, *frags)

def draw_orthogonality_matrix(out_path):
    w, h = 820, 460
    frags = []

    frags.append(rect(0, 0, w, h, fill=BG, stroke="#cbd5e1", sw=1))

    # Title
    frags.append(text(w / 2, 32, "Ортогональність характерів Діріхле та розклад дельта-функції (mod 5)", size=16, bold=True, color="#0f172a", anchor="middle"))
    frags.append(text(w / 2, 54, "Рядки ортогональні за елементами n; Стовпчики ортогональні за характерами χ", size=12, color=MUTED, anchor="middle"))

    # Matrix Table
    tx, ty = 50, 85
    cw, ch = 120, 36

    headers = ["Характер", "n = 1", "n = 2", "n = 3", "n = 4"]
    rows = [
        ["χ₀ (головний)", "1", "1", "1", "1"],
        ["χ₁ (знаковий)", "1", "-1", "-1", "1"],
        ["χ₂ (комплексний)", "1", "i", "-i", "-1"],
        ["χ₃ (комплексний)", "1", "-i", "i", "-1"]
    ]

    # Header row
    for j, h_str in enumerate(headers):
        x = tx + j * cw
        bg_col = "#e2e8f0" if j == 0 else "#dbeafe"
        frags.append(rect(x, ty, cw, ch, fill=bg_col, stroke="#94a3b8", sw=1))
        frags.append(text(x + cw / 2, ty + 23, h_str, size=12, bold=True, color="#1e293b", anchor="middle"))

    # Rows
    for i, r_data in enumerate(rows):
        y = ty + (i + 1) * ch
        r_bg = "#f8fafc" if i % 2 == 0 else BG
        for j, val in enumerate(r_data):
            x = tx + j * cw
            txt_col = "#0f172a"
            txt_bold = False
            if j == 0:
                txt_bold = True
                txt_col = "#1e3a8a"
            elif val in ["i", "-i"]:
                txt_col = "#2563eb"
                txt_bold = True
            elif val == "-1":
                txt_col = "#dc2626"
                txt_bold = True
            frags.append(rect(x, y, cw, ch, fill=r_bg, stroke="#cbd5e1", sw=1))
            frags.append(text(x + cw / 2, y + 23, val, size=12, bold=txt_bold, color=txt_col, anchor="middle"))

    # Sum Row at bottom
    y_sum = ty + 5 * ch
    frags.append(rect(tx, y_sum, cw, ch, fill="#fef3c7", stroke="#f59e0b", sw=1))
    frags.append(text(tx + cw / 2, y_sum + 23, "Сума ∑_χ χ(n)", size=11, bold=True, color="#92400e", anchor="middle"))
    
    col_sums = ["4", "0", "0", "0"]
    for j, s_val in enumerate(col_sums):
        x = tx + (j + 1) * cw
        s_bg = "#dcfce7" if s_val == "4" else "#fee2e2"
        s_col = "#166534" if s_val == "4" else "#991b1b"
        frags.append(rect(x, y_sum, cw, ch, fill=s_bg, stroke="#94a3b8", sw=1))
        frags.append(text(x + cw / 2, y_sum + 23, s_val, size=13, bold=True, color=s_col, anchor="middle"))

    # Bottom explanations panel
    bx, by = 50, 310
    bw, bh = 720, 125
    frags.append(rect(bx, by, bw, bh, fill=FILL, stroke="#cbd5e1", sw=1, rx=6))
    
    frags.append(text(bx + 20, by + 28, "1. Перша ортогональність (за елементами):", size=12, bold=True, color="#1e293b", anchor="start"))
    frags.append(text(bx + 330, by + 28, "∑_{n (mod q)} χ_a(n) · χ̄_b(n) = φ(q) · δ_{a,b}", size=12, bold=True, color="#1d4ed8", anchor="start"))

    frags.append(text(bx + 20, by + 58, "2. Друга ортогональність (за характерами):", size=12, bold=True, color="#1e293b", anchor="start"))
    frags.append(text(bx + 330, by + 58, "∑_{χ (mod q)} χ(m) · χ̄(n) = φ(q) · δ_{m ≡ n (mod q)}", size=12, bold=True, color="#1d4ed8", anchor="start"))

    frags.append(text(bx + 20, by + 95, "3. Проекція на клас остач a (mod q):", size=12, bold=True, color="#1e293b", anchor="start"))
    frags.append(text(bx + 330, by + 95, "δ(n ≡ a mod q) = (1 / φ(q)) · ∑_χ χ̄(a) · χ(n)", size=12, bold=True, color="#15803d", anchor="start"))

    return render(out_path, w, h, *frags)

def draw_conductor_projection(out_path):
    w, h = 800, 380
    frags = []

    frags.append(rect(0, 0, w, h, fill=BG, stroke="#cbd5e1", sw=1))

    # Header
    frags.append(text(w / 2, 32, "Провідник (conductor) та індукований характер", size=16, bold=True, color="#0f172a", anchor="middle"))
    frags.append(text(w / 2, 54, "Зведення індукованого характера χ (mod 12) до первісного характера χ* (mod 3)", size=12, color=MUTED, anchor="middle"))

    # Box Left: Primitive Character mod 3
    lx, ly = 50, 95
    lw, lh = 310, 240
    frags.append(rect(lx, ly, lw, lh, fill="#f0fdf4", stroke="#22c55e", sw=2, rx=6))
    frags.append(text(lx + lw / 2, ly + 30, "Первісний характер χ* (mod 3)", size=14, bold=True, color="#15803d", anchor="middle"))
    frags.append(text(lx + lw / 2, ly + 52, "Провідник d = 3 (найменший модуль)", size=11, color="#166534", anchor="middle"))

    mod3_vals = [
        ("n = 1 (mod 3):", "χ*(1) = 1"),
        ("n = 2 (mod 3):", "χ*(2) = -1"),
        ("n = 0 (mod 3):", "χ*(0) = 0")
    ]
    for i, (k_str, v_str) in enumerate(mod3_vals):
        y_pos = ly + 90 + i * 45
        frags.append(rect(lx + 20, y_pos - 15, lw - 40, 36, fill=BG, stroke="#bbf7d0", sw=1, rx=4))
        frags.append(text(lx + 35, y_pos + 8, k_str, size=12, color="#334155", anchor="start"))
        frags.append(text(lx + lw - 35, y_pos + 8, v_str, size=12, bold=True, color="#15803d", anchor="end"))

    # Arrow between boxes
    frags.append(arrow(370, 215, 430, 215, color="#2563eb", sw=2.5))
    frags.append(text(400, 200, "Індукція", size=11, bold=True, color="#1d4ed8", anchor="middle"))
    frags.append(text(400, 235, "χ(n) = χ*(n)", size=10, color="#1e40af", anchor="middle"))

    # Box Right: Induced Character mod 12
    rx, ry = 440, 95
    rw, rh = 310, 240
    frags.append(rect(rx, ry, rw, rh, fill="#eff6ff", stroke="#3b82f6", sw=2, rx=6))
    frags.append(text(rx + rw / 2, ry + 30, "Індукований характер χ (mod 12)", size=14, bold=True, color="#1e40af", anchor="middle"))
    frags.append(text(rx + rw / 2, ry + 52, "Модуль q = 12; φ(12) = 4", size=11, color="#1d4ed8", anchor="middle"))

    mod12_vals = [
        ("n = 1 (mod 12):", "1 ≡ 1 (mod 3) ⇒ χ(1) = 1"),
        ("n = 5 (mod 12):", "5 ≡ 2 (mod 3) ⇒ χ(5) = -1"),
        ("n = 7 (mod 12):", "7 ≡ 1 (mod 3) ⇒ χ(7) = 1"),
        ("n = 11 (mod 12):", "11 ≡ 2 (mod 3) ⇒ χ(11) = -1")
    ]
    for i, (k_str, v_str) in enumerate(mod12_vals):
        y_pos = ry + 82 + i * 38
        frags.append(rect(rx + 15, y_pos - 12, rw - 30, 30, fill=BG, stroke="#bfdbfe", sw=1, rx=4))
        frags.append(text(rx + 25, y_pos + 7, k_str, size=11, bold=True, color="#1e293b", anchor="start"))
        frags.append(text(rx + rw - 25, y_pos + 7, v_str, size=10, bold=True, color="#1d4ed8", anchor="end"))

    return render(out_path, w, h, *frags)

def main():
    target_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(target_dir, exist_ok=True)

    draw_roots_unity(os.path.join(target_dir, 'fig-character-roots-unity.svg'))
    draw_orthogonality_matrix(os.path.join(target_dir, 'fig-orthogonality-matrix.svg'))
    draw_conductor_projection(os.path.join(target_dir, 'fig-conductor-projection.svg'))

    print("Figures generated successfully in ./img/")

if __name__ == '__main__':
    main()
