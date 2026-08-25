import sys
import os

# Four levels up to reach repository root scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_struct_layout():
    # Diagram comparing Struct Layout v1 vs Struct Layout v2 (ABI Break)
    w, h = 720, 240
    
    out = []
    out.append('<svg width="%d" height="%d" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">' % (w, h, w, h))
    out.append('<style>text { font-family: %s; }</style>' % FONT)
    out.append(rect(0, 0, w, h, fill=BG, stroke=BG))
    
    # Title V1
    out.append(text(360, 22, "Версія 1: struct Data { char a; int b; } — 8 байтів", size=14, bold=True))
    
    # Byte offset ruler V1
    offsets_v1 = [(50, "0x00"), (130, "0x01"), (370, "0x04"), (670, "0x08")]
    for x_pos, label in offsets_v1:
        out.append(text(x_pos, 42, label, size=11, color=MUTED, anchor="start"))
    
    # Blocks V1
    b1, _, _ = textbox(90, 70, "char a\n(1 B)", size=12, pad=6, fill="#d5f5e3", stroke=FIELD, bold=True)
    out.append(b1)
    
    b2, _, _ = textbox(250, 70, "Padding (3 байти відступу)\nдля вирівнювання int", size=12, pad=6, fill="#f2f4f4", stroke=MUTED)
    out.append(b2)
    
    b3, _, _ = textbox(520, 70, "int b\n(4 байти)", size=12, pad=6, fill="#ebf5fb", stroke=NEG, bold=True)
    out.append(b3)
    
    # Separator line
    out.append(line(40, 115, 680, 115, color=MUTED, sw=1, dash="4"))
    
    # Title V2
    out.append(text(360, 137, "Версія 2 (ПОЛОМКА ABI): вставка short c між a та b", size=14, bold=True, color=POS))
    
    # Byte offset ruler V2
    offsets_v2 = [(50, "0x00"), (130, "0x01"), (210, "0x02"), (510, "0x04")]
    for x_pos, label in offsets_v2:
        out.append(text(x_pos, 157, label, size=11, color=MUTED, anchor="start"))

    # Blocks V2
    b4, _, _ = textbox(90, 185, "char a\n(1 B)", size=12, pad=6, fill="#d5f5e3", stroke=FIELD, bold=True)
    out.append(b4)
    
    b5, _, _ = textbox(170, 185, "pad\n(1 B)", size=12, pad=6, fill="#f2f4f4", stroke=MUTED)
    out.append(b5)
    
    b6, _, _ = textbox(360, 185, "short c (2 байти)\n[Нове поле зісуває наступні!]", size=12, pad=6, fill="#fadbd8", stroke=POS, bold=True)
    out.append(b6)
    
    b7, _, _ = textbox(590, 185, "int b\n(зсув змінено)", size=12, pad=6, fill="#ebf5fb", stroke=NEG, bold=True)
    out.append(b7)

    out.append("</svg>")
    
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    with open(os.path.join(img_dir, "struct-layout.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))

def generate_vtable_layout():
    # Diagram showing object vptr pointing to vtable and broken call after adding virtual function
    w, h = 720, 260
    
    out = []
    out.append('<svg width="%d" height="%d" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">' % (w, h, w, h))
    out.append('<style>text { font-family: %s; }</style>' % FONT)
    out.append(rect(0, 0, w, h, fill=BG, stroke=BG))

    # Left box: Compiled Client Code Expectations (V1 vtable)
    out.append(text(200, 25, "Старий клієнт очікує vtable V1", size=14, bold=True))
    
    tb1, _, _ = textbox(200, 70, "Об'єкт у пам'яті (Object)\n[ vptr (8 B) ] ──┐\n[ int data   ]   │", size=12, pad=8, fill="#ebf5fb", stroke=NEG)
    out.append(tb1)
    
    tb2, _, _ = textbox(200, 170, "Таблиця vtable (V1):\n[0] &Widget::draw()  <-- call obj->draw()\n[1] &Widget::resize()", size=12, pad=8, fill="#d5f5e3", stroke=FIELD)
    out.append(tb2)
    
    out.append(arrow(200, 105, 200, 130, color=NEG, sw=2))

    # Right box: New Library Header with Prepended Virtual Function (V2 vtable)
    out.append(text(520, 25, "Нова бібліотека V2 (Вставка у vtable)", size=14, bold=True, color=POS))
    
    tb3, _, _ = textbox(520, 70, "Об'єкт у пам'яті (Object)\n[ vptr (8 B) ] ──┐\n[ int data   ]   │", size=12, pad=8, fill="#ebf5fb", stroke=NEG)
    out.append(tb3)

    tb4, _, _ = textbox(520, 175, "Таблиця vtable (V2):\n[0] &Widget::audit()  [НОВА віртуальна!]\n[1] &Widget::draw()   <-- Зсунуто індекс!\n[2] &Widget::resize()", size=12, pad=8, fill="#fadbd8", stroke=POS)
    out.append(tb4)

    out.append(arrow(520, 105, 520, 135, color=NEG, sw=2))

    # Warning annotation at the bottom
    out.append(text(360, 242, "Виклик obj->draw() (індекс 0 у старому коді) виконає &Widget::audit() -> Сбій!", size=13, bold=True, color=POS))

    out.append("</svg>")
    
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    with open(os.path.join(img_dir, "vtable-layout.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))

if __name__ == "__main__":
    generate_struct_layout()
    generate_vtable_layout()
    print("Figures generated successfully.")
