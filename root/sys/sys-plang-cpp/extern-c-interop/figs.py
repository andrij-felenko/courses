# -*- coding: utf-8 -*-
"""Фігури до теми «extern "C" і сумісність із C-інтерфейсами» (reference/cpp-standards/practice)."""
import sys, os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

CLR_SRC = "#eef4ff"
CLR_COMP = "#fef9e7"
CLR_SYM = "#eaf7ee"
CLR_ERR = "#fdecea"
CLR_BARRIER = "#fff3cd"


# ── 1. Зіставлення символів у компонувальнику ────────────────────────────────
def fig_linkage_boundary():
    W, H = 960, 410
    f = []

    f.append(text(W / 2, 35, "Зіставлення символів компонувальником: без extern \"C\" та з extern \"C\"",
                  size=15, bold=True, color=INK))

    # Верхня секція: БЕЗ extern "C"
    f.append(text(80, 75, "1. Зв'язування за замовчуванням (C++ mangling):", size=13, bold=True, color=POS, anchor="start"))
    
    b1_top, w1_t, _ = textbox(180, 130, ["Одиниця C (caller)", "виклик crypto_init(cfg)", "потрібен символ: crypto_init"],
                              size=12, pad=10, fill=CLR_SRC, stroke=LINE)
    b2_top, w2_t, _ = textbox(500, 130, ["Одиниця C++ (callee)", "void crypto_init(const char*)", "експортовано: _Z11crypto_initPKc"],
                              size=12, pad=10, fill=CLR_COMP, stroke=LINE)
    b3_top, w3_t, _ = textbox(810, 130, ["Компонувальник (Linker)", "strcmp != 0 (символ не знайдено)", "undefined reference error"],
                              size=12, pad=10, fill=CLR_ERR, stroke=POS)
    f += [b1_top, b2_top, b3_top]

    f.append(arrow(180 + w1_t / 2 + 5, 130, 500 - w2_t / 2 - 5, 130, color=LINE))
    f.append(arrow(500 + w2_t / 2 + 5, 130, 810 - w3_t / 2 - 5, 130, color=POS))
    f.append(text(340, 115, "імпорт C", size=11, color=MUTED))
    f.append(text(655, 115, "колізія імен", size=11, color=POS))

    # Розділювальна лінія
    f.append(line(50, 205, 910, 205, color=MUTED, sw=1.0, dash="4,4"))

    # Нижня секція: З extern "C"
    f.append(text(80, 235, "2. Зі специфікатором зв'язування extern \"C\":", size=13, bold=True, color=FIELD, anchor="start"))
    
    b1_bot, w1_b, _ = textbox(180, 295, ["Одиниця C (caller)", "виклик crypto_init(cfg)", "потрібен символ: crypto_init"],
                              size=12, pad=10, fill=CLR_SRC, stroke=LINE)
    b2_bot, w2_b, _ = textbox(500, 295, ["Одиниця C++ (callee)", "extern \"C\" void crypto_init(...)", "експортовано: crypto_init (без mangling)"],
                              size=12, pad=10, fill=CLR_COMP, stroke=LINE)
    b3_bot, w3_b, _ = textbox(810, 295, ["Компонувальник (Linker)", "strcmp == 0 (точний збіг)", "успішне зшивання адреси"],
                              size=12, pad=10, fill=CLR_SYM, stroke=FIELD)
    f += [b1_bot, b2_bot, b3_bot]

    f.append(arrow(180 + w1_b / 2 + 5, 295, 500 - w2_b / 2 - 5, 295, color=LINE))
    f.append(arrow(500 + w2_b / 2 + 5, 295, 810 - w3_b / 2 - 5, 295, color=FIELD))
    f.append(text(340, 280, "імпорт C", size=11, color=MUTED))
    f.append(text(655, 280, "збіг символу", size=11, color=FIELD))

    f.append(text(W / 2, 385, "extern \"C\" вимикає декорування імен і гарантує сумісність двійкового виклику за C ABI",
                  size=12, color=MUTED))

    render(os.path.join(IMG, "fig-linkage-boundary.svg"), W, H, *f,
           title="Межа зв'язування та сумісність символів C/C++")


