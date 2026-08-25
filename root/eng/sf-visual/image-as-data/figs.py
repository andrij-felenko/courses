# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import colorsys

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори акцентів каналів (дані, не тема UI) — лишаємо як у джерелі
R_COL = "#cc0000"
G_COL = "#0a8f3c"
B_COL = "#1f4ed8"
ORANGE = "#d98a00"


def cell(x, y, s, g, fill):
    """Кольоровий піксель-клітинка (raw rgb — це дані, не тема)."""
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" '
            'fill="rgb(%d,%d,%d)" stroke="#cbd5e1" stroke-width="0.4"/>' % (x, y, s, g, fill[0], fill[1], fill[2]))


# ── image-as-grid: зображення — сітка чисел ───────────────────────────────────
# Ідея: фото → ділянка пікселів зблизька → ті самі пікселі як числа 0…255.

def fig_image_as_grid():
    W, H = 960, 460
    p = []

    # ── «фото»: смуга неба + сонце, рамка, виділена ділянка ──
    p.append(text(150, 100, "фото", size=12, bold=True))
    for i in range(10):
        c = (100 + i * 6, 140 + i * 8, 210)
        p.append('<rect x="70" y="%d" width="160" height="12" fill="rgb(%d,%d,%d)"/>'
                 % (124 + i * 12, c[0], min(c[1], 255), c[2]))
    p.append('<circle cx="178" cy="150" r="17" fill="#fde68a"/>')
    p.append(rect(70, 124, 160, 120, fill="none", stroke=INK, sw=1.4, rx=6))
    p.append(rect(150, 196, 26, 26, fill="none", stroke=R_COL, sw=1.8, rx=2))
    p.append(line(176, 209, 298, 184, color=R_COL, sw=1.2, dash="3,2"))

    # ── пікселі зблизька (6×6 сіра ділянка) ──
    p.append(text(360, 100, "пікселі (зблизька)", size=12, bold=True))
    gx, gy, gs = 300, 124, 20
    vals = [[90 + c * 8 + r * 18 for c in range(6)] for r in range(6)]
    for r in range(6):
        for c in range(6):
            v = min(vals[r][c], 235)
            p.append(cell(gx + c * gs, gy + r * gs, gs, gs, (v, v, v)))
    p.append(rect(gx, gy, 120, 120, fill="none", stroke=INK, sw=1.4, rx=6))
    p.append(arrow(426, 184, 462, 184, color=INK, sw=1.6))

    # ── ті самі пікселі — числа 0…255 ──
    p.append(text(700, 100, "ті самі пікселі — числа 0…255", size=12, bold=True))
    tx, ty, cw, ch = 488, 124, 34, 20
    for r in range(6):
        for c in range(6):
            v = vals[r][c]
            x = tx + c * cw
            y = ty + r * ch
            p.append(rect(x, y, cw, ch, fill=BG, stroke="#e5e7eb", sw=0.6, rx=2))
            p.append(text(x + cw / 2, y + 14, str(v), size=9, color=INK))
    p.append(rect(tx, ty, 6 * cw, 6 * ch, fill="none", stroke=INK, sw=1.2, rx=6))

    p.append(text(150, 262, "роздільність = W×H пікселів", size=10, color=MUTED))

    # ── нижня плашка-висновок ──
    box_y = 300
    p.append(rect(70, box_y, 820, 96, fill=FILL, stroke=INK, sw=1.3, rx=10))
    p.append(text(480, box_y + 24, "Кожен піксель — просто число (яскравість 0…255; 0 — чорне, 255 — біле).",
                  size=12, bold=True))
    p.append(text(96, box_y + 48,
                  "• будь-яка операція зору (розмиття, межі, пошук) — це арифметика над цією матрицею;",
                  size=10, anchor="start"))
    p.append(text(96, box_y + 70,
                  "• адресуємо піксель як [рядок, стовпець]; зрушити, додати, порівняти — усе це дії над числами.",
                  size=10, anchor="start"))

    render(os.path.join(OUT, "image-as-grid.svg"), W, H, *p,
           title="Зображення — це сітка чисел")


# ── channels: колір — це кілька сіток разом ───────────────────────────────────
# Ідея: R + G + B = колір; кожен канал — своя сіра мапа 0…255.

