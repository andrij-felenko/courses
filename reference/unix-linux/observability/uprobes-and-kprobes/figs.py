import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))

from svgkit import render, rect, text, line, arrow, textbox, mtext, INK, FIELD, POS, NEG, MUTED

def draw_kprobes():
    frags = []
    
    # Kernel Memory
    frags.append(rect(100, 50, 250, 220, fill="#f9f9f9"))
    frags.append(text(225, 40, "Пам'ять ядра (Kernel Memory)", bold=True, color=INK))
    
    # Original Instructions
    frags.append(rect(120, 70, 210, 30, fill="#ffffff"))
    frags.append(text(225, 90, "Інструкція 1", color=MUTED))
    
    # Target Instruction (INT3)
    frags.append(rect(120, 110, 210, 30, fill="#fdecea", stroke=POS))
    frags.append(text(225, 130, "INT3 (0xCC) - kprobe", color=POS, bold=True))
    
    frags.append(rect(120, 150, 210, 30, fill="#ffffff"))
    frags.append(text(225, 170, "Інструкція 3", color=MUTED))
    
    # OOL Buffer
    frags.append(rect(120, 200, 210, 50, fill="#eaf0fd", stroke=NEG))
    frags.append(text(225, 220, "OOL Буфер (Out-of-line)", color=NEG, bold=True))
    frags.append(text(225, 240, "[Копія оригінальної Інструкції 2]", size=12))

    # Kprobes Framework
    frags.append(rect(450, 70, 250, 160, fill="#e8f5e9", stroke=FIELD))
    frags.append(text(575, 95, "kprobe_handler()", bold=True, size=16))
    
    # Handler Steps
    h_steps = "1. Виклик pre_handler\n2. Налаштування EIP/RIP\n   на OOL Буфер\n3. Single-step"
    tb, w, h = textbox(575, 160, h_steps, fill="#ffffff", stroke="#a5d6a7")
    frags.append(tb)

    # Arrows
    # INT3 to Handler
    frags.append(arrow(330, 125, 450, 125, color=POS, sw=2))
    frags.append(text(390, 115, "Exception #BP", size=12, color=POS))
    
    # Handler to OOL
    frags.append(arrow(575, 230, 330, 225, color=FIELD, sw=2))
    frags.append(text(450, 240, "single-step (виконання)", size=12, color=FIELD))
    
    # OOL back to next instruction
    frags.append(arrow(120, 225, 80, 225, color=NEG, sw=2))
    frags.append(arrow(80, 225, 80, 165, color=NEG, sw=2))
    frags.append(arrow(80, 165, 120, 165, color=NEG, sw=2))
    frags.append(text(100, 195, "повернення", size=12, color=NEG, anchor="start"))
    
    render('kprobes-int3-insertion.svg', 750, 320, *frags, title="Архітектура Kprobes: вставка INT3 та OOL-буфер")

if __name__ == '__main__':
    draw_kprobes()
