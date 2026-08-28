# 📋 Довідник API керування GIL: C-макроси, стан інтерпретатора та системні параметри

Цей довідник містить повну специфікацію низькорівневих функцій та макросів CPython C API для контролю Global Interpreter Lock у нативних модулях, правила взаємодії зі станом інтерпретатора `PyThreadState`, системні параметри середовища виконання Python, інваріанти безпеки пам'яті та керування субінтерпретаторами.

## 1. Архітектура стану потоку PyThreadState та макроси вивільнення GIL

Усі модулі розширення мовами C, C++ або Rust, які виконують тривалі обчислення (чисельне моделювання, обробка мультимедіа, операції лінійної алгебри) або блокувальні системні виклики (робота з диском, мережевими сокетами, драйверами обладнання), зобов'язані тимчасово відпускати GIL. Це дозволяє планувальнику інтерпретатора запускати інші потоки Python на час виконання нативного коду.

Усередині CPython кожен системний потік, який виконує код або звертається до об'єктів віртуальної машини, асоціюється зі структурою `PyThreadState`. Ця структура містить локальний стек викликів кадрових об'єктів `PyFrameObject`, інформацію про поточні активні винятки, налаштування профілювання та посилання на батьківську структуру стану інтерпретатора `PyInterpreterState`. 

Покажчик на активний `PyThreadState` поточного потоку зберігається в локальній пам'яті потоку (Thread-Local Storage, TLS) операційної системи. Коли потік захоплює GIL, він записує адресу свого `PyThreadState` у глобальну змінну інтерпретатора `_PyRuntime.ceval.gil.last_holder`. Коли потік відпускає GIL, він обнуляє запис у TLS та сповіщає інші потоки через системну умовну змінну.

### Механіка розгортання базових макросів

Макроси `Py_BEGIN_ALLOW_THREADS` та `Py_END_ALLOW_THREADS` визначені в заголовковому файлі `ceval.h` ядра інтерпретатора. Вони утворюють нерозривну лексичну пару, яка автоматично оголошує локальну змінну-сховище на стеку C:

:::tabs
```c
// ceval.h (внутрішнє визначення макросів у CPython)
#define Py_BEGIN_ALLOW_THREADS { \
            PyThreadState *_save; \
            _save = PyEval_SaveThread();
#define Py_END_ALLOW_THREADS \
            PyEval_RestoreThread(_save); \
        }
```
```cpp
// ceval.hpp (еквівалентний C++ макросний шаблон)
#define PY_SCOPED_BEGIN_ALLOW_THREADS { \
            PyThreadState *_save = PyEval_SaveThread();
#define PY_SCOPED_END_ALLOW_THREADS \
            PyEval_RestoreThread(_save); \
        }
```
:::

Функція `PyEval_SaveThread()` виконує наступні атомарні кроки:
1. Зчитує покажчик на активний `PyThreadState` поточного потоку з пам'яті TLS.
2. Скидає поточний активний стан потоку в інтерпретаторі у значення `NULL`.
3. Звільняє системний м'ютекс `gil_mutex` та надсилає сигнал пробудження іншим сплячим потокам через `PyCOND_SIGNAL`.
4. Повертає збережений покажчик `_save` викликачеві.

Функція `PyEval_RestoreThread(PyThreadState *_save)` виконує зворотну послідовність дій:
1. Звертається до ядра інтерпретатора та ініціює системне захоплення м'ютекса `take_gil(_save)`.
2. Якщо замок зайнятий іншим потоком, поточний потік переходить у стан сну на рівні операційної системи.
3. Після успішного здобуття GIL функція відновлює покажчик `_save` у локальній пам'яті потоку TLS і робить його знову активним для циклу виконання байткоду.

### Специфікація макросів вивільнення та повторного захоплення GIL

| Макрос / Функція | Опис дії | Інваріанти безпеки |
| :--- | :--- | :--- |
| `Py_BEGIN_ALLOW_THREADS` | Відпускає GIL для поточного потоку, зберігає `PyThreadState*` у локальній змінній `_save` та викликає `PyEval_SaveThread()`. | **ЗАБОРОНЕНО** звертатися до будь-яких `PyObject*`, викликати функції C API або макроси `Py_INCREF`/`Py_DECREF`. |
| `Py_END_ALLOW_THREADS` | Відновлює стан потоку з локальної змінної `_save`, блокується до повторного захоплення GIL через `PyEval_RestoreThread()`. | Мусить викликатися в тій самій лексичній області видимості, де було викликано `Py_BEGIN_ALLOW_THREADS`. |
| `Py_BLOCK_THREADS` | Тимчасово захоплює GIL всередині блоку `Py_BEGIN_ALLOW_THREADS` для швидкого доступу до C API. | Потребує обов'язкового парного виклику `Py_UNBLOCK_THREADS` перед виходом з блоку. |
| `Py_UNBLOCK_THREADS` | Знову відпускає GIL, повертаючи потік у стан дозволеного фонового виконання нативного коду. | Працює лише як пара до `Py_BLOCK_THREADS`. |

