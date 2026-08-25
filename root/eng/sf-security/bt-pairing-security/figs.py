# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. legacy-vs-secure: Порівняння Legacy Pairing та Secure Connections ─────
def fig_legacy_vs_secure():
    W, H = 860, 340
    p = []

    # Фон і заголовки колонок
    col_w = 380
    gap = 40
    left_x = (W - (2 * col_w + gap)) / 2 + col_w / 2
    right_x = left_x + col_w + gap

    # Ліва колонка: Legacy Pairing
    p.append(rect(left_x - col_w / 2, 40, col_w, 270, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    p.append(text(left_x, 68, "Legacy Pairing (BT 1.0–2.0 / LE Legacy)", size=13, color=POS, bold=True))
    
    b1, _, _ = textbox(left_x, 112, "Спільний секрет: PIN-код (4–16 цифр)\nФіксований PIN гарнітури: «0000» або «1234»",
                       size=11, fill="#ffffff", stroke="#e0a0a0", sw=1.2, min_w=340)
    b2, _, _ = textbox(left_x, 172, "Алгоритми: E21 / E22 (SAFER+ блоковий шифр)\nШифрування каналу: потоковий шифр E0 / AES-CTR",
                       size=11, fill="#ffffff", stroke="#e0a0a0", sw=1.2, min_w=340)
    b3, _, _ = textbox(left_x, 246, "Вразливість: пасивне перехоплення 4 пакетів\nПовний злам PIN за <0.06 с (Shaked–Wool)",
                       size=11, bold=True, fill="#fdecea", stroke=POS, sw=1.5, min_w=340)
    p.extend([b1, b2, b3])

    # Права колонка: Secure Connections
    p.append(rect(right_x - col_w / 2, 40, col_w, 270, fill="#f0faf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(right_x, 68, "Secure Connections (BT 4.2+ / BT 2.1+ SSP)", size=13, color=FIELD, bold=True))

    b4, _, _ = textbox(right_x, 112, "Обмін ключами: ефемерний ECDH (P-256 / P-192)\nСекретний DHKey не передається через радіоефір",
                       size=11, fill="#ffffff", stroke="#a0d8b0", sw=1.2, min_w=340)
    b5, _, _ = textbox(right_x, 172, "Криптопримітиви: AES-CMAC (f4, f5, f6, g2)\nШифрування каналу: автентифіковане AES-CCM (128 біт)",
                       size=11, fill="#ffffff", stroke="#a0d8b0", sw=1.2, min_w=340)
    b6, _, _ = textbox(right_x, 246, "Стійкість: 128 біт проти пасивного прослуховування\nЗахист від MITM через Numeric Comparison / OOB",
                       size=11, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.5, min_w=340)
    p.extend([b4, b5, b6])

    render(os.path.join(OUT, "legacy-vs-secure.svg"), W, H, *p,
           title="Архітектурне порівняння Legacy Pairing та Secure Connections")


# ── 2. io-capabilities-matrix: Матриця вибору моделі асоціації ───────────────
def fig_io_matrix():
    W, H = 860, 360
    p = []

    p.append(text(W / 2, 30, "Матриця вибору асоціативної моделі за можливостями вводу/виводу (IO Capabilities)",
                  size=13, color=INK, bold=True))

    headers_x = [150, 290, 430, 570, 710]
    headers_y = 70
    caps = ["DisplayOnly", "DisplayYesNo", "KeyboardOnly", "NoInputNoOutput", "KeyboardDisplay"]

    # Сітка таблиці
    x0, y0 = 60, 50
    cw, ch = 140, 50
    rows = ["DisplayOnly", "DisplayYesNo", "KeyboardOnly", "NoInputNoOutput", "KeyboardDisplay"]

    # Колонки
    for j, c in enumerate(caps):
        p.append(rect(x0 + 100 + j * cw, y0, cw, 34, fill="#eef4ff", stroke=NEG, sw=1.2, rx=4))
        p.append(text(x0 + 100 + j * cw + cw / 2, y0 + 22, c, size=11, color=NEG, bold=True))

    # Рядки
    matrix_data = [
        ["Just Works", "Just Works", "Passkey Entry", "Just Works", "Passkey Entry"],
        ["Just Works", "Numeric Comp", "Passkey Entry", "Just Works", "Numeric Comp"],
        ["Passkey Entry", "Passkey Entry", "Passkey Entry", "Just Works", "Passkey Entry"],
        ["Just Works", "Just Works", "Just Works", "Just Works", "Just Works"],
        ["Passkey Entry", "Numeric Comp", "Passkey Entry", "Just Works", "Numeric Comp"],
    ]

    for i, r_name in enumerate(rows):
        ry = y0 + 38 + i * ch
        p.append(rect(x0, ry, 96, ch - 4, fill="#fdf6e3", stroke="#b8860b", sw=1.2, rx=4))
        p.append(text(x0 + 48, ry + ch / 2 - 2, r_name, size=10, color="#8a6d10", bold=True))

        for j in range(5):
            val = matrix_data[i][j]
            cx = x0 + 100 + j * cw
            if val == "Numeric Comp":
                f_color, s_color, t_color = "#eafaf0", FIELD, FIELD
                label = "Numeric Comp"
            elif val == "Passkey Entry":
                f_color, s_color, t_color = "#eef4ff", NEG, NEG
                label = "Passkey Entry"
            else:
                f_color, s_color, t_color = "#fff5f5", "#d9534f", "#c0392b"
                label = "Just Works *"

            p.append(rect(cx + 2, ry, cw - 4, ch - 4, fill=f_color, stroke=s_color, sw=1.2, rx=4))
            p.append(text(cx + cw / 2, ry + ch / 2 - 2, label, size=10, color=t_color, bold=True))

    p.append(text(W / 2, H - 16, "* Just Works забезпечує захист від пасивного перехоплення, але не захищає від MITM",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "io-capabilities-matrix.svg"), W, H, *p,
           title="Матриця вибору асоціативної моделі")


# ── 3. pairing-phases: 4 фази спарювання LE Secure Connections ───────────────
def fig_pairing_phases():
    W, H = 860, 380
    p = []

    p.append(text(W / 2, 28, "Чотири фази спарювання у протоколі безпеки LE Secure Connections (SMP)",
                  size=13, color=INK, bold=True))

    # Стовпці фаз
    pw = 190
    ph = 280
    gap = 20
    start_x = (W - (4 * pw + 3 * gap)) / 2

    phases = [
        ("Фаза 1", "Feature Exchange",
         "Обмін параметрами SMP:\n• IO Capabilities\n• Прапорець AuthReq\n• Вимоги MITM / SC\n• Розмір ключа (16 байт)",
         "#eef4ff", NEG),
        ("Фаза 2", "Key Exchange & Auth",
         "ECDH та автентифікація:\n• Обмін точками PKa, PKb\n• Обчислення DHKey\n• Stage 1: Numeric Comp\n• Stage 2: DHKey Check",
         "#fdf6e3", "#b8860b"),
        ("Фаза 3", "LTK Generation",
         "Деривація ключів:\n• Функція f5(DHKey)\n• Генерація MacKey\n• Генерація LTK (128 біт)\n• Розрахунок для CTKD",
         "#f0faf4", FIELD),
        ("Фаза 4", "Encryption & Distr",
         "Шифрування та передача:\n• Старт AES-CCM у Link Layer\n• Захищений обмін IRK\n• Передача CSRK\n• Захист адреси (RPA)",
         "#f2ecf8", "#8a5fb0"),
    ]

    for i, (title_ph, sub_ph, desc, bg_col, brd_col) in enumerate(phases):
        x = start_x + i * (pw + gap)
        y = 55
        p.append(rect(x, y, pw, ph, fill=bg_col, stroke=brd_col, sw=1.5, rx=8))
        p.append(text(x + pw / 2, y + 26, title_ph, size=13, color=brd_col, bold=True))
        p.append(text(x + pw / 2, y + 46, sub_ph, size=11, color=INK, bold=True))
        p.append(line(x + 15, y + 58, x + pw - 15, y + 58, color=brd_col, sw=1.0))

        lines = desc.split("\n")
        for line_idx, ln in enumerate(lines):
            p.append(text(x + 14, y + 84 + line_idx * 26, ln, size=10, color=INK, anchor="start"))

        if i < 3:
            ax = x + pw + 3
            ay = y + ph / 2
            p.append(arrow(ax, ay, ax + gap - 6, ay, color=LINE, sw=1.8))

    p.append(text(W / 2, H - 14, "Шифрування радіоефіру активується на Фазі 4; усі ключі розподілу передаються виключно в зашифрованому каналі",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "pairing-phases.svg"), W, H, *p,
           title="Фази процедури спарювання Bluetooth")


# ── 4. mitm-protection-stages: Механізм захисту в Numeric Comparison ──────────
def fig_mitm_stages():
    W, H = 860, 360
    p = []

    p.append(text(W / 2, 28, "Криптографічний захист від MITM у моделі Numeric Comparison (LE Secure Connections)",
                  size=13, color=INK, bold=True))

    # Ліва сторона: Ініціатор (A), Права сторона: Відповідач (B), Центр: Радіоефір
    ax, bx = 160, 700
    top_y = 60
    p.append(rect(ax - 90, top_y, 180, 38, fill="#eef4ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(ax, top_y + 24, "Ініціатор (A)", size=12, color=NEG, bold=True))

    p.append(rect(bx - 90, top_y, 180, 38, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(bx, top_y + 24, "Відповідач (B)", size=12, color=FIELD, bold=True))

    # Вертикальні часові лінії
    p.append(line(ax, top_y + 38, ax, 305, color=NEG, sw=1.5, dash="4,4"))
    p.append(line(bx, top_y + 38, bx, 305, color=FIELD, sw=1.5, dash="4,4"))

    # Крок 1: Зобов'язання C_a
    y1 = 120
    p.append(arrow(ax, y1, bx, y1, color=LINE, sw=1.5))
    p.append(text(W / 2, y1 - 8, "1. Зобов'язання C_a = f4(PK_a, PK_b, N_a, 0)", size=10, color=INK, bold=True))

    # Крок 2: Випадкове число N_b
    y2 = 165
    p.append(arrow(bx, y2, ax, y2, color=LINE, sw=1.5))
    p.append(text(W / 2, y2 - 8, "2. Відкриття випадкового числа N_b", size=10, color=INK, bold=True))

    # Крок 3: Розкриття N_a та перевірка C_a
    y3 = 210
    p.append(arrow(ax, y3, bx, y3, color=LINE, sw=1.5))
    p.append(text(W / 2, y3 - 8, "3. Розкриття N_a -> B перевіряє C_a == f4(PK_a, PK_b, N_a, 0)", size=10, color=INK, bold=True))

    # Крок 4: Розрахунок коду звірки
    y4 = 255
    b_calc, _, _ = textbox(W / 2, y4, "Обидва рахують: V = g2(PK_a, PK_b, N_a, N_b) mod 10⁶\nКористувач бачить 6 цифр на обох екранах і натискає «Підтвердити»",
                           size=10, fill="#fdf6e3", stroke="#b8860b", sw=1.2, min_w=460)
    p.append(b_calc)

    # Крок 5: DHKey Check
    y5 = 300
    p.append(text(W / 2, y5 - 4, "Stage 2: Взаємний обмін DHKey Check (E_a та E_b через функцію f6)", size=10, color=FIELD, bold=True))

    p.append(text(W / 2, H - 14, "Активний зловмисник (MITM) не може підмінити ключі непомітно: шанс вгадати 6 цифр без розбіжності = 10⁻⁶",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "mitm-protection-stages.svg"), W, H, *p,
           title="Захист від MITM у Numeric Comparison")


def main():
    fig_legacy_vs_secure()
    fig_io_matrix()
    fig_pairing_phases()
    fig_mitm_stages()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
