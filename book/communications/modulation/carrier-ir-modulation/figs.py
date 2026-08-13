# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальна палітра за змістом
MSG  = FIELD        # корисне повідомлення / огинаюча (зелений)
CAR  = NEG          # несуча 38 кГц / радіо-сигнал (синій)
HOT  = POS          # оптичний шум / завади (червоний)
LO   = MUTED        # допоміжні лінії та підписи
FILL_BG = "#f8f9fa"

def path(pts, color, sw=2.0, fill="none", dash=None):
    d = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, color, sw, da)

def samp(x0, x1, n=300):
    return [x0 + (x1 - x0) * i / (n - 1) for i in range(n)]

# ── Фігура 1: Фоновий оптичний шум проти модульованого ІЧ-сигналу ─────────────
def fig_bg_light_vs_modulated():
    W, H = 760, 420
    x0, x1 = 75, 705
    p = []

    # Верхня панель: Прямі імпульси без несучої (Baseband IR) у сонячному світлі
    cy1 = 110
    p.append(line(x0, cy1, x1, cy1, color=MUTED, sw=1.0, dash="3 3"))
    p.append(text(x0 - 8, cy1 + 4, "Світло", size=12, color=HOT, bold=True, anchor="end"))
    p.append(text(x0, 36, "Прямий ІЧ-імпульс без несучої: тоне у сонячному світлі та 100 Гц пульсаціях", size=12.5, color=HOT, bold=True, anchor="start"))

    # Постійне сонце + 100 Гц пульсації + корисний прямий імпульс
    pts1 = []
    xs = samp(x0, x1, 400)
    for x in xs:
        t = (x - x0) / (x1 - x0)
        sun_dc = 35                                   # сонячне DC засвічування
        flicker = 12 * math.sin(2 * math.pi * 3 * t)  # 100 Гц мережевий шум
        pulse = 18 if (0.35 <= t <= 0.45 or 0.65 <= t <= 0.75) else 0 # корисний імпульс
        y = cy1 - (sun_dc + flicker + pulse)
        pts1.append((x, y))
    
    p.append(path(pts1, HOT, sw=1.8))
    p.append(text(x1 - 10, cy1 - 50, "DC-зсув від сонця + 100 Гц лампи", size=11, color=HOT, bold=True, anchor="end"))
    p.append(text(x0 + 270, cy1 + 32, "імпульс тоне в шумі", size=11, color=MUTED, bold=True))

    # Нижня панель: Модульована несуча 38 кГц + Смуговий фільтр
    cy2 = 300
    p.append(line(x0, cy2, x1, cy2, color=MUTED, sw=1.0, dash="3 3"))
    p.append(text(x0 - 8, cy2 + 4, "38 кГц", size=12, color=CAR, bold=True, anchor="end"))
    p.append(text(x0, 216, "Модульована несуча 38 кГц: смуговий фільтр повністю зрізає DC і 100 Гц завади", size=12.5, color=MSG, bold=True, anchor="start"))

    pts2_in = []
    pts2_out = []
    for x in xs:
        t = (x - x0) / (x1 - x0)
        sun_dc = 30
        flicker = 10 * math.sin(2 * math.pi * 3 * t)
        is_burst = (0.35 <= t <= 0.45 or 0.65 <= t <= 0.75)
        carrier = 25 * math.sin(2 * math.pi * 45 * t) if is_burst else 0
        
        # Сигнал на діоді (з шумом)
        y_in = cy2 - (sun_dc + flicker + carrier)
        pts2_in.append((x, y_in))
        
        # Сигнал після смугового фільтра 38 кГц (DC і flicker зрізано)
        y_out = cy2 - carrier
        pts2_out.append((x, y_out))

    p.append(path(pts2_in, MUTED, sw=1.1, dash="2 2"))
    p.append(path(pts2_out, CAR, sw=1.8))

    # Виділення огинаючої на виході приймача (Active LOW envelope)
    env_pts = []
    for x in xs:
        t = (x - x0) / (x1 - x0)
        is_burst = (0.35 <= t <= 0.45 or 0.65 <= t <= 0.75)
        env_val = -35 if is_burst else +35
        env_pts.append((x, cy2 + 55 + env_val))
    
    p.append(line(x0, cy2 + 55, x1, cy2 + 55, color=MUTED, sw=1.0, dash="3 3"))
    p.append(path(env_pts, MSG, sw=2.2))
    p.append(text(x0 - 8, cy2 + 59, "Вихід", size=11.5, color=MSG, bold=True, anchor="end"))
    p.append(text(x1 - 10, cy2 + 32, "активний LOW логічний вихід", size=11, color=MSG, bold=True, anchor="end"))

    b, bw, bh = textbox(W / 2, 400, "Смуговий фільтр виділяє вузьку смугу 38 кГц, а демодулятор відновлює чистий логічний імпульс.",
                        size=11.5, color=INK, fill="#eef6ef", stroke=MSG, min_w=W - 140)
    p.append(b)

    render(os.path.join(OUT, "bg-light-vs-modulated.svg"), W, H, *p,
           title="Відсів оптичних завад за допомогою модуляції несучої 38 кГц")

