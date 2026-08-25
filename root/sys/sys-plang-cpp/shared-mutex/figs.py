# -*- coding: utf-8 -*-
import os
import sys

# Path to scripts directory from reference/cpp-standards/concurrency/shared-mutex
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
from svgkit import *

img_dir = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(img_dir, exist_ok=True)

def generate_fig1():
    w, h = 800, 340
    frags = []
    
    # Left Panel: Shared Mode
    frags.append(rect(15, 15, 375, 310, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(202, 42, "Спільний режим (Shared / Read)", size=15, bold=True, color=INK))
    
    # Mutex Box
    b1 = fitbox(102, 68, 200, 48, "std::shared_mutex\n[Лічильник читачів = 3]", size=12, fill="#e8f5e9", stroke=FIELD, sw=1.5)
    frags.append(b1)
    
    # Readers
    r1 = fitbox(35, 145, 100, 42, "Потік R1\n(lock_shared)", size=11, fill="#eaf0fd", stroke=NEG, sw=1.2)
    r2 = fitbox(152, 145, 100, 42, "Потік R2\n(lock_shared)", size=11, fill="#eaf0fd", stroke=NEG, sw=1.2)
    r3 = fitbox(269, 145, 100, 42, "Потік R3\n(lock_shared)", size=11, fill="#eaf0fd", stroke=NEG, sw=1.2)
    frags.extend([r1, r2, r3])
    
    frags.append(arrow(85, 145, 150, 116, color=NEG, sw=1.5))
    frags.append(arrow(202, 145, 202, 116, color=NEG, sw=1.5))
    frags.append(arrow(319, 145, 254, 116, color=NEG, sw=1.5))
    
    # Shared Resource
    res1 = fitbox(52, 230, 300, 65, "Спільний ресурс (стан не змінюється)\nПаралельне читання без взаємного блокування", size=12, fill="#ffffff", stroke="#94a3b8", sw=1.5)
    frags.append(res1)
    
    frags.append(arrow(85, 187, 102, 230, color=NEG, sw=1.5))
    frags.append(arrow(202, 187, 202, 230, color=NEG, sw=1.5))
    frags.append(arrow(319, 187, 302, 230, color=NEG, sw=1.5))

    # Right Panel: Exclusive Mode
    frags.append(rect(410, 15, 375, 310, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(597, 42, "Виключний режим (Exclusive / Write)", size=15, bold=True, color=INK))
    
    # Mutex Box
    b2 = fitbox(497, 68, 200, 48, "std::shared_mutex\n[Прапорець запису = 1]", size=12, fill="#fdecea", stroke=POS, sw=1.5)
    frags.append(b2)
    
    # Writer
    w1 = fitbox(430, 145, 110, 42, "Потік W1\n(lock)", size=11, fill="#fdecea", stroke=POS, sw=1.5)
    frags.append(w1)
    frags.append(arrow(485, 145, 547, 116, color=POS, sw=1.8))
    
    # Blocked Readers Queue
    q1 = fitbox(580, 145, 185, 42, "Черга очікування:\nПотік R4, R5 (блоковані)", size=11, fill="#fff7ed", stroke="#f97316", sw=1.2, dash="4,3")
    frags.append(q1)
    frags.append(line(672, 145, 647, 116, color="#f97316", sw=1.5, dash="3,3"))
    
    # Exclusive Resource
    res2 = fitbox(447, 230, 300, 65, "Спільний ресурс (модифікація стану)\nПовний монопольний доступ одного потоку", size=12, fill="#ffffff", stroke="#94a3b8", sw=1.5)
    frags.append(res2)
    
    frags.append(arrow(485, 187, 547, 230, color=POS, sw=1.8))

    render(os.path.join(img_dir, "shared-vs-exclusive.svg"), w, h, *frags)

def generate_fig2():
    w, h = 820, 360
    frags = []
    
    # 4 Main States
    s_unlocked = fitbox(40, 140, 180, 75, "ВІЛЬНИЙ СТАН\nЛічильник = 0\nПисьменник = 0", size=12, fill="#f4f6f8", stroke="#64748b", sw=1.8)
    s_shared   = fitbox(320, 40, 200, 75, "СПІЛЬНЕ ЧИТАННЯ\nЛічильник читачів R > 0\nПисьменник = 0", size=12, fill="#eaf0fd", stroke=NEG, sw=1.8)
    s_excl     = fitbox(320, 240, 200, 75, "ВИКЛЮЧНИЙ ЗАПИС\nЛічильник читачів = 0\nПрапорець запису = 1", size=12, fill="#fdecea", stroke=POS, sw=1.8)
    s_pending  = fitbox(600, 140, 180, 75, "ОЧІКУВАННЯ ЗАПИСУ\nWriters Pending > 0\nНові читачі блокуються", size=12, fill="#fff7ed", stroke="#f97316", sw=1.8)
    
    frags.extend([s_unlocked, s_shared, s_excl, s_pending])
    
    # Transitions
    # Unlocked -> Shared
    frags.append(arrow(150, 140, 320, 95, color=NEG, sw=1.6))
    frags.append(text(210, 105, "lock_shared()", size=11, color=NEG, bold=True))
    
    # Shared -> Unlocked
    frags.append(arrow(320, 110, 190, 155, color="#64748b", sw=1.5))
    frags.append(text(220, 148, "unlock_shared() [R=0]", size=10, color="#64748b"))

    # Unlocked -> Exclusive
    frags.append(arrow(150, 215, 320, 260, color=POS, sw=1.6))
    frags.append(text(210, 255, "lock()", size=11, color=POS, bold=True))
    
    # Exclusive -> Unlocked
    frags.append(arrow(320, 275, 190, 230, color="#64748b", sw=1.5))
    frags.append(text(220, 230, "unlock()", size=10, color="#64748b"))

    # Shared -> Pending (when writer arrives)
    frags.append(arrow(520, 80, 630, 140, color="#f97316", sw=1.6))
    frags.append(text(600, 95, "lock() під час читання", size=11, color="#f97316", bold=True))

    # Pending -> Exclusive (when R hits 0)
    frags.append(arrow(630, 215, 520, 275, color=POS, sw=1.6))
    frags.append(text(600, 260, "R досягає 0 -> запис", size=11, color=POS, bold=True))

    render(os.path.join(img_dir, "shared-mutex-state-machine.svg"), w, h, *frags)

def generate_fig3():
    w, h = 800, 360
    frags = []
    
    # Sequence diagram headers
    h1 = fitbox(120, 30, 180, 45, "Потік A (Reader 1)", size=13, fill="#eaf0fd", stroke=NEG, sw=1.5)
    h2 = fitbox(500, 30, 180, 45, "Потік B (Reader 2)", size=13, fill="#eaf0fd", stroke=NEG, sw=1.5)
    frags.extend([h1, h2])
    
    # Vertical lifelines
    frags.append(line(210, 75, 210, 330, color="#cbd5e1", sw=1.5, dash="4,4"))
    frags.append(line(590, 75, 590, 330, color="#cbd5e1", sw=1.5, dash="4,4"))
    
    # Step 1: Thread A acquires shared lock
    frags.append(rect(195, 95, 30, 40, fill="#e8f5e9", stroke=FIELD, sw=1.2))
    frags.append(text(210, 90, "1. lock_shared() — УСПІХ", size=11, color=FIELD, anchor="middle", bold=True))
    
    # Step 2: Thread B acquires shared lock
    frags.append(rect(575, 135, 30, 40, fill="#e8f5e9", stroke=FIELD, sw=1.2))
    frags.append(text(590, 130, "2. lock_shared() — УСПІХ", size=11, color=FIELD, anchor="middle", bold=True))
    
    # Step 3: Thread A wants to UPGRADE -> calls lock()
    frags.append(rect(195, 185, 30, 120, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(arrow(210, 195, 575, 195, color=POS, sw=1.5))
    frags.append(text(390, 188, "3. Спроба lock(): чекає завершення Потоку B", size=11, color=POS, bold=True))
    
    # Step 4: Thread B also wants to UPGRADE -> calls lock()
    frags.append(rect(575, 225, 30, 80, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(arrow(590, 235, 225, 235, color=POS, sw=1.5))
    frags.append(text(390, 228, "4. Спроба lock(): чекає завершення Потоку A", size=11, color=POS, bold=True))

    # Deadlock Alert Box
    d_box = fitbox(280, 280, 240, 50, "ГЛУХИЙ КУТ (DEADLOCK)!\nОбидва потоки чекають один одного", size=12, fill="#fdecea", stroke=POS, sw=2, bold=True)
    frags.append(d_box)

    render(os.path.join(img_dir, "lock-upgrade-deadlock.svg"), w, h, *frags)

if __name__ == "__main__":
    generate_fig1()
    generate_fig2()
    generate_fig3()
    print("Figures generated successfully.")
