# -*- coding: utf-8 -*-
import os
import sys

# 4 levels up to courses root scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def render_tracepoint_lifecycle(path):
    frags = []

    # Column 1: Main code path
    b1_header = fitbox(30, 50, 240, 40, "1. Потік коду ядра (Hot Path)", fill="#e8f4f8", stroke="#2b7b98", bold=True, size=13)
    b1_body = fitbox(30, 95, 240, 165, "Виклик trace_sched_switch(...)\n\n• Вимкнено: інструкція NOP (5 байтів)\n  Нульове навантаження на кеш і CPU\n\n• Увімкнено: інструкція JMP\n  Атомарно замінена через text_poke\n  Перехід на out-of-line трамплін", fill="#ffffff", stroke="#2b7b98", size=12)
    frags.extend([b1_header, b1_body])

    # Column 2: Out-of-line Trampoline & Dispatcher
    b2_header = fitbox(300, 50, 260, 40, "2. Диспетчер обробників (RCU)", fill="#f9f2e7", stroke="#d98c21", bold=True, size=13)
    b2_body = fitbox(300, 95, 260, 165, "Трамплін __tracepoint_sched_switch\n\n• Вхід у секцію RCU-читача\n• rcu_dereference_raw(tp->funcs)\n• Безблокувальний обхід масиву\n• Виклик зареєстрованих функцій:\n  - ftrace_event_probe()\n  - bpf_trace_run()\n  - perf_trace_run()", fill="#ffffff", stroke="#d98c21", size=12)
    frags.extend([b2_header, b2_body])

    # Column 3: Consumers & Storage
    b3_header = fitbox(590, 50, 240, 40, "3. Споживачі та Кільцевий буфер", fill="#eef7e9", stroke="#4b9932", bold=True, size=13)
    b3_body = fitbox(590, 95, 240, 165, "Запис події у кільцевий буфер\n\n• TP_fast_assign: бінарне копіювання\n• Per-CPU буфер без блокувань\n• eBPF програми (raw tracepoints)\n• Агрегація у пам'яті (hist triggers)\n• Читання через tracefs / trace_pipe", fill="#ffffff", stroke="#4b9932", size=12)
    frags.extend([b3_header, b3_body])

    # Connecting arrows
    frags.append(arrow(270, 175, 300, 175, color="#2b7b98", sw=2))
    frags.append(arrow(560, 175, 590, 175, color="#d98c21", sw=2))

    # Bottom notes
    note1 = fitbox(30, 275, 380, 50, "Static Keys (Jump Labels):\nПри вимкненні відновлюється NOP, усуваючи будь-який оверхед гілкування", fill="#f4f6f8", stroke="#888888", size=11)
    note2 = fitbox(450, 275, 380, 50, "Безпека RCU та NMI:\nРеєстрація та відключення проб не вимагають блокувань у гарячому шляху", fill="#f4f6f8", stroke="#888888", size=11)
    frags.extend([note1, note2])

    render(path, 860, 340, *frags, title="Життєвий цикл трасувальної точки ядра: від Static Key до обробників")

