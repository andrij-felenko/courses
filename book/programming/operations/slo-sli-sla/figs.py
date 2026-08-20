# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Піраміда рівнів обслуговування (SLI, SLO, SLA) ────────────────────
def fig_sli_slo_sla_pyramid(path):
    W, H = 960, 480
    p = []
    
    # Фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Заголовок
    p.append(text(W / 2, 38, "Ієрархія та зв'язок між SLI, SLO, SLA та бюджетом помилок", size=15, color=INK, bold=True))
    
    # Ліва колонка: Тріада концепцій у вигляді трьох блоків різного рівня
    # Блок 1: SLI (Фундамент — що вимірюємо)
    x1, y1, bw, bh = 40, 70, 420, 110
    p.append(rect(x1, y1, bw, bh, fill="#eff6ff", stroke="#2563eb", sw=1.6, rx=6))
    p.append(text(x1 + 20, y1 + 28, "1. SLI (Service Level Indicator) — Індикатор", size=13, color="#2563eb", bold=True, anchor="start"))
    p.append(mtext(x1 + 20, y1 + 52, [
        "Фактичний числовий вимір якості роботи системи в рантаймі.",
        "Формула: (Кількість успішних подій) ÷ (Загальна кількість подій) · 100%",
        "Приклад: 99.93% запитів успішно виконано із затримкою < 200 мс."
    ], size=11, color=INK, anchor="start", lh=1.35))
    
    # Блок 2: SLO (Внутрішня інженерна ціль)
    y2 = 200
    p.append(rect(x1, y2, bw, bh, fill="#fdf4ff", stroke="#c026d3", sw=1.6, rx=6))
    p.append(text(x1 + 20, y2 + 28, "2. SLO (Service Level Objective) — Внутрішня ціль", size=13, color="#c026d3", bold=True, anchor="start"))
    p.append(mtext(x1 + 20, y2 + 52, [
        "Цільовий рівень надійності, узгоджений розробкою та продуктом.",
        "Визначає допустиму частку збоїв — Бюджет помилок (100% − SLO).",
        "Приклад: Ціль 99.9% за ковзне 30-денне вікно (бюджет = 0.1%)."
    ], size=11, color=INK, anchor="start", lh=1.35))
    
    # Блок 3: SLA (Зовнішній юридичний контракт)
    y3 = 330
    p.append(rect(x1, y3, bw, bh, fill="#fffbeb", stroke="#d97706", sw=1.6, rx=6))
    p.append(text(x1 + 20, y3 + 28, "3. SLA (Service Level Agreement) — Зовнішній контракт", size=13, color="#d97706", bold=True, anchor="start"))
    p.append(mtext(x1 + 20, y3 + 52, [
        "Юридична угода з клієнтами із прямими фінансовими санкціями.",
        "Завжди м'якша за SLO для створення захисного буфера безпеки.",
        "Приклад: 99.5% доступності (при порушенні — повернення 25% вартості)."
    ], size=11, color=INK, anchor="start", lh=1.35))
    
    # Права колонка: Числовий графік зон надійності та запасів міцності
    gx, gy, gw, gh = 510, 70, 410, 370
    p.append(rect(gx, gy, gw, gh, fill="#f8fafc", stroke="#94a3b8", sw=1.4, rx=6))
    p.append(text(gx + gw / 2, gy + 30, "Шкала надійності та захисні інтервали", size=13, color=INK, bold=True))
    
    # Зони на шкалі
    zx, zw = gx + 40, gw - 80
    
    # 1. Зона бюджету помилок (99.9% .. 100%)
    p.append(rect(zx, gy + 65, zw, 65, fill="#dcfce7", stroke="#16a34a", sw=1.4, rx=4))
    p.append(text(zx + zw / 2, gy + 90, "Бюджет помилок (Error Budget): 0.1%", size=11.5, color="#15803d", bold=True))
    p.append(text(zx + zw / 2, gy + 112, "Простір для релізів, експериментів та міграцій", size=10, color="#166534"))
    
    # Межа SLO: 99.9%
    p.append(line(zx - 15, gy + 130, zx + zw + 15, gy + 130, color="#c026d3", sw=2))
    p.append(text(zx + zw + 20, gy + 134, "SLO = 99.9%", size=11, color="#c026d3", bold=True, anchor="start"))
    
    # 2. Захисний буфер (99.5% .. 99.9%)
    p.append(rect(zx, gy + 130, zw, 85, fill="#fef3c7", stroke="#d97706", sw=1.4, rx=4))
    p.append(text(zx + zw / 2, gy + 160, "Захисний буфер безпеки: 0.4%", size=11.5, color="#b45309", bold=True))
    p.append(mtext(zx + zw / 2, gy + 182, [
        "Внутрішній інцидент: замороження релізів,",
        "але клієнтський контракт SLA ще НЕ порушено"
    ], size=10, color="#92400e", lh=1.3))
    
    # Межа SLA: 99.5%
    p.append(line(zx - 15, gy + 215, zx + zw + 15, gy + 215, color="#d97706", sw=2))
    p.append(text(zx + zw + 20, gy + 219, "SLA = 99.5%", size=11, color="#d97706", bold=True, anchor="start"))
    
    # 3. Зона фінансових штрафів (< 99.5%)
    p.append(rect(zx, gy + 215, zw, 105, fill="#fee2e2", stroke="#dc2626", sw=1.4, rx=4))
    p.append(text(zx + zw / 2, gy + 250, "Зона фінансових штрафів та виплат", size=11.5, color="#b91c1c", bold=True))
    p.append(mtext(zx + zw / 2, gy + 275, [
        "Порушення договірних зобов'язань SLA,",
        "виплата неустойки, втрата репутації бізнесу"
    ], size=10, color="#991b1b", lh=1.3))
    
    # Стрілка нерівності
    p.append(text(gx + 20, gy + 345, "Золоте правило інженерії:  SLA  <  SLO  <  100%", size=12, color="#1e293b", bold=True, anchor="start"))
    
    return render(path, W, H, *p)