def fig_channels():
    W, H = 960, 470
    p = []
    gs = 20
    grid_y = 132

    # шаблони яскравостей для кожного каналу (5×5), значення -> сірий
    R_pat = [[40, 40, 150, 40, 40],
             [40, 150, 240, 150, 40],
             [150, 240, 240, 240, 150],
             [40, 150, 240, 150, 40],
             [40, 40, 150, 40, 40]]
    G_pat = [[42, 42, 100, 42, 42],
             [42, 100, 150, 100, 42],
             [100, 150, 150, 150, 100],
             [42, 100, 150, 100, 42],
             [42, 42, 100, 42, 42]]
    B_pat = [[62, 62, 55, 62, 62],
             [62, 55, 40, 55, 62],
             [55, 40, 40, 40, 55],
             [62, 55, 40, 55, 62],
             [62, 62, 55, 62, 62]]

    def draw_grid(ox, vals, gray=True, rgb_from=None):
        out = []
        for r in range(5):
            for c in range(5):
                if gray:
                    v = vals[r][c]
                    out.append(cell(ox + c * gs, grid_y + r * gs, gs, gs, (v, v, v)))
                else:
                    col = (R_pat[r][c], G_pat[r][c], B_pat[r][c])
                    out.append(cell(ox + c * gs, grid_y + r * gs, gs, gs, col))
        return out

    # R
    p.append(text(130, 120, "канал R", size=12, color=R_COL, bold=True))
    p += draw_grid(80, R_pat)
    p.append(rect(80, grid_y, 100, 100, fill="none", stroke=R_COL, sw=2, rx=2))
    p.append(text(196, 188, "+", size=22, bold=True))

    # G
    p.append(text(280, 120, "канал G", size=12, color=G_COL, bold=True))
    p += draw_grid(230, G_pat)
    p.append(rect(230, grid_y, 100, 100, fill="none", stroke=G_COL, sw=2, rx=2))
    p.append(text(346, 188, "+", size=22, bold=True))

    # B
    p.append(text(430, 120, "канал B", size=12, color=B_COL, bold=True))
    p += draw_grid(380, B_pat)
    p.append(rect(380, grid_y, 100, 100, fill="none", stroke=B_COL, sw=2, rx=2))
    p.append(text(496, 188, "=", size=22, bold=True))

    # = колір
    p.append(text(640, 120, "колір", size=12, bold=True))
    p += draw_grid(590, None, gray=False)
    p.append(rect(590, grid_y, 100, 100, fill="none", stroke=INK, sw=2, rx=2))

    p.append(text(640, 250, "кожен канал — «скільки» одного основного кольору (0…255)",
                  size=10, color=MUTED))

    # нижня плашка
    by = 290
    p.append(rect(80, by, 800, 110, fill="#eef2ff", stroke=B_COL, sw=1.4, rx=11))
    p.append(text(480, by + 24, "Що варто запам'ятати про канали", size=12, color=B_COL, bold=True))
    p.append(text(110, by + 48, "• кольорове зображення = три сірі мапи (R, G, B) одна над одною → форма H×W×3;",
                  size=10, anchor="start"))
    p.append(text(110, by + 69, "• відтінок сірого = 1 канал (утричі менше даних — часто цього досить для форм і меж);",
                  size=10, anchor="start"))
    p.append(text(110, by + 90, "• «глибина» 8 біт → значення 0…255 на канал; буває 10–12 біт (ширший діапазон).",
                  size=10, anchor="start"))

    render(os.path.join(OUT, "channels.svg"), W, H, *p,
           title="Канали: колір — це кілька сіток разом")


# ── color-spaces: один колір — три записи (RGB / HSV / YUV) ────────────────────
# Ідея: той самий помаранчевий піксель, записаний у трьох просторах.

