# -*- coding: utf-8 -*-
"""Фігури до теми «COM: бінарна модель компонентів Windows»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM   = "#fdecea"   # перевантаження / небезпека / стан пам'яті
COOL   = "#eaf0fd"   # інтерфейси / проксі / нейтральне
GOOD   = "#e8f6ee"   # успіх / об'єкт / реалізація
ACCENT = "#fbf4db"   # фабрики / vtable / перехідні стани


# ── 1. Бінарна розкладка пам'яті: екземпляр об'єкта та таблиці vtable ──────────
def com_vtable_layout():
    W, H = 1000, 560
    f = []

    # Заголовки колонок
    f.append(rect(40, 25, 300, 40, fill=GOOD, stroke=FIELD, sw=1.5))
    f.append(text(190, 50, "Екземпляр об'єкта в купі (Heap)", size=14, color=FIELD, bold=True))

    f.append(rect(520, 25, 430, 40, fill=ACCENT, stroke=LINE, sw=1.5))
    f.append(text(735, 50, "Віртуальні таблиці методів (vtable у Read-Only Data)", size=14, color=INK, bold=True))

    # Тіло екземпляра
    f.append(rect(40, 85, 300, 390, fill=FILL, stroke=LINE, sw=1.5))

    # Слот 1: vptr ICalculator
    f.append(rect(55, 105, 270, 60, fill=COOL, stroke=NEG, sw=1.5))
    f.append(text(190, 130, "vptr_ICalculator (8 байтів)", size=13, color=NEG, bold=True))
    f.append(text(190, 150, "Вказівник на таблицю ICalculator", size=11, color=MUTED))

    # Слот 2: vptr IPersist
    f.append(rect(55, 185, 270, 60, fill=COOL, stroke=NEG, sw=1.5))
    f.append(text(190, 210, "vptr_IPersist (8 байтів)", size=13, color=NEG, bold=True))
    f.append(text(190, 230, "Вказівник на таблицю IPersist", size=11, color=MUTED))

    # Внутрішній стан
    f.append(rect(55, 265, 270, 185, fill=WARM, stroke=POS, sw=1.5))
    f.append(text(190, 295, "Внутрішні поля об'єкта (Private State)", size=12, color=POS, bold=True))
    f.append(line(70, 310, 310, 310, color=POS, sw=1, dash="3,3"))
    f.append(text(190, 335, "LONG m_refCount = 2", size=12, color=INK))
    f.append(text(190, 365, "double m_accumulator = 0.0", size=12, color=INK))
    f.append(text(190, 395, "CRITICAL_SECTION m_cs", size=12, color=INK))
    f.append(text(190, 425, "Зміна розміру не ламає vtable ABI", size=11, color=POS, italic=True))

    # vtable ICalculator
    f.append(rect(520, 85, 430, 230, fill=FILL, stroke=LINE, sw=1.5))
    f.append(text(735, 110, "Таблиця методів ICalculator (vtable)", size=13, color=INK, bold=True))
    f.append(line(535, 120, 935, 120, color=MUTED, sw=1))

    f.append(fitbox(535, 130, 400, 32, "[0] QueryInterface(REFIID, void**)", size=12, fill=GOOD, stroke=FIELD))
    f.append(fitbox(535, 168, 400, 32, "[1] AddRef() -> ULONG", size=12, fill=GOOD, stroke=FIELD))
    f.append(fitbox(535, 206, 400, 32, "[2] Release() -> ULONG", size=12, fill=GOOD, stroke=FIELD))
    f.append(fitbox(535, 244, 400, 32, "[3] Add(double, double, double*)", size=12, fill=COOL, stroke=NEG))
    f.append(fitbox(535, 278, 400, 32, "[4] Multiply(double, double, double*)", size=12, fill=COOL, stroke=NEG))

    # vtable IPersist
    f.append(rect(520, 335, 430, 185, fill=FILL, stroke=LINE, sw=1.5))
    f.append(text(735, 360, "Таблиця методів IPersist (vtable)", size=13, color=INK, bold=True))
    f.append(line(535, 370, 935, 370, color=MUTED, sw=1))

    f.append(fitbox(535, 380, 400, 30, "[0] QueryInterface(REFIID, void**)", size=12, fill=GOOD, stroke=FIELD))
    f.append(fitbox(535, 415, 400, 30, "[1] AddRef() -> ULONG", size=12, fill=GOOD, stroke=FIELD))
    f.append(fitbox(535, 450, 400, 30, "[2] Release() -> ULONG", size=12, fill=GOOD, stroke=FIELD))
    f.append(fitbox(535, 485, 400, 30, "[3] GetClassID(CLSID*)", size=12, fill=COOL, stroke=NEG))

    # Стрілки зв'язку
    f.append(arrow(325, 135, 520, 145, color=NEG, sw=2))
    f.append(arrow(325, 215, 520, 395, color=NEG, sw=2))

    # Пояснення знизу
    f.append(fitbox(40, 495, 450, 48,
                    "Клієнтський інтерфейсний вказівник: pCalc -> vptr -> vtable[method]\nДворівневе розіменування відокремлює бінарний контракт від компілятора",
                    size=11, fill="#ffffff", stroke=MUTED))

    f.append(fitbox(520, 525, 430, 25,
                    "Усі COM-інтерфейси починаються з трьох слотів IUnknown",
                    size=11, fill=ACCENT, stroke=LINE, bold=True))

    render(os.path.join(OUT, 'com-vtable-layout.svg'), W, H, *f)


# ── 2. Закони QueryInterface та ідентичність об'єкта ───────────────────────────
def iunknown_query_interface():
    W, H = 1000, 580
    f = []

    # Фонова плашка об'єкта
    f.append(rect(50, 30, 900, 510, fill="#fafbfc", stroke=LINE, sw=1.5, rx=10))
    f.append(text(500, 60, "Єдиний COM-об'єкт (COM Component Instance)", size=16, color=INK, bold=True))

    # Центральний канонічний IUnknown
    f.append(rect(340, 90, 320, 110, fill=GOOD, stroke=FIELD, sw=2.5, rx=8))
    f.append(text(500, 120, "Канонічний IUnknown", size=14, color=FIELD, bold=True))
    f.append(text(500, 145, "Вказівник адреси об'єкта (0x1000)", size=12, color=INK))
    f.append(text(500, 170, "Закон ідентичності: QI(IID_IUnknown) завжди повертає 0x1000", size=10.5, color=FIELD, bold=True))

    # Інтерфейс A: ICalculator
    f.append(rect(100, 260, 240, 110, fill=COOL, stroke=NEG, sw=1.8, rx=8))
    f.append(text(220, 290, "Інтерфейс ICalculator", size=13, color=NEG, bold=True))
    f.append(text(220, 315, "Вказівник: 0x1000 (vptr #1)", size=11, color=INK))
    f.append(text(220, 340, "Методи: Add, Multiply", size=11, color=MUTED))

    # Інтерфейс B: IPersist
    f.append(rect(660, 260, 240, 110, fill=COOL, stroke=NEG, sw=1.8, rx=8))
    f.append(text(780, 290, "Інтерфейс IPersist", size=13, color=NEG, bold=True))
    f.append(text(780, 315, "Вказівник: 0x1008 (vptr #2)", size=11, color=INK))
    f.append(text(780, 340, "Методи: GetClassID", size=11, color=MUTED))

    # Інтерфейс C: ISupportErrorInfo
    f.append(rect(380, 390, 240, 95, fill=ACCENT, stroke=LINE, sw=1.8, rx=8))
    f.append(text(500, 420, "Інтерфейс ISupportErrorInfo", size=13, color=INK, bold=True))
    f.append(text(500, 445, "Вказівник: 0x1010 (vptr #3)", size=11, color=INK))
    f.append(text(500, 465, "Методи: InterfaceSupportsErrorInfo", size=10, color=MUTED))

    # Стрілки навігації між інтерфейсами
    f.append(arrow(220, 260, 400, 200, color=FIELD, sw=2))
    f.append(arrow(780, 260, 600, 200, color=FIELD, sw=2))
    f.append(arrow(500, 390, 500, 200, color=FIELD, sw=2))

    # Симетричність та транзитивність між A, B, C
    f.append(arrow(340, 315, 660, 315, color=NEG, sw=2))
    f.append(arrow(660, 335, 340, 335, color=NEG, sw=2))
    f.append(text(500, 305, "Симетрія: QI(IPersist) ⇄ QI(ICalculator)", size=11, color=NEG, bold=True))

    f.append(arrow(300, 370, 400, 400, color=MUTED, sw=1.5))
    f.append(arrow(700, 370, 600, 400, color=MUTED, sw=1.5))

    # Пояснювальні плашки аксіом внизу
    f.append(fitbox(70, 490, 260, 40,
                    "Рефлексивність:\npA->QI(IID_A) завжди успішний",
                    size=10.5, fill=GOOD, stroke=FIELD))

    f.append(fitbox(370, 490, 260, 40,
                    "Транзитивність:\nякщо A->B і B->C, то A->C гарантовано",
                    size=10.5, fill=GOOD, stroke=FIELD))

    f.append(fitbox(670, 490, 260, 40,
                    "Сталість у часі:\nуспішний запит завжди лишається успішним",
                    size=10.5, fill=GOOD, stroke=FIELD))

    render(os.path.join(OUT, 'iunknown-query-interface.svg'), W, H, *f)


# ── 3. Конвеєр активації: CoCreateInstance та фабрика класів ───────────────────
def com_activation_pipeline():
    W, H = 1040, 560
    f = []

    # Крок 1: Клієнт
    f.append(rect(30, 80, 210, 280, fill=COOL, stroke=NEG, sw=1.8, rx=8))
    f.append(text(135, 110, "1. Клієнтський код", size=14, color=NEG, bold=True))
    f.append(line(45, 125, 225, 125, color=MUTED, sw=1))
    f.append(text(135, 150, "CoCreateInstance(", size=11, color=INK, bold=True))
    f.append(text(135, 175, "  CLSID_Calculator,", size=11, color=POS))
    f.append(text(135, 200, "  CLSCTX_INPROC,", size=11, color=MUTED))
    f.append(text(135, 225, "  IID_ICalculator,", size=11, color=NEG))
    f.append(text(135, 250, "  (void**)&pCalc);", size=11, color=INK, bold=True))
    f.append(text(135, 300, "Отримує готовий", size=11, color=FIELD))
    f.append(text(135, 325, "вказівник pCalc", size=12, color=FIELD, bold=True))

    # Крок 2: Реєстр Windows
    f.append(rect(280, 40, 240, 160, fill=ACCENT, stroke=LINE, sw=1.8, rx=8))
    f.append(text(400, 65, "2. Реєстр Windows (COM SCM)", size=13, color=INK, bold=True))
    f.append(line(295, 78, 505, 78, color=MUTED, sw=1))
    f.append(text(400, 100, "HKCR\\CLSID\\{...}", size=11, color=POS))
    f.append(text(400, 125, "InprocServer32 = calc.dll", size=11, color=INK, bold=True))
    f.append(text(400, 150, "ThreadingModel = Apartment", size=10.5, color=MUTED))
    f.append(text(400, 175, "Локалізація DLL за GUID", size=10.5, color=FIELD))

    # Крок 3: Завантаження DLL та DllGetClassObject
    f.append(rect(280, 240, 240, 160, fill=FILL, stroke=LINE, sw=1.8, rx=8))
    f.append(text(400, 265, "3. Динамічна бібліотека", size=13, color=INK, bold=True))
    f.append(line(295, 278, 505, 278, color=MUTED, sw=1))
    f.append(text(400, 300, "LoadLibrary(\"calc.dll\")", size=11, color=INK))
    f.append(text(400, 325, "GetProcAddress(", size=11, color=INK))
    f.append(text(400, 350, "  \"DllGetClassObject\")", size=11, color=NEG, bold=True))
    f.append(text(400, 375, "Отримання фабрики", size=11, color=MUTED))

    # Крок 4: Фабрика класів IClassFactory
    f.append(rect(560, 120, 220, 220, fill=ACCENT, stroke=FIELD, sw=2, rx=8))
    f.append(text(670, 150, "4. IClassFactory", size=14, color=FIELD, bold=True))
    f.append(line(575, 165, 765, 165, color=MUTED, sw=1))
    f.append(text(670, 195, "CreateInstance(", size=12, color=INK, bold=True))
    f.append(text(670, 220, "  pUnkOuter, IID, ppv)", size=11, color=INK))
    f.append(text(670, 255, "Створює екземпляр через", size=11, color=MUTED))
    f.append(text(670, 280, "оператор new у пам'яті DLL", size=11, color=INK, bold=True))
    f.append(text(670, 310, "LockServer(BOOL fLock)", size=11, color=MUTED))

    # Крок 5: Екземпляр COM-компонента
    f.append(rect(820, 120, 190, 220, fill=GOOD, stroke=FIELD, sw=2, rx=8))
    f.append(text(915, 150, "5. Екземпляр CCalc", size=13, color=FIELD, bold=True))
    f.append(line(835, 165, 995, 165, color=MUTED, sw=1))
    f.append(text(915, 195, "vptr -> vtable", size=12, color=NEG, bold=True))
    f.append(text(915, 225, "m_refCount = 1", size=11, color=POS))
    f.append(text(915, 255, "QueryInterface(", size=11, color=INK))
    f.append(text(915, 280, "  IID_ICalculator)", size=11, color=NEG))
    f.append(text(915, 310, "Повернення клієнту", size=11, color=FIELD, bold=True))

    # Стрілки процесу
    f.append(arrow(240, 140, 280, 120, color=INK, sw=2))
    f.append(arrow(400, 200, 400, 240, color=INK, sw=2))
    f.append(arrow(520, 320, 560, 260, color=INK, sw=2))
    f.append(arrow(780, 230, 820, 230, color=FIELD, sw=2))
    f.append(arrow(820, 300, 240, 300, color=FIELD, sw=2.5))

    # Пояснення знизу
    f.append(fitbox(30, 430, 980, 95,
                    "Повний життєвий цикл активації:\n"
                    "1. Клієнт звертається за CLSID → 2. SCM знаходить шлях до DLL у реєстрі → "
                    "3. SCM вантажить DLL та викликає DllGetClassObject →\n"
                    "4. Фабрика IClassFactory виділяє пам'ять об'єкта → 5. Інтерфейсний вказівник повертається клієнту, а фабрика звільняється.",
                    size=12, fill="#ffffff", stroke=MUTED))

    render(os.path.join(OUT, 'com-activation-pipeline.svg'), W, H, *f)


# ── 4. Моделі багатопоточності: STA, MTA та міжпотоковий маршалінг ─────────────
def com_apartments_sta_mta():
    W, H = 1040, 560
    f = []

    # Апартамент STA (Single-Threaded Apartment)
    f.append(rect(40, 40, 430, 440, fill="#f8fafc", stroke=NEG, sw=2, rx=10))
    f.append(text(255, 70, "STA: Однопотоковий апартамент (Single-Threaded)", size=13.5, color=NEG, bold=True))

    f.append(rect(65, 95, 380, 80, fill=COOL, stroke=NEG, sw=1.5))
    f.append(text(255, 120, "Виділений потік користувацького інтерфейсу (UI Thread)", size=11.5, color=NEG, bold=True))
    f.append(text(255, 145, "Цикл обробки повідомлень: GetMessage / DispatchMessage", size=11, color=INK))

    f.append(rect(65, 190, 380, 90, fill=ACCENT, stroke=LINE, sw=1.5))
    f.append(text(255, 215, "Приховане системне вікно (Hidden HWND)", size=12, color=INK, bold=True))
    f.append(text(255, 240, "Вхідні виклики з інших потоків чергуються як", size=11, color=MUTED))
    f.append(text(255, 260, "повідомлення WM_USER у черзі потоку", size=11, color=POS, bold=True))

    f.append(rect(65, 295, 380, 165, fill=GOOD, stroke=FIELD, sw=1.5))
    f.append(text(255, 325, "COM-об'єкт в STA", size=13, color=FIELD, bold=True))
    f.append(text(255, 355, "Виконується СТРОГО в одному потоці", size=12, color=INK, bold=True))
    f.append(text(255, 385, "Потокобезпека без внутрішніх м'ютексів", size=11.5, color=FIELD))
    f.append(text(255, 415, "Небезпека: блокування потоку зупиняє весь UI", size=11, color=POS))
    f.append(text(255, 440, "Вхідний виклик викликає реентрабельність повідомлень", size=10.5, color=MUTED, italic=True))

    # Апартамент MTA (Multi-Threaded Apartment)
    f.append(rect(570, 40, 430, 440, fill="#f8fafc", stroke=FIELD, sw=2, rx=10))
    f.append(text(785, 70, "MTA: Багатопотоковий апартамент (Multi-Threaded)", size=13.5, color=FIELD, bold=True))

    f.append(rect(595, 95, 380, 80, fill=GOOD, stroke=FIELD, sw=1.5))
    f.append(text(785, 120, "Пул робочих потоків (Worker Threads)", size=12, color=FIELD, bold=True))
    f.append(text(785, 145, "Потік 1, Потік 2, Потік N заходять паралельно", size=11, color=INK))

    f.append(rect(595, 190, 380, 90, fill=FILL, stroke=LINE, sw=1.5))
    f.append(text(785, 215, "Прямий паралельний виклик методів", size=12, color=INK, bold=True))
    f.append(text(785, 240, "Немає циклу Windows Messages", size=11, color=MUTED))
    f.append(text(785, 260, "Виклики не серіалізуються чергою", size=11, color=FIELD, bold=True))

    f.append(rect(595, 295, 380, 165, fill=WARM, stroke=POS, sw=1.5))
    f.append(text(785, 325, "COM-об'єкт в MTA", size=13, color=POS, bold=True))
    f.append(text(785, 355, "Одночасний доступ з багатьох ядер", size=12, color=INK, bold=True))
    f.append(text(785, 385, "ОБОВ'ЯЗКОВА синхронізація:", size=11.5, color=POS, bold=True))
    f.append(text(785, 415, "CRITICAL_SECTION, SRWLock, Interlocked", size=11, color=INK))
    f.append(text(785, 440, "Висока пропускна здатність на серверах", size=10.5, color=FIELD))

    # Міжапартаментний міст (Маршалінг)
    f.append(arrow(470, 230, 570, 230, color=POS, sw=2.5))
    f.append(arrow(570, 260, 470, 260, color=POS, sw=2.5))
    f.append(fitbox(450, 120, 140, 75,
                    "Міжпотоковий\nмаршалінг\n(Proxy / Stub)\nCoMarshal...",
                    size=10.5, fill="#ffffff", stroke=POS, bold=True))

    # Пояснення знизу
    f.append(fitbox(40, 495, 960, 48,
                    "Пряма передача сирого вказівника між апартаментами ЗАБОРОНЕНА. "
                    "COM створює проксі для безпечного перемикання контексту потоків.",
                    size=11.5, fill=ACCENT, stroke=LINE, bold=True))

    render(os.path.join(OUT, 'com-apartments-sta-mta.svg'), W, H, *f)


# ── 5. Розподілений DCOM: Проксі, Стаби, RPC та прозорість розташування ────────
def dcom_proxy_stub_rpc():
    W, H = 1040, 560
    f = []

    # Клієнтський процес (Process A / Host A)
    f.append(rect(30, 40, 420, 440, fill="#f8fafc", stroke=NEG, sw=2, rx=10))
    f.append(text(240, 68, "Клієнтський процес (Client Process)", size=14, color=NEG, bold=True))

    f.append(rect(55, 95, 370, 95, fill=COOL, stroke=NEG, sw=1.5))
    f.append(text(240, 120, "Клієнтський застосунок", size=13, color=NEG, bold=True))
    f.append(text(240, 145, "Виклик: pCalc->Add(10.0, 20.0, &res)", size=12, color=INK, bold=True))
    f.append(text(240, 170, "Прозорість: думає, що об'єкт поруч у пам'яті", size=10.5, color=MUTED, italic=True))

    f.append(rect(55, 210, 370, 120, fill=ACCENT, stroke=LINE, sw=1.5))
    f.append(text(240, 235, "In-Process Proxy (Proxy DLL / ole32.dll)", size=12.5, color=INK, bold=True))
    f.append(text(240, 260, "Реалізує vtable інтерфейсу ICalculator", size=11, color=NEG, bold=True))
    f.append(text(240, 285, "Серіалізація параметрів у буфер NDR", size=11, color=INK))
    f.append(text(240, 310, "Канал передачі: IRpcChannelBuffer", size=10.5, color=FIELD))

    f.append(rect(55, 350, 370, 110, fill=FILL, stroke=LINE, sw=1.5))
    f.append(text(240, 375, "RPC Клієнтський рантайм", size=12, color=INK, bold=True))
    f.append(text(240, 400, "Передача через ALPC (між процесами) або", size=11, color=MUTED))
    f.append(text(240, 425, "DCOM TCP/IP Порт 135 + динамічний порт", size=11, color=POS, bold=True))

    # Серверний процес (Process B / Host B)
    f.append(rect(590, 40, 420, 440, fill="#f8fafc", stroke=FIELD, sw=2, rx=10))
    f.append(text(800, 68, "Серверний процес (Server Process / DCOM)", size=14, color=FIELD, bold=True))

    f.append(rect(615, 95, 370, 95, fill=GOOD, stroke=FIELD, sw=2))
    f.append(text(800, 120, "Справжній COM-об'єкт (Real Object)", size=13, color=FIELD, bold=True))
    f.append(text(800, 145, "Виконує обчислення в локальній пам'яті", size=11.5, color=INK, bold=True))
    f.append(text(800, 170, "Повертає обчислений результат та HRESULT", size=10.5, color=MUTED))

    f.append(rect(615, 210, 370, 120, fill=ACCENT, stroke=LINE, sw=1.5))
    f.append(text(800, 235, "In-Process Stub (Stub DLL / ole32.dll)", size=12.5, color=INK, bold=True))
    f.append(text(800, 260, "Десеріалізація аргументів з NDR-буфера", size=11, color=INK))
    f.append(text(800, 285, "Виклик цільового методу через vtable", size=11, color=FIELD, bold=True))
    f.append(text(800, 310, "Пакування результату в буфер відповіді", size=10.5, color=POS))

    f.append(rect(615, 350, 370, 110, fill=FILL, stroke=LINE, sw=1.5))
    f.append(text(800, 375, "RPC Серверний рантайм", size=12, color=INK, bold=True))
    f.append(text(800, 400, "Слухає сокет / ALPC порт повідомлень", size=11, color=MUTED))
    f.append(text(800, 425, "Прийом запиту та повернення пакета відповіді", size=11, color=INK))

    # Зв'язки всередині клієнтського процесу (вниз)
    f.append(arrow(240, 190, 240, 210, color=NEG, sw=2))
    f.append(arrow(240, 330, 240, 350, color=INK, sw=2))

    # Зв'язки через мережу/IPC (горизонтальні)
    f.append(arrow(425, 385, 615, 385, color=POS, sw=2.5))
    f.append(arrow(615, 415, 425, 415, color=FIELD, sw=2))

    # Зв'язки всередині серверного процесу (вгору)
    f.append(arrow(800, 350, 800, 330, color=INK, sw=2))
    f.append(arrow(800, 210, 800, 190, color=FIELD, sw=2))

    # Плашка на межі
    f.append(fitbox(450, 170, 140, 95,
                    "Межа процесу\nабо мережі\n(IPC / RPC / DCOM)\nNDR Protocol",
                    size=11, fill="#ffffff", stroke=POS, bold=True))

    # Пояснення знизу
    f.append(fitbox(30, 495, 980, 48,
                    "Прозорість розташування (Location Transparency): клієнт викликає той самий vtable-інтерфейс, "
                    "а вся складна мережева та міжпроцесна комунікація прихована парою Proxy/Stub.",
                    size=11.5, fill=GOOD, stroke=FIELD, bold=True))

    render(os.path.join(OUT, 'dcom-proxy-stub-rpc.svg'), W, H, *f)


if __name__ == '__main__':
    com_vtable_layout()
    iunknown_query_interface()
    com_activation_pipeline()
    com_apartments_sta_mta()
    dcom_proxy_stub_rpc()
    print("Всі фігури COM успішно згенеровано.")
