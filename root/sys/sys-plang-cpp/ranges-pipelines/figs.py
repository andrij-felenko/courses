# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_pipeline_vs_eager():
    """Схема 1: Жадібне виконання STL проти лінивого конвеєра Ranges"""
    w, h = 820, 420
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>']
    
    out.append(text(w/2, 28, "Класичний STL (Жадібний) проти C++20 Ranges (Лінивий конвеєр)", size=16, bold=True, color=INK))
    
    # ── Блок 1: Класичний STL ──
    out.append(rect(15, 50, 790, 160, fill="#fdf2f2", stroke="#e74c3c", sw=1.2, rx=8))
    out.append(text(35, 75, "Класичний STL (std::transform -> std::copy_if): Багатопрохідний & Буферизований", size=13, bold=True, color="#c0392b", anchor="start"))
    
    b1, w1, h1 = textbox(90, 130, "std::vector<int>\nВхідні дані (N)", size=11, fill="#ffffff", stroke="#c0392b", min_w=120)
    out.append(b1)
    
    b2, w2, h2 = textbox(310, 130, "Тимчасовий vector 1\n[Проміжне виділення O(N)]", size=11, fill="#fadbd8", stroke="#e74c3c", min_w=160)
    out.append(b2)
    
    b3, w3, h3 = textbox(550, 130, "Тимчасовий vector 2\n[Проміжне виділення O(K)]", size=11, fill="#fadbd8", stroke="#e74c3c", min_w=160)
    out.append(b3)
    
    b4, w4, h4 = textbox(740, 130, "Результат\nstd::vector", size=11, fill="#ffffff", stroke="#c0392b", min_w=100)
    out.append(b4)
    
    out.append(arrow(155, 130, 225, 130, color="#c0392b", sw=1.5))
    out.append(text(190, 118, "Крок 1: transform", size=10, color="#c0392b"))
    
    out.append(arrow(395, 130, 465, 130, color="#c0392b", sw=1.5))
    out.append(text(430, 118, "Крок 2: copy_if", size=10, color="#c0392b"))
    
    out.append(arrow(635, 130, 685, 130, color="#c0392b", sw=1.5))
    out.append(text(660, 118, "Копіювання", size=10, color="#c0392b"))
    
    out.append(text(410, 188, "Недоліки: виділення кучі на кожному кроці, скидання кешу L1/L2, висока затримка", size=11, color="#922b21", italic=True))
    
    # ── Блок 2: C++20 Ranges ──
    out.append(rect(15, 230, 790, 165, fill="#eafaf1", stroke="#27ae60", sw=1.2, rx=8))
    out.append(text(35, 255, "C++20 Ranges Pipeline: Однопрохідний & Без додаткової пам'яті (O(1) memory)", size=13, bold=True, color="#1e8449", anchor="start"))
    
    c1, cw1, ch1 = textbox(90, 310, "Джерело\nstd::vector", size=11, fill="#ffffff", stroke="#27ae60", min_w=110)
    out.append(c1)
    
    c2, cw2, ch2 = textbox(280, 310, "views::transform\n(Обгортка викладу)", size=11, fill="#d5f5e3", stroke="#27ae60", min_w=150)
    out.append(c2)
    
    c3, cw3, ch3 = textbox(480, 310, "views::filter\n(Обгортка викладу)", size=11, fill="#d5f5e3", stroke="#27ae60", min_w=150)
    out.append(c3)
    
    c4, cw4, ch4 = textbox(700, 310, "Споживач / for loop\n(Pull елементів)", size=11, fill="#ffffff", stroke="#1e8449", min_w=150)
    out.append(c4)
    
    out.append(arrow(625, 310, 560, 310, color="#1e8449", sw=1.8))
    out.append(text(592, 295, "next()", size=10, color="#1e8449"))
    
    out.append(arrow(400, 310, 360, 310, color="#1e8449", sw=1.8))
    out.append(text(380, 295, "next()", size=10, color="#1e8449"))
    
    out.append(arrow(200, 310, 150, 310, color="#1e8449", sw=1.8))
    out.append(text(175, 295, "fetch", size=10, color="#1e8449"))
    
    out.append(text(410, 375, "Переваги: обчислення на вимогу (on-demand), 0 виділень кучі, дружність до кешу CPU", size=11, color="#145a32", italic=True))
    
    out.append('</svg>')
    return "\n".join(out)