# ── 2. Архітектура непрозорого дескриптора та бар'єра винятків ──────────────
def fig_opaque_handle():
    W, H = 960, 390
    f = []

    f.append(text(W / 2, 35, "Архітектура Opaque Handle та бар'єра винятків (Exception Barrier)",
                  size=15, bold=True, color=INK))

    # 4 вертикальні зони
    b1, w1, _ = textbox(135, 175, ["Клієнт C / FFI", "struct engine_t* h;", "engine_process(h, data);", "Отримує числовий", "статус помилки"],
                        size=12, pad=10, fill=CLR_SRC, stroke=NEG)
    
    b2, w2, _ = textbox(375, 175, ["Заголовок C-API (.h)", "typedef struct engine_t engine_t;", "int engine_process(", "  engine_t* h, ...);", "Incomplete type"],
                        size=12, pad=10, fill=CLR_COMP, stroke=LINE)
    
    b3, w3, _ = textbox(625, 175, ["Бар'єр винятків (.cpp)", "try {", "  impl->process(data);", "  return STATUS_OK;", "} catch (...) {", "  return STATUS_ERR;", "}"],
                        size=11, pad=10, fill=CLR_BARRIER, stroke=POS)
    
    b4, w4, _ = textbox(855, 175, ["Ядро на C++ (.hpp/.cpp)", "class EngineCore {", "  std::vector<uint8_t> buf;", "  std::string name;", "  void process(...);", "};"],
                        size=11, pad=10, fill=CLR_SYM, stroke=FIELD)
    
    f += [b1, b2, b3, b4]

    # Стрілки передачі викликів
    f.append(arrow(135 + w1 / 2 + 5, 150, 375 - w2 / 2 - 5, 150, color=LINE))
    f.append(arrow(375 + w2 / 2 + 5, 150, 625 - w3 / 2 - 5, 150, color=LINE))
    f.append(arrow(625 + w3 / 2 + 5, 150, 855 - w4 / 2 - 5, 150, color=FIELD))

    # Стрілки повернення статусів
    f.append(arrow(855 - w4 / 2 - 5, 205, 625 + w3 / 2 + 5, 205, color=FIELD))
    f.append(arrow(625 - w3 / 2 - 5, 205, 375 + w2 / 2 + 5, 205, color=POS))
    f.append(arrow(375 - w2 / 2 - 5, 205, 135 + w1 / 2 + 5, 205, color=POS))

    # Підписи під стрілками
    f.append(text(255, 135, "виклик функції", size=11, color=MUTED))
    f.append(text(500, 135, "C-ABI виклик", size=11, color=MUTED))
    f.append(text(740, 135, "C++ метод", size=11, color=MUTED))

    f.append(text(500, 225, "код помилки", size=11, color=POS))
    f.append(text(740, 225, "виняток / результат", size=11, color=FIELD))

    # Нижні пояснення
    f.append(text(W / 2, 335, "Жоден виняток C++ не повинен перетинати межу C-ABI: перехоплення в try/catch обов'язкове",
                  size=12, bold=True, color=POS))
    f.append(text(W / 2, 360, "Неповний тип struct engine_t ізолює внутрішню пам'ять і розмітку C++ класів від клієнта",
                  size=12, color=MUTED))

    render(os.path.join(IMG, "fig-opaque-handle.svg"), W, H, *f,
           title="Архітектура Opaque Handle та Exception Barrier")


# ── 3. Трамплін зворотних викликів (Callback Trampoline) ────────────────────
def fig_callback_trampoline():
    W, H = 960, 380
    f = []

    f.append(text(W / 2, 35, "Трамплін зворотного виклику: зв'язування C function pointer та C++ контексту",
                  size=15, bold=True, color=INK))

    # 3 ключові блоки
    b1, w1, _ = textbox(160, 175, ["C Джерело подій", "on_event(cb, user_data)", "Збережено: вказівник", "на функцію + void* ptr", "Спрацювання: cb(id, ptr)"],
                        size=12, pad=10, fill=CLR_SRC, stroke=LINE)
    
    b2, w2, _ = textbox(480, 175, ["Статичний трамплін (C++)", "static void trampoline(int id, void* u) {", "  auto* obj = static_cast<Listener*>(u);", "  obj->handle(id);", "}", "Вільна функція без захоплення"],
                        size=11, pad=10, fill=CLR_COMP, stroke=LINE)
    
    b3, w3, _ = textbox(800, 175, ["C++ Об'єкт / Замикання", "class Listener {", "  std::vector<Event> log;", "  void handle(int id) { ... }", "};", "Повноцінний стан і методи"],
                        size=11, pad=10, fill=CLR_SYM, stroke=FIELD)
    
    f += [b1, b2, b3]

    # Стрілки
    f.append(arrow(160 + w1 / 2 + 5, 150, 480 - w2 / 2 - 5, 150, color=LINE))
    f.append(arrow(480 + w2 / 2 + 5, 150, 800 - w3 / 2 - 5, 150, color=FIELD))

    f.append(text(320, 135, "cb(id, user_data)", size=11, color=MUTED))
    f.append(text(640, 135, "obj->handle(id)", size=11, color=FIELD))

    # Виноски-пояснення знизу
    f.append(text(W / 2, 305, "Покажчик на метод класу C++ або лямбда із захопленням не відповідають сигнатурі C function pointer",
                  size=12, color=POS))
    f.append(text(W / 2, 335, "Параметр void* user_data передає покажчик на екземпляр, який трамплін безпечно відновлює через static_cast",
                  size=12, color=MUTED))

    render(os.path.join(IMG, "fig-callback-trampoline.svg"), W, H, *f,
           title="Трамплін зворотного виклику (Callback Trampoline)")


def main():
    fig_linkage_boundary()
    fig_opaque_handle()
    fig_callback_trampoline()
    print("Фігури для extern-c-interop згенеровано успішно.")


if __name__ == "__main__":
    main()
