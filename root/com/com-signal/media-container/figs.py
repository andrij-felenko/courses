# -*- coding: utf-8 -*-
"""Фігури до теми «Медіаконтейнер: як стиснені кадри складають у файл».
Запуск: python figs.py -> генерує SVG у ./img/
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Архітектура медіаконтейнера та мультиплексування ──────────────────────
def fig_media_container_architecture():
    W, H = 840, 370
    f = [text(W / 2, 25, "Концептуальна схема медіаконтейнера та мультиплексування потоків", size=16, bold=True)]

    # Елементарні потоки (ліворуч)
    f.append(fitbox(20, 60, 150, 110, "Відеопотік (Video ES)\n\n• H.264 / AV1 NAL\n• Стиснені кадри\n• Поліпшення/різниця", size=11, fill="#eff6ff", stroke="#3b82f6"))
    f.append(fitbox(20, 200, 150, 110, "Аудіопотік (Audio ES)\n\n• AAC / Opus фрейми\n• PCM відліки\n• Спектральні кванти", size=11, fill="#f0fdf4", stroke="#16a34a"))

    # Стрілки в мультиплексор
    f.append(arrow(170, 115, 230, 155, color="#3b82f6", sw=2))
    f.append(text(200, 125, "Кадри", size=10, color="#3b82f6", bold=True))

    f.append(arrow(170, 255, 230, 215, color="#16a34a", sw=2))
    f.append(text(200, 245, "Фрейми", size=10, color="#16a34a", bold=True))

    # Мультиплексор (посереднику)
    f.append(fitbox(230, 130, 140, 110, "Мультиплексор\n(Muxer)\n\n• Шкала часу\n• Прив'язка PTS/DTS\n• Формування чанків", size=11, fill="#fefce8", stroke="#ca8a04", bold=True))

    # Стрілка у контейнерний файл
    f.append(arrow(370, 185, 430, 185, color=LINE, sw=2))

    # Медіаконтейнерний файл (праворуч)
    f.append(rect(430, 55, 390, 275, fill="#fafafa", stroke="#4b5563", rx=6, sw=1.5))
    f.append(text(625, 75, "Структура файлу медіаконтейнера (.mp4 / .mkv)", size=12, color=INK, bold=True))

    # Заголовок / Метадані / Індекс
    f.append(fitbox(445, 90, 360, 50, "Метадані та індексні таблиці (moov / Cues)\n• Карти зсувів кадри (stco) • Таблиця тривалості (stts)\n• Профілі кодеків & Параметри ініціалізації", size=10, fill="#faf5ff", stroke="#9333ea"))

    # Черговані чанки медіаданих (mdat)
    f.append(rect(445, 150, 360, 165, fill="#f1f5f9", stroke="#64748b", rx=4))
    f.append(text(625, 168, "Основний масив медіаданих (mdat / Cluster)", size=10, color=MUTED, bold=True))

    f.append(fitbox(455, 180, 105, 45, "Chunk 1 (Video)\nI-кадр + P-кадри\nPTS: 0.0s - 0.5s", size=9, fill="#eff6ff", stroke="#3b82f6"))
    f.append(fitbox(570, 180, 105, 45, "Chunk 1 (Audio)\nAAC фрейми\nPTS: 0.0s - 0.5s", size=9, fill="#f0fdf4", stroke="#16a34a"))
    f.append(fitbox(685, 180, 105, 45, "Chunk 2 (Video)\nP-кадри / B-кадри\nPTS: 0.5s - 1.0s", size=9, fill="#eff6ff", stroke="#3b82f6"))

    f.append(fitbox(455, 235, 105, 45, "Chunk 2 (Audio)\nAAC фрейми\nPTS: 0.5s - 1.0s", size=9, fill="#f0fdf4", stroke="#16a34a"))
    f.append(fitbox(570, 235, 105, 45, "Chunk 3 (Video)\nIDR Keyframe\nPTS: 1.0s - 1.5s", size=9, fill="#eff6ff", stroke="#3b82f6"))
    f.append(fitbox(685, 235, 105, 45, "Chunk 3 (Audio)\nAAC фрейми\nPTS: 1.0s - 1.5s", size=9, fill="#f0fdf4", stroke="#16a34a"))

    f.append(text(625, 302, "← Синхронне чергування в часі запобігає перемотуванню диска →", size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, 'media-container-architecture.svg'), W, H, *f)


# ── 2. Чергування кадрів та хронометрія PTS vs DTS ──────────────────────────
def fig_interleaving_pts_dts():
    W, H = 820, 360
    f = [text(W / 2, 25, "Хронометрія кадрів: порядок відображення (PTS) проти декодування (DTS)", size=16, bold=True)]

    # Шкала відображення (PTS)
    f.append(text(120, 65, "Порядок відображення (PTS):", size=11, bold=True, anchor="start", color="#1e293b"))
    pts_frames = [
        ("I0", "PTS=0", "#dbeafe", "#1d4ed8"),
        ("B1", "PTS=1", "#fef3c7", "#b45309"),
        ("B2", "PTS=2", "#fef3c7", "#b45309"),
        ("P3", "PTS=3", "#e0e7ff", "#4338ca"),
        ("B4", "PTS=4", "#fef3c7", "#b45309"),
        ("P5", "PTS=5", "#e0e7ff", "#4338ca")
    ]
    for i, (name, pts, bg, fg) in enumerate(pts_frames):
        x = 120 + i * 110
        f.append(fitbox(x, 75, 95, 45, f"{name}\n{pts}", size=11, fill=bg, stroke=fg, bold=True))
        if i < len(pts_frames) - 1:
            f.append(arrow(x + 95, 97, x + 110, 97, color=MUTED, sw=1.2))

    # Шкала декодування (DTS у контейнері)
    f.append(text(120, 160, "Порядок у контейнері та декодері (DTS):", size=11, bold=True, anchor="start", color="#1e293b"))
    dts_frames = [
        ("I0", "DTS=0, PTS=0", "#dbeafe", "#1d4ed8"),
        ("P3", "DTS=1, PTS=3", "#e0e7ff", "#4338ca"),
        ("B1", "DTS=2, PTS=1", "#fef3c7", "#b45309"),
        ("B2", "DTS=3, PTS=2", "#fef3c7", "#b45309"),
        ("P5", "DTS=4, PTS=5", "#e0e7ff", "#4338ca"),
        ("B4", "DTS=5, PTS=4", "#fef3c7", "#b45309")
    ]
    for i, (name, times, bg, fg) in enumerate(dts_frames):
        x = 120 + i * 110
        f.append(fitbox(x, 170, 95, 50, f"{name}\n{times}", size=10, fill=bg, stroke=fg, bold=True))

    # Пояснювальні стрелочки перевпорядкування для P3 та B1
    f.append(line(265, 120, 265, 140, color="#dc2626", sw=1.5, dash="3,3"))
    f.append(arrow(265, 140, 475, 170, color="#dc2626", sw=1.5))
    f.append(text(380, 142, "P3 передається раніше B-кадрів!", size=10, color="#dc2626", bold=True))

    # Буфер затримки декодера
    f.append(rect(120, 245, 645, 95, fill="#f8fafc", stroke="#64748b", rx=6))
    f.append(text(442, 265, "Механізм буфера відновлення порядку (Reordering Buffer / DPB)", size=11, bold=True, color="#334155"))
    f.append(text(442, 285, "• B-кадри вимагають майбутній опорний P-кадр для обчислення двонаправленого руху.", size=10, color=MUTED))
    f.append(text(442, 305, "• Декодер затримує видачу B-кадрів на екран, доки не розпакує P3, досягаючи PTS-синхронізації.", size=10, color=MUTED))

    render(os.path.join(IMG, 'interleaving-pts-dts.svg'), W, H, *f)


# ── 3. Ієрархія боксів ISOBMFF / MP4 ─────────────────────────────────────────
def fig_mp4_box_tree():
    W, H = 820, 370
    f = [text(W / 2, 25, "Ієрархічна структура атомарних боксів ISOBMFF (MP4 File Layout)", size=16, bold=True)]

    # Корневі бокси (Root File Level)
    f.append(rect(20, 55, 780, 290, fill="#f8fafc", stroke="#334155", rx=6, sw=1.5))
    f.append(text(70, 75, "Файл MP4 (Root)", size=12, bold=True, color="#0f172a"))

    # ftyp
    f.append(fitbox(30, 90, 110, 50, "ftyp\n(FileType Box)\n• Brand: mp42", size=10, fill="#e0f2fe", stroke="#0284c7"))

    # moov
    f.append(rect(150, 90, 480, 240, fill="#faf5ff", stroke="#9333ea", rx=6, sw=1.5))
    f.append(text(210, 110, "moov (Movie Metadata Box)", size=11, bold=True, color="#6b21a8"))

    f.append(fitbox(160, 125, 100, 40, "mvhd\nHeader", size=10, fill="#ffffff", stroke="#9333ea"))

    # trak Video
    f.append(rect(270, 125, 170, 195, fill="#eff6ff", stroke="#2563eb", rx=4))
    f.append(text(355, 142, "trak (Video Track)", size=10, bold=True, color="#1e40af"))
    f.append(fitbox(280, 155, 150, 30, "tkhd (Track Header)", size=9, fill="#ffffff", stroke="#2563eb"))
    f.append(rect(280, 190, 150, 120, fill="#ffffff", stroke="#3b82f6", rx=4))
    f.append(text(355, 205, "mdia -> minf -> stbl", size=9, bold=True, color="#1d4ed8"))
    f.append(fitbox(285, 215, 140, 20, "stts (Sample Times)", size=8, fill="#eff6ff", stroke="#3b82f6"))
    f.append(fitbox(285, 238, 140, 20, "stsc (Sample To Chunk)", size=8, fill="#eff6ff", stroke="#3b82f6"))
    f.append(fitbox(285, 261, 140, 20, "stsz (Sample Sizes)", size=8, fill="#eff6ff", stroke="#3b82f6"))
    f.append(fitbox(285, 284, 140, 20, "stco / co64 (Offsets)", size=8, fill="#eff6ff", stroke="#3b82f6"))

    # trak Audio
    f.append(rect(450, 125, 170, 195, fill="#f0fdf4", stroke="#16a34a", rx=4))
    f.append(text(535, 142, "trak (Audio Track)", size=10, bold=True, color="#166534"))
    f.append(fitbox(460, 155, 150, 30, "tkhd (Track Header)", size=9, fill="#ffffff", stroke="#16a34a"))
    f.append(rect(460, 190, 150, 120, fill="#ffffff", stroke="#22c55e", rx=4))
    f.append(text(535, 205, "mdia -> minf -> stbl", size=9, bold=True, color="#15803d"))
    f.append(fitbox(465, 215, 140, 20, "stts (Sample Times)", size=8, fill="#f0fdf4", stroke="#16a34a"))
    f.append(fitbox(465, 238, 140, 20, "stsc (Sample To Chunk)", size=8, fill="#f0fdf4", stroke="#16a34a"))
    f.append(fitbox(465, 261, 140, 20, "stsz (Sample Sizes)", size=8, fill="#f0fdf4", stroke="#16a34a"))
    f.append(fitbox(465, 284, 140, 20, "stco / co64 (Offsets)", size=8, fill="#f0fdf4", stroke="#16a34a"))

    # mdat
    f.append(fitbox(640, 90, 150, 240, "mdat\n(Media Data Box)\n\n• Сирі НУ-пакети H.264\n• AAC аудіо-фрейми\n\nДані адресуються\nчерез вказівники stco\nіз блоку moov", size=10, fill="#fff7ed", stroke="#ea580c"))

    render(os.path.join(IMG, 'mp4-box-tree.svg'), W, H, *f)


if __name__ == '__main__':
    fig_media_container_architecture()
    fig_interleaving_pts_dts()
    fig_mp4_box_tree()
    print("Генерацію фігур завершено успішно.")
