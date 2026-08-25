# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: П'ятифазний життєвий цикл штатного вимкнення ──────────────────────
def fig_shutdown_phases():
    W, H = 960, 480
    p = []
    
    # Заголовок та підкладка
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # 5 фаз по горизонталі
    phases = [
        ("1. Сигнал і статус", "SIGTERM від оркестратора\nЗміна Readiness: 503\nСповіщення Ingress", "#e8f4fd", "#2457d6"),
        ("2. Пауза поширення", "Очікування оновлення IP\nМаршрути вилучають вузол\nНові SYN ще долітають", "#fff8e6", "#d97706"),
        ("3. Дренаж запитів", "Закриття listen-сокета\nConnection: close / GOAWAY\nДоведення inflight-робіт", "#ecfdf5", "#059669"),
        ("4. Згортання ресурсів", "Flush логів і трейсів\nЗакриття пулів БД/кешу\nЗвільнення дескрипторів", "#f5f3ff", "#7c3aed"),
        ("5. Фінал / Дедлайн", "Чистий вихід exit(0)\nАБО таймер дедлайну\nForce-abort до SIGKILL", "#fef2f2", "#dc2626")
    ]
    
    box_w = 168.0
    box_h = 130.0
    gap = 20.0
    start_x = 24.0
    y_pos = 90.0
    
    # Часова вісь знизу
    axis_y = 270.0
    p.append(line(30, axis_y, W - 40, axis_y, color=LINE, sw=1.8))
    p.append(arrow(W - 70, axis_y, W - 30, axis_y, color=LINE, sw=2.0))
    p.append(text(W - 45, axis_y - 12, "Час →", size=13, color=INK, bold=True, anchor="end"))
    
    for i, (title_text, desc_text, bg_col, stroke_col) in enumerate(phases):
        x = start_x + i * (box_w + gap)
        
        # Блок фази
        p.append(rect(x, y_pos, box_w, box_h, fill=bg_col, stroke=stroke_col, sw=1.8, rx=6))
        p.append(text(x + box_w / 2, y_pos + 26, title_text, size=13, color=stroke_col, bold=True))
        
        lines = desc_text.split("\n")
        p.append(mtext(x + box_w / 2, y_pos + 56, lines, size=11, color=INK, lh=1.4))
        
        # Точка на осі часу
        cx = x + box_w / 2
        p.append(line(cx, y_pos + box_h, cx, axis_y, color=stroke_col, sw=1.2, dash="4 3"))
        p.append(circle(cx, axis_y, 4.5, fill=stroke_col, stroke="#ffffff", sw=1.5))
        
        # Стрілка переходу до наступної фази
        if i < len(phases) - 1:
            next_x = start_x + (i + 1) * (box_w + gap)
            p.append(arrow(x + box_w + 3, y_pos + box_h / 2, next_x - 3, y_pos + box_h / 2, color=LINE, sw=1.4))
            
    # Нижня панель із системними компонентами
    panel_y = 310.0
    panel_h = 135.0
    p.append(rect(24, panel_y, W - 48, panel_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(40, panel_y + 24, "Дії системних рівнів під час штатного вимкнення:", size=13, color=INK, bold=True, anchor="start"))
    
    rows = [
        ("Балансувальник / Ingress:", "Викреслює IP зі списку бекендів (readiness probe = false, endpoint removal)", FIELD),
        ("Серверний процес:", "Перестає брати нові TCP-з'єднання, досилає 200 OK з Connection: close / GOAWAY", NEG),
        ("Воркери і черги:", "Зупиняють вибірку (basic.cancel / pause), докручують активні транзакції, роблять ACK", POS),
        ("Сторожовий таймер:", "Запобігає зависанню на недоступних залежностях; форсує вихід до прильоту SIGKILL", MUTED),
    ]
    
    ry = panel_y + 48
    for label_txt, desc_txt, col in rows:
        p.append(circle(45, ry, 3.5, fill=col, stroke=col, sw=1.0))
        p.append(text(58, ry + 4, label_txt, size=12, color=INK, bold=True, anchor="start"))
        p.append(text(250, ry + 4, desc_txt, size=12, color=MUTED, anchor="start"))
        ry += 22
        
    render(os.path.join(OUT, "shutdown-phases.svg"), W, H, *p)

# ── Фіг. 2: Порівняння: раптовий обрив проти узгодженого дренажу ──────────────
def fig_race_condition_without_drain():
    W, H = 960, 490
    p = []
    
    # Фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # ── ВЕРХНЯ СЕКЦІЯ: Раптовий обрив (без дренажу) ──────────────────────────
    top_y = 35.0
    p.append(rect(24, top_y, W - 48, 195, fill="#fff5f5", stroke="#fca5a5", sw=1.4, rx=6))
    p.append(text(40, top_y + 24, "Аварійне / некоректне вимкнення (раптовий exit або SIGKILL):", size=13, color="#b91c1c", bold=True, anchor="start"))
    
    # Блоки верхньої схеми
    bx_y = top_y + 45
    
    # 1. Сигнал
    p.append(rect(45, bx_y, 180, 120, fill="#ffffff", stroke="#dc2626", sw=1.4, rx=6))
    p.append(text(135, bx_y + 24, "Процес падає", size=12.5, color="#dc2626", bold=True))
    p.append(mtext(135, bx_y + 50, ["Негайний exit(0)", "Сокети рвуться", "Пул БД руйнується"], size=11, color=INK, lh=1.35))
    
    # Стрілка 1->2
    p.append(arrow(230, bx_y + 60, 270, bx_y + 60, color="#dc2626", sw=1.6))
    
    # 2. Клієнти і балансувальник
    p.append(rect(275, bx_y, 290, 120, fill="#ffffff", stroke="#dc2626", sw=1.4, rx=6))
    p.append(text(420, bx_y + 24, "Мережеві перегони", size=12.5, color="#dc2626", bold=True))
    p.append(mtext(420, bx_y + 50, [
        "Ingress не встиг оновити таблицю",
        "Нові клієнти отримують ECONNREFUSED",
        "Активні запити обриваються: 502 Bad Gateway"
    ], size=11, color=INK, lh=1.35))
    
    # Стрілка 2->3
    p.append(arrow(570, bx_y + 60, 610, bx_y + 60, color="#dc2626", sw=1.6))
    
    # 3. Наслідки в сховищі
    p.append(rect(615, bx_y, 295, 120, fill="#ffffff", stroke="#dc2626", sw=1.4, rx=6))
    p.append(text(762, bx_y + 24, "Втрата даних і повтори", size=12.5, color="#dc2626", bold=True))
    p.append(mtext(762, bx_y + 50, [
        "Транзакція обірвана наполовину",
        "Черга перечитує задачу → подвійне списання",
        "Буферизовані логи втрачено назавжди"
    ], size=11, color=INK, lh=1.35))

    # ── НИЖНЯ СЕКЦІЯ: Штатне вимкнення з дренажем ───────────────────────────
    bot_y = 250.0
    p.append(rect(24, bot_y, W - 48, 205, fill="#f0fdf4", stroke="#86efac", sw=1.4, rx=6))
    p.append(text(40, bot_y + 24, "Штатне вимкнення з координатором (Drain & Graceful Shutdown):", size=13, color="#15803d", bold=True, anchor="start"))
    
    bx2_y = bot_y + 45
    
    # 1. Сигнал і зняття готовності
    p.append(rect(45, bx2_y, 180, 130, fill="#ffffff", stroke="#16a34a", sw=1.4, rx=6))
    p.append(text(135, bx2_y + 24, "Unreadiness + пауза", size=12.5, color="#16a34a", bold=True))
    p.append(mtext(135, bx2_y + 50, [
        "Readiness → 503",
        "Пауза на поширення IP",
        "Listen закривається плавно"
    ], size=11, color=INK, lh=1.35))
    
    # Стрілка 1->2
    p.append(arrow(230, bx2_y + 65, 270, bx2_y + 65, color="#16a34a", sw=1.6))
    
    # 2. Акуратний дренаж
    p.append(rect(275, bx2_y, 290, 130, fill="#ffffff", stroke="#16a34a", sw=1.4, rx=6))
    p.append(text(420, bx2_y + 24, "Дренаж і протокольні сигнали", size=12.5, color="#16a34a", bold=True))
    p.append(mtext(420, bx2_y + 50, [
        "Ingress скеровує нові на сусідів",
        "Connection: close / GOAWAY надіслано",
        "Всі активні запити отримують 200 OK"
    ], size=11, color=INK, lh=1.35))
    
    # Стрілка 2->3
    p.append(arrow(570, bx2_y + 65, 610, bx2_y + 65, color="#16a34a", sw=1.6))
    
    # 3. Чисте згортання
    p.append(rect(615, bx2_y, 295, 130, fill="#ffffff", stroke="#16a34a", sw=1.4, rx=6))
    p.append(text(762, bx2_y + 24, "Послідовне звільнення", size=12.5, color="#16a34a", bold=True))
    p.append(mtext(762, bx2_y + 50, [
        "Черги зупинені, задачі зафіксовані (ACK)",
        "Пули БД закриваються після inflight-робіт",
        "Логи змито на диск, чистий вихід 0"
    ], size=11, color=INK, lh=1.35))

    render(os.path.join(OUT, "race-condition-without-drain.svg"), W, H, *p)

if __name__ == "__main__":
    fig_shutdown_phases()
    fig_race_condition_without_drain()
    print("Generated 2 SVG figures successfully.")
