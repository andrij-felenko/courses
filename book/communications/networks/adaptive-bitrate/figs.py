# -*- coding: utf-8 -*-
"""Фігури до теми «Адаптивний бітрейт (ABR): HLS, DASH та алгоритми».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b9770e"     # бурштиновий: перехідні стани / буферні зони
PURPLE = "#7c3aed"    # фіолетовий: маніфести / службові структури
CYAN = "#0891b2"      # бірюзовий: CDN / транспортні потоки


# ── 1. Архітектура адаптивного потокового відео (ABR Pipeline) ────────────────
def fig_abr_architecture():
    W, H = 860, 430
    p = [text(W / 2, 28, "Архітектура сегментованої доставки відео з адаптивним бітрейтом (ABR)", size=15, bold=True)]

    stages = [
        ("1. Кодування", "Транскодер створює профіль якості (Ladder):",
         ["1080p @ 6.0 Мбіт/с", "720p @ 3.0 Мбіт/с", "480p @ 1.2 Мбіт/с", "360p @ 0.6 Мбіт/с"],
         POS, "#fdecea"),
        ("2. Сегментація", "Пакувальник ріже потік на чанки 2–6 с (fMP4/TS):",
         ["Вирівняні GOP (I-кадри)", "Маніфести .m3u8 / .mpd", "Ініціалізаційні чанки"],
         PURPLE, "#f5f3ff"),
        ("3. Доставка", "Стандартні веб-сервери та мережа CDN:",
         ["Кешування на Edge-вузлах", "HTTP GET / Range-запити", "Масштабування на мільйони"],
         CYAN, "#ecfeff"),
        ("4. Клієнт (ABR)", "Відеоплеєр керує завантаженням та буфером:",
         ["Вимір швидкості каналу", "Контроль рівня буфера", "Динамічний вибір чанка"],
         FIELD, "#eafaf0"),
    ]

    bw = 192
    gap = 20
    x0 = (W - (4 * bw + 3 * gap)) / 2
    y0 = 60
    bh = 320

    for i, (title, subtitle, items, col, fill) in enumerate(stages):
        x = x0 + i * (bw + gap)
        p.append(rect(x, y0, bw, bh, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(text(x + bw / 2, y0 + 26, title, size=12, color=col, bold=True))
        p.append(line(x + 10, y0 + 38, x + bw - 10, y0 + 38, color=col, sw=1.0))
        p.append(mtext(x + bw / 2, y0 + 56, subtitle, size=10, color=INK, anchor="middle", lh=1.25))
        for j, it in enumerate(items):
            iy = y0 + 130 + j * 42
            p.append(rect(x + 8, iy, bw - 16, 32, fill="#ffffff", stroke=col, sw=1.0, rx=4))
            p.append(text(x + bw / 2, iy + 20, it, size=10, color=INK, bold=False))

        if i < 3:
            ax = x + bw + 2
            ay = y0 + bh / 2
            p.append(arrow(ax, ay, ax + gap - 4, ay, color=INK, sw=1.8))

    p.append(text(W / 2, H - 16, "Клієнт самостійно вирішує, яку якість кожного наступного чанка запросити через звичайний HTTP GET.",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "abr-architecture.svg"), W, H, *p)


# ── 2. Структура маніфестів: HLS vs MPEG-DASH ──────────────────────────────────
def fig_manifest_structure():
    W, H = 880, 460
    p = [text(W / 2, 28, "Ієрархія маніфестів: Apple HLS (M3U8) проти MPEG-DASH (MPD)", size=15, bold=True)]

    col_w = 405
    cx1 = 25
    cx2 = 450
    top_y = 60
    box_h = 355

    # Ліва колонка: HLS
    p.append(rect(cx1, top_y, col_w, box_h, fill="#fdf6e3", stroke=AMBER, sw=1.8, rx=8))
    p.append(text(cx1 + col_w / 2, top_y + 24, "HLS (HTTP Live Streaming) — Текстові плейлисти", size=11.5, color=AMBER, bold=True))
    p.append(line(cx1 + 10, top_y + 36, cx1 + col_w - 10, top_y + 36, color=AMBER, sw=1.0))

    # Master Playlist
    p.append(rect(cx1 + 14, top_y + 46, col_w - 28, 72, fill="#ffffff", stroke=AMBER, sw=1.2, rx=5))
    p.append(text(cx1 + 24, top_y + 66, "Головний плейлист: master.m3u8", size=10.5, color=INK, anchor="start", bold=True))
    p.append(text(cx1 + 24, top_y + 86, "#EXT-X-STREAM-INF: BANDWIDTH=6000000, 1080p.m3u8", size=9.5, color=MUTED, anchor="start"))
    p.append(text(cx1 + 24, top_y + 104, "#EXT-X-STREAM-INF: BANDWIDTH=1200000, 480p.m3u8", size=9.5, color=MUTED, anchor="start"))

    p.append(arrow(cx1 + col_w / 2, top_y + 122, cx1 + col_w / 2, top_y + 144, color=AMBER, sw=1.5))

    # Media Playlists
    p.append(rect(cx1 + 14, top_y + 148, col_w - 28, 192, fill="#ffffff", stroke=AMBER, sw=1.2, rx=5))
    p.append(text(cx1 + 24, top_y + 170, "Медіа-плейлист якості: 1080p.m3u8", size=10.5, color=INK, anchor="start", bold=True))
    p.append(text(cx1 + 24, top_y + 194, "#EXT-X-TARGETDURATION: 6", size=10, color=INK, anchor="start"))
    p.append(text(cx1 + 24, top_y + 214, "#EXTINF:6.0, segment_0.mp4", size=10, color=POS, anchor="start"))
    p.append(text(cx1 + 24, top_y + 234, "#EXTINF:6.0, segment_1.mp4", size=10, color=POS, anchor="start"))
    p.append(text(cx1 + 24, top_y + 254, "#EXTINF:6.0, segment_2.mp4", size=10, color=POS, anchor="start"))
    p.append(text(cx1 + 24, top_y + 280, "Плейлист перелічує прямі посилання на файли чанків", size=9.5, color=MUTED, anchor="start", italic=True))
    p.append(text(cx1 + 24, top_y + 300, "Для Live: ковзне вікно з нових #EXTINF рядків", size=9.5, color=MUTED, anchor="start", italic=True))
    p.append(text(cx1 + 24, top_y + 320, "Для VoD: закривається тегом #EXT-X-ENDLIST", size=9.5, color=MUTED, anchor="start", italic=True))

    # Права колонка: DASH
    p.append(rect(cx2, top_y, col_w, box_h, fill="#f5f3ff", stroke=PURPLE, sw=1.8, rx=8))
    p.append(text(cx2 + col_w / 2, top_y + 24, "MPEG-DASH — XML-дерево маніфесту (MPD)", size=11.5, color=PURPLE, bold=True))
    p.append(line(cx2 + 10, top_y + 36, cx2 + col_w - 10, top_y + 36, color=PURPLE, sw=1.0))

    # MPD Tree
    p.append(rect(cx2 + 14, top_y + 46, col_w - 28, 294, fill="#ffffff", stroke=PURPLE, sw=1.2, rx=5))
    p.append(text(cx2 + 24, top_y + 68, "<MPD minBufferTime=\"PT2S\">", size=10.5, color=PURPLE, anchor="start", bold=True))
    p.append(text(cx2 + 38, top_y + 90, "<Period duration=\"PT1H\">", size=10, color=INK, anchor="start", bold=True))
    p.append(text(cx2 + 52, top_y + 112, "<AdaptationSet mimeType=\"video/mp4\">", size=10, color=CYAN, anchor="start", bold=True))
    
    # Representations
    p.append(rect(cx2 + 62, top_y + 124, col_w - 82, 54, fill="#faf5ff", stroke=PURPLE, sw=1.0, rx=4))
    p.append(text(cx2 + 70, top_y + 144, "<Representation id=\"1080p\" bandwidth=\"6M\"/>", size=9.5, color=INK, anchor="start"))
    p.append(text(cx2 + 70, top_y + 164, "<Representation id=\"480p\"  bandwidth=\"1.2M\"/>", size=9.5, color=INK, anchor="start"))

    # SegmentTemplate
    p.append(rect(cx2 + 62, top_y + 186, col_w - 82, 74, fill="#f0fdf4", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(cx2 + 70, top_y + 206, "<SegmentTemplate init=\"init-$RepID$.mp4\"", size=9.5, color=FIELD, anchor="start", bold=True))
    p.append(text(cx2 + 70, top_y + 226, "  media=\"chunk-$RepID$-$Number$.m4s\"", size=9.5, color=FIELD, anchor="start", bold=True))
    p.append(text(cx2 + 70, top_y + 246, "  duration=\"2000\" startNumber=\"1\"/>", size=9.5, color=FIELD, anchor="start", bold=True))

    p.append(text(cx2 + 52, top_y + 280, "</AdaptationSet>", size=10, color=CYAN, anchor="start", bold=True))
    p.append(text(cx2 + 38, top_y + 302, "</Period>", size=10, color=INK, anchor="start", bold=True))
    p.append(text(cx2 + 24, top_y + 324, "</MPD>", size=10.5, color=PURPLE, anchor="start", bold=True))

    p.append(text(W / 2, H - 16, "HLS явно перелічує сегменти або їх ковзне вікно; DASH формує URL чанків динамічно за шаблоном SegmentTemplate.",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, "manifest-structure.svg"), W, H, *p)


# ── 3. Логіка Buffer-Based Adaptation (BBA) ───────────────────────────────────
def fig_buffer_bba_mapping():
    W, H = 840, 420
    p = [text(W / 2, 28, "Алгоритм BBA: Функція відображення наповненості буфера в бітрейт", size=15, bold=True)]

    ox, oy = 90, 330
    gw, gh = 660, 240

    r_frac = 0.22      # Резервуар r = 8 с (із 40 с макс)
    c_frac = 0.55      # Подушка c = 20 с (до 28 с)
    rx_val = ox + gw * r_frac
    cx_val = ox + gw * (r_frac + c_frac)

    # 1. Резервуар (небезпека зависання)
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" opacity="0.8"/>'
             % (ox, oy - gh, rx_val - ox, gh))
    # 2. Подушка (робочий діапазон адаптації)
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eafaf0" opacity="0.8"/>'
             % (rx_val, oy - gh, cx_val - rx_val, gh))
    # 3. Максимальний буфер (безпека максимальної якості)
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eef4ff" opacity="0.8"/>'
             % (cx_val, oy - gh, ox + gw - cx_val, gh))

    p.append(arrow(ox, oy, ox + gw + 20, oy, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - gh - 20, color=INK, sw=1.8))
    p.append(text(ox + gw + 10, oy + 24, "Рівень буфера B(t) [секунди] →", size=11, color=INK, anchor="end", bold=True))
    p.append(text(ox - 10, oy - gh - 10, "Бітрейт R_k [Мбіт/с] ↑", size=11, color=INK, anchor="end", bold=True))

    p.append(line(rx_val, oy - 4, rx_val, oy + 4, color=INK, sw=1.5))
    p.append(text(rx_val, oy + 20, "r (Резервуар, 8 с)", size=10, color=POS, bold=True))
    p.append(line(cx_val, oy - 4, cx_val, oy + 4, color=INK, sw=1.5))
    p.append(text(cx_val, oy + 20, "r + c (Подушка, 28 с)", size=10, color=FIELD, bold=True))
    p.append(text(ox + gw - 20, oy + 20, "B_max (40 с)", size=10, color=NEG, bold=True))

    rates = [
        (0.6, "R_min = 0.6 М", oy - gh * 0.12),
        (1.5, "1.5 М", oy - gh * 0.32),
        (3.0, "3.0 М", oy - gh * 0.58),
        (6.0, "R_max = 6.0 М", oy - gh * 0.90),
    ]

    for rate, label, y_pos in rates:
        p.append(line(ox, y_pos, ox + gw, y_pos, color="#d1d5db", sw=1.0, dash="4 4"))
        p.append(text(ox - 8, y_pos + 4, label, size=9.5, color=MUTED, anchor="end"))

    y_min = rates[0][2]
    y_max = rates[3][2]

    p.append(line(ox, y_min, rx_val, y_min, color=MUTED, sw=1.5, dash="3 3"))
    p.append(line(rx_val, y_min, cx_val, y_max, color=MUTED, sw=1.5, dash="3 3"))
    p.append(line(cx_val, y_max, ox + gw, y_max, color=MUTED, sw=1.5, dash="3 3"))

    step_pts = [
        (ox, y_min), (rx_val + (cx_val - rx_val) * 0.25, y_min),
        (rx_val + (cx_val - rx_val) * 0.25, rates[1][2]), (rx_val + (cx_val - rx_val) * 0.60, rates[1][2]),
        (rx_val + (cx_val - rx_val) * 0.60, rates[2][2]), (cx_val, rates[2][2]),
        (cx_val, y_max), (ox + gw, y_max)
    ]
    for k in range(len(step_pts) - 1):
        p.append(line(step_pts[k][0], step_pts[k][1], step_pts[k+1][0], step_pts[k+1][1], color=FIELD, sw=3.0))

    p.append(text(ox + (rx_val - ox) / 2, oy - gh + 24, "Зона захисту від паузи", size=10, color=POS, bold=True))
    p.append(text(ox + (rx_val - ox) / 2, oy - gh + 40, "Завжди R_min", size=9.5, color=POS))

    p.append(text(rx_val + (cx_val - rx_val) / 2, oy - gh + 24, "Динамічна зона адаптації (Cushion)", size=10, color=FIELD, bold=True))
    p.append(text(rx_val + (cx_val - rx_val) / 2, oy - gh + 40, "Бітрейт зростає пропорційно буферу", size=9.5, color=FIELD))

    p.append(text(cx_val + (ox + gw - cx_val) / 2, oy - gh + 24, "Зона насичення", size=10, color=NEG, bold=True))
    p.append(text(cx_val + (ox + gw - cx_val) / 2, oy - gh + 40, "Завжди R_max", size=9.5, color=NEG))

    p.append(text(W / 2, H - 14, "BBA не намагається вгадати швидкість каналу на шумі TCP, а обирає якість виключно за запасом часу в буфері.",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, "buffer-bba-mapping.svg"), W, H, *p)


# ── 4. Трилема якості QoE (Trade-off Triangle) ─────────────────────────────────
def fig_qoe_tradeoff_triangle():
    W, H = 840, 430
    p = [text(W / 2, 28, "Трилема користувацького досвіду (QoE) в адаптивному потоковому відео", size=15, bold=True)]

    vx_top, vy_top = W / 2, 80
    vx_left, vy_left = 180, 310
    vx_right, vy_right = 660, 310

    p.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#f8fafc" stroke="%s" stroke-width="2.0"/>'
             % (vx_top, vy_top, vx_left, vy_left, vx_right, vy_right, LINE))

    cx_core, cy_core = W / 2, 220
    p.append(circle(cx_core, cy_core, 54, fill="#ffffff", stroke=PURPLE, sw=2.0))
    p.append(text(cx_core, cy_core - 18, "Максимум QoE", size=11, color=PURPLE, bold=True))
    p.append(text(cx_core, cy_core + 2, "max ∑ q(R_k)", size=10, color=INK, bold=True))
    p.append(text(cx_core, cy_core + 18, "− λ·T_stall", size=9.5, color=POS, bold=True))
    p.append(text(cx_core, cy_core + 34, "− μ·|ΔR_k|", size=9.5, color=AMBER, bold=True))

    p.append(line(vx_top, vy_top + 45, cx_core, cy_core - 54, color=POS, sw=1.5, dash="4 4"))
    p.append(line(vx_left + 45, vy_left - 20, cx_core - 48, cy_core + 20, color=NEG, sw=1.5, dash="4 4"))
    p.append(line(vx_right - 45, vy_right - 20, cx_core + 48, cy_core + 20, color=AMBER, sw=1.5, dash="4 4"))

    # Вершина 1: Високий бітрейт
    bw, bh = 230, 68
    p.append(rect(vx_top - bw / 2, vy_top - 20, bw, bh, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    p.append(text(vx_top, vy_top + 4, "1. Високий бітрейт q(R)", size=11, color=POS, bold=True))
    p.append(text(vx_top, vy_top + 24, "Чітка 4K/1080p картинка", size=9.5, color=INK))
    p.append(text(vx_top, vy_top + 40, "Ризик: вичерпання буфера при спаді смуги", size=9.5, color=POS))

    # Вершина 2: Відсутність пауз
    p.append(rect(vx_left - bw / 2, vy_left - 10, bw, bh, fill="#eef4ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(vx_left, vy_left + 14, "2. Безперервність (No Stall)", size=11, color=NEG, bold=True))
    p.append(text(vx_left, vy_left + 34, "Нульовий Rebuffering, глибокий буфер", size=9.5, color=INK))
    p.append(text(vx_left, vy_left + 50, "Ризик: надмірно занижена якість (мило)", size=9.5, color=NEG))

    # Вершина 3: Стабільність якості
    p.append(rect(vx_right - bw / 2, vy_right - 10, bw, bh, fill="#fdf6e3", stroke=AMBER, sw=1.8, rx=8))
    p.append(text(vx_right, vy_right + 14, "3. Плавність (No Flapping)", size=11, color=AMBER, bold=True))
    p.append(text(vx_right, vy_right + 34, "Без різких стрибків роздільності", size=9.5, color=INK))
    p.append(text(vx_right, vy_right + 50, "Ризик: повільна реакція на зміну мережі", size=9.5, color=AMBER))

    p.append(text(W / 2, H - 16, "Головне завдання ABR — знайти парето-оптимальний баланс між цими трьома суперечливими факторами.",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "qoe-tradeoff-triangle.svg"), W, H, *p)


# ── 5. Традиційний ABR vs Low-Latency CMAF ──────────────────────────────────────
def fig_low_latency_cmaf():
    W, H = 860, 430
    p = [text(W / 2, 28, "Порівняння затримки: Традиційний ABR проти Low-Latency CMAF (Chunked Transfer)", size=15, bold=True)]

    # 1. Традиційний сегмент (2–6 секунд)
    y1 = 70
    p.append(rect(30, y1, 800, 140, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(50, y1 + 24, "Традиційний HLS / DASH (Затримка від прямого ефіру: 15–30 секунд)", size=11.5, color=POS, anchor="start", bold=True))

    tx0 = 50
    stages1 = [
        ("Кодування повного сегмента (6 с)", 220, "#fdecea", POS),
        ("Публікація на Origin & маніфест", 170, "#fef3c7", AMBER),
        ("Кешування на CDN Edge", 150, "#ecfeff", CYAN),
        ("Завантаження чанка клієнтом + 3 чанки буфера", 210, "#eef4ff", NEG),
    ]
    cur_x = tx0
    for label, w_box, fill_col, border_col in stages1:
        p.append(rect(cur_x, y1 + 45, w_box, 46, fill=fill_col, stroke=border_col, sw=1.2, rx=4))
        p.append(mtext(cur_x + w_box / 2, y1 + 64, label, size=9.5, color=INK, anchor="middle", lh=1.2))
        cur_x += w_box + 6

    p.append(text(50, y1 + 120, "Сегмент доступний для запиту ЛИШЕ після того, як кодер повністю запише і закриє 6-секундний файл.",
                  size=10, color=POS, anchor="start", bold=True))

    # 2. Low-Latency CMAF / Chunked Transfer
    y2 = 230
    p.append(rect(30, y2, 800, 155, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(50, y2 + 24, "Low-Latency CMAF / LL-HLS (Затримка: 1.5–3 секунди)", size=11.5, color=FIELD, anchor="start", bold=True))

    cmaf_chunks = [
        ("Chunk #1 (200 мс)\nmoof + mdat", 115),
        ("Chunk #2 (200 мс)\nmoof + mdat", 115),
        ("Chunk #3 (200 мс)\nmoof + mdat", 115),
        ("Chunk #4 (200 мс)\nmoof + mdat", 115),
        ("Chunk #5 (200 мс)\nmoof + mdat", 115),
        ("Chunk #N (200 мс)...", 125),
    ]
    cur_x = tx0
    for title, w_box in cmaf_chunks:
        p.append(rect(cur_x, y2 + 45, w_box, 48, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
        p.append(mtext(cur_x + w_box / 2, y2 + 64, title, size=9.5, color=FIELD, anchor="middle", lh=1.2, bold=True))
        cur_x += w_box + 6

    p.append(arrow(tx0, y2 + 108, 770, y2 + 108, color=FIELD, sw=1.8))
    p.append(text(780, y2 + 111, "HTTP Chunked Transfer → Клієнт отримує кадри ще під час кодування сегмента",
                  size=9.5, color="#15803d", anchor="end", bold=True))
    p.append(text(50, y2 + 134, "CMAF розбиває 2-секундний фрагмент на мікро-блоки (chunks), які відправляються клієнту конвеєрно.",
                  size=10, color=MUTED, anchor="start", italic=True))

    p.append(text(W / 2, H - 12, "Low-Latency ABR передає відео частинами через HTTP/2 та HTTP/3 без очікування завершення повного сегмента.",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, "low-latency-cmaf.svg"), W, H, *p)


if __name__ == "__main__":
    fig_abr_architecture()
    fig_manifest_structure()
    fig_buffer_bba_mapping()
    fig_qoe_tradeoff_triangle()
    fig_low_latency_cmaf()
    print("OK: 5 figures written to", IMG)

