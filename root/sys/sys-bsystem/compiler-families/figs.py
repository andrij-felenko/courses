# -*- coding: utf-8 -*-
"""Фігури до теми «GCC, Clang і MSVC: де вони розходяться»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

PANEL = "#f8fafc"
GCC_COLOR = "#b45309"
LLVM_COLOR = "#1d4ed8"
MSVC_COLOR = "#047857"


# ── 1. Архітектурні моделі трьох родин компіляторів ──────────────────────────
def fig_pipeline_comparison():
    W, H = 1040, 520
    p = []

    # Колонка 1: GCC
    p.append(rect(40, 50, 300, 440, fill=PANEL, stroke=GCC_COLOR, sw=1.8))
    p.append(text(190, 80, "GCC (GNU Toolchain)", size=16, bold=True, color=GCC_COLOR))
    p.append(fitbox(65, 105, 250, 45, "Джерело (.c / .cpp)", size=13.5, fill=BG))
    p.append(arrow(190, 150, 190, 175, color=LINE, sw=1.5))
    p.append(fitbox(65, 175, 250, 55, "Фронтенд cc1 / cc1plus\n(AST → GENERIC)", size=13, fill=BG))
    p.append(arrow(190, 230, 190, 255, color=LINE, sw=1.5))
    p.append(fitbox(65, 255, 250, 55, "GIMPLE (Tree-SSA)\n→ RTL (Register Transfer)", size=13, fill=BG))
    p.append(arrow(190, 310, 190, 335, color=LINE, sw=1.5))
    p.append(fitbox(65, 335, 250, 50, "Бекенд кодогенерації\n→ Асемблерний файл (.s)", size=13, fill=BG))
    p.append(arrow(190, 385, 190, 410, color=LINE, sw=1.5))
    p.append(fitbox(65, 410, 250, 60, "Зовнішні GNU as та ld\n→ Бінарний ELF / .o", size=13, fill="#fef3c7", stroke=GCC_COLOR))

    # Колонка 2: Clang / LLVM
    p.append(rect(370, 50, 300, 440, fill=PANEL, stroke=LLVM_COLOR, sw=1.8))
    p.append(text(520, 80, "Clang / LLVM", size=16, bold=True, color=LLVM_COLOR))
    p.append(fitbox(395, 105, 250, 45, "Джерело (.c / .cpp)", size=13.5, fill=BG))
    p.append(arrow(520, 150, 520, 175, color=LINE, sw=1.5))
    p.append(fitbox(395, 175, 250, 55, "libclang (Lexer + Parser)\n→ Модульний Clang AST", size=13, fill=BG))
    p.append(arrow(520, 230, 520, 255, color=LINE, sw=1.5))
    p.append(fitbox(395, 255, 250, 55, "LLVM IR (Intermediate Repr.)\n+ Бібліотека оптимізацій opt", size=13, fill=BG))
    p.append(arrow(520, 310, 520, 335, color=LINE, sw=1.5))
    p.append(fitbox(395, 335, 250, 50, "LLVM Target / MC Layer\n(Інтегрований асемблер)", size=13, fill=BG))
    p.append(arrow(520, 385, 520, 410, color=LINE, sw=1.5))
    p.append(fitbox(395, 410, 250, 60, "LLD / Системний лінкер\n(ELF, Mach-O, COFF/lld-link)", size=13, fill="#dbeafe", stroke=LLVM_COLOR))

    # Колонка 3: MSVC
    p.append(rect(700, 50, 300, 440, fill=PANEL, stroke=MSVC_COLOR, sw=1.8))
    p.append(text(850, 80, "MSVC (cl.exe)", size=16, bold=True, color=MSVC_COLOR))
    p.append(fitbox(725, 105, 250, 45, "Джерело (.c / .cpp)", size=13.5, fill=BG))
    p.append(arrow(850, 150, 850, 175, color=LINE, sw=1.5))
    p.append(fitbox(725, 175, 250, 55, "Фронтенд c1.dll / c1xx.dll\n(Синтаксис і семантика)", size=13, fill=BG))
    p.append(arrow(850, 230, 850, 255, color=LINE, sw=1.5))
    p.append(fitbox(725, 255, 250, 55, "C2 / UTC Optimizer\n(Внутрішнє проміжне IL)", size=13, fill=BG))
    p.append(arrow(850, 310, 850, 335, color=LINE, sw=1.5))
    p.append(fitbox(725, 335, 250, 50, "Генерація машинного коду\n→ COFF об'єктний файл (.obj)", size=13, fill=BG))
    p.append(arrow(850, 385, 850, 410, color=LINE, sw=1.5))
    p.append(fitbox(725, 410, 250, 60, "Microsoft LINK (link.exe)\n→ Windows PE / DLL / EXE", size=13, fill="#d1fae5", stroke=MSVC_COLOR))

    render(os.path.join(IMG, "pipeline-comparison.svg"), W, H, *p)


# ── 2. Itanium ABI проти Microsoft C++ ABI (розкладка пам'яті) ───────────────
def fig_vtable_layout_abi():
    W, H = 1040, 510
    p = []

    # Ліва секція: Itanium C++ ABI
    p.append(rect(40, 50, 460, 430, fill=PANEL, stroke=LINE, sw=1.5))
    p.append(text(270, 80, "Itanium C++ ABI (Linux, macOS, MinGW)", size=15.5, bold=True, color=LLVM_COLOR))

    # Об'єкт у пам'яті
    p.append(text(150, 115, "Об'єкт у пам'яті (Derived)", size=13.5, bold=True))
    p.append(fitbox(60, 130, 180, 40, "vptr (вказівник на vtable)", size=12.5, fill="#e0f2fe", stroke=LLVM_COLOR))
    p.append(fitbox(60, 175, 180, 35, "BaseA fields", size=12.5, fill=BG))
    p.append(fitbox(60, 215, 180, 40, "vptr_BaseB (вторинний vptr)", size=12.5, fill="#e0f2fe", stroke=LLVM_COLOR))
    p.append(fitbox(60, 260, 180, 35, "BaseB fields", size=12.5, fill=BG))
    p.append(fitbox(60, 300, 180, 35, "Derived fields", size=12.5, fill=BG))
    p.append(fitbox(60, 340, 180, 35, "Virtual Base fields", size=12.5, fill="#fef3c7", stroke=GCC_COLOR))

    # Спільна Таблиця vtable Itanium
    p.append(text(380, 115, "Єдина vtable структури", size=13.5, bold=True))
    p.append(fitbox(280, 130, 200, 35, "virtual base offset (-24)", size=12, fill="#fef3c7", stroke=GCC_COLOR))
    p.append(fitbox(280, 170, 200, 35, "offset-to-top (0)", size=12, fill=BG))
    p.append(fitbox(280, 210, 200, 35, "RTTI type_info pointer", size=12, fill="#f3e8ff", stroke="#9333ea"))
    p.append(fitbox(280, 250, 200, 40, "vfunc1() entry [vptr points here]", size=12, fill="#e0f2fe", stroke=LLVM_COLOR, bold=True))
    p.append(fitbox(280, 295, 200, 35, "vfunc2() entry", size=12, fill=BG))
    p.append(fitbox(280, 335, 200, 40, "thunk to vfunc3() (adjust this)", size=12, fill="#fee2e2", stroke=POS))

    # Стрілка зв'язку vptr -> vfunc1
    p.append(arrow(240, 150, 275, 270, color=LLVM_COLOR, sw=1.6))
    p.append(fitbox(60, 395, 420, 70, "В Itanium ABI зсуви віртуальних баз та RTTI\nзберігаються у від'ємних індексах тієї ж vtable;\nвказівник на метод завжди має розмір 16 байтів.", size=12, fill=BG, stroke=MUTED))

    # Права секція: Microsoft C++ ABI
    p.append(rect(540, 50, 460, 430, fill=PANEL, stroke=LINE, sw=1.5))
    p.append(text(770, 80, "Microsoft Visual C++ ABI (Windows cl.exe)", size=15.5, bold=True, color=MSVC_COLOR))

    # Об'єкт у пам'яті MSVC
    p.append(text(650, 115, "Об'єкт у пам'яті (Derived)", size=13.5, bold=True))
    p.append(fitbox(560, 130, 180, 36, "vftptr (вказівник на vftbl)", size=12, fill="#d1fae5", stroke=MSVC_COLOR))
    p.append(fitbox(560, 170, 180, 36, "BaseA data", size=12, fill=BG))
    p.append(fitbox(560, 210, 180, 36, "vbptr (вказівник на vbtbl)", size=12, fill="#fef3c7", stroke=GCC_COLOR, bold=True))
    p.append(fitbox(560, 250, 180, 36, "Derived data", size=12, fill=BG))
    p.append(fitbox(560, 290, 180, 36, "Virtual Base data", size=12, fill=BG))

    # Дві окремі таблиці MSVC: vftbl та vbtbl
    p.append(text(880, 115, "Окремі таблиці функцій і баз", size=13.5, bold=True))
    p.append(fitbox(780, 130, 200, 35, "Complete Object Locator (RTTI)", size=12, fill="#f3e8ff", stroke="#9333ea"))
    p.append(fitbox(780, 170, 200, 38, "vftbl: [vfunc1, vfunc2...]", size=12, fill="#d1fae5", stroke=MSVC_COLOR, bold=True))
    p.append(fitbox(780, 220, 200, 45, "vbtbl: [Зсув до Derived (0),\nЗсув до Virtual Base (+24)]", size=12, fill="#fef3c7", stroke=GCC_COLOR, bold=True))

    # Стрілки
    p.append(arrow(740, 148, 775, 185, color=MSVC_COLOR, sw=1.6))
    p.append(arrow(740, 228, 775, 240, color=GCC_COLOR, sw=1.6))
    p.append(fitbox(560, 395, 420, 70, "У MSVC віртуальні функції (vftbl) та віртуальні\nбази (vbtbl) розділені на різні таблиці й вказівники;\nрозмір вказівника на метод варіюється від 8 до 32 байтів.", size=12, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, "vtable-layout-abi.svg"), W, H, *p)


# ── 3. Моделі обробки винятків: DWARF/.eh_frame проти Windows SEH ─────────────
def fig_exception_unwinding():
    W, H = 1040, 490
    p = []

    # Ліва панель: Itanium Zero-Cost
    p.append(rect(40, 50, 460, 410, fill=PANEL, stroke=LLVM_COLOR, sw=1.5))
    p.append(text(270, 80, "Itanium ABI: DWARF .eh_frame (Zero-Cost)", size=15, bold=True, color=LLVM_COLOR))
    p.append(fitbox(60, 105, 420, 50, "Нормальне виконання: жодних накладних витрат\n(реєстрація блоків try/catch у рантаймі відсутня)", size=12.5, fill="#f0fdf4", stroke=FIELD))
    p.append(arrow(270, 160, 270, 185, color=LINE, sw=1.5))
    p.append(fitbox(60, 185, 420, 50, "Виклик throw → libunwind (_Unwind_RaiseException)\nФаза 1 (Search): Пошук обробника catch стеком угору", size=12.5, fill=BG))
    p.append(arrow(270, 240, 270, 265, color=LINE, sw=1.5))
    p.append(fitbox(60, 265, 420, 55, "Читання .eh_frame (CFI) + LSDA таблиць компілятора\nВиклик __gxx_personality_v0 для звірки типів", size=12.5, fill="#f3e8ff", stroke="#9333ea"))
    p.append(arrow(270, 325, 270, 350, color=LINE, sw=1.5))
    p.append(fitbox(60, 350, 420, 55, "Фаза 2 (Cleanup): Розмотка кадрів стека,\nвиклики деструкторів RAII та перехід у блок catch", size=12.5, fill="#eff6ff", stroke=LLVM_COLOR))

    # Права панель: Windows SEH
    p.append(rect(540, 50, 460, 410, fill=PANEL, stroke=MSVC_COLOR, sw=1.5))
    p.append(text(770, 80, "Microsoft C++: Windows SEH + __CxxFrameHandler", size=15, bold=True, color=MSVC_COLOR))
    p.append(fitbox(560, 105, 420, 50, "Нормальне виконання на x64: також Zero-Cost\n(усі метадані збережені у статичних секціях PE)", size=12.5, fill="#f0fdf4", stroke=FIELD))
    p.append(arrow(770, 160, 770, 185, color=LINE, sw=1.5))
    p.append(fitbox(560, 185, 420, 50, "throw → RtlRaiseException (Ядро/ntdll SEH диспетчер)\nПошук функції за адресою RIP у секції .pdata (RUNTIME_FUNCTION)", size=12.5, fill=BG))
    p.append(arrow(770, 240, 770, 265, color=LINE, sw=1.5))
    p.append(fitbox(560, 265, 420, 55, "Читання .xdata (UNWIND_INFO) + виклик __CxxFrameHandler3/4\nАналіз таблиць станів (State Index) та типів CatchableType", size=12.5, fill="#f3e8ff", stroke="#9333ea"))
    p.append(arrow(770, 325, 770, 350, color=LINE, sw=1.5))
    p.append(fitbox(560, 350, 420, 55, "RtlUnwindEx: виклик деструкторів локальних об'єктів\nза таблицею станів та передача керування в catch-блок", size=12.5, fill="#ecfdf5", stroke=MSVC_COLOR))

    render(os.path.join(IMG, "exception-unwinding.svg"), W, H, *p)


if __name__ == "__main__":
    fig_pipeline_comparison()
    fig_vtable_layout_abi()
    fig_exception_unwinding()
    print("All figures generated successfully.")
