import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def render_quadrature_signals():
    # Width 760, Height 260
    frags = []
    
    # Background panel
    frags.append(rect(10, 10, 740, 240, rx=8, fill="#F8FAFC", stroke="#CBD5E1", sw=1.5))
    
    # Title / section headers
    frags.append(text(30, 35, "Сигнали квадратурного енкодера (Канал A та B) й фазовий зсув 90°", color=INK, size=14, bold=True, anchor="start"))
    
    # Signal A line and waveform
    frags.append(text(30, 80, "Канал A", color=NEG, size=13, bold=True, anchor="start"))
    # A waveform
    d_a = (
        "M 100 95 L 140 95 L 140 60 L 220 60 L 220 95 L 300 95 "
        "L 300 60 L 380 60 L 380 95 L 460 95 L 460 60 L 540 60 L 540 95 L 580 95"
    )
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_a, NEG))
    
    # Signal B line and waveform (shifted by 40px = 90 deg phase shift)
    frags.append(text(30, 140, "Канал B", color=POS, size=13, bold=True, anchor="start"))
    # B waveform
    d_b = (
        "M 100 155 L 180 155 L 180 120 L 260 120 L 260 155 L 340 155 "
        "L 340 120 L 420 120 L 420 155 L 500 155 L 500 120 L 580 120"
    )
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_b, POS))
    
    # Edge vertical guide dashed lines
    edges = [140, 180, 220, 260, 300, 340, 380, 420, 460, 500, 540]
    for i, x in enumerate(edges):
        frags.append(line(x, 50, x, 165, color="#94A3B8", sw=1, dash="3,3"))
        if i < 8:
            frags.append(text(x + 5, 180, f"e{i+1}", color="#64748B", size=10, anchor="start"))

    # Phase annotation arrow / bracket
    frags.append(line(140, 48, 180, 48, color="#475569", sw=1.5))
    frags.append(text(145, 42, "Δφ = 90°", color="#334155", size=11, bold=True, anchor="start"))

    # Quadrature state explanation boxes using fitbox
    frags.append(fitbox(590, 50, 150, 60, "За годинниковою (CW):\nA випереджає B\n(00 -> 10 -> 11 -> 01)", fill="#F1F5F9", stroke="#94A3B8", color=INK, size=10))
    frags.append(fitbox(590, 120, 150, 60, "Проти годинникової (CCW):\nB випереджає A\n(00 -> 01 -> 11 -> 10)", fill="#F1F5F9", stroke="#94A3B8", color=INK, size=10))
    
    # Bottom legend for X1/X2/X4 decoding
    frags.append(fitbox(30, 195, 710, 45, "Режими декодування підсистеми Counter:\n• X1 (Pulse/Dir): тільки передній фронт A   • X2: обидва фронти A\n• X4 (Quadrature X4): передній та задній фронти каналів A і B (4 імпульси/цикл)", fill="#FFFFFF", stroke="#CBD5E1", color=INK, size=11))

    render(os.path.join(IMG, 'quadrature-signals.svg'), 760, 260, *frags, title="Сигнали квадратурного енкодера")

def render_counter_architecture():
    # Width 780, Height 360
    frags = []

    frags.append(rect(10, 10, 760, 340, rx=8, fill="#F8FAFC", stroke="#CBD5E1", sw=1.5))
    frags.append(text(30, 35, "Архітектурні абстракції Linux Counter Subsystem", color=INK, size=15, bold=True, anchor="start"))

    # Box 1: Hardware Inputs / Signals
    frags.append(fitbox(30, 65, 140, 150, "Signal (Сигнал)\n\n• Signal 0: Phase A\n• Signal 1: Phase B\n• Signal 2: Index Z\n(Апаратні входи)", fill="#EEF2FF", stroke="#6366F1", color="#1E1B4B", size=11))

    # Connecting Arrow 1
    frags.append(arrow(170, 140, 210, 140, color="#475569", sw=2))

    # Box 2: Synapse
    frags.append(fitbox(210, 65, 150, 150, "Synapse (Синапс)\n\n• Action A: Both Edges\n• Action B: Both Edges\n• Action Z: Rising Edge\n(Зв'язок входу та дії)", fill="#F0FDF4", stroke="#22C55E", color="#052E16", size=11))

    # Connecting Arrow 2
    frags.append(arrow(360, 140, 400, 140, color="#475569", sw=2))

    # Box 3: Count & Function
    frags.append(fitbox(400, 65, 160, 150, "Count (Лічильник)\n\n• Function:\n  Quadrature X4\n• Value: 64-bit int\n• Extensions:\n  ceiling, floor, mode", fill="#FEF3C7", stroke="#F59E0B", color="#451A03", size=11))

    # Connecting Arrow 3
    frags.append(arrow(560, 140, 600, 140, color="#475569", sw=2))

    # Box 4: Counter Device
    frags.append(fitbox(600, 65, 150, 150, "counter_device\n\nЯдерний пристрій:\nstruct counter_device\nops: read/write\nevents: ring buffer", fill="#F1F5F9", stroke="#475569", color=INK, size=11))

    # Arrow Down to Userspace
    frags.append(arrow(675, 215, 675, 245, color="#475569", sw=2))
    frags.append(arrow(480, 215, 480, 245, color="#475569", sw=2))

    # Userspace box: Sysfs & Chardev
    frags.append(fitbox(30, 245, 450, 85, "Інтерфейс Sysfs (/sys/bus/counter/devices/counter0/)\n• count0/count (значення)    • count0/function (режим)\n• count0/ceiling (межа)     • signal0/signal (рівень)", fill="#FFFFFF", stroke="#94A3B8", color=INK, size=11))

    frags.append(fitbox(500, 245, 250, 85, "Символьний пристрій (/dev/counter0)\n• High-rate events (counter_event)\n• Timestamps (CLOCK_MONOTONIC)\n• Poll/epoll + ring buffer", fill="#EFF6FF", stroke="#3B82F6", color="#1E3A8A", size=11))

    render(os.path.join(IMG, 'counter-architecture-abstractions.svg'), 780, 360, *frags, title="Архітектура підсистеми Counter")

if __name__ == '__main__':
    render_quadrature_signals()
    render_counter_architecture()