### Базовий патерн використання в C та ідіоматичний RAII-патерн у C++

При написанні C-розширень найнебезпечнішою помилкою є вихід з функції через оператор `return` або генерацію винятку C++ всередині блоку `Py_BEGIN_ALLOW_THREADS` без виклику `Py_END_ALLOW_THREADS`. Якщо GIL не буде відновлено, стан потоку в TLS залишиться порожнім, і наступний виклик будь-якої функції CPython з цього потоку спричинить негайний збій розіменування нульового покажчика (*Segmentation Fault*).

У мові C++ цю проблему вирішують за допомогою ідіоми RAII (*Resource Acquisition Is Initialization*), інкапсулюючи виклики в деструкторі захисного класу:

:::tabs
```c
// native_worker.c
#include <Python.h>
#include <unistd.h>

PyObject* long_computation_c(PyObject *self, PyObject *args) {
    int duration_sec = 0;
    if (!PyArg_ParseTuple(args, "i", &duration_sec)) {
        return NULL;
    }

    // 1. Відпускаємо GIL перед блокувальною системною операцією
    Py_BEGIN_ALLOW_THREADS

    // Потік виконує чистий C-код. Інтерпретатор Python вільний для інших потоків
    sleep(duration_sec);

    // 2. Обов'язково відновлюємо GIL перед поверненням у Python
    Py_END_ALLOW_THREADS

    Py_RETURN_NONE;
}
```
```cpp
// native_worker.cpp
#include <Python.h>
#include <chrono>
#include <thread>

namespace py_guard {

// RAII обгортка для безпечного керування GIL у стилі сучасного C++
class ScopedAllowThreads {
public:
    ScopedAllowThreads() noexcept : thread_state_(PyEval_SaveThread()) {}
    
    ~ScopedAllowThreads() noexcept {
        if (thread_state_) {
            PyEval_RestoreThread(thread_state_);
        }
    }

    ScopedAllowThreads(const ScopedAllowThreads&) = delete;
    ScopedAllowThreads& operator=(const ScopedAllowThreads&) = delete;
    ScopedAllowThreads(ScopedAllowThreads&& other) noexcept 
        : thread_state_(other.thread_state_) {
        other.thread_state_ = nullptr;
    }
    ScopedAllowThreads& operator=(ScopedAllowThreads&& other) noexcept {
        if (this != &other) {
            if (thread_state_) PyEval_RestoreThread(thread_state_);
            thread_state_ = other.thread_state_;
            other.thread_state_ = nullptr;
        }
        return *this;
    }

private:
    PyThreadState* thread_state_{nullptr};
};

} // namespace py_guard

extern "C" PyObject* long_computation_cpp(PyObject *self, PyObject *args) {
    int duration_sec = 0;
    if (!PyArg_ParseTuple(args, "i", &duration_sec)) {
        return nullptr;
    }

    {
        // Конструктор ScopedAllowThreads відпускає GIL
        py_guard::ScopedAllowThreads allow_threads;

        // C++ код виконується паралельно на рівні ядра ОС
        std::this_thread::sleep_for(std::chrono::seconds(duration_sec));
        
        // Деструктор гарантовано захоплює GIL при виході з блоку або при винятку
    }

    Py_RETURN_NONE;
}
```
:::

## 2. Керування GIL зі сторонніх системних потоків: PyGILState API

Типовий сценарій у вбудованих системах, робототехніці та мережевих драйверах — виникнення апаратного переривання або системного колбека, який виконується в окремому потоці операційної системи, створеному сторонньою бібліотекою (через `pthread_create()`, `CreateThread()` або пул потоків Boost/C++). 

Такий потік від початку не має структури `PyThreadState` у локальній пам'яті TLS. Якщо код у такому системному колбеку спробує безпосередньо викликати функцію `PyObject_CallObject()` або макрос `Py_INCREF()`, інтерпретатор аварійно завершить роботу через звернення до порожнього покажчика стану.

Для реєстрації сторонніх системних потоків у середовищі CPython розроблено `PyGILState API`.

### Протокол роботи PyGILState

Функція `PyGILState_Ensure()` виконує комплексну перевірку:
1. Перевіряє, чи прив'язано до поточного системного потоку валідну структуру `PyThreadState`.
2. Якщо потік новий — автоматично виділяє пам'ять під новий `PyThreadState` в активному інтерпретаторі `PyInterpreterState` та реєструє його в TLS.
3. Блокується до повного захоплення м'ютекса GIL.
4. Повертає стан блокування `PyGILState_STATE` (`PyGILState_LOCKED` або `PyGILState_UNLOCKED`), який є обов'язковим токеном відновлення.

