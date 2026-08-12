# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_store_buffer_architecture(filepath):
    w, h = 840, 480
    elems = []
    
    elems.append(text(w/2, 28, "Апаратна підсистема пам'яті: Store Buffers та Invalidate Queues", size=18, bold=True, color=INK))
    
    # Core 0 Block (Producer)
    elems.append(rect(30, 60, 370, 240, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    elems.append(text(215, 85, "Ядро CPU 0 (Producer)", size=15, bold=True, color=NEG))
    
    elems.append(textbox(215, 125, "Конвеєр виконання (Out-of-Order)\nWRITE data = 42; WRITE flag = 1;", size=12, fill="#e0f2fe", stroke=NEG, pad=8)[0])
    elems.append(arrow(215, 150, 215, 185, color=NEG))
    
    elems.append(textbox(215, 220, "Store Buffer (Буфер відкладеного запису)\n[data=42 (затримується)] -> [flag=1 (скидається)]", size=12, fill="#fee2e2", stroke=POS, pad=8)[0])
    elems.append(arrow(215, 255, 215, 305, color=POS))
    
    # Core 1 Block (Consumer)
    elems.append(rect(440, 60, 370, 240, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    elems.append(text(625, 85, "Ядро CPU 1 (Consumer)", size=15, bold=True, color=NEG))
    
    elems.append(textbox(625, 125, "Конвеєр виконання (Out-of-Order)\nREAD flag (==1); READ data (==0! Спекулятивно)", size=12, fill="#e0f2fe", stroke=NEG, pad=8)[0])
    elems.append(arrow(625, 185, 625, 150, color=NEG))
    
    elems.append(textbox(625, 220, "Invalidate Queue (Черга інвалідації кешу)\n[Запит інвалідації data затримано в черзі]", size=12, fill="#fef3c7", stroke="#d97706", pad=8)[0])
    elems.append(arrow(625, 305, 625, 255, color="#d97706"))
    
    # L1 Caches
    elems.append(textbox(215, 345, "L1 Cache Core 0 (MESI: Modified / Exclusive)", size=13, fill="#f1f5f9", stroke=LINE, pad=8)[0])
    elems.append(textbox(625, 345, "L1 Cache Core 1 (MESI: Shared / Invalid)", size=13, fill="#f1f5f9", stroke=LINE, pad=8)[0])
    
    elems.append(arrow(215, 370, 215, 410, color=LINE))
    elems.append(arrow(625, 370, 625, 410, color=LINE))
    
    # Interconnect Bus / L2/L3 RAM
    elems.append(rect(100, 410, 640, 50, fill="#e2e8f0", stroke="#475569", sw=1.8, rx=6))
    elems.append(text(420, 440, "Системна шина інтерконнекту (Interconnect) та спільний L3 Кеш / RAM", size=14, bold=True, color=INK))
    
    # Memory barrier annotation box
    elems.append(textbox(420, 300, "smp_wmb() примусово флешить Store Buffer | smp_rmb() спорожнює Invalidate Queue", size=12, fill="#dcfce7", stroke=FIELD, pad=6, bold=True)[0])
    
    body = "\n".join(elems)
    return render(filepath, w, h, body)

def build_reordering_taxonomy(filepath):
    w, h = 840, 420
    elems = []
    
    elems.append(text(w/2, 28, "Таксономія перевпорядкування операцій у процесорних архітектурах", size=18, bold=True, color=INK))
    
    # Table headers
    elems.append(rect(40, 60, 230, 40, fill="#e2e8f0", stroke=LINE, sw=1.5))
    elems.append(text(155, 85, "Тип реодерингу", size=14, bold=True))
    
    elems.append(rect(270, 60, 170, 40, fill="#e2e8f0", stroke=LINE, sw=1.5))
    elems.append(text(355, 85, "x86-64 (TSO)", size=14, bold=True))
    
    elems.append(rect(440, 60, 170, 40, fill="#e2e8f0", stroke=LINE, sw=1.5))
    elems.append(text(525, 85, "ARM64 / RISC-V", size=14, bold=True))
    
    elems.append(rect(610, 60, 190, 40, fill="#e2e8f0", stroke=LINE, sw=1.5))
    elems.append(text(705, 85, "DEC Alpha (Historical)", size=14, bold=True))
    
    rows = [
        ("Load -> Load (Читання після Читання)", "Заборонено (OK)", "Дозволено (Weak)", "Дозволено (Weak)"),
        ("Load -> Store (Запис після Читання)", "Заборонено (OK)", "Дозволено (Weak)", "Дозволено (Weak)"),
        ("Store -> Store (Запис після Запису)", "Заборонено (OK)", "Дозволено (Weak)", "Дозволено (Weak)"),
        ("Store -> Load (Читання після Запису)", "ДОЗВОЛЕНО (StoreBuf)", "Дозволено (Weak)", "Дозволено (Weak)"),
        ("Dependent Load (Залежні читання)", "Заборонено (OK)", "Заборонено (OK)", "ДОЗВОЛЕНО (Extreme!)")
    ]
    
    y = 100
    for title, x86_stat, arm_stat, alpha_stat in rows:
        elems.append(rect(40, y, 230, 50, fill="#f8fafc", stroke=LINE))
        elems.append(text(155, y + 30, title, size=12, bold=True))
        
        # x86 box
        f_x86 = "#dcfce7" if "Заборонено" in x86_stat else "#fee2e2"
        s_x86 = FIELD if "Заборонено" in x86_stat else POS
        elems.append(rect(270, y, 170, 50, fill=f_x86, stroke=s_x86))
        elems.append(text(355, y + 30, x86_stat, size=12, bold=True, color=INK))
        
        # ARM box
        f_arm = "#fee2e2" if "Дозволено" in arm_stat else "#dcfce7"
        s_arm = POS if "Дозволено" in arm_stat else FIELD
        elems.append(rect(440, y, 170, 50, fill=f_arm, stroke=s_arm))
        elems.append(text(525, y + 30, arm_stat, size=12, bold=True, color=INK))
        
        # Alpha box
        f_alp = "#fef3c7" if "Extreme" in alpha_stat else "#fee2e2"
        s_alp = "#d97706" if "Extreme" in alpha_stat else POS
        elems.append(rect(610, y, 190, 50, fill=f_alp, stroke=s_alp))
        elems.append(text(705, y + 30, alpha_stat, size=12, bold=True, color=INK))
        
        y += 50
        
    elems.append(textbox(420, 385, "x86 вимагає smp_mb() лише для Store-Load. ARM64 вимагає Acq/Rel або DMB для всіх типів.", size=12, fill="#f1f5f9", stroke=LINE, pad=6)[0])
    
    body = "\n".join(elems)
    return render(filepath, w, h, body)

def build_acquire_release_flow(filepath):
    w, h = 860, 420
    elems = []
    
    elems.append(text(w/2, 28, "Причинно-наслідковий зв'язок (Happens-Before) у Acquire-Release", size=18, bold=True, color=INK))
    
    # Thread 1 Container
    elems.append(rect(30, 60, 360, 300, fill="#faf5ff", stroke="#a855f7", sw=1.5, rx=8))
    elems.append(text(210, 85, "Потік 1: Виробник (Producer)", size=15, bold=True, color="#7e22ce"))
    
    elems.append(textbox(210, 140, "1. Підготовка даних:\nWRITE payload = 0xDEADBEEF;", size=12, fill="#ffffff", stroke=LINE, pad=8)[0])
    elems.append(arrow(210, 175, 210, 215, color=LINE))
    
    elems.append(textbox(210, 270, "2. Публікація з Release:\nsmp_store_release(&ready, 1);\n[Бар'єр запису ВЕРХУ]", size=12, fill="#f3e8ff", stroke="#7e22ce", pad=8, bold=True)[0])
    
    # Thread 2 Container
    elems.append(rect(470, 60, 360, 300, fill="#eff6ff", stroke=NEG, sw=1.5, rx=8))
    elems.append(text(650, 85, "Потік 2: Споживач (Consumer)", size=15, bold=True, color=NEG))
    
    elems.append(textbox(650, 140, "1. Зчитання з Acquire:\nif (smp_load_acquire(&ready) == 1)\n[Бар'єр читання НИЖЧУ]", size=12, fill="#dbeafe", stroke=NEG, pad=8, bold=True)[0])
    elems.append(arrow(650, 185, 650, 225, color=NEG))
    
    elems.append(textbox(650, 270, "2. Використання даних:\nREAD payload (гарантовано 0xDEADBEEF!)", size=12, fill="#ffffff", stroke=LINE, pad=8)[0])
    
    # Label Box for Synchronizes-With positioned above the diagonal
    elems.append(textbox(430, 130, "Синхронізація\n(Synchronizes-With)", size=11, fill="#dcfce7", stroke=FIELD, pad=6, bold=True)[0])
    
    # Single clean connecting arrow from Thread 1 Release to Thread 2 Acquire
    elems.append(arrow(345, 270, 520, 160, color=FIELD, sw=2.2))
    
    elems.append(textbox(430, 390, "Операції до Release НЕ випливають нижче. Операції після Acquire НЕ піднімаються вище.", size=12, fill="#f1f5f9", stroke=LINE, pad=6)[0])
    
    body = "\n".join(elems)
    return render(filepath, w, h, body)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    
    build_store_buffer_architecture(os.path.join(img_dir, "store-buffer-architecture.svg"))
    build_reordering_taxonomy(os.path.join(img_dir, "reordering-taxonomy.svg"))
    build_acquire_release_flow(os.path.join(img_dir, "acquire-release-flow.svg"))
    print("All SVGs generated successfully.")

if __name__ == "__main__":
    main()