# ── Фігура 2: Структурна схема інтегрованого ІЧ-приймача ─────────────────────
def fig_ir_receiver_block_diagram():
    W, H = 780, 310
    p = []

    blocks = [
        ("Фотодіод", "PIN photodiode"),
        ("Підсилювач\n(TIA)", "Transimpedance"),
        ("АРУ\n(AGC)", "Auto Gain Control"),
        ("Смуговий\nфільтр", "BPF 38 kHz"),
        ("Демодулятор\n+ Піковий д.", "Detector"),
        ("Тригер\nШмітта", "Open Collector")
    ]

    bx_w = 98
    bx_h = 62
    gap = 22
    start_x = 42
    cy = 135

    x_positions = []
    for i, (ttl, sub) in enumerate(blocks):
        cx = start_x + i * (bx_w + gap) + bx_w / 2
        x_positions.append(cx)
        b = fitbox(cx - bx_w / 2, cy - bx_h / 2, bx_w, bx_h, ttl, size=12, bold=True, fill="#f4f6f8", stroke=LINE, rx=6)
        p.append(b)
        p.append(text(cx, cy + bx_h / 2 + 14, sub, size=10, color=MUTED))

        if i > 0:
            prev_cx = x_positions[i - 1]
            p.append(arrow(prev_cx + bx_w / 2, cy, cx - bx_w / 2, cy, color=LINE, sw=1.6))

    # Зворотний зв'язок від Демодулятора до АРУ (AGC feedback)
    cx_agc = x_positions[2]
    cx_demod = x_positions[4]
    y_fb = cy - bx_h / 2 - 25

    fb_path = [(cx_demod, cy - bx_h / 2),
               (cx_demod, y_fb),
               (cx_agc, y_fb),
               (cx_agc, cy - bx_h / 2)]
    p.append(path(fb_path, HOT, sw=1.5, dash="4 3"))
    p.append(arrow(cx_agc + 10, y_fb, cx_agc, cy - bx_h / 2, color=HOT, sw=1.5))
    p.append(text((cx_agc + cx_demod) / 2, y_fb - 8, "Петля АРУ (захист від насичення неперервною несучою)", size=10.5, color=HOT, bold=True))

    # Вхід (ІЧ-промені) і Вихід (OUT active-low)
    p.append(arrow(12, cy, start_x, cy, color=POS, sw=2.2))
    p.append(text(24, cy - 12, "ІЧ-світло", size=11, color=POS, bold=True, anchor="start"))

    last_cx = x_positions[-1]
    p.append(arrow(last_cx + bx_w / 2, cy, W - 15, cy, color=MSG, sw=2.2))
    p.append(text(W - 18, cy - 12, "OUT (Active LOW)", size=11, color=MSG, bold=True, anchor="end"))

    b, bw, bh = textbox(W / 2, 275, "Внутрішня трактовка TSOP: АРУ регулює підсилення, а смуговий фільтр проціджує 38 кГц.",
                        size=12, color=INK, fill="#fdfefe", stroke=MUTED, min_w=W - 160)
    p.append(b)

    render(os.path.join(OUT, "ir-receiver-block-diagram.svg"), W, H, *p,
           title="Аналогово-цифровий тракт інтегрованого ІЧ-приймача (серія TSOP)")

# ── Фігура 3: Форма пачки NEC із мікроколиваннями 38 кГц ─────────────────────
def fig_nec_frame_carrier():
    W, H = 760, 360
    x0, x1 = 70, 700
    p = []

    cy1 = 100
    cy2 = 240

    p.append(line(x0, cy1, x1, cy1, color=MUTED, sw=1.0, dash="3 3"))
    p.append(text(x0 - 8, cy1 + 4, "TX LED", size=12, color=CAR, bold=True, anchor="end"))
    p.append(text(x0, 35, "ІЧ-світловий сигнал (TX): пачки заповнені меандром 38 кГц (33% Duty Cycle)", size=12.5, color=CAR, bold=True, anchor="start"))

    # Сигнал передавача (38 кГц всередині пачок)
    xs = samp(x0, x1, 600)
    pts_tx = []
    pts_rx = []

    for x in xs:
        t = (x - x0) / (x1 - x0)
        # Пачки NEC: Leader burst (0.05..0.28), Bit 0 burst (0.45..0.55), Bit 1 burst (0.72..0.82)
        in_burst = (0.05 <= t <= 0.28) or (0.45 <= t <= 0.55) or (0.72 <= t <= 0.82)
        
        # 38 кГц меандр усередині пачки
        if in_burst:
            phase = (t * 220) % 1.0
            y_val = 45 if phase < 0.33 else 0  # 33% duty cycle
        else:
            y_val = 0
            
        pts_tx.append((x, cy1 - y_val))
        
        # Вихід приймача (Active LOW: 0 під час пачки, 1 під час паузи)
        rx_val = -35 if in_burst else +35
        pts_rx.append((x, cy2 + rx_val))

    p.append(path(pts_tx, CAR, sw=1.4))

    # Позначки періоду несучої
    p.append(line(x0 + 40, cy1 - 52, x0 + 75, cy1 - 52, color=MUTED, sw=1.2))
    p.append(text(x0 + 57, cy1 - 58, "T = 26.3 мкс (38 кГц)", size=10.5, color=MUTED, bold=True))

    p.append(line(x0, cy2, x1, cy2, color=MUTED, sw=1.0, dash="3 3"))
    p.append(text(x0 - 8, cy2 + 4, "RX OUT", size=12, color=MSG, bold=True, anchor="end"))
    p.append(text(x0, 185, "Демодульований вихід приймача (Active LOW логічні імпульси)", size=12.5, color=MSG, bold=True, anchor="start"))
    p.append(path(pts_rx, MSG, sw=2.2))

    # Текстові підписи фаз протоколу
    p.append(text(x0 + 115, cy2 + 55, "Преамбула (Leader burst)", size=11, color=INK, bold=True))
    p.append(text(x0 + 360, cy2 + 55, "Біт '0'", size=11, color=INK, bold=True))
    p.append(text(x0 + 550, cy2 + 55, "Біт '1'", size=11, color=INK, bold=True))

    b, bw, bh = textbox(W / 2, 335, "З шпаруватістю 33% світлодіод імпульсно витримує струм до 500 мА без перегріву.",
                        size=11.5, color=INK, fill="#eef6ef", stroke=MSG, min_w=W - 140)
    p.append(b)

    render(os.path.join(OUT, "nec-frame-carrier.svg"), W, H, *p,
           title="Заповнення часових інтервалів NEC-протоколу несучою 38 кГц")

