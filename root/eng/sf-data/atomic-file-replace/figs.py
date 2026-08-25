# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARN_FILL, WARN_STROKE = "#fff6e0", "#caa24a"
GOOD_FILL, GOOD_STROKE = "#eef6ef", FIELD
NEW_FILL, NEW_STROKE = "#eaf0fd", NEG
ERR_FILL, ERR_STROKE = "#fdecea", POS


# ── 1. Прямий запис проти атомарної заміни ─────────────────────────────────────
def fig_naive_vs_atomic():
    W, H = 760, 360
    p = []
    
    # Заголовок зверху
    p.append(rect(20, 15, 720, 150, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=6))
    p.append(text(40, 40, "Прямий запис на місці (in-place truncate & write) — небезпечно", size=13, color=POS, bold=True, anchor="start"))
    
    # Кроки наївного підходу
    b1, _, _ = textbox(140, 95, "1. open(..., O_TRUNC)\nРозмір стає 0 байтів;\nстарі дані стерто з кешу", size=11, color=INK, fill="#ffffff", stroke="#d0d7de", sw=1.2, pad=8)
    p.append(b1)
    p.append(arrow(220, 95, 260, 95, color=MUTED, sw=1.4))
    
    b2, _, _ = textbox(345, 95, "2. write(buf, 4096)\nЗаписано першу частину;\nдані лише в RAM", size=11, color=INK, fill="#ffffff", stroke="#d0d7de", sw=1.2, pad=8)
    p.append(b2)
    p.append(arrow(430, 95, 470, 95, color=POS, sw=1.6))
    
    b3, _, _ = textbox(595, 95, "3. ЗБІЙ ЖИВЛЕННЯ!\nФайл порожній (0 байтів)\nабо містить уривок сміття", size=11, color=POS, fill=ERR_FILL, stroke=ERR_STROKE, sw=1.5, bold=True, pad=8)
    p.append(b3)

    # Нижня панель: атомарна заміна
    p.append(rect(20, 185, 720, 155, fill="#f6fcf7", stroke="#c3e6cb", sw=1.2, rx=6))
    p.append(text(40, 210, "Атомарна заміна через тимчасовий файл (write-fsync-rename) — надійно", size=13, color=FIELD, bold=True, anchor="start"))
    
    c1, _, _ = textbox(135, 270, "1. Запис у .tmp-файл\nОригінал недоторканий;\nчитачі бачать старе ціле", size=11, color=INK, fill="#ffffff", stroke="#c3e6cb", sw=1.2, pad=8)
    p.append(c1)
    p.append(arrow(215, 270, 255, 270, color=FIELD, sw=1.4))
    
    c2, _, _ = textbox(340, 270, "2. fsync() тимчасового\nУсі нові байти й інод\nскинуто на фізичний диск", size=11, color=INK, fill="#ffffff", stroke="#c3e6cb", sw=1.2, pad=8)
    p.append(c2)
    p.append(arrow(425, 270, 465, 270, color=FIELD, sw=1.4))
    
    c3, _, _ = textbox(595, 270, "3. rename() + fsync(dir)\nМиттєва підміна покажчика;\nстан завжди 100% цілий", size=11, color=FIELD, fill=GOOD_FILL, stroke=GOOD_STROKE, sw=1.5, bold=True, pad=8)
    p.append(c3)
    
    return render(os.path.join(OUT, "naive-vs-atomic.svg"), W, H, *p)