# ── Фіг. 2: Топологія точок вимірювання SLI ──────────────────────────────────
def fig_sli_measurement_boundaries(path):
    W, H = 960, 460
    p = []
    
    # Фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Заголовок
    p.append(text(W / 2, 36, "Точки збору SLI в архітектурі: від клієнтського пристрою до сховища", size=15, color=INK, bold=True))
    
    # Горизонтальний ланцюжок компонентів
    nodes = [
        ("Клієнт (App/JS)", "Браузер / Мобільний", "#f8fafc", "#475569", 40),
        ("CDN / Edge", "Cloudflare / Edge", "#eff6ff", "#2563eb", 230),
        ("Ingress / API GW", "Envoy / Nginx GW", "#f0fdf4", "#16a34a", 420),
        ("Мікросервіс", "Бекенд / Бізнес-код", "#fdf4ff", "#c026d3", 610),
        ("База даних", "PostgreSQL / Redis", "#fffbeb", "#d97706", 800)
    ]
    
    bw, bh = 130, 95
    y_nodes = 75
    
    for i, (title, sub, fill, stroke, nx) in enumerate(nodes):
        p.append(rect(nx, y_nodes, bw, bh, fill=fill, stroke=stroke, sw=1.6, rx=6))
        p.append(text(nx + bw / 2, y_nodes + 28, title, size=11, color=stroke, bold=True))
        p.append(mtext(nx + bw / 2, y_nodes + 54, sub.split(" / "), size=9.5, color=INK, lh=1.3))
        
        if i < len(nodes) - 1:
            next_x = nodes[i + 1][4]
            p.append(arrow(nx + bw + 4, y_nodes + bh / 2, next_x - 4, y_nodes + bh / 2, color=LINE, sw=1.6))
    
    # Нижня частина: порівняння трьох ключових точок вимірювання SLI
    y_cards = 210
    cw, ch = 280, 220
    
    # Картка 1: Клієнтська телеметрія (RUM)
    p.append(rect(40, y_cards, cw, ch, fill="#f8fafc", stroke="#64748b", sw=1.4, rx=6))
    p.append(text(40 + cw / 2, y_cards + 26, "Клієнт (Real User Monitoring)", size=12, color="#334155", bold=True))
    p.append(mtext(40 + 15, y_cards + 52, [
        "+ Справжнє сприйняття користувачем",
        "+ Враховує DNS, рендеринг і мережу",
        "− Шум від поганого Wi-Fi/мобільного зв'язку",
        "− Недоставка логів при повному збої мережі",
        "− Неможливо гарантувати SLA інфраструктури"
    ], size=10, color=INK, anchor="start", lh=1.45))
    
    # Картка 2: Точка входу (Ingress / API Gateway) — ЗОЛОТИЙ СТАНДАРТ
    p.append(rect(340, y_cards, cw, ch, fill="#ecfdf5", stroke="#059669", sw=1.8, rx=6))
    p.append(text(340 + cw / 2, y_cards + 26, "Ingress / API Gateway (Стандарт)", size=12, color="#059669", bold=True))
    p.append(mtext(340 + 15, y_cards + 52, [
        "+ Золотий стандарт для SLI доступності",
        "+ Бачить усі вхідні запити та відмови бекенду",
        "+ Фіксує 5xx, таймаути проксі та затримки",
        "+ Ізольовано від шуму останньої милі клієнта",
        "+ Ідеальна основа для SLO та алертів вигорання"
    ], size=10, color=INK, anchor="start", lh=1.45))
    
    # Картка 3: Внутрішній сервіс (Вузький SLI)
    p.append(rect(640, y_cards, cw, ch, fill="#fdf4ff", stroke="#c026d3", sw=1.4, rx=6))
    p.append(text(640 + cw / 2, y_cards + 26, "Внутрішній сервіс / База даних", size=12, color="#c026d3", bold=True))
    p.append(mtext(640 + 15, y_cards + 52, [
        "+ Точна діагностика конкретного компонента",
        "+ Вимірює чистий час обробки процесором",
        "− Сліпий до падінь балансувальника та шлюзу",
        "− Не враховує мережеві черги та Envoy timeouts",
        "− Застосовується як компонентний, а не бізнес-SLI"
    ], size=10, color=INK, anchor="start", lh=1.45))
    
    return render(path, W, H, *p)