def fig_color_spaces():
    W, H = 960, 460
    p = []

    # зразок кольору вгорі
    p.append(text(480, 84, "той самий піксель", size=11, color=MUTED))
    p.append('<rect x="442" y="92" width="76" height="24" rx="5" fill="rgb(240,140,20)" '
             'stroke="%s" stroke-width="1.2"/>' % INK)
    p.append(text(480, 134, "…записаний трьома способами:", size=10, color=MUTED))

    cols = [
        (70, B_COL, "RGB",
         [("R", "240"), ("G", "140"), ("B", "20")],
         ["адитивний; як сенсор і екран.",
          "Яскравість «розмазана» по всіх",
          "трьох — погано шукати колір."]),
        (360, G_COL, "HSV",
         [("H тон", "32°"), ("S насич.", "92%"), ("V яскр.", "94%")],
         ["тон ОКРЕМО від яскравості →",
          "знайти колір легко й стійко до",
          "світла. Найкраще для зору!"]),
        (650, ORANGE, "YUV / YCbCr",
         [("Y яскр.", "178"), ("U / Cb", "−60"), ("V / Cr", "+70")],
         ["яскравість окремо від кольору →",
          "відео й JPEG;",
          "око бачить Y докладніше."]),
    ]
    bx, by, bw, bh = None, 156, 270, 208
    for x, col, name, rows, notes in cols:
        cx = x + bw / 2
        p.append(rect(x, by, bw, bh, fill=FILL, stroke=col, sw=1.9, rx=12))
        p.append(text(cx, by + 26, name, size=13, color=col, bold=True))
        for i, (lab, val) in enumerate(rows):
            ry = by + 54 + i * 28
            p.append(text(x + 26, ry, lab, size=10, color=INK, anchor="start"))
            p.append(text(x + bw - 26, ry, val, size=11, color=col, bold=True, anchor="end"))
        p.append(line(x + 18, by + 146, x + bw - 18, by + 146, color="#e5e7eb", sw=1))
        for i, ln in enumerate(notes):
            p.append(text(x + 20, by + 164 + i * 14, ln, size=9, color=INK, anchor="start"))

    p.append(text(480, 446,
                  "Колір не міняється — міняється ЗАПИС. Обирай простір так, щоб задача стала легкою: "
                  "HSV для кольору, сіре для форми.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "color-spaces.svg"), W, H, *p,
           title="Колірні простори: різні способи записати той самий колір")


# ── hsv-for-vision: чому для зору беруть HSV, а не RGB ─────────────────────────
# Ідея: «помаранчевий м'яч» при яскравому/тьмяному світлі: у RGB усі 3 числа
# повзуть, у HSV тон H майже сталий; смужка тону 20–40° на райдузі.

def fig_hsv_for_vision():
    W, H = 960, 470
    p = []

    # ── ліва панель: у RGB важко ──
    p.append(rect(60, 110, 400, 250, fill="#fef2f2", stroke=R_COL, sw=1.8, rx=12))
    p.append(text(260, 134, "у RGB — важко", size=12, color=R_COL, bold=True))
    p.append('<circle cx="150" cy="196" r="30" fill="rgb(250,150,40)" stroke="%s" stroke-width="1.2"/>' % INK)
    p.append(text(150, 240, "яскраве світло", size=9, color=MUTED))
    p.append(text(150, 256, "R250 G150 B40", size=9, bold=True))
    p.append('<circle cx="360" cy="196" r="30" fill="rgb(120,70,18)" stroke="%s" stroke-width="1.2"/>' % INK)
    p.append(text(360, 240, "тьмяне світло", size=9, color=MUTED))
    p.append(text(360, 256, "R120 G70 B18", size=9, bold=True))
    p.append(text(260, 298, "усі три числа поповзли!", size=10, color=R_COL, bold=True))
    p.append(text(260, 320, "«помаранчевий» — рухома ціль у 3D,", size=9, color=MUTED))
    p.append(text(260, 336, "яку важко задати порогом", size=9, color=MUTED))

    # ── права панель: у HSV легко ──
    p.append(rect(500, 110, 400, 250, fill="#eafaef", stroke=G_COL, sw=1.8, rx=12))
    p.append(text(700, 134, "у HSV — легко", size=12, color="#15803d", bold=True))
    p.append('<circle cx="590" cy="196" r="30" fill="rgb(250,150,40)" stroke="%s" stroke-width="1.2"/>' % INK)
    p.append(text(590, 240, "яскраве", size=9, color=MUTED))
    p.append(text(590, 256, "H32° S84 V98", size=9, bold=True))
    p.append('<circle cx="810" cy="196" r="30" fill="rgb(120,70,18)" stroke="%s" stroke-width="1.2"/>' % INK)
    p.append(text(810, 240, "тьмяне", size=9, color=MUTED))
    p.append(text(810, 256, "H32° S85 V47", size=9, bold=True))
    p.append(text(700, 298, "тон H майже не змінився!", size=10, color="#15803d", bold=True))
    p.append(text(700, 320, "«помаранчевий» = смужка тону 20–40°", size=9, color=MUTED))
    p.append(text(700, 336, "→ один поріг, стійко до світла", size=9, color=MUTED))

    # ── райдуга тонів (hue strip) зі смужкою 20–40° ──
    strip_x, strip_y, sw_, sh = 250, 384, 14, 18
    n = 32
    for i in range(n):
        hue = i / float(n)  # 0..1
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        col = (int(r * 255), int(g * 255), int(b * 255))
        p.append('<rect x="%.1f" y="%d" width="%d" height="%d" fill="rgb(%d,%d,%d)"/>'
                 % (strip_x + i * sw_, strip_y, sw_, sh, col[0], col[1], col[2]))
    total_w = n * sw_
    p.append(rect(strip_x, strip_y, total_w, sh, fill="none", stroke=INK, sw=1, rx=2))
    # рамка-виділення смужки помаранчевого тону (~20–40° → клітинки 2-3)
    p.append(rect(strip_x + int(2 * sw_) - 1, strip_y - 3, 2 * sw_ + 2, sh + 6,
                  fill="none", stroke=INK, sw=2, rx=2))
    p.append(text(strip_x + int(3 * sw_), strip_y + 34, "↑ смужка «помаранчевого» тону",
                  size=9, bold=True))

    p.append(text(700, 456,
                  "Тому колір шукають у HSV: тон тримається попри світло. RGB→HSV, узяв смужку тону — і ось ціль.",
                  size=10, color=MUTED, italic=True, anchor="end"))

    render(os.path.join(OUT, "hsv-for-vision.svg"), W, H, *p,
           title="Чому для зору беруть HSV, а не RGB")


# ── summer-1966: «розв'яжемо зір за канікули» ─────────────────────────────────
# Ідея: записка Summer Vision Project 1966 → стрілка → таймлінія «а насправді
# будують досі».

def fig_summer_1966():
    W, H = 960, 460
    p = []

    # ── картка-записка ──
    p.append(rect(80, 110, 300, 180, fill="#fffef7", stroke=INK, sw=1.6, rx=6))
    p.append('<rect x="80" y="110" width="300" height="32" rx="6" fill="#fff5e6"/>')
    p.append(text(230, 131, "MIT · Project MAC · AI Group", size=10, bold=True))
    p.append(text(100, 164, "THE SUMMER VISION PROJECT", size=12, bold=True, anchor="start"))
    p.append(text(100, 183, "Seymour Papert · 7 липня 1966", size=9, color=MUTED, anchor="start"))
    for i, ln in enumerate([
        "Мета: за літо зробити систему,",
        "що поділить кадр на об'єкти",
        "й тло — і назве прості тіла.",
        "Координує Джеральд Сассмен",
        "(студент) з гуртом студентів.",
    ]):
        p.append(text(100, 208 + i * 17, ln, size=9, anchor="start"))

    p.append(arrow(398, 200, 466, 200, color=INK, sw=2))

    # ── таймлінія «а насправді» ──
    p.append(text(700, 126, "а насправді…", size=12, color=R_COL, bold=True))
    p.append(line(500, 200, 900, 200, color=MUTED, sw=2))
    marks = [(520, G_COL, ["1966", "літо"]), (640, ORANGE, ["1980-ті"]),
             (770, ORANGE, ["2010-ті"]), (885, R_COL, ["досі"])]
    for mx, col, labs in marks:
        p.append('<circle cx="%d" cy="200" r="5" fill="%s" stroke="%s" stroke-width="1"/>' % (mx, col, INK))
        for j, lab in enumerate(labs):
            p.append(text(mx, 222 + j * 13, lab, size=9, color=col, bold=True))
    p.append(text(700, 262, "те, що думали зробити за літо,", size=10, color=MUTED))
    p.append(text(700, 277, "будують і досі — це ціла наука", size=10, color=MUTED))

    # ── нижня плашка ──
    by = 320
    p.append(rect(80, by, 800, 92, fill=FILL, stroke=INK, sw=1.3, rx=10))
    p.append(text(480, by + 24, "Чому ця історія — на початку розділу про машинне бачення?",
                  size=11, bold=True))
    p.append(text(118, by + 46,
                  "Бо це найвідоміший урок про те, що «очевидне» для людини буває страшенно важким для машини.",
                  size=10, anchor="start"))
    p.append(text(118, by + 64,
                  "Саме з цього невдалого літа й виріс увесь напрям, ази якого ми пройдемо в цьому розділі.",
                  size=10, anchor="start"))

    render(os.path.join(OUT, "summer-1966.svg"), W, H, *p,
           title="Літо 1966-го: «розв'яжемо зір за канікули»")


# ── semantic-gap: людина бачить «куб+м'яч», машина — сітку чисел ───────────────
# Ідея: ліворуч сцена (куб, м'яч, стіл), праворуч та сама ділянка як числа;
# між ними «?» — семантична прірва.

def fig_semantic_gap():
    W, H = 960, 470
    p = []

    # ── що бачить людина ──
    p.append(rect(70, 110, 360, 250, fill="#eef2ff", stroke=B_COL, sw=1.8, rx=12))
    p.append(text(250, 134, "що бачить ЛЮДИНА", size=12, color=B_COL, bold=True))
    p.append('<rect x="110" y="278" width="280" height="14" rx="4" fill="#94a3b8"/>')  # стіл
    p.append('<rect x="152" y="230" width="58" height="48" rx="4" fill="#f59e0b" stroke="%s" stroke-width="1.4"/>' % INK)
    p.append('<circle cx="300" cy="254" r="25" fill="#60a5fa" stroke="%s" stroke-width="1.4"/>' % INK)
    p.append(text(181, 316, "куб", size=10, bold=True))
    p.append(text(300, 316, "м'яч", size=10, bold=True))
    p.append(text(250, 342, "«куб і м'яч на столі» — умить, без зусиль", size=9, color=MUTED))

    # ── що дано машині (сітка чисел) ──
    p.append(rect(530, 110, 360, 250, fill=FILL, stroke=ORANGE, sw=1.8, rx=12))
    p.append(text(710, 134, "що дано МАШИНІ", size=12, color="#b06b00", bold=True))
    nums = [
        [137, 140, 139, 141, 138, 142, 140, 138],
        [138, 139, 250, 251, 249, 250, 141, 139],
        [139, 251, 252, 250, 248, 250, 252, 138],
        [140, 250, 249, 251, 250, 249, 251, 141],
        [141, 139, 140, 250, 251, 250, 141, 140],
        [139, 140, 141, 139, 138, 140, 142, 139],
    ]
    col0, row0, dx, dy = 572.5, 167, 33, 33
    for r in range(6):
        for c in range(8):
            v = nums[r][c]
            col = "#b06b00" if v > 200 else "#94a3b8"
            p.append(text(col0 + c * dx, row0 + r * dy, str(v), size=9, color=col))
    p.append(rect(556, 150, 264, 198, fill="none", stroke="#cbd5e1", sw=1, rx=8))
    p.append(text(710, 360, "лише сітка чисел-яскравостей — і ні слова про «куб»", size=9, color=MUTED))

    # ── «?» прірва ──
    p.append(text(480, 248, "?", size=44, color=R_COL, bold=True))
    p.append(text(480, 392, "семантична прірва", size=12, color=R_COL, bold=True))

    p.append(text(480, 440,
                  "Машина не «бачить» куб — вона має лише числа. Перетворити числа на зміст і є вся задача машинного бачення.",
                  size=11, color=MUTED, italic=True))
    p.append(text(480, 456,
                  "Те, що мозок робить непомітно, машині треба збудувати покроково — від пікселя до поняття.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "semantic-gap.svg"), W, H, *p,
           title="Чому здавалося легко: пастка «я ж бачу одразу»")


# ── project-goals: ланцюг кадр → фігура/тло → області → назвати тіла ──────────

def fig_project_goals():
    W, H = 960, 450
    p = []
    by, bw, bh = 150, 190, 150

    def dark_box(x, title, col, sub):
        out = [rect(x, by, bw, bh, fill="#0f172a", stroke=col, sw=2.0, rx=10)]
        out.append(text(x + bw / 2, by + 26, title, size=12, color=col, bold=True))
        for i, ln in enumerate(sub):
            out.append(text(x + bw / 2, by + 110 + i * 15, ln, size=9, color="#e2e8f0"))
        return out

    cx0 = 40
    # 1) кадр — із сирими пікселями
    p += dark_box(cx0, "кадр", B_COL, ["сирий знімок", "з камери", "(vidisector)"])
    gx, gy, gs = 105, 196, 9
    for r in range(4):
        for c in range(6):
            base = 130 + c * 11 + r * 7
            col = (min(base, 255), min(base - 6, 255), min(base - 9, 255))
            p.append('<rect x="%.1f" y="%d" width="%d" height="%d" fill="rgb(%d,%d,%d)"/>'
                     % (gx + c * gs, gy + r * gs, gs, gs, col[0], col[1], col[2]))
    p.append(arrow(230, 225, 260, 225, color=INK, sw=1.8))

    # 2) фігура / тло
    cx1 = 260
    p += dark_box(cx1, "фігура / тло", ORANGE, ["відділити", "об'єкти", "від тла"])
    p.append('<rect x="325" y="196" width="60" height="40" rx="4" fill="#1e293b"/>')
    p.append('<rect x="341" y="204" width="30" height="26" rx="3" fill="none" stroke="%s" '
             'stroke-width="2" stroke-dasharray="3,2"/>' % ORANGE)
    p.append(arrow(450, 225, 480, 225, color=INK, sw=1.8))

    # 3) області
    cx2 = 480
    p += dark_box(cx2, "області", ORANGE, ["об'єкт ·", "тло ·", "хаос"])
    p.append('<rect x="545" y="196" width="60" height="40" rx="4" fill="#334155"/>')
    p.append('<rect x="563" y="202" width="26" height="28" rx="3" fill="#f59e0b" stroke="white" stroke-width="1"/>')
    p.append(arrow(670, 225, 700, 225, color=INK, sw=1.8))

    # 4) назвати
    cx3 = 700
    p += dark_box(cx3, "назвати", G_COL, ["куб, м'яч,", "циліндр", "(прості тіла)"])
    p.append('<rect x="779" y="198" width="32" height="34" rx="4" fill="#f59e0b" stroke="white" stroke-width="1.2"/>')
    p.append(text(795, 220, "✓", size=15, color="white", bold=True))

    # нижня плашка
    ny = 330
    p.append(rect(40, ny, 880, 72, fill="#fff5f5", stroke=R_COL, sw=1.4, rx=10))
    p.append(text(480, ny + 24,
                  "Кожна стрілка тут — окрема велика задача (і кожна стала окремою темою цього розділу).",
                  size=10, bold=True))
    p.append(text(480, ny + 47,
                  "Команда думала пройти весь ланцюг за літо. Перша ж ланка — «де об'єкт, а де тло» — виявилась проваллям.",
                  size=10, color=MUTED))

    render(os.path.join(OUT, "project-goals.svg"), W, H, *p,
           title="Що насправді замовили: від пікселів до названих тіл")


# ── roadmap: дев'ять кроків розділу ───────────────────────────────────────────
# Ідея: змійка з 9 кроків (без номерів) від пікселя до вартості обчислень.

def fig_roadmap():
    W, H = 960, 470
    p = []
    bw, bh = 160, 84

    steps = [
        ("піксель,", "канали", B_COL),
        ("яскравість,", "гістограма", B_COL),
        ("згортки,", "фільтри", ORANGE),
        ("межі:", "Собель/Канні", ORANGE),
        ("пороги,", "морфологія", ORANGE),
        ("об'єкти:", "форма/Хаф", ORANGE),
        ("нейро-", "детектори", G_COL),
        ("трекінг →", "«піксель → кут»", G_COL),
        ("вартість", "обчислень", G_COL),
    ]

    # позиції змійкою: верхній ряд зліва-направо (0..4), потім нижній справа-наліво (5..8)
    top_y, bot_y = 128, 290
    top_xs = [40, 220, 400, 580, 760]              # 5 кроків
    bot_xs = [760, 540, 320, 100]                  # 4 кроки (справа наліво)
    pos = [(x, top_y) for x in top_xs] + [(x, bot_y) for x in bot_xs]

    for i, (l1, l2, col) in enumerate(steps):
        x, y = pos[i]
        p.append(rect(x, y, bw, bh, fill=FILL, stroke=col, sw=1.7, rx=10))
        # лівий кольоровий корінець
        p.append('<rect x="%d" y="%d" width="48" height="%d" rx="10" fill="%s" fill-opacity="0.16"/>'
                 % (x, y, bh, col))
        p.append(text(x + 24, y + 47, "•", size=16, color=col, bold=True))
        p.append(text(x + 58, y + 36, l1, size=9, anchor="start"))
        p.append(text(x + 58, y + 54, l2, size=9, anchor="start"))

    # стрілки вздовж змійки
    # верхній ряд: між сусідами зліва-направо
    for i in range(4):
        x = top_xs[i]
        p.append(arrow(x + bw, top_y + bh / 2, top_xs[i + 1], top_y + bh / 2, color=INK, sw=1.6))
    # вигин: з 5-го (top last) вниз
    p.append(arrow(top_xs[4] + bw / 2, top_y + bh, top_xs[4] + bw / 2, bot_y, color=INK, sw=1.6))
    # нижній ряд: справа наліво
    for i in range(3):
        x = bot_xs[i]
        p.append(arrow(x, bot_y + bh / 2, bot_xs[i + 1] + bw, bot_y + bh / 2, color=INK, sw=1.6))

    # позначка про окрему історію нейромереж біля кроку нейро-детектори (bot_xs[1]=540)
    p.append(text(620, 304, "📜 окрема історія нейромереж", size=9, color=MUTED, anchor="start"))

    # нижня плашка
    ny = 392
    p.append(rect(40, ny, 880, 60, fill="#eef2ff", stroke=B_COL, sw=1.4, rx=10))
    p.append(text(480, ny + 24,
                  "Дев'ять кроків від голих чисел-пікселів до того, щоб «піксель став кутом» і замкнув керування.",
                  size=10, bold=True))
    p.append(text(480, ny + 45,
                  "Те, що 1966-го гадали зробити за літо. Ми пройдемо ці ази по черзі.",
                  size=10, color=MUTED))

    render(os.path.join(OUT, "roadmap.svg"), W, H, *p,
           title="Зір виявився не задачею, а наукою")


# ── packed-vs-planar: YUYV (packed 4:2:2) vs NV12 (planar 4:2:0) ──────────────
# Ідея: як ті самі пікселі лежать у пам'яті двома форматами камери.
# YUYV — один потік, Y/U/Y/V упереміш; NV12 — спершу площина Y, потім площина UV.

def fig_packed_vs_planar():
    W, H = 980, 540
    p = []
    Y_COL = "#334155"
    U_COL = "#1f4ed8"
    V_COL = "#cc0000"

    def byte(x, y, w, h, fill, lab, tcol="white"):
        out = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" '
               'fill="%s" stroke="white" stroke-width="0.8"/>' % (x, y, w, h, fill)]
        out.append(text(x + w / 2, y + h / 2 + 4, lab, size=10, color=tcol, bold=True))
        return "".join(out)

    bw, bh = 44, 34

    # ── YUYV (packed 4:2:2) ──
    p.append(text(70, 80, "YUYV — packed 4:2:2 (один потік)", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(70, 100, "2 пікселі = 4 байти; U/V — одні на пару (по горизонталі)",
                  size=10, color=MUTED, anchor="start"))
    seq = [("Y0", Y_COL), ("U0", U_COL), ("Y1", Y_COL), ("V0", V_COL),
           ("Y2", Y_COL), ("U2", U_COL), ("Y3", Y_COL), ("V2", V_COL)]
    x0, y0 = 70, 116
    for i, (lab, col) in enumerate(seq):
        p.append(byte(x0 + i * bw, y0, bw, bh, col, lab))
    # дужки «піксель 0 = Y0+U0+V0» / «піксель 1 = Y1+U0+V0»
    p.append(line(x0, y0 + bh + 8, x0 + 4 * bw, y0 + bh + 8, color=MUTED, sw=1.2))
    p.append(text(x0 + 2 * bw, y0 + bh + 24, "пікселі 0,1 ділять U0,V0", size=9, color=MUTED))
    p.append(line(x0 + 4 * bw, y0 + bh + 8, x0 + 8 * bw, y0 + bh + 8, color=MUTED, sw=1.2))
    p.append(text(x0 + 6 * bw, y0 + bh + 24, "пікселі 2,3 ділять U2,V2", size=9, color=MUTED))
    p.append(text(70, y0 + bh + 50, "адреса пікселя x:  base + y·stride + (x & ~1)·2   (крок по 4 байти на пару)",
                  size=9, color=INK, anchor="start"))

    # ── NV12 (planar 4:2:0) ──
    ny = 280
    p.append(text(70, ny, "NV12 — planar 4:2:0 (дві площини)", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(70, ny + 20, "спершу вся площина Y (W×H), потім напівплощина UV (W×H/2), U/V чергуються",
                  size=10, color=MUTED, anchor="start"))
    # площина Y — рядок клітинок
    yy = ny + 36
    p.append(text(70, yy - 4, "площина Y (яскравість, повна роздільність)", size=9, color=Y_COL, anchor="start"))
    for i in range(8):
        p.append(byte(70 + i * bw, yy + 4, bw, bh, Y_COL, "Y%d" % i))
    p.append(text(70 + 8 * bw + 14, yy + 4 + bh / 2 + 4, "… W·H байтів", size=9, color=MUTED, anchor="start"))
    # напівплощина UV — чергування
    uy = yy + bh + 26
    p.append(text(70, uy - 4, "напівплощина UV (одна пара на 2×2 блок, чергується)", size=9, color=U_COL, anchor="start"))
    uv = [("U0", U_COL), ("V0", V_COL), ("U1", U_COL), ("V1", V_COL),
          ("U2", U_COL), ("V2", V_COL), ("U3", U_COL), ("V3", V_COL)]
    for i, (lab, col) in enumerate(uv):
        p.append(byte(70 + i * bw, uy + 4, bw, bh, col, lab))
    p.append(text(70 + 8 * bw + 14, uy + 4 + bh / 2 + 4, "… W·H/2 байтів", size=9, color=MUTED, anchor="start"))

    # нижня плашка-висновок
    by = 470
    p.append(rect(70, by, 840, 52, fill=FILL, stroke=INK, sw=1.3, rx=10))
    p.append(text(490, by + 21,
                  "Packed: усе впереміш в одному буфері — зручно копіювати. Planar: Y окремо — зручно "
                  "взяти саму яскравість (сіре) без розбору колірності.",
                  size=10, bold=True))
    p.append(text(490, by + 40,
                  "4:2:2 проріджує колір лише по горизонталі; 4:2:0 — і по горизонталі, і по вертикалі (удвічі менше колірних байтів).",
                  size=9, color=MUTED))

    render(os.path.join(OUT, "packed-vs-planar.svg"), W, H, *p,
           title="Пам'ять буфера камери: YUYV (packed) vs NV12 (planar)")


# ── hsv-hexcone: тон по колу, насиченість по радіусу, яскравість по осі ───────
# Ідея: геометрія HSV — кутова природа H, ахроматична вісь (S=0), обід (S=1),
# граничні точки V=0 (чорне) і V=1.

def fig_hsv_hexcone():
    W, H = 940, 520
    p = []
    cx, cy, R = 300, 250, 150

    # колірне коло (тон по куту, насиченість по радіусу) — кільцями
    rings = 7
    sectors = 60
    import math
    for ri in range(rings):
        r_in = R * ri / rings
        r_out = R * (ri + 1) / rings
        s = (ri + 0.5) / rings           # насиченість росте від центру до обода
        for si in range(sectors):
            a0 = 2 * math.pi * si / sectors
            a1 = 2 * math.pi * (si + 1) / sectors
            hue = si / float(sectors)
            rr, gg, bb = colorsys.hsv_to_rgb(hue, s, 1.0)
            col = (int(rr * 255), int(gg * 255), int(bb * 255))
            x0 = cx + r_in * math.cos(a0); y0 = cy + r_in * math.sin(a0)
            x1 = cx + r_out * math.cos(a0); y1 = cy + r_out * math.sin(a0)
            x2 = cx + r_out * math.cos(a1); y2 = cy + r_out * math.sin(a1)
            x3 = cx + r_in * math.cos(a1); y3 = cy + r_in * math.sin(a1)
            p.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="rgb(%d,%d,%d)"/>'
                     % (x0, y0, x1, y1, x2, y2, x3, y3, col[0], col[1], col[2]))
    p.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="1.4"/>' % (cx, cy, R, INK))

    # центр — ахроматична точка (S=0)
    p.append('<circle cx="%d" cy="%d" r="6" fill="#bfbfbf" stroke="%s" stroke-width="1.2"/>' % (cx, cy, INK))
    p.append(text(cx, cy - 14, "S=0 (сіре)", size=9, color=INK, bold=True))
    p.append(text(cx, cy + 24, "тут тон не визначений", size=9, color=MUTED))

    # кут тону: 0°, та помаранчевий ~32°
    p.append(line(cx, cy, cx + R, cy, color=INK, sw=1.3, dash="3,2"))
    p.append(text(cx + R + 26, cy + 4, "H=0° (червоний)", size=9, color=INK))
    a = math.radians(32)
    p.append(line(cx, cy, cx + R * math.cos(a), cy + R * math.sin(a), color=INK, sw=1.6))
    p.append(text(cx + R * math.cos(a) + 6, cy + R * math.sin(a) + 18, "H≈32° помаранчевий", size=9, color=INK, anchor="start"))
    # дужка-кут
    p.append('<path d="M %.1f %.1f A 40 40 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.2"/>'
             % (cx + 40, cy, cx + 40 * math.cos(a), cy + 40 * math.sin(a), POS))
    p.append(text(cx + 54, cy + 20, "H", size=11, color=POS, bold=True))
    # підпис радіуса = S
    p.append(text(cx + R * 0.5, cy - 8, "S →", size=10, color=INK, bold=True))

    p.append(text(cx, cy + R + 34, "Тон H — це КУТ (0…360°); насиченість S — радіус (0 у центрі → 1 на ободі)",
                  size=10, color=MUTED))

    # ── вісь V збоку (вертикальний стовпчик яскравості) ──
    vx, vtop, vbot = 720, 110, 410
    n = 24
    for i in range(n):
        v = 1.0 - i / float(n)
        g = int(v * 255)
        p.append('<rect x="%d" y="%.1f" width="48" height="%.1f" fill="rgb(%d,%d,%d)"/>'
                 % (vx, vtop + i * (vbot - vtop) / n, (vbot - vtop) / n + 0.6, g, g, g))
    p.append(rect(vx, vtop, 48, vbot - vtop, fill="none", stroke=INK, sw=1.3, rx=2))
    p.append(text(vx + 24, vtop - 12, "вісь V", size=11, color=INK, bold=True))
    p.append(text(vx + 64, vtop + 6, "V=1 (повна яскравість)", size=9, color=INK, anchor="start"))
    p.append(text(vx + 64, vbot - 2, "V=0 (чорне — тон і S не важать)", size=9, color=INK, anchor="start"))
    p.append(text(vx + 24, vbot + 22, "яскравість", size=9, color=MUTED))

    # нижня плашка
    by = 446
    p.append(rect(60, by, 820, 60, fill="#eef2ff", stroke=B_COL, sw=1.4, rx=11))
    p.append(text(470, by + 22, "Геометрія HSV: тон — кут, насиченість — радіус, яскравість — окрема вісь",
                  size=11, color=B_COL, bold=True))
    p.append(text(470, by + 44,
                  "Граничні точки: на осі (S=0) тон не визначений; на дні (V=0) і тон, і S не мають значення — це просто чорне.",
                  size=10, color=MUTED))

    render(os.path.join(OUT, "hsv-hexcone.svg"), W, H, *p,
           title="Колірне коло HSV: тон — кут, насиченість — радіус, яскравість — вісь")


# ── stride-align: чому рядок доповнюють і де ховається перекіс ────────────────
# Ідея: width*bpp < stride; «хвіст» padding; неврахований крок → зсув щорядка → перекіс.

def fig_stride_align():
    W, H = 960, 470
    p = []
    Y_COL = "#334155"
    PAD = "#fca5a5"

    # ── правильно: адресуємо через stride ──
    p.append(text(70, 84, "Рядок у пам'яті: корисні байти + доповнення до вирівнювання",
                  size=12, color=INK, bold=True, anchor="start"))
    rows = 4
    cellw, cellh = 30, 26
    usefuln = 18          # width*bpp
    padn = 6              # доповнення
    x0, y0 = 70, 104
    for r in range(rows):
        ry = y0 + r * (cellh + 8)
        for c in range(usefuln):
            g = 120 + ((c * 7 + r * 13) % 90)
            p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="rgb(%d,%d,%d)" '
                     'stroke="white" stroke-width="0.5"/>' % (x0 + c * cellw, ry, cellw, cellh, g, g, g))
        for c in range(padn):
            p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
                     'stroke="white" stroke-width="0.5"/>' % (x0 + (usefuln + c) * cellw, ry, cellw, cellh, PAD))
    # підписи дужок
    p.append(line(x0, y0 - 8, x0 + usefuln * cellw, y0 - 8, color=Y_COL, sw=1.4))
    p.append(text(x0 + usefuln * cellw / 2, y0 - 14, "width · bpp (корисні)", size=9, color=Y_COL))
    p.append(line(x0 + usefuln * cellw, y0 - 8, x0 + (usefuln + padn) * cellw, y0 - 8, color=POS, sw=1.4))
    p.append(text(x0 + (usefuln + padn / 2) * cellw, y0 - 14, "padding", size=9, color=POS))
    fullw = (usefuln + padn) * cellw
    p.append(line(x0, y0 + rows * (cellh + 8) + 4, x0 + fullw, y0 + rows * (cellh + 8) + 4, color=INK, sw=1.4))
    p.append(text(x0 + fullw / 2, y0 + rows * (cellh + 8) + 20, "stride (повний крок рядка, кратний N байтам)",
                  size=10, color=INK, bold=True))

    # ── формула вирівнювання ──
    fy = 330
    p.append(rect(70, fy, 400, 110, fill=FILL, stroke=INK, sw=1.3, rx=10))
    p.append(text(270, fy + 24, "Як порахувати крок", size=11, color=INK, bold=True))
    p.append(text(90, fy + 50, "stride = align_up(width · bpp, N)", size=11, color=INK, anchor="start"))
    p.append(text(90, fy + 74, "align_up(v,N) = (v + N−1) & ~(N−1)", size=10, color=MUTED, anchor="start"))
    p.append(text(90, fy + 94, "N: 4 (типово), 16 (NEON/SIMD), 32/64 (DMA-burst)", size=9, color=MUTED, anchor="start"))

    # ── помилка: узяв width замість stride → перекіс ──
    p.append(text(700, fy - 6, "Узяв width замість stride →", size=11, color=POS, bold=True))
    p.append(text(700, fy + 12, "щорядка зсув на padding → перекіс", size=10, color=POS))
    sx, sy = 560, fy + 24
    for r in range(6):
        shift = r * 10            # накопичений зсув
        for c in range(14):
            g = 90 + ((c + r) % 2) * 110
            p.append('<rect x="%.1f" y="%.1f" width="14" height="12" fill="rgb(%d,%d,%d)"/>'
                     % (sx + c * 14 + shift, sy + r * 14, g, g, g))
    p.append(text(700, sy + 6 * 14 + 18, "«діагональні смуги» — класичний підпис сплутаного кроку",
                  size=9, color=MUTED))

    render(os.path.join(OUT, "stride-align.svg"), W, H, *p,
           title="Stride і вирівнювання: чому рядок доповнюють і звідки перекіс")


if __name__ == "__main__":
    fig_image_as_grid()
    fig_channels()
    fig_color_spaces()
    fig_hsv_for_vision()
    fig_summer_1966()
    fig_semantic_gap()
    fig_project_goals()
    fig_roadmap()
    fig_packed_vs_planar()
    fig_hsv_hexcone()
    fig_stride_align()
    print("OK: figures written to", OUT)