# ── 2. Повний 6-кроковий конвеєр надійного оновлення ───────────────────────────
def fig_six_step_pipeline():
    W, H = 760, 390
    p = []
    
    # Сітка з 6 кроків у два ряди по три
    steps = [
        ("Крок 1: open(.tmp, O_CREAT|O_EXCL)", "Створення тимчасового файлу\nу ТОМУ САМОМУ каталозі\n(той самий розділ / суперблок)", NEW_FILL, NEW_STROKE, NEG),
        ("Крок 2: write() у циклі", "Повний запис корисного навантаження\nз обробкою неповної видачі\n(дані потрапляють у Page Cache)", "#ffffff", "#d0d7de", INK),
        ("Крок 3: fsync(file_fd)", "Примусове скидання кешу ОС\nта енергонезалежного буфера диска\n(гарантія збереження байтів)", WARN_FILL, WARN_STROKE, "#9a6700"),
        ("Крок 4: close(file_fd)", "Закриття файлового дескриптора\n(звільнення запису в таблиці ОС;\nдані вже збережено на диску)", "#ffffff", "#d0d7de", INK),
        ("Крок 5: rename(tmp, target)", "Атомарне перемикання запису dentry\nу структурі каталогу файлової системи\n(неподільна операція для читачів)", GOOD_FILL, GOOD_STROKE, FIELD),
        ("Крок 6: fsync(dir_fd)", "Фіксація оновленого каталогу на диску\n(захист від зникнення нового імені\nпісля відновлення журналів)", GOOD_FILL, GOOD_STROKE, FIELD)
    ]
    
    box_w, box_h = 220, 115
    xs = [30, 270, 510]
    ys = [40, 210]
    
    for i, (hdr, desc, fill_c, strk_c, txt_c) in enumerate(steps):
        r_idx = i // 3
        c_idx = i % 3
        bx = xs[c_idx]
        by = ys[r_idx]
        
        p.append(rect(bx, by, box_w, box_h, fill=fill_c, stroke=strk_c, sw=1.5, rx=6))
        p.append(text(bx + box_w / 2, by + 24, hdr, size=11, color=txt_c, bold=True))
        p.append(line(bx + 10, by + 34, bx + box_w - 10, by + 34, color=strk_c, sw=0.8))
        
        lines = desc.split("\n")
        for l_idx, ln in enumerate(lines):
            p.append(text(bx + box_w / 2, by + 54 + l_idx * 17, ln, size=10, color=INK))
            
    # Стрілки між кроками
    # 1 -> 2
    p.append(arrow(xs[0] + box_w + 2, ys[0] + box_h / 2, xs[1] - 4, ys[0] + box_h / 2, color=INK, sw=1.5))
    # 2 -> 3
    p.append(arrow(xs[1] + box_w + 2, ys[0] + box_h / 2, xs[2] - 4, ys[0] + box_h / 2, color=INK, sw=1.5))
    # 3 -> 4 (з правого верхнього вниз)
    p.append(line(xs[2] + box_w / 2, ys[0] + box_h + 2, xs[2] + box_w / 2, ys[1] - 18, color=INK, sw=1.5))
    p.append(arrow(xs[2] + box_w / 2, ys[1] - 18, xs[2] + box_w / 2, ys[1] - 4, color=INK, sw=1.5))
    # 4 -> 5 (наліво)
    p.append(arrow(xs[2] - 2, ys[1] + box_h / 2, xs[1] + box_w + 4, ys[1] + box_h / 2, color=INK, sw=1.5))
    # 5 -> 6 (наліво)
    p.append(arrow(xs[1] - 2, ys[1] + box_h / 2, xs[0] + box_w + 4, ys[1] + box_h / 2, color=INK, sw=1.5))
    
    # Нижній висновок
    p.append(text(W / 2, 360, "Результат: при збої на будь-якому кроці 1–4 цілий старий файл; після кроку 5–6 — новий", size=12, color=FIELD, bold=True))
    
    return render(os.path.join(OUT, "six-step-pipeline.svg"), W, H, *p)


