# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Порівняння URL-інвалідації та сурогатних ключів (Surrogate Keys) ──
def fig_purge_vs_surrogate_keys():
    W, H = 960, 520
    p = []
    
    # Загальна рамка
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # ── Ліва колонка: Традиційний URL Purge (проблема розмноження шляхів) ──
    col_w = 440.0
    col_h = 470.0
    left_x = 26.0
    top_y = 26.0
    
    p.append(rect(left_x, top_y, col_w, col_h, fill="#fff8f8", stroke="#fca5a5", sw=1.4, rx=6))
    p.append(text(left_x + col_w / 2, top_y + 26, "Традиційний URL / Prefix Purge", size=14, color="#b91c1c", bold=True))
    p.append(text(left_x + col_w / 2, top_y + 46, "Очищення за точними адресами запитів", size=11, color=MUTED))
    
    # Джерело даних (Origin)
    p.append(rect(left_x + 120, top_y + 68, 200, 52, fill="#ffffff", stroke="#dc2626", sw=1.3, rx=5))
    p.append(text(left_x + 220, top_y + 90, "Бекенд (Origin)", size=12.5, color="#dc2626", bold=True))
    p.append(text(left_x + 220, top_y + 107, "Зміна товару id=42", size=10.5, color=MUTED))
    
    # Стрілки розгалуження на різні URL
    p.append(line(left_x + 220, top_y + 120, left_x + 220, top_y + 140, color="#dc2626", sw=1.3))
    p.append(line(left_x + 70, top_y + 140, left_x + 370, top_y + 140, color="#dc2626", sw=1.3))
    
    urls = [
        ("HTML сторінка", "/p/42-phone", left_x + 20),
        ("JSON API", "/api/v1/p/42", left_x + 160),
        ("Мобільний віджет", "/widget/p/42", left_x + 300)
    ]
    
    for title_u, path_u, ux in urls:
        p.append(arrow(ux + 60, top_y + 140, ux + 60, top_y + 165, color="#dc2626", sw=1.3))
        p.append(rect(ux, top_y + 165, 120, 52, fill="#ffffff", stroke="#991b1b", sw=1.2, rx=4))
        p.append(text(ux + 60, top_y + 185, title_u, size=11, color="#991b1b", bold=True))
        p.append(text(ux + 60, top_y + 203, path_u, size=9.5, color=MUTED))
        
        # Стрілка вниз до крайових вузлів
        p.append(arrow(ux + 60, top_y + 217, ux + 60, top_y + 248, color=LINE, sw=1.2))
        
    # Блок крайових серверів PoP
    pop_box_y = top_y + 250
    p.append(rect(left_x + 20, pop_box_y, col_w - 40, 100, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=5))
    p.append(text(left_x + col_w / 2, pop_box_y + 22, "Розподілені крайові вузли (Edge PoPs)", size=12, color=INK, bold=True))
    p.append(text(left_x + col_w / 2, pop_box_y + 44, "Потрібно N окремих викликів PURGE на кожен URL", size=10.5, color="#dc2626"))
    p.append(text(left_x + col_w / 2, pop_box_y + 64, "Або ресурсомісткий wildcard-перебір префіксів", size=10.5, color=MUTED))
    p.append(text(left_x + col_w / 2, pop_box_y + 84, "Ризик: пропущений URL віддає застарілу ціну", size=10.5, color="#b91c1c", bold=True))
    
    # Підсумок лівої колонки
    p.append(rect(left_x + 20, top_y + 365, col_w - 40, 85, fill="#fee2e2", stroke="#f87171", sw=1.1, rx=5))
    p.append(text(left_x + 32, top_y + 386, "Властивості URL-інвалідації:", size=11.5, color="#991b1b", bold=True, anchor="start"))
    p.append(text(left_x + 32, top_y + 406, "• Складність росте як O(Кількість представлень)", size=10.5, color=INK, anchor="start"))
    p.append(text(left_x + 32, top_y + 424, "• Бекенд повинен знати всі згенеровані URL-маршрути", size=10.5, color=INK, anchor="start"))
    p.append(text(left_x + 32, top_y + 442, "• Масовий Purge створює навантаження на API CDN", size=10.5, color=INK, anchor="start"))
    
    # ── Права колонка: Сурогатні ключі (Surrogate Keys / Cache-Tags) ──
    right_x = 494.0
    
    p.append(rect(right_x, top_y, col_w, col_h, fill="#f0fdf4", stroke="#86efac", sw=1.4, rx=6))
    p.append(text(right_x + col_w / 2, top_y + 26, "Сурогатні ключі (Surrogate-Key / Cache-Tag)", size=14, color="#15803d", bold=True))
    p.append(text(right_x + col_w / 2, top_y + 46, "Семантична інвалідація за спільним тегом сутності", size=11, color=MUTED))
    
    # Джерело даних (Origin) з тегуванням
    p.append(rect(right_x + 100, top_y + 68, 240, 52, fill="#ffffff", stroke="#16a34a", sw=1.3, rx=5))
    p.append(text(right_x + 220, top_y + 88, "Бекенд (Origin)", size=12.5, color="#16a34a", bold=True))
    p.append(text(right_x + 220, top_y + 107, "Surrogate-Key: prod-42 cat-phones", size=10, color="#15803d", bold=True))
    
    # Єдиний запит на інвалідацію
    p.append(arrow(right_x + 220, top_y + 120, right_x + 220, top_y + 165, color="#16a34a", sw=1.8))
    
    # Блок єдиної команди інвалідації
    p.append(rect(right_x + 70, top_y + 165, 300, 52, fill="#dcfce7", stroke="#22c55e", sw=1.3, rx=5))
    p.append(text(right_x + 220, top_y + 186, "Єдиний виклик: PURGE /key/prod-42", size=12, color="#15803d", bold=True))
    p.append(text(right_x + 220, top_y + 204, "Один виклик атомарно інвалідує всі пов'язані URL", size=10.5, color=INK))
    
    # Стрілка вниз до індексу крайових вузлів
    p.append(arrow(right_x + 220, top_y + 217, right_x + 220, top_y + 248, color="#16a34a", sw=1.8))
    
    # Блок крайових серверів з інвертованим індексом
    p.append(rect(right_x + 20, pop_box_y, col_w - 40, 100, fill="#ffffff", stroke="#86efac", sw=1.2, rx=5))
    p.append(text(right_x + col_w / 2, pop_box_y + 22, "Крайовий індекс тегів (Edge Tag Inverted Index)", size=12, color=INK, bold=True))
    p.append(text(right_x + col_w / 2, pop_box_y + 44, "Ключ «prod-42» зіставляється з адресами в пам'яті:", size=10.5, color=MUTED))
    p.append(text(right_x + col_w / 2, pop_box_y + 64, "['/p/42-phone', '/api/v1/p/42', '/widget/p/42']", size=10, color="#166534", bold=True))
    p.append(text(right_x + col_w / 2, pop_box_y + 84, "Миттєве скидання за O(1) або O(k) без перебору диску", size=10.5, color="#15803d"))
    
    # Підсумок правої колонки
    p.append(rect(right_x + 20, top_y + 365, col_w - 40, 85, fill="#ecfdf5", stroke="#86efac", sw=1.1, rx=5))
    p.append(text(right_x + 32, top_y + 386, "Властивості сурогатних ключів:", size=11.5, color="#166534", bold=True, anchor="start"))
    p.append(text(right_x + 32, top_y + 406, "• Складність інвалідації: O(1) за єдиним тегом сутності", size=10.5, color=INK, anchor="start"))
    p.append(text(right_x + 32, top_y + 424, "• Повна декомпозиція: бекенду байдуже до структури URL", size=10.5, color=INK, anchor="start"))
    p.append(text(right_x + 32, top_y + 442, "• Підтримка ієрархій (за товаром, за брендом, за категорією)", size=10.5, color=INK, anchor="start"))
    
    render(os.path.join(OUT, "purge-vs-surrogate-keys.svg"), W, H, *p)

