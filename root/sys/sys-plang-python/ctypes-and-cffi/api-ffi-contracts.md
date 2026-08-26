# 📋 Зіставлення типів і сигнатур: контракт ctypes та cffi

Будь-яка взаємодія високорівневого коду Python із нативними бібліотеками C та C++ спирається на двійковий контракт: точну відповідність розмірів базових типів, правил вирівнювання полів у структурах, порядку передачі аргументів через регістри або стек, обробки системних помилок та угод звільнення пам'яті. У CPython модулі `ctypes` та `cffi` надають два принципово різні підходи до опису цього контракту: динамічні Python-класи над типами `libffi` у `ctypes` та пряму мову C-декларацій у `cffi`.

Нижче наведено детальні таблиці та пояснення механік відповідності типів, структур, вказівників, керування пам'яттю, обробки системних помилок і зворотних викликів.

---

## 1. Таблиця відповідності базових скалярних типів

Розміри типів у мові C не є універсальними і жорстко прив'язані до двійкової моделі цільової операційної системи та архітектури процесора. На 64-бітних системах UNIX (Linux, macOS, FreeBSD) діє модель даних LP64, у якій типи `long`, `size_t` та вказівники займають 64 біти (8 байтів), а тип `int` — 32 біти (4 байти). На відміну від них, 64-бітні операційні системи Windows використовують модель LLP64, у якій тип `long` залишається 32-бітним (4 байти), а 64-бітним цілим є виключно `long long` (`int64_t`).

Модуль `ctypes` зіставляє типи за допомогою спеціалізованих Python-типів, визначених у просторі імен `ctypes`, тоді як `cffi` підтримує стандартний синтаксис декларацій C99/C11 та системні типи з `<stdint.h>`.

| Тип мови C / C++ | Тип у `ctypes` | Оголошення в `cffi` | Еквівалентний тип Python | Розмір на x86-64 |
| :--- | :--- | :--- | :--- | :--- |
| `bool` / `_Bool` | `ctypes.c_bool` | `bool` або `_Bool` | `bool` | 1 байт |
| `char` / `signed char` | `ctypes.c_char` / `c_byte` | `char` / `signed char` | `bytes` (довжини 1) / `int` | 1 байт |
| `unsigned char` / `uint8_t` | `ctypes.c_ubyte` / `c_uint8` | `unsigned char` / `uint8_t` | `int` (0..255) | 1 байт |
| `short` / `int16_t` | `ctypes.c_short` / `c_int16` | `short` / `int16_t` | `int` | 2 байти |
| `unsigned short` / `uint16_t` | `ctypes.c_ushort` / `c_uint16` | `unsigned short` / `uint16_t`| `int` | 2 байти |
| `int` / `int32_t` | `ctypes.c_int` / `c_int32` | `int` / `int32_t` | `int` | 4 байти |
| `unsigned int` / `uint32_t` | `ctypes.c_uint` / `c_uint32` | `unsigned int` / `uint32_t` | `int` | 4 байти |
| `long` (Linux: 64 біти, Win: 32) | `ctypes.c_long` | `long` | `int` | 4 або 8 байтів |
| `unsigned long` | `ctypes.c_ulong` | `unsigned long` | `int` | 4 або 8 байтів |
| `long long` / `int64_t` | `ctypes.c_longlong` / `c_int64`| `long long` / `int64_t` | `int` | 8 байтів |
| `unsigned long long` / `uint64_t`| `ctypes.c_ulonglong` | `unsigned long long` | `int` | 8 байтів |
| `size_t` | `ctypes.c_size_t` | `size_t` | `int` | 8 байтів (на 64-біт) |
| `ssize_t` | `ctypes.c_ssize_t` | `ssize_t` | `int` | 8 байтів (на 64-біт) |
| `float` (IEEE 754) | `ctypes.c_float` | `float` | `float` | 4 байти |
| `double` (IEEE 754) | `ctypes.c_double` | `double` | `float` | 8 байтів |
| `char*` (рядок з нуль-термінатором)| `ctypes.c_char_p` | `char *` | `bytes` | 8 байтів (вказівник) |
| `wchar_t*` (Unicode рядок) | `ctypes.c_wchar_p` | `wchar_t *` | `str` | 8 байтів (вказівник) |
| `void*` (сирий вказівник) | `ctypes.c_void_p` | `void *` | `int` / адреса пам'яті | 8 байтів (вказівник) |

