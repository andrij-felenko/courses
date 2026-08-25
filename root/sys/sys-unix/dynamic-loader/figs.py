# -*- coding: utf-8 -*-
import os
import sys

# Path to scripts directory (4 levels up)
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from svgkit import *

def generate_flow_diagram(out_dir):
    width = 900
    height = 560
    
    # Elements list
    elements = [
        ('<?xml version="1.0" encoding="UTF-8"?>'),
        ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (width, height, width, height)),
        ('<defs>'),
        ('<marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'),
        ('<path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % LINE),
        ('</marker>'),
        ('</defs>'),
        (rect(0, 0, width, height, fill=BG, stroke="none")),
        
        # Title
        text(width / 2, 30, "Життєвий цикл запуску та роботи динамічного завантажувача (rtld)", size=18, bold=True, color=INK),
        
        # Outer container for Kernel space
        rect(30, 60, 840, 90, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8),
        text(50, 80, "ЯДРО LINUX (Kernel Space)", size=12, bold=True, color=MUTED, anchor="start"),
        
        # Kernel steps
        textbox(160, 115, "1. execve()\nПеревірка ELF, заголовка PT_INTERP", size=12, pad=8, fill="#e2e8f0", stroke="#64748b")[0],
        arrow(260, 115, 300, 115),
        textbox(430, 115, "2. mmap() сегментів PT_LOAD\nВідображення ELF і ld-linux.so", size=12, pad=8, fill="#e2e8f0", stroke="#64748b")[0],
        arrow(560, 115, 600, 115),
        textbox(720, 115, "3. Формування AUXV\nПередача керування _rtld_start", size=12, pad=8, fill="#e2e8f0", stroke="#64748b")[0],
        
        # Arrow from Kernel to Userspace
        arrow(720, 150, 720, 185),
        
        # Outer container for Userspace loader
        rect(30, 185, 840, 260, fill="#f0f9ff", stroke="#0284c7", sw=1.5, rx=8),
        text(50, 205, "ПРОСТІР КОРИСТУВАЧА: ld-linux.so (rtld)", size=12, bold=True, color="#0369a1", anchor="start"),
        
        # Loader steps inside userspace
        textbox(720, 240, "4. Bootstrap (_dl_start)\nСаморелокація rtld без libc", size=12, pad=8, fill="#e0f2fe", stroke="#0284c7")[0],
        arrow(620, 240, 580, 240),
        textbox(450, 240, "5. Парсинг AUXV та .dynamic\nЗбирання списку DT_NEEDED", size=12, pad=8, fill="#e0f2fe", stroke="#0284c7")[0],
        arrow(320, 240, 280, 240),
        textbox(160, 240, "6. Пошук та mmap() бібліотек\nrpath → LD_LIBRARY_PATH → cache", size=12, pad=8, fill="#e0f2fe", stroke="#0284c7")[0],
        
        arrow(160, 275, 160, 310),
        
        textbox(160, 345, "7. Релокації та Символи\nLoad-time (.got) & Lazy (.plt)", size=12, pad=8, fill="#e0f2fe", stroke="#0284c7")[0],
        arrow(260, 345, 300, 345),
        textbox(450, 345, "8. Конструктори (.init_array)\nВиконання ініціалізаторів .so", size=12, pad=8, fill="#e0f2fe", stroke="#0284c7")[0],
        arrow(600, 345, 640, 345),
        textbox(730, 345, "9. Реєстрація r_debug\nСповіщення налагоджувача", size=12, pad=8, fill="#e0f2fe", stroke="#0284c7")[0],
        
        # Arrow from Loader to Main application
        arrow(730, 380, 730, 470),
        
        # Outer container for Target Application
        rect(30, 460, 840, 80, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8),
        text(50, 480, "ПРОСТІР КОРИСТУВАЧА: ОСНОВНА ПРОГРАМА", size=12, bold=True, color="#15803d", anchor="start"),
        
        textbox(730, 505, "10. Точка входу _start\nПерехід з регістра e_entry", size=12, pad=6, fill="#dcfce7", stroke="#16a34a")[0],
        arrow(640, 505, 590, 505),
        textbox(450, 505, "11. __libc_start_main\nІніціалізація C runtime & env", size=12, pad=6, fill="#dcfce7", stroke="#16a34a")[0],
        arrow(310, 505, 260, 505),
        textbox(160, 505, "12. Виклик main(argc, argv)\nВиконання коду програми", size=12, pad=6, fill="#dcfce7", stroke="#16a34a")[0],
        
        '</svg>'
    ]
    
    filepath = os.path.join(out_dir, 'dynamic-loader-flow.svg')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(elements))
    print(f"Generated {filepath}")

def generate_search_order_diagram(out_dir):
    width = 860
    height = 500
    
    elements = [
        ('<?xml version="1.0" encoding="UTF-8"?>'),
        ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (width, height, width, height)),
        ('<defs>'),
        ('<marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'),
        ('<path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />' % LINE),
        ('</marker>'),
        ('</defs>'),
        (rect(0, 0, width, height, fill=BG, stroke="none")),
        
        text(width / 2, 30, "Порядок і пріоритет пошуку спільних бібліотек (.so)", size=18, bold=True, color=INK),
        
        # Step 1: DT_RPATH
        textbox(430, 80, "1. DT_RPATH (якщо відсутній DT_RUNPATH)\nЗашитий у бінарник шлях. Найвищий пріоритет (застарілий).", size=13, pad=10, fill="#fee2e2", stroke="#dc2626", min_w=760)[0],
        arrow(430, 115, 430, 140),
        
        # Step 2: LD_LIBRARY_PATH
        textbox(430, 165, "2. Змінна середовища LD_LIBRARY_PATH\nШляхи через двокрапку. Ігнорується у SUID/SGID програмах для безпеки.", size=13, pad=10, fill="#fef3c7", stroke="#d97706", min_w=760)[0],
        arrow(430, 200, 430, 225),
        
        # Step 3: DT_RUNPATH
        textbox(430, 250, "3. DT_RUNPATH\nЗашитий у бінарник шлях. Перекривається змінною LD_LIBRARY_PATH.", size=13, pad=10, fill="#e0e7ff", stroke="#4f46e5", min_w=760)[0],
        arrow(430, 285, 430, 310),
        
        # Step 4: /etc/ld.so.cache
        textbox(430, 335, "4. Системний кеш /etc/ld.so.cache\nБінарний індекс усіх бібліотек у системі, згенерований ldconfig.", size=13, pad=10, fill="#dbeafe", stroke="#2563eb", min_w=760)[0],
        arrow(430, 370, 430, 395),
        
        # Step 5: Default paths
        textbox(430, 420, "5. Стандартні системні каталоги\n/lib64, /usr/lib64 (або /lib, /usr/lib відповідно до архітектури).", size=13, pad=10, fill="#f3f4f6", stroke="#4b5563", min_w=760)[0],
        
        '</svg>'
    ]
    
    filepath = os.path.join(out_dir, 'library-search-order-diagram.svg')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(elements))
    print(f"Generated {filepath}")

def main():
    topic_dir = os.path.dirname(__file__)
    img_dir = os.path.join(topic_dir, 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    generate_flow_diagram(img_dir)
    generate_search_order_diagram(img_dir)

if __name__ == '__main__':
    main()
