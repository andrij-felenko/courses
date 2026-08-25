# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ACCENT = "#b08900"


def fig_sync_problem():
    """Проблема розсинхронізації: ідеальна синхронізація vs розсинхронізація."""
    W, H = 760, 360
    p = []
    
    # Верхня панель
    p.append(rect(20, 20, 720, 155, fill="#f8faf8", stroke=POS, sw=1.5, rx=4))
    p.append(text(40, 42, "Ідеальна синхронізація: Tx та Rx на одному каналі у той самий час", size=12.5, color=POS, bold=True))
    
    p.append(text(40, 82, "Передавач (Tx):", size=11, color=INK, bold=True))
    p.append(text(40, 122, "Приймач (Rx):", size=11, color=INK, bold=True))
    
    channels = ["f3", "f7", "f1", "f5"]
    for i, ch in enumerate(channels):
        cx = 210 + i * 135
        # Tx блок
        b_tx, _, _ = textbox(cx, 80, f"Канал {ch}", size=10.5, fill="#d4edda", stroke=POS, sw=1.5, rx=3, color=POS, bold=True, min_w=105)
        p.append(b_tx)
        # Rx блок
        b_rx, _, _ = textbox(cx, 120, f"Канал {ch}", size=10.5, fill="#d4edda", stroke=POS, sw=1.5, rx=3, color=POS, bold=True, min_w=105)
        p.append(b_rx)
        
        p.append(text(cx, 158, f"Стрибок {i+1}: OK", size=9.5, color=POS, bold=True, anchor="middle"))

    # Нижня панель
    p.append(rect(20, 190, 720, 155, fill="#fff5f5", stroke=NEG, sw=1.5, rx=4))
    p.append(text(40, 212, "Розсинхронізація: зсув у часі або невідповідність послідовності", size=12.5, color=NEG, bold=True))
    
    p.append(text(40, 252, "Передавач (Tx):", size=11, color=INK, bold=True))
    p.append(text(40, 292, "Приймач (Rx):", size=11, color=INK, bold=True))
    
    rx_channels = ["f3", "f1", "f7", "f2"]
    for i in range(4):
        cx_tx = 210 + i * 135
        cx_rx = 210 + i * 135 + 30
        
        # Tx блок
        b_tx, _, _ = textbox(cx_tx, 250, f"Канал {channels[i]}", size=10.5, fill="#e2e3e5", stroke=MUTED, sw=1.2, rx=3, color=INK, bold=True, min_w=105)
        p.append(b_tx)
        
        # Rx блок
        b_rx, _, _ = textbox(cx_rx, 290, f"Канал {rx_channels[i]}", size=10.5, fill="#f8d7da", stroke=NEG, sw=1.5, rx=3, color=NEG, bold=True, min_w=105)
        p.append(b_rx)
        
        p.append(text(cx_tx, 330, "ВТРАТА СИГНАЛУ", size=9.5, color=NEG, bold=True, anchor="middle"))

    render(os.path.join(OUT, "sync-problem.svg"), W, H, *p)


def fig_tracking_guard():
    """Анатомія стрибка: PLL Lock, Dwell Time, Guard Interval."""
    W, H = 760, 260
    p = []
    
    p.append(rect(20, 20, 720, 230, fill="#fafafa", stroke="#d0d0d0", sw=1.2, rx=4))
    p.append(text(40, 45, "Структура часового слота стрибка (T_hop)", size=13.5, color=INK, bold=True))
    
    x_start = 60
    w_hop = 640
    
    w_lock = 110
    w_dwell = 400
    w_guard = 130
    
    # Слоти
    p.append(rect(x_start, 65, w_lock, 65, fill="#fff3cd", stroke=ACCENT, sw=1.5, rx=2))
    p.append(text(x_start + w_lock/2, 92, "PLL Lock", size=11.5, color=ACCENT, bold=True, anchor="middle"))
    p.append(text(x_start + w_lock/2, 112, "T_lock (~100 µs)", size=10, color=MUTED, anchor="middle"))
    
    p.append(rect(x_start + w_lock, 65, w_dwell, 65, fill="#d4edda", stroke=POS, sw=1.5, rx=2))
    p.append(text(x_start + w_lock + w_dwell/2, 92, "Dwell Time (Передача даних / Преамбула / CRC)", size=12, color=POS, bold=True, anchor="middle"))
    p.append(text(x_start + w_lock + w_dwell/2, 112, "T_dwell (Основна робоча фаза кадру)", size=10, color=MUTED, anchor="middle"))
    
    p.append(rect(x_start + w_lock + w_dwell, 65, w_guard, 65, fill="#cce5ff", stroke="#004085", sw=1.5, rx=2))
    p.append(text(x_start + w_lock + w_dwell + w_guard/2, 92, "Guard Interval", size=11.5, color="#004085", bold=True, anchor="middle"))
    p.append(text(x_start + w_lock + w_dwell + w_guard/2, 112, "T_guard (Буфер дрейфу)", size=10, color=MUTED, anchor="middle"))
    
    # Позначення
    p.append(line(x_start, 150, x_start + w_hop, 150, color=INK, sw=1.5))
    p.append(text(x_start + w_hop/2, 175, "Загальний період стрибка T_hop = T_lock + T_dwell + T_guard", size=11, color=INK, bold=True, anchor="middle"))
    
    p.append(text(x_start + w_lock + w_dwell + w_guard/2, 145, "поглинає ±Δt дрейфу", size=9.5, color="#004085", anchor="middle"))
    p.append(text(x_start + 10, 220, "Стабілізація ФАПЧ -> Модуляція символів -> Захисний часовий інтервал", size=10, color=MUTED))

    render(os.path.join(OUT, "tracking-guard.svg"), W, H, *p)


