# -*- coding: utf-8 -*-
"""Фігури до теми «Винятки: кидання, розкрутка стека, перехоплення»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

DIE = "#fdecea"   # заливка кадрів, що зникають
LIVE = "#e8f6ee"  # заливка того, що лишається живим


# ── 1. Об'єкт винятка лежить осторонь від кадрів ────────────────────────────
def fig_storage():
    W, H = 1000, 470
    f = []

    f.append(text(190, 72, "стек викликів", size=13, color=MUTED))

    # кадри згори вниз: main — найстарший
    f.append(fitbox(60, 88, 260, 58, "main()\ntry { … } catch (…)", size=12,
                    fill=LIVE, stroke=FIELD))
    f.append(fitbox(60, 158, 260, 58, "load_config()", size=12, fill=DIE, stroke=POS))
    f.append(fitbox(60, 228, 260, 58, "parse_file()", size=12, fill=DIE, stroke=POS))
    f.append(fitbox(60, 298, 260, 58, "parse_line()\nthrow std::runtime_error{…}",
                    size=12, fill=DIE, stroke=POS))

    f.append(text(190, 392, "ці три кадри зникнуть", size=12, color=POS))

    # сховище рантайму
    f.append(text(790, 132, "сховище рантайму (купа)", size=13, color=MUTED))
    f.append(fitbox(650, 150, 290, 86,
                    "об'єкт винятка\nstd::runtime_error\n\"bad line 42\"", size=13,
                    fill=LIVE, stroke=FIELD))
    f.append(text(790, 262, "живе, доки не вийде останній catch", size=11, color=MUTED))

    # throw кладе об'єкт у сховище
    f.append(arrow(330, 322, 646, 224))
    f.append(text(500, 348, "throw ініціалізує копією", size=12))

    # catch читає його вже після смерті кадрів
    f.append(arrow(646, 176, 330, 112))
    f.append(text(500, 100, "catch зв'язує посилання", size=12))

    f.append(text(500, 434,
                  "кадри від точки кидка до обробника зникають — об'єкт винятка ні",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'storage.svg'), W, H, *f,
           title="Де живе об'єкт винятка")


# ── 2. Дві фази розкрутки ──────────────────────────────────────────────────
def fig_two_phase():
    W, H = 1100, 500
    f = []

    # ── ліва панель: пошук ──
    f.append(text(250, 74, "Фаза 1 — пошук", size=15, bold=True))
    f.append(fitbox(130, 96, 250, 52, "main()", size=12, fill=LIVE, stroke=FIELD))
    f.append(fitbox(130, 166, 250, 52, "load_config()", size=12))
    f.append(fitbox(130, 236, 250, 52, "parse_file()", size=12))
    f.append(fitbox(130, 306, 250, 52, "parse_line()  throw", size=12,
                    fill=DIE, stroke=POS))

    f.append(arrow(108, 320, 108, 262))
    f.append(arrow(108, 250, 108, 192))
    f.append(arrow(108, 180, 108, 122))

    f.append(text(392, 127, "так — запам'ятали", size=12, color=FIELD, anchor="start"))
    f.append(text(392, 197, "ні", size=12, color=MUTED, anchor="start"))
    f.append(text(392, 267, "ні", size=12, color=MUTED, anchor="start"))

    f.append(text(250, 398, "стек цілий, деструктори не викликані", size=12, color=MUTED))
    f.append(text(250, 424, "не знайшли нікого — terminate тут-таки", size=12, color=MUTED))

    # роздільник
    f.append(line(560, 66, 560, 450, color=MUTED, sw=1, dash="6 5"))

    # ── права панель: розкрутка ──
    f.append(text(830, 74, "Фаза 2 — розкрутка", size=15, bold=True))
    f.append(fitbox(700, 96, 280, 52, "main()  →  тіло catch", size=12,
                    fill=LIVE, stroke=FIELD))
    f.append(fitbox(700, 166, 280, 52, "load_config()   ~Buffer()", size=12,
                    fill=DIE, stroke=POS))
    f.append(fitbox(700, 236, 280, 52, "parse_file()   ~ifstream()", size=12,
                    fill=DIE, stroke=POS))
    f.append(fitbox(700, 306, 280, 52, "parse_line()   ~Guard()", size=12,
                    fill=DIE, stroke=POS))

    f.append(arrow(678, 320, 678, 262))
    f.append(arrow(678, 250, 678, 192))
    f.append(arrow(678, 180, 678, 122))

    f.append(text(830, 398, "кадри знищуються знизу вгору,", size=12, color=MUTED))
    f.append(text(830, 424, "деструктори — у зворотному порядку", size=12, color=MUTED))

    render(os.path.join(OUT, 'two-phase.svg'), W, H, *f,
           title="Два проходи по тих самих кадрах")


# ── 3. Перебір catch-гілок ─────────────────────────────────────────────────
def fig_catch_match():
    W, H = 1080, 400
    f = []

    f.append(fitbox(50, 140, 220, 74, "кинуто\nParseError", size=14,
                    fill=DIE, stroke=POS))
    f.append(arrow(276, 122, 344, 122))

    f.append(text(560, 74, "перевірка згори вниз", size=12, color=MUTED))

    rows = [
        ("1   catch (const std::bad_alloc&)", "тип не той", MUTED, FILL, LINE),
        ("2   catch (const ParseError&)", "збіг — сюди", FIELD, LIVE, FIELD),
        ("3   catch (const std::exception&)", "підійшов би, але пізно", MUTED, FILL, LINE),
        ("4   catch (...)", "не дійде", MUTED, FILL, LINE),
    ]
    y = 96
    for label, verdict, vc, fill, stroke in rows:
        f.append(fitbox(350, y, 380, 52, label, size=13, fill=fill, stroke=stroke))
        f.append(text(756, y + 32, verdict, size=12, color=vc, anchor="start"))
        y += 70

    f.append(text(540, 372,
                  "перемагає перша підхожа гілка, а не найточніша",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'catch-match.svg'), W, H, *f,
           title="Який catch спіймає")


# ── 4. Відновлення проти завершення (до історичної вставки) ────────────────
def fig_resumption_vs_termination():
    W, H = 1200, 470
    f = []

    # ── ліва панель: відновлення ──
    f.append(text(300, 54, "Відновлення: PL/I, Mesa", size=15, bold=True))

    f.append(fitbox(130, 84, 340, 58,
                    "обробник вирішує:\n«полагодив — працюй далі»", size=12,
                    fill=LIVE, stroke=FIELD))
    f.append(fitbox(130, 164, 340, 58, "проміжний кадр — живий", size=12))
    f.append(fitbox(130, 244, 340, 58,
                    "SIGNAL Err\nнаступний рядок ВИКОНАЄТЬСЯ", size=12,
                    fill=DIE, stroke=POS))

    f.append(arrow(112, 250, 112, 148, color=POS))
    f.append(text(78, 202, "сигнал", size=11, color=POS))

    f.append(arrow(496, 148, 496, 250, color=FIELD))
    f.append(text(534, 202, "resume", size=11, color=FIELD))

    f.append(mtext(300, 348,
                   ["точка кидка мусить бути готова продовжити роботу",
                    "і не може вважати передумови перевіреними"],
                   size=11, color=MUTED))

    # роздільник
    f.append(line(600, 40, 600, 430, color=MUTED, sw=1, dash="6 5"))

    # ── права панель: завершення ──
    f.append(text(880, 54, "Завершення: CLU, Ada, C++", size=15, bold=True))

    f.append(fitbox(710, 84, 340, 58,
                    "catch (Err&)\nкерування лишається тут", size=12,
                    fill=LIVE, stroke=FIELD))
    f.append(fitbox(710, 164, 340, 58, "проміжний кадр — знищено", size=12,
                    fill=DIE, stroke=POS))
    f.append(fitbox(710, 244, 340, 58,
                    "throw Err{}\nнаступний рядок НЕДОСЯЖНИЙ", size=12,
                    fill=DIE, stroke=POS))

    f.append(arrow(692, 250, 692, 148, color=POS))
    f.append(text(658, 202, "кидок", size=11, color=POS))

    f.append(mtext(880, 348,
                   ["дороги назад немає — кадри вже розібрано,",
                    "тож після throw передумови гарантовано не діють"],
                   size=11, color=MUTED))

    f.append(text(600, 428,
                  "суперечка 1989–1990 років була саме про цю стрілку вниз",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'resumption-vs-termination.svg'), W, H, *f,
           title="Відновлення проти завершення")


# ── Що перетинає межу C-інтерфейсу (вставка proj-exception-boundary) ───────
def fig_boundary():
    W, H = 1180, 540
    f = []

    # ── ліворуч: кадри всередині бібліотеки ──
    f.append(text(245, 76, "усередині бібліотеки: таблиці розкрутки є",
                  size=13, color=MUTED))
    f.append(fitbox(80, 96, 330, 54, "impl.load()", size=13, fill=DIE, stroke=POS))
    f.append(fitbox(80, 166, 330, 54, "parse_file()", size=13, fill=DIE, stroke=POS))
    f.append(fitbox(80, 236, 330, 54, "parse_line()\nthrow cfg::SyntaxError", size=13,
                    fill=DIE, stroke=POS))
    f.append(arrow(60, 238, 60, 168))
    f.append(arrow(60, 158, 60, 98))

    # ── посередині: сама межа ──
    f.append(fitbox(440, 96, 320, 194,
                    "МЕЖА — parser_load()\n \ntry { impl.load(path); }\ncatch (...) →\n"
                    "record(ctx, current_exception())",
                    size=13, fill=LIVE, stroke=FIELD))
    f.append(arrow(420, 122, 436, 122))

    # ── бар'єр і те, що крізь нього проходить ──
    f.append(arrow(764, 130, 876, 130))
    f.append(text(820, 116, "число", size=12))

    f.append(arrow(764, 250, 800, 250, color=POS))
    f.append(line(810, 240, 830, 260, color=POS, sw=2.5))
    f.append(line(830, 240, 810, 260, color=POS, sw=2.5))
    f.append(text(820, 294, "виняток", size=12, color=POS))
    f.append(text(820, 314, "далі не йде", size=12, color=POS))

    # ── праворуч: чужий бік ──
    f.append(text(1015, 76, "виклик ззовні: C, Python, C#", size=13, color=MUTED))
    f.append(fitbox(880, 96, 270, 54, "parser_load(ctx, path)", size=13,
                    fill=FILL, stroke=LINE))
    f.append(fitbox(880, 200, 270, 74, "повернуло\nPARSER_E_SYNTAX", size=13,
                    fill=FILL, stroke=LINE))
    f.append(text(1015, 306, "таблиць розкрутки тут немає", size=12, color=MUTED))

    # ── унизу: об'єкт винятка лишається живим на C++-боці ──
    f.append(fitbox(200, 384, 420, 76,
                    "об'єкт cfg::SyntaxError лишається живим\nctx->failure — std::exception_ptr",
                    size=13, fill=LIVE, stroke=FIELD))
    f.append(arrow(578, 298, 470, 380))

    f.append(text(590, 508,
                  "через межу переходить лише число; деталі лишаються на C++-боці "
                  "й чекають на parser_last_error()",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'boundary.svg'), W, H, *f,
           title="Що перетинає межу, а що лишається")


# ── Лічильник uncaught_exceptions() у трьох випадках ───────────────────────
def fig_unwind_depth():
    W, H = 1120, 440
    f = []

    cases = [
        (210, "нормальний вихід із блока", "0", "0",
         "0 > 0 — хибно\nвідкату немає", LIVE, FIELD),
        (560, "вихід розкруткою", "0", "1",
         "1 > 0 — істина\nвідкочуємо", DIE, POS),
        (910, "вартовий створено\nвсередині catch", "1", "1",
         "1 > 1 — хибно\nвідкату немає", LIVE, FIELD),
    ]

    for cx, head, ctor, dtor, verdict, fill, stroke in cases:
        x = cx - 150
        f.append(fitbox(x, 66, 300, 56, head, size=13, fill=FILL, stroke=LINE, bold=True))
        f.append(fitbox(x, 144, 300, 52, "конструктор бачить " + ctor, size=13,
                        fill=FILL, stroke=LINE))
        f.append(fitbox(x, 216, 300, 52, "деструктор бачить " + dtor, size=13,
                        fill=FILL, stroke=LINE))
        f.append(fitbox(x, 288, 300, 64, verdict, size=13, fill=fill, stroke=stroke))

    f.append(text(560, 404,
                  "стара uncaught_exception() у третьому випадку казала «так» — "
                  "і вартовий відкочував удалу роботу",
                  size=12, color=POS))

    render(os.path.join(OUT, 'unwind-depth.svg'), W, H, *f,
           title="Що бачить вартовий блока в std::uncaught_exceptions()")


# ── Два поверхи контракту розкрутки (вставка api-unwind-abi) ───────────────
def fig_abi_layers():
    W, H = 1160, 600
    f = []

    LX, BW_ = 90, 980

    f.append(fitbox(LX, 66, BW_, 60, "код, який породив компілятор",
                    size=16, bold=True, fill=LIVE, stroke=FIELD))
    f.append(text(LX + BW_ / 2, 150,
                  "throw   ·   ділянки try   ·   landing pad   ·   тіло catch",
                  size=13, color=MUTED))

    f.append(fitbox(LX, 246, BW_, 60, "libstdc++ — знає про C++",
                    size=16, bold=True, fill=FILL, stroke=LINE))
    f.append(text(LX + BW_ / 2, 330,
                  "__cxa_allocate_exception · __cxa_throw · __cxa_begin_catch · "
                  "__cxa_end_catch · __gxx_personality_v0",
                  size=12, color=MUTED))

    f.append(fitbox(LX, 426, BW_, 60, "libgcc_s — про C++ не знає нічого",
                    size=16, bold=True, fill=FILL, stroke=LINE))
    f.append(text(LX + BW_ / 2, 510,
                  "_Unwind_RaiseException · _Unwind_Resume · _Unwind_GetIP · "
                  "_Unwind_SetGR · _Unwind_GetLanguageSpecificData",
                  size=12, color=MUTED))

    # виклики вниз — ліворуч
    f.append(arrow(230, 172, 230, 240))
    f.append(text(248, 210, "throw: виділити й кинути", size=13, anchor="start"))

    f.append(arrow(230, 352, 230, 420))
    f.append(text(248, 390, "_Unwind_RaiseException(&hdr)", size=13, anchor="start"))

    # зворотні виклики вгору — праворуч
    f.append(arrow(930, 420, 930, 352, color=POS))
    f.append(text(912, 390, "виклик персональної функції на кожен кадр",
                  size=13, color=POS, anchor="end"))

    f.append(arrow(930, 240, 930, 172, color=POS))
    f.append(text(912, 210, "_Unwind_SetIP: стрибок у landing pad",
                  size=13, color=POS, anchor="end"))

    f.append(text(W / 2, 566,
                  "обхід кадрів веде нижній поверх, але «моє / не моє» "
                  "щоразу питає у верхнього",
                  size=13, color=MUTED))

    render(os.path.join(OUT, 'abi-layers.svg'), W, H, *f,
           title="Два поверхи контракту розкрутки")


# ── Розкладка .gcc_except_table (вставка api-unwind-abi) ───────────────────
def fig_lsda_layout():
    W, H = 1200, 620
    f = []

    BX, LW = 70, 230
    DX, DW = 420, 700

    rows = [
        (70, 112, "Заголовок",
         "LPStart-кодування (1 байт)  ·  сам LPStart, якщо не пропущено\n"
         "TType-кодування (1 байт)  ·  зсув до таблиці типів (uleb128)\n"
         "кодування точок виклику (1 байт)  ·  довжина їхньої таблиці"),
        (202, 112, "Таблиця\nточок виклику",
         "на кожен запис — чотири числа:\n"
         "початок ділянки · довжина · landing pad (0 — нічого не робити)\n"
         "зсув у таблицю дій, зсунутий на 1 (0 — самі деструктори)"),
        (334, 112, "Таблиця дій",
         "запис — два sleb128, записи зчеплені в список:\n"
         "ttypeIndex ( >0 — номер типу, 0 — прибирання, <0 — специфікація )\n"
         "зсув до наступного запису ( 0 — кінець списку )"),
        (466, 112, "Таблиця типів",
         "покажчики на std::type_info, індексовані НАЗАД від кінця:\n"
         "номер 1 — останній запис, номер 2 — передостанній\n"
         "запис зі значенням 0 означає catch (...)"),
    ]

    for y, h, label, detail in rows:
        f.append(fitbox(BX, y, LW, h, label, size=15, bold=True,
                        fill=FILL, stroke=LINE))
        f.append(fitbox(DX, y, DW, h, detail, size=13, fill=BG, stroke=MUTED))
        f.append(line(BX + LW, y + h / 2, DX, y + h / 2,
                      color=MUTED, sw=1, dash="5 4"))

    f.append(arrow(360, 396, 360, 500, color=FIELD))
    f.append(text(348, 452, "ttypeIndex", size=12, color=FIELD, anchor="end"))

    f.append(text(W / 2, 600,
                  "адресу цієї таблиці для поточного кадру віддає "
                  "_Unwind_GetLanguageSpecificData()",
                  size=13, color=MUTED))

    render(os.path.join(OUT, 'lsda-layout.svg'), W, H, *f,
           title="Розкладка .gcc_except_table (LSDA)")


if __name__ == "__main__":
    fig_storage()
    fig_two_phase()
    fig_catch_match()
    fig_resumption_vs_termination()
    fig_boundary()
    fig_unwind_depth()
    fig_abi_layers()
    fig_lsda_layout()
    print("ok")
