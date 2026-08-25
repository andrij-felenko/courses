# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def fig_rip_relative_addressing():
    W, H = 840, 360
    p = []

    # Тло
    p.append(rect(0, 0, W, H, fill="#f8fafc", stroke="none"))

    # Сегмент коду (Left)
    p.append(rect(40, 50, 340, 260, fill="#f1f5f9", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(210, 80, "Сегмент коду (.text) [Read-Only]", size=14, color=INK, bold=True))

    # Інструкція в коді
    b1 = fitbox(60, 130, 300, 45, "mov rax, QWORD PTR [rip + 0x2008]", size=12, fill="#ffffff", stroke="#94a3b8", sw=1.2, color="#0f172a", bold=True)
    p.append(b1)

    p.append(text(210, 205, "Поточний RIP = 0x7fff00001000", size=12, color=MUTED))
    p.append(text(210, 230, "Зміщення = +0x2008 (константа збірки)", size=12, color=POS, bold=True))
    p.append(text(210, 275, "Адреса цілі = 0x7fff00003008", size=12.5, color=POS, bold=True))

    # Сегмент даних (Right)
    p.append(rect(460, 50, 340, 260, fill="#f1f5f9", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(630, 80, "Сегмент даних (.got / .data) [Read-Write]", size=14, color=INK, bold=True))

    # Слот в GOT / Змінна
    b2 = fitbox(480, 150, 300, 60, "Слот GOT / Глобальна змінна\nАдреса: 0x7fff00003008", size=12, fill="#e0f2fe", stroke="#0284c7", sw=1.5, color="#0369a1", bold=True)
    p.append(b2)

    p.append(text(630, 250, "Значення: Покажчик на дані в libc.so", size=12, color=INK))

    # Стрілка з відносним зсувом
    p.append(arrow(360, 152, 480, 180, color=POS, sw=2))

    render(os.path.join(OUT, "rip-relative-addressing.svg"), W, H, *p)

def fig_got_plt_flow():
    W, H = 880, 420
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))
    p.append(text(W / 2, 22, "Покроковий потік розв'язання символів через GOT і PLT", size=15, bold=True))

    # Панель 1: Основний код
    p.append(rect(30, 40, 230, 340, fill="#f8fafc", stroke="#e2e8f0", sw=1.5, rx=8))
    p.append(text(145, 70, "Виконуваний код", size=13.5, color=INK, bold=True))
    
    b_call = fitbox(45, 110, 200, 40, "call printf@PLT", size=12, fill="#eff6ff", stroke="#3b82f6", sw=1.3, color="#1d4ed8", bold=True)
    p.append(b_call)
    p.append(text(145, 180, "Прямий відносний виклик\nлокальної секції .plt", size=11.5, color=MUTED))

    # Панель 2: PLT Стуб
    p.append(rect(290, 40, 280, 340, fill="#f8fafc", stroke="#e2e8f0", sw=1.5, rx=8))
    p.append(text(430, 70, "Секція .plt (PLT Stub)", size=13.5, color=INK, bold=True))

    b_plt1 = fitbox(305, 105, 250, 36, "jmp QWORD PTR [rip + GOT_offset]", size=11, fill="#fef3c7", stroke="#f59e0b", sw=1.3, color="#b45309", bold=True)
    p.append(b_plt1)
    
    p.append(text(430, 160, "Перший виклик:", size=11.5, color=POS, bold=True))
    b_plt2 = fitbox(305, 180, 250, 34, "push relocation_index", size=11, fill="#fff", stroke="#cbd5e1", color=INK)
    p.append(b_plt2)

    b_plt3 = fitbox(305, 225, 250, 34, "jmp PLT0 -> Dynamic Resolver", size=11, fill="#fef2f2", stroke="#ef4444", color="#b91c1c", bold=True)
    p.append(b_plt3)

    p.append(text(430, 290, "Після резолву:\nJMP одразу переходить у libc!", size=11.5, color=POS, bold=True))

    # Панель 3: GOT Таблиця та Libc
    p.append(rect(600, 40, 250, 340, fill="#f8fafc", stroke="#e2e8f0", sw=1.5, rx=8))
    p.append(text(725, 70, "GOT та Цільовий код", size=13.5, color=INK, bold=True))

    b_got = fitbox(615, 110, 220, 50, "GOT Entry (printf)\nСпочатку: вказує на push в PLT\nДалі: адреса реального printf", size=10.5, fill="#e0e7ff", stroke="#6366f1", sw=1.3, color="#4338ca", bold=True)
    p.append(b_got)

    b_libc = fitbox(615, 230, 220, 70, "libc.so (.text)\nАдреса: 0x7ffff7a80120\nРеальне виконання printf()", size=11, fill="#dcfce7", stroke="#22c55e", sw=1.3, color="#15803d", bold=True)
    p.append(b_libc)

    # Стрілки
    p.append(arrow(245, 130, 305, 123, color="#3b82f6", sw=1.8))
    p.append(arrow(555, 123, 615, 135, color="#f59e0b", sw=1.8))
    p.append(arrow(725, 160, 725, 230, color="#22c55e", sw=1.8))

    render(os.path.join(OUT, "got-plt-flow.svg"), W, H, *p)