# ── 3. Перемикання покажчиків інодів у каталозі ─────────────────────────────────
def fig_inode_dentry_swap():
    W, H = 760, 320
    p = []
    
    # Каталог (Directory)
    p.append(rect(40, 40, 240, 240, fill="#f8f9fa", stroke="#6c757d", sw=1.5, rx=6))
    p.append(text(160, 68, "Каталог (dentry namespace)", size=13, color=INK, bold=True))
    p.append(line(55, 80, 265, 80, color="#adb5bd", sw=1))
    
    # Записи dentry
    p.append(rect(55, 100, 210, 55, fill="#ffffff", stroke="#495057", sw=1.2, rx=4))
    p.append(text(160, 122, 'Ім\'я: "config.json"', size=12, color=INK, bold=True))
    p.append(text(160, 142, "Вказівник: Інод #401", size=11, color=FIELD, bold=True))
    
    p.append(rect(55, 185, 210, 65, fill="#fff3cd", stroke="#ffc107", sw=1.2, rx=4))
    p.append(text(160, 206, 'Було: ".config.json.tmp"', size=11, color="#856404"))
    p.append(text(160, 224, "Вказівник: Інод #402", size=11, color=NEG, bold=True))
    p.append(text(160, 241, "(вилучено після rename)", size=10, color=MUTED, italic=True))
    
    # Іноди праворуч
    # Старий інод
    p.append(rect(470, 40, 250, 110, fill=GOOD_FILL, stroke=GOOD_STROKE, sw=1.5, rx=6))
    p.append(text(595, 65, "Старий Інод #401 (версія 1)", size=12, color=FIELD, bold=True))
    p.append(text(595, 87, "Блоки даних: [A1, A2, A3]", size=11, color=INK))
    p.append(text(595, 107, "Посилання: link_count = 0", size=11, color=POS))
    p.append(text(595, 127, "Читач A тримає відкритий fd → читає далі", size=10, color=MUTED, italic=True))
    
    # Новий інод
    p.append(rect(470, 170, 250, 110, fill=NEW_FILL, stroke=NEW_STROKE, sw=1.5, rx=6))
    p.append(text(595, 195, "Новий Інод #402 (версія 2)", size=12, color=NEG, bold=True))
    p.append(text(595, 217, "Блоки даних: [B1, B2, B3, B4]", size=11, color=INK))
    p.append(text(595, 237, "Посилання: link_count = 1", size=11, color=FIELD, bold=True))
    p.append(text(595, 257, "Нові open() відкривають саме цей інод", size=10, color=FIELD, italic=True))
    
    # Стрілки перемикання
    # Перекреслена стрілка до старого інода
    p.append(line(265, 120, 465, 85, color=POS, sw=1.4, dash="4 3"))
    p.append(text(355, 92, "перервано", size=10, color=POS, bold=True))
    
    # Нова активна стрілка до нового інода
    p.append(arrow(265, 135, 465, 215, color=FIELD, sw=2.2))
    p.append(text(375, 185, "rename()", size=12, color=FIELD, bold=True))
    
    return render(os.path.join(OUT, "inode-dentry-swap.svg"), W, H, *p)


# ── 4. Загроза пропущеного fsync батьківського каталогу ────────────────────────
def fig_directory_fsync_hazard():
    W, H = 760, 310
    p = []
    
    # Оперативна пам'ять (Page Cache)
    p.append(rect(40, 35, 310, 200, fill="#eef2f7", stroke="#4a69bd", sw=1.5, rx=6))
    p.append(text(195, 60, "Оперативна пам'ять (RAM / Page Cache)", size=12, color=NEG, bold=True))
    
    b_ram1, _, _ = textbox(195, 105, "Каталог оновлено:\nconfig.json → Інод #402 (новий)", size=11, color=FIELD, fill="#ffffff", stroke="#4a69bd", sw=1.2, pad=8)
    p.append(b_ram1)
    
    b_ram2, _, _ = textbox(195, 175, "Інод #402 та його блоки скинуто,\nале запис каталогу лишився брудним!", size=10, color=POS, fill=ERR_FILL, stroke=ERR_STROKE, sw=1.2, pad=8)
    p.append(b_ram2)
    
    # Фізичний диск
    p.append(rect(410, 35, 310, 200, fill="#fdfbf7", stroke="#e58e26", sw=1.5, rx=6))
    p.append(text(565, 60, "Фізичний накопичувач (Disk / NVMe)", size=12, color="#9a6700", bold=True))
    
    b_dsk1, _, _ = textbox(565, 105, "Каталог на диску (старий стан):\nconfig.json → Інод #401 (старий)", size=11, color=POS, fill="#ffffff", stroke="#e58e26", sw=1.2, pad=8)
    p.append(b_dsk1)
    
    b_dsk2, _, _ = textbox(565, 175, "Інод #402 записано, але каталог\nне вказує на нього (сирота в lost+found)", size=10, color=MUTED, fill="#ffffff", stroke="#d0d7de", sw=1.2, pad=8)
    p.append(b_dsk2)
    
    # Збій між ними
    p.append(line(380, 20, 380, 250, color=POS, sw=2, dash="5 4"))
    p.append(text(380, 268, "ЗБІЙ ЖИВЛЕННЯ ДО fsync(dir_fd)", size=11, color=POS, bold=True))
    
    # Висновок знизу
    p.append(text(W / 2, 295, "Без fsync(dir_fd) файлова система після збою відкочує каталог до старого інода", size=12, color=INK, bold=True))
    
    return render(os.path.join(OUT, "directory-fsync-hazard.svg"), W, H, *p)


if __name__ == "__main__":
    fig_naive_vs_atomic()
    fig_six_step_pipeline()
    fig_inode_dentry_swap()
    fig_directory_fsync_hazard()
    print("All figures generated successfully.")