Функція `PyGILState_Release(PyGILState_STATE state)` звільняє GIL. Якщо `PyGILState_Ensure()` створив тимчасову структуру `PyThreadState` виключно на час цього виклику, `PyGILState_Release` автоматично видаляє її з черги інтерпретатора та вивільняє пам'ять, запобігаючи витоку ресурсів.

:::tabs
```c
// callback_handler.c
#include <Python.h>

void on_hardware_interrupt_c(int sensor_id, double value) {
    // Сторонній потік переривання ОС реєструється в CPython
    PyGILState_STATE gstate = PyGILState_Ensure();

    // Тепер безпечно викликати Python C API
    PyObject *module = PyImport_ImportModule("telemetry_service");
    if (module) {
        PyObject *func = PyObject_GetAttrString(module, "on_sensor_event");
        if (func && PyCallable_Check(func)) {
            PyObject *args = Py_BuildValue("(id)", sensor_id, value);
            PyObject *res = PyObject_CallObject(func, args);
            Py_XDECREF(res);
            Py_DECREF(args);
            Py_DECREF(func);
        }
        Py_DECREF(module);
    }

    // Звільняємо GIL і знищуємо прив'язку потоку
    PyGILState_Release(gstate);
}
```
```cpp
// callback_handler.cpp
#include <Python.h>
#include <utility>

namespace py_guard {

class ScopedGILState {
public:
    ScopedGILState() noexcept : state_(PyGILState_Ensure()) {}
    
    ~ScopedGILState() noexcept {
        PyGILState_Release(state_);
    }

    ScopedGILState(const ScopedGILState&) = delete;
    ScopedGILState& operator=(const ScopedGILState&) = delete;
    ScopedGILState(ScopedGILState&&) = delete;
    ScopedGILState& operator=(ScopedGILState&&) = delete;

private:
    PyGILState_STATE state_;
};

} // namespace py_guard

extern "C" void on_hardware_interrupt_cpp(int sensor_id, double value) {
    // Автоматичне захоплення та вивільнення GIL через RAII
    py_guard::ScopedGILState gil_lock;

    PyObject *module = PyImport_ImportModule("telemetry_service");
    if (!module) {
        PyErr_Clear();
        return;
    }

    PyObject *func = PyObject_GetAttrString(module, "on_sensor_event");
    if (func && PyCallable_Check(func)) {
        PyObject *args = Py_BuildValue("(id)", sensor_id, value);
        PyObject *res = PyObject_CallObject(func, args);
        Py_XDECREF(res);
        Py_XDECREF(args);
        Py_DECREF(func);
    }
    Py_DECREF(module);
}
```
:::

## 3. Системний інтерфейс Python: модуль `sys` та параметри середовища

Інтерпретатор надає прикладний інтерфейс у стандартній бібліотеці для діагностики, моніторингу та динамічного регулювання інтервалів перемикання потоків.

### Функції модуля `sys`

| Функція | Сигнатура | Опис та поведінка |
| :--- | :--- | :--- |
| `sys.getswitchinterval()` | `() -> float` | Повертає поточний інтервал перемикання потоків у секундах (за замовчуванням `0.005` с, тобто 5 мілісекунд). |
| `sys.setswitchinterval(interval)` | `(interval: float) -> None` | Встановлює інтервал перемикання потоків. Зменшення інтервалу покращує чутливість UI, але збільшує накладні витрати на перемикання контексту ОС. |
| `sys._is_gil_enabled()` | `() -> bool` | *(Починаючи з Python 3.13)* Повертає `True`, якщо інтерпретатор запущено з активним GIL, або `False` у збірці `python3.13t` без GIL. |

### Змінні оточення та прапорці командного рядка для Python 3.13+

У збірках Python 3.13+ з підтримкою PEP 703 (free-threaded binary `python3.13t`) глобальний замок інтерпретатора можна вимикати або вмикати як під час запуску через аргументи CLI, так і через змінні оточення для дочірніх процесів:

| Прапорець / Змінна | Приклад виклику | Дія на інтерпретатор |
| :--- | :--- | :--- |
| `-X gil=0` | `python3.13t -X gil=0 app.py` | Повністю вимикає GIL під час запуску програми. |
| `-X gil=1` | `python3.13t -X gil=1 app.py` | Примусово активує GIL для зворотної сумісності зі старими C-модулями. |
| `PYTHON_GIL=0` | `export PYTHON_GIL=0` | Вимикає GIL через змінну середовища для всіх дочірніх процесів. |
| `PYTHON_GIL=1` | `export PYTHON_GIL=1` | Примусово активує GIL через змінну середовища. |

### Спеціальний слот модуля Py_mod_gil

Для забезпечення безпеки C-розширень у збірці `python3.13t` впроваджено спеціальний слот ініціалізації модуля `Py_mod_gil`:

:::tabs
```c
// module_definition.c
#include <Python.h>

static PyModuleDef_Slot telemetry_slots[] = {
    {Py_mod_gil, Py_MOD_GIL_NOT_USED}, // Декларуємо сумісність з free-threaded
    {0, NULL}
};

static struct PyModuleDef telemetry_module = {
    PyModuleDef_HEAD_INIT,
    "telemetry_c",
    "Телеметричний модуль без GIL",
    0,
    NULL,
    telemetry_slots,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC PyInit_telemetry_c(void) {
    return PyModuleDef_Init(&telemetry_module);
}
```
```cpp
// module_definition.cpp
#include <Python.h>
#include <array>

namespace {

constexpr std::array<PyModuleDef_Slot, 2> module_slots = {{
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {0, nullptr}
}};

PyModuleDef telemetry_module = {
    PyModuleDef_HEAD_INIT,
    "telemetry_cpp",
    "Телеметричний C++ модуль без GIL",
    0,
    nullptr,
    const_cast<PyModuleDef_Slot*>(module_slots.data()),
    nullptr,
    nullptr,
    nullptr
};

} // namespace

extern "C" PyMODINIT_FUNC PyInit_telemetry_cpp(void) {
    return PyModule_Create(&telemetry_module);
}
```
:::

Якщо імпортоване бінарне розширення не містить слота `Py_MOD_GIL_NOT_USED`, інтерпретатор `python3.13t` видає попередження середовища виконання `RuntimeWarning` і автоматично повторно вмикає GIL для всього процесу, щоб захистити неадаптоване розширення від станів гонитви та пошкодження пам'яті.

## 4. Обробка системних сигналів та перевірка винятків у C API

Коли потік виконує довгий чисельний C/C++ розрахунок із вивільненим GIL, він перестає реагувати на стандартні системні сигнали POSIX, зокрема сигнал переривання користувача `SIGINT` (комбінація клавіш `Ctrl+C`). Системний обробник сигналів операційної системи встановлює внутрішній прапорець у CPython, але сам виняток `KeyboardInterrupt` не може бути згенерований доти, доки потік не захопить GIL і не викличе функцію перевірки сигналів.

Для забезпечення коректного реагування на сигнали тривалі чисельні цикли в нативному коді розбивають на порції (chunks) і періодично викликають функцію `PyErr_CheckSignals()`:

:::tabs
```c
// interruptible_loop.c
#include <Python.h>

int compute_with_signals_c(size_t total_iterations) {
    for (size_t i = 0; i < total_iterations; i += 10000) {
        // Виконуємо порцію чисельних розрахунків без GIL
        Py_BEGIN_ALLOW_THREADS
        // Нативний чисельний розрахунок 10 000 ітерацій
        Py_END_ALLOW_THREADS

        // Перевіряємо, чи надійшов сигнал переривання (SIGINT)
        if (PyErr_CheckSignals() != 0) {
            // Сигнал отримано: виняток уже виставлено в інтерпретаторі
            return -1;
        }
    }
    return 0;
}
```
```cpp
// interruptible_loop.cpp
#include <Python.h>
#include <cstddef>

int compute_with_signals_cpp(std::size_t total_iterations) noexcept {
    for (std::size_t i = 0; i < total_iterations; i += 10000) {
        Py_BEGIN_ALLOW_THREADS
        // Нативний чисельний розрахунок 10 000 ітерацій
        Py_END_ALLOW_THREADS

        if (PyErr_CheckSignals() != 0) {
            return -1;
        }
    }
    return 0;
}
```
:::

## 5. Зведена таблиця інваріантів безпеки пам'яті

Для запобігання пошкодженню адресного простору розробник C-розширень зобов'язаний дотримуватися суворих правил володіння GIL:

| Стан потоку | Дозволені операції | Суворо заборонені дії |
| :--- | :--- | :--- |
| **GIL захоплено (`PyThreadState` активний)** | • Виділення пам'яті під нові об'єкти `PyObject`<br>• Модифікація списків, словників, об'єктів<br>• Виклики `Py_INCREF` / `Py_DECREF`<br>• Виконання байткоду інтерпретатора | • Тривалі блокувальні системні виклики I/O<br>• Довгі важкі чисельні цикли C/C++ без періодичної перевірки системних сигналів |
| **GIL звільнено (після `Py_BEGIN_ALLOW_THREADS`)** | • Чисельні розрахунки у C/C++/Rust<br>• Векторні інструкції SIMD, AVX2, OpenMP<br>• Блокувальні виклики `read()`, `write()`, `select()`<br>• Робота з сирою нативною пам'яттю | • Читання/запис будь-яких полів `PyObject`<br>• Зміна лічильників `ob_refcnt`<br>• Виклики C API без попереднього `PyGILState_Ensure` |