# ── Фіг. 3: Бюджет помилок як інженерна валюта балансу ───────────────────────
def fig_error_budget_as_currency(path):
    W, H = 960, 460
    p = []
    
    # Фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Заголовок
    p.append(text(W / 2, 36, "Бюджет помилок як інструмент балансу між інноваціями та стабільністю", size=15, color=INK, bold=True))
    
    # Ліва колонка: Продуктова команда (Швидкість / Деплої)
    x1, y1, bw, bh = 40, 75, 270, 350
    p.append(rect(x1, y1, bw, bh, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=6))
    p.append(text(x1 + bw / 2, y1 + 30, "Продуктова розробка (Dev)", size=13, color="#2563eb", bold=True))
    p.append(mtext(x1 + 15, y1 + 65, [
        "Ціль: максимальна швидкість постачання.",
        "",
        "На що витрачається бюджет:",
        "• Часті релізи нових фіч;",
        "• Експерименти та A/B-тести;",
        "• Оновлення версій фреймворків;",
        "• Ризиковані рефакторинги коду;",
        "• Масштабні міграції баз даних."
    ], size=10.5, color=INK, anchor="start", lh=1.4))
    
    # Центральна колонка: Резервуар бюджету помилок (Валюта)
    x2 = 345
    bw2 = 270
    p.append(rect(x2, y1, bw2, bh, fill="#f8fafc", stroke="#475569", sw=1.8, rx=6))
    p.append(text(x2 + bw2 / 2, y1 + 30, "Бюджет помилок = 100% − SLO", size=13, color=INK, bold=True))
    
    # Візуальний рівень залишку бюджету
    p.append(rect(x2 + 25, y1 + 65, bw2 - 50, 180, fill="#e2e8f0", stroke="#94a3b8", sw=1.4, rx=4))
    # Зелена заповнена частина (залишок 65%)
    p.append(rect(x2 + 25, y1 + 125, bw2 - 50, 120, fill="#bbf7d0", stroke="#16a34a", sw=1.4, rx=4))
    p.append(text(x2 + bw2 / 2, y1 + 100, "Витрачено: 35%", size=11, color="#b91c1c", bold=True))
    p.append(text(x2 + bw2 / 2, y1 + 175, "Доступний залишок: 65%", size=11.5, color="#15803d", bold=True))
    p.append(text(x2 + bw2 / 2, y1 + 200, "(Ковзне вікно 30 днів)", size=9.5, color="#166534"))
    
    # Правило політики
    p.append(rect(x2 + 15, y1 + 260, bw2 - 30, 75, fill="#fffbeb", stroke="#d97706", sw=1.2, rx=4))
    p.append(text(x2 + bw2 / 2, y1 + 282, "Політика бюджету (Policy):", size=10.5, color="#b45309", bold=True))
    p.append(mtext(x2 + bw2 / 2, y1 + 304, [
        "Залишок > 0 → релізи дозволено",
        "Залишок ≤ 0 → релізний фриз і стабілізація"
    ], size=9.5, color=INK, lh=1.35))
    
    # Права колонка: Команда експлуатації / SRE (Надійність)
    x3 = 650
    p.append(rect(x3, y1, bw, bh, fill="#fdf4ff", stroke="#c026d3", sw=1.5, rx=6))
    p.append(text(x3 + bw / 2, y1 + 30, "Експлуатація / SRE", size=13, color="#c026d3", bold=True))
    p.append(mtext(x3 + 15, y1 + 65, [
        "Ціль: захист користувацького досвіду.",
        "",
        "Дії при вичерпанні бюджету:",
        "• Автоматичне блокування CI/CD;",
        "• 100% фокус на багах і надійності;",
        "• Покращення автотестів і канарок;",
        "• Розширення моніторингу та алертингу;",
        "• Оновлення архітектури відмовостійкості."
    ], size=10.5, color=INK, anchor="start", lh=1.4))
    
    # Стрілки взаємодії
    p.append(arrow(x1 + bw + 4, y1 + 110, x2 - 4, y1 + 110, color="#2563eb", sw=1.8))
    p.append(text((x1 + bw + x2) / 2, y1 + 100, "Витрата", size=9.5, color="#2563eb", bold=True))
    
    p.append(arrow(x3 - 4, y1 + 110, x2 + bw2 + 4, y1 + 110, color="#c026d3", sw=1.8))
    p.append(text((x2 + bw2 + x3) / 2, y1 + 100, "Захист", size=9.5, color="#c026d3", bold=True))
    
    return render(path, W, H, *p)