def fig_acquisition_methods():
    """Схеми початкового захоплення: Beacon, Sliding Correlator, Fast/Slow Scan."""
    W, H = 760, 300
    p = []
    
    p.append(rect(20, 20, 720, 270, fill="#ffffff", stroke="#cccccc", sw=1.2, rx=4))
    p.append(text(40, 45, "Три класичні методи початкового захоплення FHSS-синхронізації", size=13.5, color=INK, bold=True))
    
    # 1. Beacon channel
    p.append(rect(35, 65, 215, 205, fill="#f8faf8", stroke=POS, sw=1.5, rx=3))
    p.append(text(142, 90, "1. Маяковий канал", size=12, color=POS, bold=True, anchor="middle"))
    p.append(text(142, 110, "(Rendezvous Channel)", size=9.5, color=MUTED, anchor="middle"))
    p.append(rect(55, 130, 175, 40, fill="#d4edda", stroke=POS, sw=1.2, rx=2))
    p.append(text(142, 154, "Фіксований Beacon f0", size=10.5, color=POS, bold=True, anchor="middle"))
    p.append(text(142, 190, "Rx чекає на f0", size=10, color=INK, anchor="middle"))
    p.append(text(142, 210, "Tx надсилає Sync Frame", size=10, color=INK, anchor="middle"))
    p.append(text(142, 240, "Швидкий старт", size=9.5, color=MUTED, anchor="middle"))

    # 2. Sliding Correlator
    p.append(rect(272, 65, 215, 205, fill="#fff3cd", stroke=ACCENT, sw=1.5, rx=3))
    p.append(text(380, 90, "2. Ковзний корелятор", size=12, color=ACCENT, bold=True, anchor="middle"))
    p.append(text(380, 110, "(Sliding Correlator)", size=9.5, color=MUTED, anchor="middle"))
    p.append(rect(292, 130, 175, 40, fill="#ffecb3", stroke=ACCENT, sw=1.2, rx=2))
    p.append(text(380, 154, "Rx замирає на ch_k", size=10.5, color=ACCENT, bold=True, anchor="middle"))
    p.append(text(380, 190, "Tx стрибає по сітці", size=10, color=INK, anchor="middle"))
    p.append(text(380, 210, "Перетин на кроці K", size=10, color=INK, anchor="middle"))
    p.append(text(380, 240, "Висока прихованість", size=9.5, color=MUTED, anchor="middle"))

    # 3. Fast/Slow scanning
    p.append(rect(510, 65, 215, 205, fill="#e8f4f8", stroke="#0275d8", sw=1.5, rx=3))
    p.append(text(617, 90, "3. Двошвидкісний скан", size=12, color="#0275d8", bold=True, anchor="middle"))
    p.append(text(617, 110, "(Fast/Slow Scan)", size=9.5, color=MUTED, anchor="middle"))
    p.append(rect(530, 130, 175, 40, fill="#d1ecf1", stroke="#0275d8", sw=1.2, rx=2))
    p.append(text(617, 154, "Rx & Tx стрибають оба", size=10.5, color="#0275d8", bold=True, anchor="middle"))
    p.append(text(617, 190, "Різні швидкості хопу", size=10, color=INK, anchor="middle"))
    p.append(text(617, 210, "Фазовий перетин", size=10, color=INK, anchor="middle"))
    p.append(text(617, 240, "Динамічний компроміс", size=9.5, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "acquisition-methods.svg"), W, H, *p)


if __name__ == "__main__":
    fig_sync_problem()
    fig_tracking_guard()
    fig_acquisition_methods()
    print("SVGs generated successfully.")