При роботі зі скалярними типами у `ctypes` слід пам'ятати про автоматичне перетворення: під час передачі числа `42` у функцію з типом аргументу `ctypes.c_int` інтерпретатор автоматично створює тимчасовий C-об'єкт. Якщо тип повернення нативної функції задано як `c_int`, результат автоматично розпаковується у звичайне ціле число Python `int`. Якщо ж результат задано як покажчик `c_void_p`, `ctypes` повертає ціле число, що містить шістнадцяткову адресу комірки пам'яті.

---

## 2. Оголошення структур, об'єднань та вирівнювання пам'яті

Розташування полів структури в оперативній пам'яті визначається апаратними правилами вирівнювання процесора. На процесорах x86-64 змінні розміром `N` байтів повинні починатися з адреси, кратної `N` (наприклад, 8-байтний `double` повинен мати зміщення, кратне 8). Якщо попереднє поле має менший розмір, компілятор автоматично вставляє між полями невикористані байти заповнення — паддінг (*padding*).

### Структура мовою C / C++

:::tabs
```c
// point_struct.h
#include <stdint.h>

typedef struct {
    int32_t x;
    int32_t y;
    double  weight;
    uint8_t flags;
    // Компілятор додає 7 байтів padding у кінці, щоб загальний розмір структури
    // був кратний максимальному вирівнюванню поля double (8 байтів).
} PointRecord;

typedef union {
    uint32_t as_uint;
    float    as_float;
    uint8_t  as_bytes[4];
} FloatIntUnion;
```
```cpp
// point_struct.hpp
#pragma once
#include <cstdint>
#include <array>

struct PointRecord {
    std::int32_t x;
    std::int32_t y;
    double       weight;
    std::uint8_t flags;
};

union FloatIntUnion {
    std::uint32_t           as_uint;
    float                   as_float;
    std::array<std::uint8_t, 4> as_bytes;
};
```
:::

### Оголошення в ctypes

У `ctypes` структура створюється як спадкоємець базового класу `ctypes.Structure`, а опис полів задається через спеціальний класовий атрибут `_fields_`, який містить список кортежів `("назва_поля", ctypes_тип)`:

```python
import ctypes

class PointRecord(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_int32),
        ("y", ctypes.c_int32),
        ("weight", ctypes.c_double),
        ("flags", ctypes.c_uint8),
    ]

class FloatIntUnion(ctypes.Union):
    _fields_ = [
        ("as_uint", ctypes.c_uint32),
        ("as_float", ctypes.c_float),
        ("as_bytes", ctypes.c_uint8 * 4),
    ]

# Перевірка розміру пам'яті
p = PointRecord(x=10, y=20, weight=3.14, flags=1)
print(f"Розмір структури: {ctypes.sizeof(p)} байтів")  # Рівно 24 байти
```

### Керування порядком байтів і упаковані структури

Якщо структури передаються через мережу або зчитуються з бінарних форматів файлів, часто виникає потреба у щільному пакуванні полів без паддінгу або у фіксації порядку байтів (*Endianness*):

- **Упаковані структури (`_pack_`):** Встановлення `_pack_ = 1` скасовує апаратне вирівнювання полів, змушуючи `ctypes` розміщувати поля впритул одне до одного. Розмір структури `PointRecord` у такому разі становить рівно `4 + 4 + 8 + 1 = 17` байтів.
- **Порядок байтів:** Для роботи з даними у форматі Big-Endian використовується базовий клас `ctypes.BigEndianStructure`, а для Little-Endian — `ctypes.LittleEndianStructure`.

### Оголошення в cffi (API Mode)

У бібліотеці `cffi` опис структур повністю повторює стандартну мову C:

```python
from cffi import FFI

ffibuilder = FFI()
ffibuilder.cdef("""
    typedef struct {
        int32_t x;
        int32_t y;
        double  weight;
        uint8_t flags;
        ...; /* cffi самостійно розрахує вирівнювання через C-компілятор */
    } PointRecord;

    typedef union {
        uint32_t as_uint;
        float    as_float;
        uint8_t  as_bytes[4];
    } FloatIntUnion;
""")
```

Символ `...;` у вихідному описі `cffi` наказує генератору модуля не вгадувати зсуви самостійно, а звернутися до компілятора мови C під час збірки для підстановки реальних розмірів і вирівнювання безпосередньо з системних заголовків.