def generate_view_wrapper_structure():
    """Схема 2: Внутрішня структура обгорток View та передача ітераторів"""
    w, h = 800, 380
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>']
    
    out.append(text(w/2, 25, "Композиція обгорток std::ranges::transform_view<filter_view<V, Pred>, Func>", size=15, bold=True, color=INK))
    
    out.append(rect(30, 50, 740, 300, fill="#ebf5fb", stroke="#2980b9", sw=2, rx=10))
    out.append(text(50, 75, "transform_view (Зовнішній вигляд)", size=13, bold=True, color="#1b4f72", anchor="start"))
    
    b_tf_fun, _, _ = textbox(140, 150, "func_: Func\n(Предикат/Функція)", size=11, fill="#ffffff", stroke="#2980b9", min_w=140)
    out.append(b_tf_fun)
    
    out.append(rect(240, 90, 510, 240, fill="#e8f8f5", stroke="#16a085", sw=1.8, rx=8))
    out.append(text(260, 115, "base_: filter_view (Внутрішній вигляд)", size=12, bold=True, color="#0e6251", anchor="start"))
    
    b_fl_pred, _, _ = textbox(360, 160, "pred_: Predicate\n(Фільтр умова)", size=11, fill="#ffffff", stroke="#16a085", min_w=140)
    out.append(b_fl_pred)
    
    b_fl_cache, _, _ = textbox(360, 230, "cached_begin_: cache\n(Кеш першого елемента)", size=11, fill="#f9e79f", stroke="#d4ac0d", min_w=170)
    out.append(b_fl_cache)
    
    out.append(rect(570, 135, 160, 175, fill="#ffffff", stroke="#27ae60", sw=1.5, rx=6))
    out.append(text(650, 160, "base_: V", size=12, bold=True, color="#1e8449"))
    out.append(text(650, 185, "(vector / span)", size=10, color=MUTED))
    
    out.append(line(590, 210, 710, 210, color="#27ae60", sw=1))
    out.append(text(650, 235, "begin() / end()", size=10, color="#1e8449"))
    out.append(text(650, 260, "Базовий ітератор", size=10, color=MUTED))
    
    out.append(text(140, 240, "При виклику begin():", size=11, bold=True, color="#1b4f72"))
    out.append(text(140, 260, "Створюється transform_iterator", size=10, color="#1b4f72"))
    out.append(text(140, 280, "що обгортає filter_iterator", size=10, color="#1b4f72"))
    
    out.append('</svg>')
    return "\n".join(out)

def generate_pipe_operator_mechanics():
    """Схема 3: Механіка роботи оператора pipe | та Range Adaptor Closure Objects"""
    w, h = 840, 360
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>']
    
    out.append(text(w/2, 25, "Трансформація синтаксису pipe: від r | adapt(args) до адаптера викладу", size=15, bold=True, color=INK))
    
    # Крок 1: Вхідний вираз (центр cx=210)
    b1, _, _ = textbox(210, 90, "Вираз розробника:\nvec | views::filter(pred) | views::transform(fn)", size=11, fill="#f4f6f8", stroke="#34495e", min_w=280)
    out.append(b1)
    
    # Крок 2: Часткове застосування (центр cx=630)
    b2, _, _ = textbox(630, 90, "Часткове застосування (Currying):\nviews::filter(pred) -> range_adaptor_closure", size=11, fill="#fef9e7", stroke="#f39c12", min_w=290)
    out.append(b2)
    
    out.append(arrow(360, 90, 475, 90, color="#d35400", sw=1.8))
    out.append(text(417, 76, "1. Оцінка аргументів", size=10, color="#d35400"))
    
    # Крок 3: Виклик operator| (центр cx=210)
    b3, _, _ = textbox(210, 230, "Перевантажений operator|(Range&& r, Closure&& c):\nповертає c(r)", size=11, fill="#eef9f6", stroke="#16a085", min_w=280)
    out.append(b3)
    
    # Крок 4: Результуючий вираз (центр cx=630)
    b4, _, _ = textbox(630, 230, "Результуючий вираз:\ntransform_view(filter_view(vec, pred), fn)", size=11, fill="#eaf2f8", stroke="#2980b9", min_w=290)
    out.append(b4)
    
    out.append(arrow(630, 130, 630, 185, color="#f39c12", sw=1.8))
    out.append(text(645, 160, "2. Створення closure", size=10, color="#d35400", anchor="start"))
    
    out.append(arrow(210, 130, 210, 185, color="#16a085", sw=1.8))
    out.append(text(225, 160, "3. Передача у pipe", size=10, color="#16a085", anchor="start"))
    
    out.append(arrow(360, 230, 475, 230, color="#2980b9", sw=1.8))
    out.append(text(417, 215, "4. Виклик конструктора", size=10, color="#2980b9"))
    
    out.append(text(w/2, 325, "Нульова вартість абстракції: після інлайнінгу компілятором згортається у прямі виклики ітераторів", size=11, color=MUTED, italic=True))
    
    out.append('</svg>')
    return "\n".join(out)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    files = {
        'pipeline-vs-eager.svg': generate_pipeline_vs_eager(),
        'view-wrapper-structure.svg': generate_view_wrapper_structure(),
        'pipe-operator-mechanics.svg': generate_pipe_operator_mechanics(),
    }
    
    for filename, content in files.items():
        filepath = os.path.join(img_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated: {filepath}")

if __name__ == '__main__':
    main()