def render_macro_stages(path):
    frags = []

    # Source TRACE_EVENT definition
    top_box = fitbox(50, 50, 760, 60, "Визначення TRACE_EVENT(sched_switch, TP_PROTO(...), TP_ARGS(...), TP_STRUCT__entry(...), TP_fast_assign(...), TP_printk(...))", fill="#fdf3e7", stroke="#d98c21", bold=True, size=12)
    frags.append(top_box)

    # 3 Stages horizontal
    s1 = fitbox(50, 135, 235, 125, "Фаза 1: Структура події\n\ninclude/trace/trace_events.h\nГенерація C-структури:\nstruct trace_event_raw_sched_switch\nз типами полів із\nTP_STRUCT__entry", fill="#e8f4f8", stroke="#2b7b98", size=11)
    s2 = fitbox(312, 135, 235, 125, "Фаза 2: Обробник та запис\n\ninclude/trace/trace_events.h\nГенерація функції-проби:\ntrace_event_raw_event_sched_switch()\nСеріалізація через TP_fast_assign\nу кільцевий буфер ftrace", fill="#f3e8f8", stroke="#7b2b98", size=11)
    s3 = fitbox(575, 135, 235, 125, "Фаза 3: Метадані й VFS\n\ninclude/trace/trace_events.h\nГенерація дескриптора формату:\ntrace_event_fields_sched_switch[]\nСтворення записів у tracefs:\nformat, filter, enable, trigger", fill="#eef7e9", stroke="#4b9932", size=11)
    frags.extend([s1, s2, s3])

    # Downward arrows from top to stages
    frags.append(arrow(167, 110, 167, 135, color="#d98c21"))
    frags.append(arrow(430, 110, 430, 135, color="#d98c21"))
    frags.append(arrow(692, 110, 692, 135, color="#d98c21"))

    # Bottom summary box
    bot_box = fitbox(50, 280, 760, 65, "Результат компіляції: єдиний макрос TRACE_EVENT створює двійковий макет, функцію запису,\nінтерфейс фільтрації та експорт у /sys/kernel/tracing/events/ без дублювання коду", fill="#f4f6f8", stroke="#888888", size=12)
    frags.append(bot_box)

    render(path, 860, 360, *frags, title="Багатофазна кодогенерація макросу TRACE_EVENT через define_trace.h")

def render_hist_pipeline(path):
    frags = []

    # 4 stages of pipeline
    b1 = fitbox(30, 60, 175, 110, "1. Подія ядра\n\nВиклик tracepoint\nНаприклад:\nsched:sched_switch\nабо net:netif_rx", fill="#e8f4f8", stroke="#2b7b98", size=12)
    b2 = fitbox(235, 60, 185, 110, "2. Фільтр ftrace\n\nОбчислення предиката\nПарсинг полів у ядрі:\nprev_state == 1 &&\nprev_prio > 100", fill="#f9f2e7", stroke="#d98c21", size=12)
    b3 = fitbox(450, 60, 185, 110, "3. Хеш-таблиця hist\n\nАгрегація в пам'яті:\nКлючі (keys=prev_comm)\nЗначення (vals=hitcount)\nМодифікатори (.log2)", fill="#f3e8f8", stroke="#7b2b98", size=12)
    b4 = fitbox(665, 60, 165, 110, "4. Експорт / tracefs\n\nЧитання файлу hist\nГотовий звіт розподілу\nБез викликів userspace\nНульовий I/O оверхед", fill="#eef7e9", stroke="#4b9932", size=12)

    frags.extend([b1, b2, b3, b4])

    frags.append(arrow(205, 115, 235, 115, color="#2b7b98", sw=2))
    frags.append(arrow(420, 115, 450, 115, color="#d98c21", sw=2))
    frags.append(arrow(635, 115, 665, 115, color="#7b2b98", sw=2))

    # Synthetic events box below
    syn_box = fitbox(30, 195, 800, 75, "Синтетичні події (Synthetic Events):\nЗбереження мітки часу в точці А (наприклад, sched_waking) -> обчислення дельти в точці Б (sched_switch)\nРезультат: розрахунок латентності планувальника повністю всередині ядра Linux", fill="#eef7e9", stroke="#4b9932", size=12)
    frags.append(syn_box)

    render(path, 860, 290, *frags, title="Конвеєр внутрішньоядерної агрегації даних через hist-тригери ftrace")

def build_svgs():
    render_tracepoint_lifecycle(os.path.join(IMG, "tracepoint-lifecycle.svg"))
    render_macro_stages(os.path.join(IMG, "trace-event-macro-stages.svg"))
    render_hist_pipeline(os.path.join(IMG, "hist-trigger-pipeline.svg"))
    print("Tracepoints SVG figures generated successfully in img/.")

if __name__ == "__main__":
    build_svgs()