---

## 3. Бітові поля (Bitfields)

Бітові поля дозволяють щільно пакувати булеві прапорці та дрібні числові діапазони у суцільні бітові комірки слів процесора.

### Бітові поля у ctypes

У `ctypes` для оголошення бітового поля третім елементом кортежу у списку `_fields_` передається кількість бітів:

```python
class DeviceControlRegister(ctypes.Structure):
    _fields_ = [
        ("enable",      ctypes.c_uint8, 1), # 1 біт (0 або 1)
        ("interrupt",   ctypes.c_uint8, 1), # 1 біт
        ("speed_mode",  ctypes.c_uint8, 2), # 2 біти (значення 0..3)
        ("reserved",    ctypes.c_uint8, 4), # 4 біти
    ]
```

### Бітові поля у cffi

У `cffi` використовується прямий синтаксис мови C:

```python
ffibuilder.cdef("""
    typedef struct {
        uint8_t enable:1;
        uint8_t interrupt:1;
        uint8_t speed_mode:2;
        uint8_t reserved:4;
    } DeviceControlRegister;
""")
```

---

## 4. Масиви, покажчики та робота з буферами пам'яті

Робота з покажчиками та масивами пам'яті становить основу системного програмування.

| Операція | Синтаксис `ctypes` | Синтаксис `cffi` | Механіка виконання |
| :--- | :--- | :--- | :--- |
| **Виділення масиву з N елементів** | `(ctypes.c_int * N)()` | `ffi.new("int[]", N)` | Пам'ять виділяється у купі, занулюється |
| **Отримання покажчика на змінну** | `ctypes.byref(val)` | `ffi.new("int *", val)` | `byref` створює швидкий CArgObject без обгортки |
| **Створення повного типу-покажчика** | `ctypes.pointer(val)` | `ffi.new("int *", val)` | `pointer` створює повноцінний Python-об'єкт покажчика |
| **Розіменування покажчика** | `ptr.contents` | `ptr[0]` | Доступ до базового значення в пам'яті |
| **Каст (приведення типів)** | `ctypes.cast(ptr, new_type)` | `ffi.cast("char *", ptr)` | Зміна типу покажчика без зміни адреси |
| **Створення сирого байтового буфера**| `ctypes.create_string_buffer(N)`| `ffi.new("char[]", N)` | Виділення мутабельного неперервного блоку байтів |
| **Zero-Copy буфер (Buffer Protocol)** | `ctypes.c_char.from_buffer(obj)` | `ffi.from_buffer("char[]", obj)` | Отримання прямого покажчика без копіювання |
| **Зчитування байтів у Python `bytes`**| `bytes(ctypes_buffer)` | `ffi.buffer(c_ptr, N)[:]` | Копіювання нативних байтів у новий Python bytes |

### Відмінність між ctypes.byref() та ctypes.pointer()

У `ctypes` існують два способи передачі аргументу за покажчиком:
1. `ctypes.byref(obj)` — створює надлегкий проміжний об'єкт `PyCArgObject`, який містить лише фізичну адресу переданого значення. Цей об'єкт оптимізований для безпосередньої передачі у виклик `ffi_call` і не підтримує розіменування в коді Python.
2. `ctypes.pointer(obj)` — створює повноцінний екземпляр класу `POINTER(type(obj))`, який має власні методи, атрибут `.contents` і може зберігатися у структурах або передаватися між функціями. Через накладні витрати на виділення повноцінного об'єкта `pointer()` працює значно повільніше за `byref()`.

---

## 5. Керування пам'яттю та фіналізатори (ffi.gc)

Коли пам'ять або системні дескриптори виділяються за допомогою функцій нативної бібліотеки (наприклад, `malloc()`, `fopen()` або `socket()`), віртуальна машина Python нічого не знає про виділені ресурси і не може автоматично вивільнити їх після завершення роботи з об'єктом.

Бібліотека `cffi` пропонує детермінований механізм автоматичного звільнення нативних ресурсів через прив'язку деструктора за допомогою `ffi.gc()`:

```python
# Нативна функція повертає сирий покажчик, виділений через C malloc()
raw_ptr = lib.allocate_custom_buffer(1024)

# Створюємо керований об'єкт, прив'язуючи C-функцію free_custom_buffer
safe_ptr = ffi.gc(raw_ptr, lib.free_custom_buffer)

# safe_ptr можна вільно передавати між функціями Python;
# коли лічильник посилань на safe_ptr досягає нуля, CPython автоматично
# викликає зареєстровану функцію lib.free_custom_buffer(raw_ptr).
```

Якщо C-функція деструктора потребує додаткових параметрів або очищення списку пов'язаних ресурсів, у `ffi.gc` можна передати кастомну лямбда-функцію:

```python
safe_device = ffi.gc(
    raw_device_ptr,
    lambda ptr: lib.device_close_with_flags(ptr, 0x01)
)
```

В еквівалентному коді на `ctypes` такий захист вимагає створення власного класу-обгортки з ручним перевизначенням методу `__del__`, що створює помітні накладні витрати на рівні інтерпретатора.

---

## 6. Сигнатури функцій і конвенції викликів

### Завантаження бібліотеки

:::tabs
```python
# ctypes
import ctypes

# Завантаження зі стандартною конвенцією cdecl (POSIX / Windows cdecl)
lib_cdecl = ctypes.CDLL("./libmath.so")

# Завантаження зі специфічною конвенцією stdcall (Windows 32-bit Win32 API)
# lib_stdcall = ctypes.WinDLL("kernel32.dll")
```
```python
# cffi (ABI Mode)
from cffi import FFI
ffi = FFI()
lib = ffi.dlopen("./libmath.so")
```
:::

### Оголошення прототипу функції

```python
# ctypes: явне налаштування argtypes та restype
lib_cdecl.calculate_matrix.argtypes = [
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_size_t,
    ctypes.c_size_t,
    ctypes.c_double
]
lib_cdecl.calculate_matrix.restype = ctypes.c_int32

# cffi: прямий C-заголовок
ffi.cdef("""
    int calculate_matrix(double *data, size_t rows, size_t cols, double factor);
""")
```

---

## 7. Робота з системними помилками (errno та GetLastError)

При виклику C-функцій операційної системи коди помилок часто повертаються через глобальну змінну `errno` (у POSIX) або через системну функцію `GetLastError()` (у Windows).

Оскільки під час роботи багатопотокового інтерпретатора інші потоки Python можуть виконувати системні виклики та перезаписувати глобальний `errno`, як `ctypes`, так і `cffi` зберігають копію `errno` локально для потоку відразу після повернення з FFI-виклику.

### Обробка errno у ctypes

```python
import ctypes

# Для автоматичного захоплення errno використовується use_errno=True
libc = ctypes.CDLL(None, use_errno=True)

res = libc.close(-1)  # Завідомо некоректний файловий дескриптор
if res == -1:
    err = ctypes.get_errno()
    print(f"Помилка закриття дескриптора, errno = {err}")  # EBADF (9)
```

### Обробка errno у cffi

```python
res = lib.close(-1)
if res == -1:
    err = ffi.errno
    print(f"cffi зафіксував errno = {err}")
```

---

## 8. Зворотні виклики (C-to-Python Callbacks)

Якщо бібліотека C потребує передачі вказівника на функцію-компаратор чи обробник подій:

### Оголошення зворотного виклику в ctypes

```python
# Оголошення типу вказівника на функцію: (restype, *argtypes)
CALLBACK_TYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int)

@CALLBACK_TYPE
def py_comparator(a, b):
    return (a > b) - (a < b)

# Передача у функцію C
lib.register_callback(py_comparator)
# УВАГА: py_comparator повинен утримуватися в пам'яті Python,
# інакше GC збере його і виклик із C призведе до Segmentation Fault.
```

### Оголошення зворотного виклику в cffi (API Mode)

```python
ffibuilder.cdef("""
    typedef int (*comparator_t)(int, int);
    void register_callback(comparator_t cb);
    extern "Python" int py_comparator(int a, int b);
""")

# У модулі реалізації:
@ffi.def_extern()
def py_comparator(a, b):
    return (a > b) - (a < b)

lib.register_callback(lib.py_comparator)
```

Механізм `@ffi.def_extern()` у `cffi` генерує C-трамплін під час компіляції модуля. Цей трамплін автоматично викликає `PyGILState_Ensure()`, захищаючи інтерпретатор від збоїв при виклику з довільного фонового потоку операційної системи.