def fig_aslr_pie_layout():
    W, H = 840, 440
    p = []

    p.append(rect(0, 0, W, H, fill="#f8fafc", stroke="none"))
    p.append(text(W / 2, 22, "Структура адресного простору процесу: Non-PIE проти PIE", size=15, bold=True))

    # Панель 1: Без PIE
    p.append(rect(40, 50, 360, 350, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(220, 80, "Виконуваний файл БЕЗ PIE", size=14, color=POS, bold=True))
    p.append(text(220, 105, "Фіксоване розміщення в пам'яті", size=12, color=MUTED))

    # Секції без PIE
    b_nopie_code = fitbox(60, 130, 320, 45, "Код програми (.text)\nАдреса ФІКСОВАНА: 0x00400000", size=11.5, fill="#fde8e8", stroke="#f87171", sw=1.2, color="#991b1b", bold=True)
    p.append(b_nopie_code)

    b_nopie_data = fitbox(60, 185, 320, 45, "Глобальні дані (.data / .bss)\nАдреса ФІКСОВАНА: 0x00601000", size=11.5, fill="#fde8e8", stroke="#f87171", sw=1.2, color="#991b1b", bold=True)
    p.append(b_nopie_data)

    b_nopie_lib = fitbox(60, 255, 320, 45, "Спільні бібліотеки (libc.so)\nРандомізовано через ASLR", size=11.5, fill="#dcfce7", stroke="#4ade80", sw=1.2, color="#166534")
    p.append(b_nopie_lib)

    b_nopie_stack = fitbox(60, 310, 320, 45, "Стек і Купа (Stack / Heap)\nРандомізовано через ASLR", size=11.5, fill="#dcfce7", stroke="#4ade80", sw=1.2, color="#166534")
    p.append(b_nopie_stack)

    # Панель 2: З PIE
    p.append(rect(440, 50, 360, 350, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(620, 80, "Позиційно-незалежний бінарник (PIE)", size=14, color="#0284c7", bold=True))
    p.append(text(620, 105, "Повна рандомізація адресного простору", size=12, color=MUTED))

    # Секції з PIE
    b_pie_code = fitbox(460, 130, 320, 45, "Код програми (.text)\nВИПАДКОВА адреса: 0x55a4b18f0000", size=11.5, fill="#e0f2fe", stroke="#38bdf8", sw=1.2, color="#075985", bold=True)
    p.append(b_pie_code)

    b_pie_data = fitbox(460, 185, 320, 45, "Глобальні дані (.data / .got)\nВИПАДКОВА адреса: 0x55a4b18f3000", size=11.5, fill="#e0f2fe", stroke="#38bdf8", sw=1.2, color="#075985", bold=True)
    p.append(b_pie_data)

    b_pie_lib = fitbox(460, 255, 320, 45, "Спільні бібліотеки (libc.so)\nВИПАДКОВА адреса: 0x7f3a90100000", size=11.5, fill="#dcfce7", stroke="#4ade80", sw=1.2, color="#166534")
    p.append(b_pie_lib)

    b_pie_stack = fitbox(460, 310, 320, 45, "Стек і Купа (Stack / Heap)\nВИПАДКОВА адреса: 0x7ffc88210000", size=11.5, fill="#dcfce7", stroke="#4ade80", sw=1.2, color="#166534")
    p.append(b_pie_stack)

    render(os.path.join(OUT, "aslr-pie-layout.svg"), W, H, *p)

def main():
    fig_rip_relative_addressing()
    fig_got_plt_flow()
    fig_aslr_pie_layout()

if __name__ == "__main__":
    main()
