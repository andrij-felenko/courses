# -*- coding: utf-8 -*-
"""Фігури до теми «Що готує C++26: рефлексія, контракти, senders/receivers»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_cpp26_architecture_map():
    """Схема ключових архітектурних стовпів стандарту C++26."""
    W, H = 1000, 480
    out = []

    out.append(text(W / 2, 45, "Головні вектори C++26: компіляторна рефлексія, надійність контрактів, асинхронність та лінійна алгебра", size=13, color=MUTED))

    col_w = 220
    gap = 20
    start_x = 25
    y_top = 70
    h_col = 380

    pillars = [
        {
            "num": "Статична рефлексія",
            "title": "Static Reflection",
            "fill": "#eef4ff",
            "stroke": NEG,
            "items": [
                "Оператор рефлексії ^^T",
                "Дескриптор std::meta::info",
                "Оператор генерації [: ... :]",
                "Pack Indexing (T...[I])",
                "Змінні-плейсхолдери _"
            ],
            "desc": ["Інспекція коду та кодогенерація", "без макросів, RTTI", "чи зовнішніх препроцесорів"]
        },
        {
            "num": "Контрактне програмування",
            "title": "Language Contracts",
            "fill": "#f0fdf4",
            "stroke": FIELD,
            "items": [
                "Преумови: pre (cond)",
                "Постумови: post (cond)",
                "Твердження: contract_assert",
                "Семантики: enforce / observe",
                "Обробник порушень контракту"
            ],
            "desc": ["Формальна верифікація", "інваріантів та надійна", "оптимізація компілятора"]
        },
        {
            "num": "Асинхронна модель",
            "title": "Senders / Receivers",
            "fill": "#fffbeb",
            "stroke": "#d97706",
            "items": [
                "std::execution середовище",
                "Ланцюги sender | then()",
                "Підключення connect()",
                "Контексти та schedulers",
                "Структурований паралелізм"
            ],
            "desc": ["Уніфікований конвеєр задач", "без зайвих алокацій пам'яті", "та гонитви станів"]
        },
        {
            "num": "Обчислення та STL",
            "title": "Compute & Library",
            "fill": "#fdf2f8",
            "stroke": POS,
            "items": [
                "std::linalg (BLAS для mdspan)",
                "Векторні операції std::simd",
                "Розширення constexpr new/del",
                "Покращення std::format/print",
                "Причини вилучення delete(\"msg\")"
            ],
            "desc": ["Стандартизована матрична", "алгебра, SIMD-реєстри", "та зручний вивід даних"]
        }
    ]

    for i, p in enumerate(pillars):
        cx = start_x + i * (col_w + gap) + col_w / 2

        out.append(rect(cx - col_w / 2, y_top, col_w, h_col, fill=p["fill"], stroke=p["stroke"], sw=2, rx=8))
        out.append(text(cx, y_top + 24, p["num"], size=12, color=p["stroke"], bold=True))
        out.append(text(cx, y_top + 46, p["title"], size=13, bold=True))
        out.append(line(cx - col_w / 2 + 12, y_top + 58, cx + col_w / 2 - 12, y_top + 58, color=p["stroke"], sw=1))

        item_y = y_top + 82
        for item in p["items"]:
            bb, _, _ = textbox(cx, item_y, item, size=11, pad=5, fill="#ffffff", stroke="#d1d5db", sw=1, min_w=col_w - 24)
            out.append(bb)
            item_y += 44

        out.append(line(cx - col_w / 2 + 12, y_top + 310, cx + col_w / 2 - 12, y_top + 310, color="#d1d5db", sw=1))
        out.append(mtext(cx, y_top + 332, p["desc"], size=11, color=INK, lh=1.35, bold=False))

    render(os.path.join(IMG, 'cpp26-architecture-map.svg'), W, H, *out,
           title="Архітектурні стовпи стандарту C++26")


def fig_reflection_splice_pipeline():
    """Схема конвеєра статичної рефлексії та генерації коду через сплайсинг."""
    W, H = 960, 420
    out = []

    out.append(text(W / 2, 45, "Від аналізу синтаксичного дерева AST до вставки коду під час компіляції", size=13, color=MUTED))

    steps = [
        {
            "cx": 130, "cy": 220, "w": 180, "h": 240,
            "tag": "1. Вхідний тип", "title": "Вихідний AST",
            "fill": "#f8fafc", "stroke": "#64748b",
            "lines": ["struct User {", "  int id;", "  string name;", "  double rate;", "};"]
        },
        {
            "cx": 370, "cy": 220, "w": 190, "h": 240,
            "tag": "2. Рефлексія ^^", "title": "std::meta::info",
            "fill": "#eef4ff", "stroke": NEG,
            "lines": ["constexpr auto r =", "  ^^User;", "consteval обчислення:", "members_of(r)", "name_of(r)"]
        },
        {
            "cx": 610, "cy": 220, "w": 190, "h": 240,
            "tag": "3. Трансформація", "title": "constexpr алгоритми",
            "fill": "#fffbeb", "stroke": "#d97706",
            "lines": ["Фільтрація полів,", "генерація JSON / DTO,", "перевірка типів", "у чистому C++", "без макросів"]
        },
        {
            "cx": 845, "cy": 220, "w": 170, "h": 240,
            "tag": "4. Сплайсинг [: :]", "title": "Генерований код",
            "fill": "#f0fdf4", "stroke": FIELD,
            "lines": ["Вставка виразів:", "u.[: member :]", "Вставка типів:", "[: type_meta :]", "Готовий двійковий код"]
        }
    ]

    for st in steps:
        cx, cy, w, h = st["cx"], st["cy"], st["w"], st["h"]
        out.append(rect(cx - w / 2, cy - h / 2, w, h, fill=st["fill"], stroke=st["stroke"], sw=2, rx=8))
        out.append(text(cx, cy - h / 2 + 22, st["tag"], size=11, color=st["stroke"], bold=True))
        out.append(text(cx, cy - h / 2 + 42, st["title"], size=12, bold=True))
        out.append(line(cx - w / 2 + 10, cy - h / 2 + 54, cx + w / 2 - 10, cy - h / 2 + 54, color=st["stroke"], sw=1))

        ly = cy - h / 2 + 78
        for ln in st["lines"]:
            bb, _, _ = textbox(cx, ly, ln, size=11, pad=4, fill="#ffffff", stroke="#cbd5e1", sw=1, min_w=w - 20)
            out.append(bb)
            ly += 32

    out.append(arrow(225, 220, 270, 220, color=NEG, sw=2))
    out.append(arrow(470, 220, 510, 220, color="#d97706", sw=2))
    out.append(arrow(710, 220, 755, 220, color=FIELD, sw=2))

    render(os.path.join(IMG, 'reflection-splice-pipeline.svg'), W, H, *out,
           title="Конвеєр статичної рефлексії та сплайсингу в C++26")


def fig_senders_receivers_lifecycle():
    """Схема життєвого циклу моделі Senders/Receivers P2300."""
    W, H = 960, 430
    out = []

    out.append(text(W / 2, 45, "Трифазна модель асинхронності: опис графа задач, матеріалізація стану та виконання", size=13, color=MUTED))

    phases = [
        {
            "cx": 165, "w": 250, "color": NEG, "fill": "#eff6ff",
            "phase": "Фаза 1: Опис (Sender)",
            "title": "Композиція алгоритмів",
            "items": [
                "async_read(socket)",
                "  | then(parse_packet)",
                "  | let_value(handle_data)",
                "  | starts_on(pool_scheduler)"
            ],
            "note": "Легковажна специфікація,\nробота ще не розпочата"
        },
        {
            "cx": 480, "w": 250, "color": "#d97706", "fill": "#fffbeb",
            "phase": "Фаза 2: Зв'язування (Connect)",
            "title": "Створення стану",
            "items": [
                "auto state =",
                "  std::execution::connect(",
                "    std::move(sender),",
                "    custom_receiver)",
                "operation_state у пам'яті"
            ],
            "note": "Матеріалізація всіх буферів\nта колбеків без malloc"
        },
        {
            "cx": 795, "w": 250, "color": FIELD, "fill": "#f0fdf4",
            "phase": "Фаза 3: Виконання (Start)",
            "title": "Запуск і завершення",
            "items": [
                "std::execution::start(state)",
                "  -> set_value(result...)",
                "  -> set_error(exception)",
                "  -> set_stopped()"
            ],
            "note": "Детермінований триканальний\nсигнал завершення задачі"
        }
    ]

    card_y = 75
    card_h = 325

    for p in phases:
        cx, w = p["cx"], p["w"]
        out.append(rect(cx - w / 2, card_y, w, card_h, fill=p["fill"], stroke=p["color"], sw=2, rx=8))
        out.append(text(cx, card_y + 24, p["phase"], size=12, color=p["color"], bold=True))
        out.append(text(cx, card_y + 46, p["title"], size=13, bold=True))
        out.append(line(cx - w / 2 + 12, card_y + 58, cx + w / 2 - 12, card_y + 58, color=p["color"], sw=1))

        iy = card_y + 82
        for itm in p["items"]:
            bb, _, _ = textbox(cx, iy, itm, size=11, pad=5, fill="#ffffff", stroke="#d1d5db", sw=1, min_w=w - 24)
            out.append(bb)
            iy += 38

        out.append(line(cx - w / 2 + 12, card_y + 252, cx + w / 2 - 12, card_y + 252, color="#cbd5e1", sw=1))
        out.append(mtext(cx, card_y + 278, p["note"], size=11, color=INK, lh=1.35))

    out.append(arrow(295, 210, 350, 210, color=NEG, sw=2))
    out.append(arrow(610, 210, 665, 210, color="#d97706", sw=2))

    render(os.path.join(IMG, 'senders-receivers-lifecycle.svg'), W, H, *out,
           title="Життєвий цикл асинхронних операцій у моделі Senders/Receivers")


def fig_contracts_evaluation_flow():
    """Схема режимів обчислення контрактів C++26 (P2900)."""
    W, H = 960, 420
    out = []

    out.append(text(W / 2, 45, "Три семантичні режими перевірки контрактних преумов та інваріантів", size=13, color=MUTED))

    modes = [
        {
            "cx": 165, "w": 250, "color": MUTED, "fill": "#f8fafc",
            "mode": "Режим: ignore",
            "title": "Нульовий оверхед",
            "steps": [
                "1. pre (x > 0) не обчислюється",
                "2. У машинний код перевірка",
                "   не генерується",
                "3. Компілятор може використати",
                "   твердження для оптимізації"
            ],
            "badge": "Для релізних білдів\nмаксимальної швидкості"
        },
        {
            "cx": 480, "w": 250, "color": "#d97706", "fill": "#fffbeb",
            "mode": "Режим: observe",
            "title": "Логування без зупинки",
            "steps": [
                "1. pre (x > 0) обчислюється",
                "2. Якщо умова хибна:",
                "   викликається violation handler",
                "3. Фіксується стек/лог помилки",
                "4. Робота програми триває"
            ],
            "badge": "Для діагностики в продакшені\nбез аварійного падіння"
        },
        {
            "cx": 795, "w": 250, "color": POS, "fill": "#fef2f2",
            "mode": "Режим: enforce",
            "title": "Сувора безпека",
            "steps": [
                "1. pre (x > 0) обчислюється",
                "2. Якщо умова хибна:",
                "   викликається violation handler",
                "3. Викликається std::terminate()",
                "4. Програма негайно завершується"
            ],
            "badge": "Для тестування, відладки\nта критичних за безпекою систем"
        }
    ]

    card_y = 75
    card_h = 325

    for m in modes:
        cx, w = m["cx"], m["w"]
        out.append(rect(cx - w / 2, card_y, w, card_h, fill=m["fill"], stroke=m["color"], sw=2, rx=8))
        out.append(text(cx, card_y + 24, m["mode"], size=12, color=p["mode"] if "p" in locals() else m["color"], bold=True))
        out.append(text(cx, card_y + 46, m["title"], size=13, bold=True))
        out.append(line(cx - w / 2 + 12, card_y + 58, cx + w / 2 - 12, card_y + 58, color=m["color"], sw=1))

        iy = card_y + 82
        for st in m["steps"]:
            bb, _, _ = textbox(cx, iy, st, size=11, pad=5, fill="#ffffff", stroke="#e2e8f0", sw=1, min_w=w - 24)
            out.append(bb)
            iy += 38

        out.append(line(cx - w / 2 + 12, card_y + 252, cx + w / 2 - 12, card_y + 252, color="#cbd5e1", sw=1))
        out.append(mtext(cx, card_y + 278, m["badge"], size=11, color=INK, lh=1.35))

    render(os.path.join(IMG, 'contracts-evaluation-flow.svg'), W, H, *out,
           title="Семантичні режими виконання контрактів у C++26")


if __name__ == '__main__':
    fig_cpp26_architecture_map()
    fig_reflection_splice_pipeline()
    fig_senders_receivers_lifecycle()
    fig_contracts_evaluation_flow()
    print("All C++26 figures generated successfully!")
