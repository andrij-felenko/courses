# -*- coding: utf-8 -*-
import sys, os

# Шлях до scripts/ у корені репозиторію (4 рівні вгору від root/course/embedded/tseremoniia-kliuchiv/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: Ізольоване середовище Air-Gap для церемонії ключів ─────────────
def fig_air_gap_environment():
    W, H = 840, 430
    frags = []
    
    # Заголовок
    frags.append(text(W / 2, 28, "Фізичний та мережевий контур ізоляції церемонії (Air-Gap)", size=16, bold=True))
    
    # Зовнішня зона (ненадійний світ)
    ox, oy, ow, oh = 30, 60, 220, 340
    frags.append(rect(ox, oy, ow, oh, fill="#fdf4f4", stroke=POS, sw=1.8, rx=8))
    frags.append(text(ox + ow / 2, oy + 26, "ЗОВНІШНІЙ СВІТ", size=13, color=POS, bold=True))
    frags.append(text(ox + ow / 2, oy + 44, "ненадійна мережа", size=11, color=MUTED))
    
    # Пункти зовнішнього світу
    items_out = [
        "Корпоративна мережа / Wi-Fi",
        "Інтернет та хмарні сервери",
        "Мобільний зв'язок / Bluetooth",
        "Неперевірені USB-носії"
    ]
    for i, it in enumerate(items_out):
        iy = oy + 76 + i * 58
        frags.append(rect(ox + 12, iy, ow - 24, 46, fill="#ffffff", stroke="#e0b4b4", sw=1.2, rx=5))
        frags.append(text(ox + ow / 2, iy + 28, it, size=11, color=INK))

    # Бар'єр повітряного зазору (Air-Gap Barrier)
    bx, by, bw, bh = 270, 60, 50, 340
    frags.append(rect(bx, by, bw, bh, fill="#fff8e6", stroke="#d4a373", sw=2, rx=6))
    frags.append(text(bx + bw / 2, by + 110, "A", size=15, color="#8c5820", bold=True))
    frags.append(text(bx + bw / 2, by + 130, "I", size=15, color="#8c5820", bold=True))
    frags.append(text(bx + bw / 2, by + 150, "R", size=15, color="#8c5820", bold=True))
    frags.append(text(bx + bw / 2, by + 175, "—", size=14, color="#8c5820", bold=True))
    frags.append(text(bx + bw / 2, by + 200, "G", size=15, color="#8c5820", bold=True))
    frags.append(text(bx + bw / 2, by + 220, "A", size=15, color="#8c5820", bold=True))
    frags.append(text(bx + bw / 2, by + 240, "P", size=15, color="#8c5820", bold=True))
    frags.append(text(bx + bw / 2, by + 280, "зазор", size=11, color="#8c5820"))

    # Червоний хрест блокування передачі через бар'єр
    frags.append(line(bx - 14, by + 170, bx + bw + 14, by + 170, color=POS, sw=3))
    frags.append(text(bx + bw / 2, by + 40, "ЖОДНИХ", size=11, color=POS, bold=True))
    frags.append(text(bx + bw / 2, by + 56, "кабелів", size=10, color=POS))

    # Захищена кімната церемонії (Чиста зона)
    ix, iy, iw, ih = 340, 60, 470, 340
    frags.append(rect(ix, iy, iw, ih, fill="#f2f9f4", stroke=FIELD, sw=2, rx=8))
    frags.append(text(ix + iw / 2, iy + 26, "ЗАХИЩЕНА КІМНАТА ЦЕРЕМОНІЇ (OFFLINE AIR-GAP)", size=13, color=FIELD, bold=True))
    
    # Ноутбук церемонії
    nx, ny, nw, nh = ix + 24, iy + 52, 230, 126
    frags.append(rect(nx, ny, nw, nh, fill="#ffffff", stroke=INK, sw=1.6, rx=6))
    frags.append(text(nx + nw / 2, ny + 24, "Чистий офлайн-хост", size=12, bold=True, color=INK))
    frags.append(text(nx + nw / 2, ny + 44, "• Live OS (DVD-R / захищений USB)", size=11, color=MUTED))
    frags.append(text(nx + nw / 2, ny + 64, "• Wi-Fi / Bluetooth фізично відімкнені", size=11, color=MUTED))
    frags.append(text(nx + nw / 2, ny + 84, "• Живлення від автономного акумулятора", size=11, color=MUTED))
    frags.append(text(nx + nw / 2, ny + 104, "• ОЗП затирається після вимкнення", size=11, color=MUTED))

    # Апаратний модуль безпеки (HSM / Смарт-карти)
    hx, hy, hw, hh = ix + 274, iy + 52, 172, 126
    frags.append(rect(hx, hy, hw, hh, fill="#fdfbf7", stroke="#c28e00", sw=1.6, rx=6))
    frags.append(text(hx + hw / 2, hy + 24, "Апаратний HSM / Токен", size=12, bold=True, color="#8c5820"))
    frags.append(text(hx + hw / 2, hy + 48, "• Апаратний TRNG", size=11, color=INK))
    frags.append(text(hx + hw / 2, hy + 70, "• Генерація ключа в чипі", size=11, color=INK))
    frags.append(text(hx + hw / 2, hy + 92, "• Захист від зчитування", size=11, color=INK))
    frags.append(text(hx + hw / 2, hy + 112, "• FIPS 140-3 Level 3/4", size=11, color=MUTED))

    # Стрілка зв'язку між ноутбуком і HSM
    frags.append(arrow(nx + nw + 2, ny + nh / 2, hx - 4, ny + nh / 2, color=INK, sw=1.8))
    frags.append(text(nx + nw + 22, ny + nh / 2 - 10, "USB", size=10, color=MUTED))

    # Нижня частина чистої зони: Фізичний аудит і свідки
    ax, ay, aw, ah = ix + 24, iy + 196, 422, 124
    frags.append(rect(ax, ay, aw, ah, fill="#ffffff", stroke=NEG, sw=1.4, rx=6))
    frags.append(text(ax + aw / 2, ay + 24, "Процедурний контроль і фіксація", size=12, bold=True, color=NEG))
    
    # 3 блоки підтвердження
    bw3 = 126
    # 1. Відеозапис
    frags.append(rect(ax + 10, ay + 38, bw3, 72, fill="#f4f6fc", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(ax + 10 + bw3 / 2, ay + 60, "Відеокамера", size=11, bold=True, color=INK))
    frags.append(text(ax + 10 + bw3 / 2, ay + 80, "Постійний запис", size=10, color=MUTED))
    frags.append(text(ax + 10 + bw3 / 2, ay + 96, "без сліпих зон", size=10, color=MUTED))
    
    # 2. Паперовий чекліст
    frags.append(rect(ax + 148, ay + 38, bw3, 72, fill="#f4f6fc", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(ax + 148 + bw3 / 2, ay + 60, "Паперовий акт", size=11, bold=True, color=INK))
    frags.append(text(ax + 148 + bw3 / 2, ay + 80, "Покроковий сценарій", size=10, color=MUTED))
    frags.append(text(ax + 148 + bw3 / 2, ay + 96, "підписи свідків", size=10, color=MUTED))

    # 3. Сейф-пакети
    frags.append(rect(ax + 286, ay + 38, bw3, 72, fill="#f4f6fc", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(ax + 286 + bw3 / 2, ay + 60, "Сейф-пакети", size=11, bold=True, color=INK))
    frags.append(text(ax + 286 + bw3 / 2, ay + 80, "Номерні пломби", size=10, color=MUTED))
    frags.append(text(ax + 286 + bw3 / 2, ay + 96, "індикатори зламу", size=10, color=MUTED))

    render(os.path.join(OUT, 'air-gap-environment.svg'), W, H, *frags)


# ── Фігура 2: Принцип подвійного контролю та розподіл ролей ───────────────────
def fig_roles_and_dual_control():
    W, H = 820, 390
    frags = []
    
    frags.append(text(W / 2, 28, "Принцип розподілу обов'язків та подвійного контролю (Dual Control)", size=16, bold=True))

    # 3 ролі
    roles = [
        ("Церемоніймейстер", "Master of Ceremonies", "Керує процесом виключно за друкованим сценарієм; не має доступу до часток секрету", POS),
        ("Володарі часток", "Crypto Officers (3–5 осіб)", "Кожен володіє унікальною смарт-картою або PIN-кодом; не можуть діяти поодинці", NEG),
        ("Незалежні свідки / Аудитор", "Auditor / Independent Witnesses", "Звіряють контрольні суми на екрані, перевіряють цілісність пломб, підписують протокол", FIELD)
    ]
    
    rw = 236
    rx0 = 36
    for i, (title, eng, desc, col) in enumerate(roles):
        rx = rx0 + i * (rw + 24)
        ry = 64
        frags.append(rect(rx, ry, rw, 160, fill="#ffffff", stroke=col, sw=1.8, rx=6))
        frags.append(text(rx + rw / 2, ry + 26, title, size=13, color=col, bold=True))
        frags.append(text(rx + rw / 2, ry + 44, eng, size=10, color=MUTED, italic=True))
        frags.append(line(rx + 14, ry + 56, rx + rw - 14, ry + 56, color="#e2e8f0", sw=1))
        
        # Опис у кілька рядків
        lines = [desc[:38], desc[38:78], desc[78:]]
        lines = [l.strip() for l in lines if l.strip()]
        for li, l in enumerate(lines):
            frags.append(text(rx + rw / 2, ry + 78 + li * 20, l, size=11, color=INK))

    # Центральна дія: Консенсус і розблокування кореня
    cx, cy, cw, ch = 130, 260, 560, 100
    frags.append(rect(cx, cy, cw, ch, fill="#f8fafc", stroke=INK, sw=2, rx=8))
    frags.append(text(cx + cw / 2, cy + 28, "Правило двох осіб (Two-Person Rule / Split Knowledge)", size=14, bold=True, color=INK))
    frags.append(text(cx + cw / 2, cy + 52, "Жодна людина самостійно не здатна згенерувати, експортувати або відновити кореневий ключ", size=11, color=POS))
    frags.append(text(cx + cw / 2, cy + 76, "Будь-яка дія над секретом вимагає фізичної присутності та кворуму k із n учасників", size=11, color=MUTED))

    # Стрілки від трьох ролей до консенсусу
    for i, (_, _, _, col) in enumerate(roles):
        src_x = rx0 + i * (rw + 24) + rw / 2
        frags.append(arrow(src_x, 226, src_x, 256, color=col, sw=1.6))

    render(os.path.join(OUT, 'roles-and-dual-control.svg'), W, H, *frags)


# ── Фігура 3: Ієрархія ключів та холодний сейф ───────────────────────────────
def fig_key_hierarchy_and_cold_storage():
    W, H = 840, 420
    frags = []
    
    frags.append(text(W / 2, 28, "Ієрархія довіри: від холодного кореня до заводської прошивки", size=16, bold=True))

    # Рівень 1: Кореневий ключ (Root CA)
    k1_x, k1_y, k1_w, k1_h = 40, 64, 760, 100
    frags.append(rect(k1_x, k1_y, k1_w, k1_h, fill="#fffaf5", stroke=POS, sw=2, rx=8))
    frags.append(text(k1_x + 18, k1_y + 26, "КОРЕНЕВИЙ КЛЮЧ ВИРОБУ (ROOT CA / ROOT OF TRUST)", size=13, bold=True, color=POS, anchor="start"))
    frags.append(text(k1_x + 18, k1_y + 48, "• Термін життя: 10–25 років (на весь життєвий цикл лінійки виробів)", size=11, color=INK, anchor="start"))
    frags.append(text(k1_x + 18, k1_y + 68, "• Зберігання: офлайн у холодному банківському сейфі, розділений на частки", size=11, color=INK, anchor="start"))
    frags.append(text(k1_x + 18, k1_y + 88, "• Призначення: підписує ЛИШЕ проміжні сертифікати випуску раз на 1–2 роки", size=11, color=POS, anchor="start"))

    # Стрілка підпису 1 -> 2
    frags.append(arrow(W / 2, k1_y + k1_h + 2, W / 2, k1_y + k1_h + 38, color=POS, sw=2))
    frags.append(text(W / 2 + 120, k1_y + k1_h + 22, "Підпис сертифіката випуску під час церемонії", size=10, color=POS, bold=True))

    # Рівень 2: Проміжний ключ підпису релізів (Intermediate Release CA)
    k2_x, k2_y, k2_w, k2_h = 40, 204, 760, 94
    frags.append(rect(k2_x, k2_y, k2_w, k2_h, fill="#f4f8fd", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(k2_x + 18, k2_y + 24, "ПРОМІЖНИЙ КЛЮЧ ПІДПИСУ РЕЛІЗІВ (INTERMEDIATE / RELEASE SIGNING KEY)", size=13, bold=True, color=NEG, anchor="start"))
    frags.append(text(k2_x + 18, k2_y + 46, "• Термін життя: 1–2 роки (регулярна ротація без зміни кремнієвого кореня)", size=11, color=INK, anchor="start"))
    frags.append(text(k2_x + 18, k2_y + 66, "• Зберігання: мережевий HSM сервера релізів або складального цеху", size=11, color=INK, anchor="start"))
    frags.append(text(k2_x + 18, k2_y + 84, "• Призначення: підписує образи прошивок, маніфести та оновлення OTA", size=11, color=INK, anchor="start"))

    # Стрілка підпису 2 -> 3
    frags.append(arrow(W / 2, k2_y + k2_h + 2, W / 2, k2_y + k2_h + 36, color=NEG, sw=2))
    frags.append(text(W / 2 + 100, k2_y + k2_h + 20, "Підпис образу прошивки (.bin + signature)", size=10, color=NEG, bold=True))

    # Рівень 3: Цільовий мікроконтролер у полі (Target Device)
    k3_x, k3_y, k3_w, k3_h = 40, 336, 760, 68
    frags.append(rect(k3_x, k3_y, k3_w, k3_h, fill="#f2f9f4", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(k3_x + 18, k3_y + 24, "МІКРОКОНТРОЛЕР У ПОЛІ (SECURE BOOT eFUSE / ROM)", size=13, bold=True, color=FIELD, anchor="start"))
    frags.append(text(k3_x + 18, k3_y + 48, "У кремній (eFuse) прошито лише SHA-256 хеш ВІДКРИТОГО кореневого ключа; завантажувач перевіряє весь ланцюг", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, 'key-hierarchy-and-cold-storage.svg'), W, H, *frags)


# ── Фігура 4: Схема розділення секрету Шаміра (k з n) ─────────────────────────
def fig_shamir_secret_sharing_k_of_n():
    W, H = 820, 380
    frags = []
    
    frags.append(text(W / 2, 28, "Розподіл секрету Шаміра: схема порогу (3 з 5)", size=16, bold=True))

    # Секрет на вході
    sx, sy, sw_, sh = 40, 150, 180, 80
    frags.append(rect(sx, sy, sw_, sh, fill="#fff5f5", stroke=POS, sw=2, rx=6))
    frags.append(text(sx + sw_ / 2, sy + 28, "КОРЕНЕВИЙ СЕКРЕТ S", size=12, bold=True, color=POS))
    frags.append(text(sx + sw_ / 2, sy + 50, "P(0) = S", size=13, color=INK))
    frags.append(text(sx + sw_ / 2, sy + 68, "вільний член полінома", size=10, color=MUTED))

    # Поліном
    px, py, pw, ph = 260, 140, 240, 100
    frags.append(rect(px, py, pw, ph, fill="#fdfbf7", stroke="#d4a373", sw=1.6, rx=6))
    frags.append(text(px + pw / 2, py + 26, "Поліном степеня k − 1 = 2", size=12, bold=True, color="#8c5820"))
    frags.append(text(px + pw / 2, py + 52, "P(x) = S + a₁·x + a₂·x²  (mod p)", size=12, bold=True, color=INK))
    frags.append(text(px + pw / 2, py + 78, "a₁, a₂ — випадкові коефіцієнти", size=11, color=MUTED))

    # Стрілка від секрету до полінома
    frags.append(arrow(sx + sw_ + 2, sy + sh / 2, px - 4, sy + sh / 2, color=POS, sw=2))

    # 5 часток праворуч
    shares_x = 540
    shares = [
        ("Частка 1: (1, P(1))", "Банківський сейф А"),
        ("Частка 2: (2, P(2))", "Технічний директор (CTO)"),
        ("Частка 3: (3, P(3))", "Керівник безпеки (CISO)"),
        ("Частка 4: (4, P(4))", "Банківський сейф Б"),
        ("Частка 5: (5, P(5))", "Зовнішній аудитор")
    ]
    
    for i, (share_title, owner) in enumerate(shares):
        sy_i = 54 + i * 62
        # Забарвлюємо перші 3 як кворум
        is_quorum = i < 3
        col = FIELD if is_quorum else MUTED
        fill_col = "#f2f9f4" if is_quorum else "#f8fafc"
        
        frags.append(rect(shares_x, sy_i, 240, 52, fill=fill_col, stroke=col, sw=1.4, rx=5))
        frags.append(text(shares_x + 12, sy_i + 22, share_title, size=11, bold=True, color=col, anchor="start"))
        frags.append(text(shares_x + 12, sy_i + 40, owner, size=10, color=MUTED, anchor="start"))
        
        # Стрілки від полінома до часток
        frags.append(arrow(px + pw + 2, py + ph / 2, shares_x - 4, sy_i + 26, color=col, sw=1.2))

    # Рамка підсумку внизу
    fx, fy, fw, fh = 40, 276, 460, 76
    frags.append(rect(fx, fy, fw, fh, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(fx + fw / 2, fy + 24, "Властивість порогу безпеки:", size=12, bold=True, color=FIELD))
    frags.append(text(fx + fw / 2, fy + 44, "• Будь-які 3 частки однозначно відновлюють параболу і секрет S = P(0)", size=11, color=INK))
    frags.append(text(fx + fw / 2, fy + 62, "• Будь-які 2 частки дають рівно нуль інформації про значення S", size=11, color=POS))

    render(os.path.join(OUT, 'shamir-secret-sharing-k-of-n.svg'), W, H, *frags)


# ── Фігура 5: Інтерполяція полінома Шаміра над скінченним полем ───────────────
def fig_polynomial_interpolation():
    W, H = 780, 390
    frags = []
    
    frags.append(text(W / 2, 28, "Геометрична інтуїція схеми Шаміра: парабола крізь 3 точки", size=16, bold=True))

    # Координатна сітка
    gx0, gy0, gw, gh = 80, 70, 340, 260
    frags.append(rect(gx0, gy0, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    
    # Осі
    frags.append(arrow(gx0 + 20, gy0 + gh - 20, gx0 + gw - 10, gy0 + gh - 20, color=INK, sw=1.5)) # Вісь X
    frags.append(text(gx0 + gw - 18, gy0 + gh - 6, "x", size=13, bold=True))
    frags.append(arrow(gx0 + 30, gy0 + gh - 10, gx0 + 30, gy0 + 15, color=INK, sw=1.5)) # Вісь Y
    frags.append(text(gx0 + 16, gy0 + 24, "y", size=13, bold=True))

    # Секрет на осі Y (x=0, y=S)
    sy_pos = gy0 + 150
    frags.append(circle(gx0 + 30, sy_pos, 5, fill=POS, stroke=POS, sw=2))
    frags.append(text(gx0 + 44, sy_pos + 4, "S = P(0)", size=12, bold=True, color=POS, anchor="start"))

    # Крива полінома (істинна парабола)
    curve_path = "M %d %d Q %d %d, %d %d" % (gx0 + 30, sy_pos, gx0 + 140, gy0 + 240, gx0 + 310, gy0 + 40)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (curve_path, FIELD))

    # 3 точки часток на параболі
    pt1 = (gx0 + 110, gy0 + 192)
    pt2 = (gx0 + 200, gy0 + 162)
    pt3 = (gx0 + 280, gy0 + 82)
    
    for idx, (px, py) in enumerate([pt1, pt2, pt3]):
        frags.append(circle(px, py, 4.5, fill=NEG, stroke=NEG, sw=2))
        frags.append(text(px, py - 12, "(%d, y%d)" % (idx+1, idx+1), size=11, bold=True, color=NEG))
        frags.append(line(px, py, px, gy0 + gh - 20, color="#cbd5e1", sw=1, dash="3,3"))

    # Пояснення праворуч
    ex, ey, ew, eh = 450, 70, 290, 260
    frags.append(rect(ex, ey, ew, eh, fill="#f8fafc", stroke=INK, sw=1.4, rx=6))
    frags.append(text(ex + ew / 2, ey + 26, "Чому k точок необхідні й достатні", size=12, bold=True, color=INK))
    
    expl_lines = [
        ("Ступінь полінома d = k − 1 = 2", INK, True),
        ("Для однозначного відновлення", MUTED, False),
        ("параболи необхідно рівно 3 точки.", MUTED, False),
        ("Маючи 3 точки: інтерполяційний", FIELD, True),
        ("поліном Лагранжа дає точний S.", FIELD, False),
        ("Маючи лише 2 точки: крізь них", POS, True),
        ("проходить нескінченна кількість", POS, False),
        ("парабол із БУДЬ-ЯКИМ значенням S.", POS, False),
        ("Інформаційна ентропія = 0 біт.", POS, True)
    ]
    for i, (l_txt, l_col, l_bold) in enumerate(expl_lines):
        frags.append(text(ex + 16, ey + 56 + i * 21, l_txt, size=11, color=l_col, bold=l_bold, anchor="start"))

    render(os.path.join(OUT, 'polynomial-interpolation.svg'), W, H, *frags)


# ── Фігура 6: Послідовність генерації та перевірки артефактів ─────────────────
def fig_ceremony_transcript_flow():
    W, H = 840, 400
    frags = []
    
    frags.append(text(W / 2, 26, "Послідовність виконання операцій церемонії ключів", size=16, bold=True))

    steps = [
        ("1. Завантаження", "Live OS з DVD-R, перевірка хешу середовища"),
        ("2. Ініціалізація", "Апаратний TRNG HSM, збір ентропії"),
        ("3. Генерація пари", "Створення Root CA (приватний + відкритий)"),
        ("4. Розщеплення", "Shamir Secret Sharing на n сейф-пакетів"),
        ("5. Підпис релізу", "Створення сертифіката Intermediate CA"),
        ("6. Фіксація хешів", "Свідки звіряють SHA-256 та підписують акт")
    ]
    
    sw_box = 230
    sh_box = 72
    
    # 2 ряди по 3 кроки
    coords = [
        (40, 60), (305, 60), (570, 60),
        (570, 180), (305, 180), (40, 180)
    ]
    
    for i, ((title, sub), (cx, cy)) in enumerate(zip(steps, coords)):
        col = POS if i in [2, 3] else (FIELD if i == 5 else NEG)
        frags.append(rect(cx, cy, sw_box, sh_box, fill="#ffffff", stroke=col, sw=1.6, rx=6))
        frags.append(text(cx + sw_box / 2, cy + 26, title, size=12, bold=True, color=col))
        frags.append(text(cx + sw_box / 2, cy + 48, sub, size=10, color=MUTED))
        
    # Стрілки переходу
    # Ряд 1: 0 -> 1 -> 2
    frags.append(arrow(272, 96, 303, 96, color=INK, sw=1.5))
    frags.append(arrow(537, 96, 568, 96, color=INK, sw=1.5))
    # Вниз: 2 -> 3
    frags.append(arrow(685, 134, 685, 178, color=INK, sw=1.5))
    # Ряд 2 (назад): 3 -> 4 -> 5
    frags.append(arrow(568, 216, 537, 216, color=INK, sw=1.5))
    frags.append(arrow(303, 216, 272, 216, color=INK, sw=1.5))

    # Нижня частина: Артефакти церемонії
    ay = 280
    frags.append(rect(40, ay, 760, 94, fill="#f8fafc", stroke=INK, sw=1.4, rx=6))
    frags.append(text(40 + 760 / 2, ay + 24, "Вихідні артефакти церемонії (Artifacts Transcript)", size=12, bold=True, color=INK))
    
    arts = [
        ("Відкритий Root CA", "Публікується у репозиторій та зашивається в eFuse"),
        ("Сейф-пакети часток", "Запечатуються у сховища під підпис"),
        ("Підписаний протокол", "Паперовий журнал із контрольною сумою SHA-256")
    ]
    for j, (art_name, art_desc) in enumerate(arts):
        ax_j = 56 + j * 248
        frags.append(rect(ax_j, ay + 36, 236, 46, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
        frags.append(text(ax_j + 118, ay + 54, art_name, size=11, bold=True, color=INK))
        frags.append(text(ax_j + 118, ay + 72, art_desc, size=9.5, color=MUTED))

    render(os.path.join(OUT, 'ceremony-transcript-flow.svg'), W, H, *frags)


# ── Фігура 7: Еволюція церемоній ключів ───────────────────────────────────────
def fig_dnssec_ceremony_timeline():
    W, H = 820, 360
    frags = []
    
    frags.append(text(W / 2, 28, "Еволюція церемоній ключів та операційної безпеки", size=16, bold=True))

    # Горизонтальна лінія часу
    frags.append(line(60, 160, 760, 160, color="#94a3b8", sw=2.5))

    events = [
        (120, "1960-ті", "Ядерні коди PAL", "Правило двох осіб у військових системах", POS, -80),
        (300, "1979", "Схема Шаміра", "Математичний поділ секрету k з n", "#b07a35", 40),
        (500, "2010", "DNSSEC Root KSK", "Публічна церемонія ICANN у сховищі", NEG, -80),
        (680, "Сьогодення", "Embedded Root CA", "Secure Boot, eFuse та захист IoT-парків", FIELD, 40)
    ]

    for cx, year, title, desc, col, offset_y in events:
        frags.append(circle(cx, 160, 6, fill=col, stroke="#ffffff", sw=2))
        
        box_y = 160 + offset_y
        box_h = 58
        target_y = (box_y + box_h) if offset_y < 0 else box_y
        frags.append(line(cx, 160, cx, target_y, color=col, sw=1.2, dash="2,2"))
        
        frags.append(rect(cx - 85, box_y, 170, box_h, fill="#ffffff", stroke=col, sw=1.4, rx=5))
        frags.append(text(cx, box_y + 18, year + " — " + title, size=11, bold=True, color=col))
        frags.append(text(cx, box_y + 36, desc[:24], size=9.5, color=MUTED))
        frags.append(text(cx, box_y + 50, desc[24:], size=9.5, color=MUTED))

    render(os.path.join(OUT, 'dnssec-ceremony-timeline.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_air_gap_environment()
    fig_roles_and_dual_control()
    fig_key_hierarchy_and_cold_storage()
    fig_shamir_secret_sharing_k_of_n()
    fig_polynomial_interpolation()
    fig_ceremony_transcript_flow()
    fig_dnssec_ceremony_timeline()
    print("All figures generated successfully into img/")