# ── Фігура 4: Частотна характеристика смугового фільтра ─────────────────────
def fig_bpf_frequency_response():
    W, H = 740, 360
    ax, ay, axw = 75, 270, 600
    p = []

    p.append(line(ax, ay, ax + axw, ay, color=INK, sw=1.6))
    p.append(arrow(ax + axw - 20, ay, ax + axw, ay, color=INK, sw=1.6))
    p.append(text(ax + axw + 6, ay + 5, "f (кГц)", size=14, color=INK, italic=True, anchor="start"))

    p.append(line(ax, ay, ax, ay - 210, color=INK, sw=1.6))
    p.append(arrow(ax, ay - 190, ax, ay - 210, color=INK, sw=1.6))
    p.append(text(ax - 10, ay - 215, "K(f)", size=14, color=INK, italic=True, anchor="end"))

    fc_x = ax + 300  # 38 кГц
    
    # Крива смугового фільтра (Q ≈ 7)
    pts = []
    for i in range(350):
        fx = ax + i * (axw / 350)
        f_khz = 10 + i * (60 / 350)
        # Лоренціан для резонансу
        df = f_khz - 38
        gain = 1.0 / (1.0 + (df / 2.8) ** 2)
        y = ay - 170 * gain
        pts.append((fx, y))

    p.append(path(pts, CAR, sw=2.4))

    # Позначка центральної частоти 38 кГц
    p.append(line(fc_x, ay, fc_x, ay - 170, color=CAR, sw=1.2, dash="3 3"))
    p.append(text(fc_x, ay + 20, "38 кГц", size=12.5, color=CAR, bold=True))

    # Загасання DC і лампових завад (100 Гц)
    p.append(line(ax + 10, ay, ax + 10, ay - 10, color=HOT, sw=3.0))
    p.append(text(ax + 10, ay - 25, "DC (сонце) & 100 Гц", size=11, color=HOT, bold=True, anchor="start"))
    p.append(text(ax + 10, ay - 10, "придушено на > 60 дБ", size=10.5, color=MUTED, anchor="start"))

    # Смуга пропускання (BW = 38 ± 2 кГц)
    bw_left = fc_x - 30
    bw_right = fc_x + 30
    p.append(line(bw_left, ay - 120, bw_right, ay - 120, color=MSG, sw=1.4))
    p.append(line(bw_left, ay - 115, bw_left, ay - 125, color=MSG, sw=1.4))
    p.append(line(bw_right, ay - 115, bw_right, ay - 125, color=MSG, sw=1.4))
    p.append(text(fc_x, ay - 132, "Смуга Δf ≈ 4 кГц (Q ≈ 9.5)", size=11, color=MSG, bold=True))

    b, bw, bh = textbox(W / 2, 335, "Відхилення частоти передавача всього на 2 кГц зменшує чутливість приймача майже вдвічі.",
                        size=11.5, color=INK, fill="#fdfefe", stroke=MUTED, min_w=W - 140)
    p.append(b)

    render(os.path.join(OUT, "bpf-frequency-response.svg"), W, H, *p,
           title="Амплітудно-частотна характеристика смугового фільтра 38 кГц")

if __name__ == "__main__":
    fig_bg_light_vs_modulated()
    fig_ir_receiver_block_diagram()
    fig_nec_frame_carrier()
    fig_bpf_frequency_response()
    print("OK: figures written to", OUT)