# ── Фіг. 4: Мульти-віконний алертинг за швидкістю вигорання (Burn Rate) ──────
def fig_multi_window_burn_rate(path):
    W, H = 960, 480
    p = []
    
    # Фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Заголовок
    p.append(text(W / 2, 36, "Мульти-віконний алертинг за швидкістю вигорання (Multi-Window Multi-Burn-Rate)", size=15, color=INK, bold=True))
    
    # Верхня схема: Логічне об'єднання двох вікон (Short + Long)
    x1, y1 = 40, 70
    box_w, box_h = 240, 120
    
    # Коротке вікно (Short Window)
    p.append(rect(x1, y1, box_w, box_h, fill="#eff6ff", stroke="#2563eb", sw=1.6, rx=6))
    p.append(text(x1 + box_w / 2, y1 + 26, "Коротке вікно (5 хв)", size=12, color="#2563eb", bold=True))
    p.append(mtext(x1 + 15, y1 + 52, [
        "Burn Rate (5 хв) > 14.4×",
        "Швидко фіксує початок гострої аварії,",
        "але може давати хибні спрацювання",
        "на одиничних коротких сплесках."
    ], size=9.5, color=INK, anchor="start", lh=1.35))
    
    # Довге вікно (Long Window)
    x2 = 340
    p.append(rect(x2, y1, box_w, box_h, fill="#fdf4ff", stroke="#c026d3", sw=1.6, rx=6))
    p.append(text(x2 + box_w / 2, y1 + 26, "Довге вікно (1 година)", size=12, color="#c026d3", bold=True))
    p.append(mtext(x2 + 15, y1 + 52, [
        "Burn Rate (1 год) > 14.4×",
        "Підтверджує сталість вигорання,",
        "фільтрує короткочасні сплески,",
        "захищає чергового від шуму."
    ], size=9.5, color=INK, anchor="start", lh=1.35))
    
    # Логічний блок "І" (AND)
    x_and = 640
    p.append(circle(x_and + 30, y1 + box_h / 2, 30, fill="#f8fafc", stroke="#1e293b", sw=2))
    p.append(text(x_and + 30, y1 + box_h / 2 + 5, "AND (І)", size=12, color=INK, bold=True))
    
    # Стрілки в AND
    p.append(arrow(x1 + box_w + 4, y1 + box_h / 2, x_and - 2, y1 + box_h / 2, color=LINE, sw=1.6))
    p.append(arrow(x2 + box_w + 4, y1 + box_h / 2, x_and - 2, y1 + box_h / 2, color=LINE, sw=1.6))
    
    # Результат: Пейджинг чергового
    x_res = 750
    p.append(rect(x_res, y1 + 10, 170, 100, fill="#fee2e2", stroke="#dc2626", sw=1.8, rx=6))
    p.append(text(x_res + 85, y1 + 42, "Критичний пейдж", size=12.5, color="#b91c1c", bold=True))
    p.append(mtext(x_res + 85, y1 + 68, [
        "Витрата 2% бюджету",
        "за 1 годину! Виклик чергового"
    ], size=9.5, color="#991b1b", lh=1.35))
    
    p.append(arrow(x_and + 62, y1 + box_h / 2, x_res - 4, y1 + box_h / 2, color="#dc2626", sw=2))
    
    # Нижня частина: Таблиця рівнів вигорання (Burn Rate Matrix)
    ty = 220
    p.append(rect(40, ty, W - 80, 230, fill="#f8fafc", stroke="#94a3b8", sw=1.4, rx=6))
    p.append(text(W / 2, ty + 26, "Матриця рівнів швидкості вигорання (Burn Rate Alert Matrix)", size=13, color=INK, bold=True))
    
    headers = ["Швидкість (Burn Rate)", "Частка бюджету", "Довге вікно", "Коротке вікно", "Дія / Канал сповіщення"]
    col_x = [60, 240, 380, 520, 680]
    
    # Шапка таблиці
    p.append(rect(50, ty + 42, W - 100, 28, fill="#e2e8f0", stroke="#cbd5e1", sw=1, rx=3))
    for i, h in enumerate(headers):
        p.append(text(col_x[i], ty + 60, h, size=10.5, color="#1e293b", bold=True, anchor="start"))
        
    rows = [
        ("14.4× (100% за 2 дні)", "2% бюджету", "1 година", "5 хвилин", "Критичний пейдж (PagerDuty)", "#dc2626", "#fef2f2"),
        ("6.0×  (100% за 5 днів)", "5% бюджету", "6 годин", "30 хвилин", "Терміновий пейдж (PagerDuty)", "#ea580c", "#fff7ed"),
        ("3.0×  (100% за 10 днів)", "10% бюджету", "24 години", "2 години", "Тікет / Сповіщення в чат", "#d97706", "#fffbeb"),
        ("1.0×  (100% за 30 днів)", "10% бюджету", "3 дні", "6 годин", "Звіт у робочий час / Трекер", "#2563eb", "#eff6ff")
    ]
    
    row_y = ty + 75
    for r_rate, r_part, r_long, r_short, r_action, r_col, r_bg in rows:
        p.append(rect(50, row_y, W - 100, 32, fill=r_bg, stroke=r_col, sw=1, rx=3))
        p.append(text(col_x[0], row_y + 20, r_rate, size=10, color=r_col, bold=True, anchor="start"))
        p.append(text(col_x[1], row_y + 20, r_part, size=10, color=INK, anchor="start"))
        p.append(text(col_x[2], row_y + 20, r_long, size=10, color=INK, anchor="start"))
        p.append(text(col_x[3], row_y + 20, r_short, size=10, color=INK, anchor="start"))
        p.append(text(col_x[4], row_y + 20, r_action, size=10, color=r_col, bold=True, anchor="start"))
        row_y += 36
        
    return render(path, W, H, *p)


# ── Головний запуск ──────────────────────────────────────────────────────────
def main():
    figs = [
        ("sli-slo-sla-pyramid.svg", fig_sli_slo_sla_pyramid),
        ("sli-measurement-boundaries.svg", fig_sli_measurement_boundaries),
        ("error-budget-as-currency.svg", fig_error_budget_as_currency),
        ("multi-window-burn-rate.svg", fig_multi_window_burn_rate)
    ]
    
    for filename, func in figs:
        path = os.path.join(OUT, filename)
        func(path)
        print(f"Generated: {path}")

if __name__ == "__main__":
    main()