# ── Фіг. 2: Жорстка інвалідація проти м'якої зі схлопуванням запитів ───────────
def fig_soft_purge_and_coalescing():
    W, H = 960, 520
    p = []
    
    # Загальна рамка
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # ── ВЕРХНЯ ЧАСТИНА: Hard Purge (Каскадна аварія / Cache Stampede) ──
    top_y = 26.0
    top_h = 225.0
    p.append(rect(24, top_y, W - 48, top_h, fill="#fff5f5", stroke="#fca5a5", sw=1.4, rx=6))
    p.append(text(40, top_y + 24, "Жорсткий Purge (Hard Purge): шквал запитів на Origin (Cache Stampede)", size=13.5, color="#b91c1c", bold=True, anchor="start"))
    
    # 3 етапи зліва направо
    # 1. Purge
    p.append(rect(45, top_y + 46, 260, 155, fill="#ffffff", stroke="#dc2626", sw=1.3, rx=5))
    p.append(text(175, top_y + 70, "1. Подія Hard Purge", size=12.5, color="#dc2626", bold=True))
    p.append(mtext(175, top_y + 98, [
        "Об'єкт негайно видаляється",
        "з оперативної пам'яті та SSD",
        "на всіх крайових PoP-вузлах.",
        "Кеш-стан: EMPTY (пусто)"
    ], size=11, color=INK, lh=1.35))
    
    p.append(arrow(308, top_y + 125, 348, top_y + 125, color="#dc2626", sw=1.6))
    
    # 2. Клієнтський наплив
    p.append(rect(350, top_y + 46, 260, 155, fill="#ffffff", stroke="#dc2626", sw=1.3, rx=5))
    p.append(text(480, top_y + 70, "2. Одночасні Cache Miss", size=12.5, color="#dc2626", bold=True))
    p.append(mtext(480, top_y + 98, [
        "10 000 користувачів/сек",
        "приходять на 50 PoP-вузлів.",
        "Усі запити фіксують Miss.",
        "Кожен потік летить на бекенд"
    ], size=11, color=INK, lh=1.35))
    
    p.append(arrow(613, top_y + 125, 653, top_y + 125, color="#dc2626", sw=1.6))
    
    # 3. Падіння Origin
    p.append(rect(655, top_y + 46, 260, 155, fill="#fee2e2", stroke="#b91c1c", sw=1.4, rx=5))
    p.append(text(785, top_y + 70, "3. Перевантаження Origin", size=12.5, color="#991b1b", bold=True))
    p.append(mtext(785, top_y + 98, [
        "База даних вичерпує пули з'єднань.",
        "Час відповіді зростає до 8000 мс.",
        "Шквал помилок 504 Gateway Timeout.",
        "Каскадна відмова системи"
    ], size=11, color="#7f1d1d", lh=1.35))
    
    # ── НИЖНЯ ЧАСТИНА: Soft Purge + Stale-While-Revalidate + Coalescing ──
    bot_y = 265.0
    bot_h = 230.0
    p.append(rect(24, bot_y, W - 48, bot_h, fill="#f0fdf4", stroke="#86efac", sw=1.4, rx=6))
    p.append(text(40, bot_y + 24, "М'який Purge (Soft Purge): фонове оновлення та схлопування (Request Coalescing)", size=13.5, color="#15803d", bold=True, anchor="start"))
    
    # 1. Soft Purge маркування
    p.append(rect(45, bot_y + 46, 260, 160, fill="#ffffff", stroke="#16a34a", sw=1.3, rx=5))
    p.append(text(175, bot_y + 70, "1. Подія Soft Purge", size=12.5, color="#16a34a", bold=True))
    p.append(mtext(175, bot_y + 98, [
        "Об'єкт НЕ видаляється з пам'яті.",
        "TTL виставляється в 0,",
        "але прапорець STALE активний.",
        "Кеш-стан: STALE (застарілий)"
    ], size=11, color=INK, lh=1.35))
    
    p.append(arrow(308, bot_y + 125, 348, bot_y + 125, color="#16a34a", sw=1.6))
    
    # 2. М'яка віддача та схлопування
    p.append(rect(350, bot_y + 46, 260, 160, fill="#ffffff", stroke="#16a34a", sw=1.3, rx=5))
    p.append(text(480, bot_y + 70, "2. Stale-While-Revalidate", size=12.5, color="#16a34a", bold=True))
    p.append(mtext(480, bot_y + 98, [
        "Користувачі миттєво отримують",
        "stale-копію з латентністю < 15 мс.",
        "Перший запит ініціює Single-Flight.",
        "Решта запитів чекають або читають stale"
    ], size=11, color=INK, lh=1.35))
    
    p.append(arrow(613, bot_y + 125, 653, bot_y + 125, color="#16a34a", sw=1.6))
    
    # 3. Захищений Origin
    p.append(rect(655, bot_y + 46, 260, 160, fill="#dcfce7", stroke="#15803d", sw=1.4, rx=5))
    p.append(text(785, bot_y + 70, "3. Захищений Origin", size=12.5, color="#166534", bold=True))
    p.append(mtext(785, bot_y + 98, [
        "Бекенд отримує РІВНО 1 запит",
        "від Origin Shield проксі.",
        "Нова версія атомарно замінює",
        "stale-об'єкт у кеші без перерви"
    ], size=11, color="#14532d", lh=1.35))
    
    render(os.path.join(OUT, "soft-purge-and-coalescing.svg"), W, H, *p)

if __name__ == "__main__":
    fig_purge_vs_surrogate_keys()
    fig_soft_purge_and_coalescing()
    print("Figures generated successfully.")
