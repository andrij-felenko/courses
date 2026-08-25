# 📋 Довідник API деманґлінгу: abi::__cxa_demangle та DbgHelp

Програмний деманґлінг — це процес зворотного синтаксичного відновлення людиночитабельного імені C++ зі спотвореного ідентифікатора компонувальника. Ця процедура розгортає закодовані префікси, ієрархії просторів імен, назви класів, параметри шаблонів, конвенції виклику та типи аргументів у вихідну форму вихідного коду мови.

У системній розробці деманґлінг є обов'язковим будівельним блоком для інструментів профілювання (таких як perf, Valgrind, VTune), систем генерації аварійних дампів пам'яті (Crash Dump), діагностичних стек-трейсів та динамічної інтроспекції типів через RTTI (`typeid`).

Цей довідник надає повну технічну специфікацію двох головних стандартів програмного деманґлінгу: відкритого інтерфейсу **Itanium C++ ABI** (застосовується в Linux, macOS, iOS, Android, FreeBSD, QNX компіляторами GCC, Clang, Intel) та інтерфейсу **MSVC ABI** в операційній системі Windows.

---

## 1. Специфікація Itanium C++ ABI: функція abi::__cxa_demangle

У системній архітектурі Itanium C++ ABI процес деманґлінгу стандартизований як частина низькорівневого середовища виконання C++ Runtime (бібліотеки `libsupc++` у компіляторі GCC або `libcxxabi` у проєкті LLVM/Clang). Публічний C-інтерфейс оголошено в заголовку `<cxxabi.h>`.

### 1.1. Оголошення функції та сигнатура

```cpp
#include <cxxabi.h>

namespace abi {
    extern "C" char* __cxa_demangle(
        const char* mangled_name,
        char*       output_buffer,
        size_t*     length,
        int*        status
    );
}
```

Функція експортується з C-сумісним зв'язуванням (`extern "C"`) усередині простору імен `abi` (у деяких реалізаціях синонімічного з `__cxxabiv1`), що уможливлює її прямий виклик як із програм на чистому C, так і з сучасного коду на C++.

:::tabs
```c
#include <cxxabi.h>
#include <stdio.h>
#include <stdlib.h>

void print_symbol_info(const char* mangled) {
    int status = 0;
    char* demangled = abi::__cxa_demangle(mangled, NULL, NULL, &status);
    
    if (status == 0 && demangled != NULL) {
        printf("Оригінальний символ:  %s\n", mangled);
        printf("Декодований вигляд:   %s\n", demangled);
        free(demangled);
    } else {
        printf("Не вдалося декодувати символ %s (код помилки: %d)\n", mangled, status);
    }
}
```
```cpp
#include <cxxabi.h>
#include <iostream>
#include <memory>
#include <string>
#include <string_view>

std::string demangle(std::string_view mangled) {
    if (mangled.empty()) {
        return {};
    }
    
    int status = 0;
    std::unique_ptr<char, void(*)(void*)> buffer{
        abi::__cxa_demangle(mangled.data(), nullptr, nullptr, &status),
        std::free
    };
    
    if (status == 0 && buffer) {
        return std::string(buffer.get());
    }
    return std::string(mangled);
}
```
:::

### 1.2. Детальна специфікація параметрів

Функція приймає чотири параметри, кожен із яких керує розподілом пам'яті або поверненням діагностичної інформації:

1. **`mangled_name` (`const char*`, вхідний):** Вказівник на нуль-термінований рядок ASCII, який містить спотворений символ згідно з формальною граматикою Itanium ABI. Для звичайних функцій та глобальних змінних такий символ починається з префікса `_Z`. Для структур RTTI (типових дескрипторів) символ починається з префікса `_ZTS` або `_ZTI`. Параметр не може бути нульовим (`NULL`): передача нульового вказівника викликає негайне завершення зі статусом помилки аргументів.
2. **`output_buffer` (`char*`, вхідний/вихідний):** Вказівник на буфер у купі, попередньо виділений викликачем через `std::malloc`. Якщо викликач передає `nullptr` (або `NULL`), функція самостійно виділяє новий блок пам'яті через системний `malloc`. Якщо переданий буфер замалий для збереження результуючого декодованого рядка, функція автоматично змінює його розмір через `std::realloc`.
3. **`length` (`size_t*`, вхідний/вихідний):** Вказівник на цілочисельну змінну, яка на момент виклику містить поточний розмір буфера `output_buffer` у байтах. На момент повернення з функції ця змінна перезаписується новим фактичним розміром виділеної пам'яті (включаючи нульовий термінатор `\0`). Якщо `output_buffer == nullptr`, цей параметр може бути переданий як `nullptr`.
4. **`status` (`int*`, вихідний):** Вказівник на цілочисельну змінну для збереження результату виконання. Значення за цим вказівником обов'язково перевіряється викликачем перед розіменуванням поверненого покажчика на рядок.

### 1.3. Коди статусу виконання та діагностика

Змінна `status` після завершення виклику гарантовано отримує одне з чотирьох стандартизованих числових значень:

| Код статусу | Символічний ідентифікатор | Причина виникнення | Дії та рекомендації для коду |
| :--- | :--- | :--- | :--- |
| `0` | `SUCCESS` | Декодування виконано успішно. Повернений покажчик дійсний і містить коректний C-рядок. | Прочитати рядок і обов'язково звільнити виділений блок пам'яті викликом `std::free()`. |
| `-1` | `MEMORY_ALLOC_FAILURE` | Помилка виділення динамічної пам'яті в купі (`malloc` або `realloc` повернув `NULL` через вичерпання адресної пам'яті). | Зафіксувати брак системної пам'яті. Функція повертає `nullptr`. Оригінальний буфер не знищується. |
| `-2` | `INVALID_MANGLED_NAME` | Вхідний рядок не відповідає граматичним правилам Itanium ABI (наприклад, звичайний C-символ без префікса `_Z`, пошкоджений рядок пам'яті або символ від компілятора MSVC). | Вважати вхідне ім'я звичайним текстом і використовувати його без змін. Функція повертає `nullptr`. |
| `-3` | `INVALID_ARGUMENTS` | Передано некоректну комбінацію вхідних параметрів (наприклад, `mangled_name == NULL`). | Виправити логічну помилку в коді виклику. Функція повертає `nullptr`. |

### 1.4. Внутрішній автомат парсера та коефіцієнт розгортання пам'яті

Внутрішній алгоритм деманґлера побудовано на основі рекурсивного спускового парсера, який під час читання токенів будує таблицю підстановок (Substitutions Dictionary). Коли парсер зустрічає токен підстановки `S_`, `S0_`, `S1_` або скорочення `St`, `Ss`, він підставляє раніше розібраний AST-вузол типу чи простору імен.

Через це виникає ефект **вибухового коефіцієнта розгортання пам'яті**: компактний спотворений символ довжиною 60–80 байтів, що містить вкладені шаблони стандартної бібліотеки (наприклад, `std::map<std::string, std::vector<int>>`), під час деманґлінгу розгортається у повний C++ вираз довжиною понад 1000–1500 символів разом з алокаторами та типами за замовчуванням.

З цієї причини початковий розмір буфера при ручному виділенні рекомендується встановлювати не менше 512–1024 байтів.

### 1.5. Правила володіння пам'яттю та оптимізація пакетної обробки

1. **Сувора вимога до звільнення:** Повернений покажчик завжди вказує на блок пам'яті, виділений C-алокатором. Звільняти його дозволено **виключно через `std::free()`**. Використання C++ оператора `delete` або `delete[]` є грубою помилкою, оскільки перемішування C++ оператора видалення з низькорівневим C-алокатором на багатьох платформах руйнує заголовки арени пам'яті.
2. **Багаторазове використання буфера (Buffer Reuse):** При профілюванні тисяч адрес викликів постійні алокації та звільнення пам'яті створюють значне навантаження на купу. Передача одного й того самого буфера між викликами дозволяє алокатору одноразово розширити його до максимального розміру й повторно використовувати для всіх наступних символів:

:::tabs
```c
#include <cxxabi.h>
#include <stdio.h>
#include <stdlib.h>

void process_symbol_batch(const char** list, size_t count) {
    size_t capacity = 512;
    char* buffer = (char*)malloc(capacity);
    int status = 0;

    for (size_t i = 0; i < count; ++i) {
        char* result = abi::__cxa_demangle(list[i], buffer, &capacity, &status);
        if (status == 0 && result != NULL) {
            buffer = result; // Покажчик міг змінитися після виклику realloc
            printf("[%zu] %s\n", i, buffer);
        } else {
            printf("[%zu] %s (без змін)\n", i, list[i]);
        }
    }
    free(buffer);
}
```
```cpp
#include <cxxabi.h>
#include <iostream>
#include <memory>
#include <span>
#include <string_view>
#include <vector>

void process_symbol_batch_cpp(std::span<const char* const> symbols) {
    size_t capacity = 512;
    std::unique_ptr<char, void(*)(void*)> buffer{
        static_cast<char*>(std::malloc(capacity)),
        std::free
    };
    int status = 0;

    for (size_t i = 0; i < symbols.size(); ++i) {
        char* raw_ptr = buffer.release();
        char* result = abi::__cxa_demangle(symbols[i], raw_ptr, &capacity, &status);
        buffer.reset(result ? result : raw_ptr);

        if (status == 0 && buffer) {
            std::cout << "[" << i << "] " << buffer.get() << '\n';
        } else {
            std::cout << "[" << i << "] " << symbols[i] << " (без змін)\n";
        }
    }
}
```
:::

### 1.6. Потокобезпека та заборона виклику в обробниках сигналів

- **Багатопотокова реентрабельність (Thread Safety):** Функція `abi::__cxa_demangle` є цілком безпечною для одночасного виклику з різних паралельних потоків, якщо кожен потік використовує власний буфер `output_buffer`. Внутрішній стан парсера є повністю локальним.
- **Асинхронна безпека до сигналів (Async-Signal Safety):** Функція **категорично не є безпечною для виклику в обробниках асинхронних сигналів POSIX** (`SIGSEGV`, `SIGABRT`, `SIGBUS`, `SIGFPE`). Оскільки всередині виконуються виклики `malloc` та `realloc`, а системні алокатори glibc/musl блокують внутрішні м'ютекси купи, виклик деманґлера під час переривання потоку сигналом призводить до **миттєвого вічного дедлоку (Deadlock)** усього процесу.

---

## 2. Специфікація MSVC ABI: функція UnDecorateSymbolName

В операційній системі Windows функціонал деманґлінгу імен стандарту MSVC ABI надається системною бібліотекою `DbgHelp.dll`. Оголошення інтерфейсу знаходиться в заголовковому файлі `<dbghelp.h>`.

### 2.1. Оголошення та підключення

```cpp
#include <windows.h>
#include <dbghelp.h>

#pragma comment(lib, "dbghelp.lib")

DWORD WINAPI UnDecorateSymbolName(
    PCSTR DecoratedName,
    PSTR  UnDecoratedName,
    DWORD UndecoratedLength,
    DWORD Flags
);
```

:::tabs
```c
#include <windows.h>
#include <dbghelp.h>
#include <stdio.h>

void win32_print_symbol(const char* decorated) {
    char buffer[1024];
    DWORD len = UnDecorateSymbolName(
        decorated,
        buffer,
        sizeof(buffer),
        UNDNAME_COMPLETE
    );
    
    if (len > 0) {
        printf("Windows декодовано: %s\n", buffer);
    } else {
        printf("Помилка декодування, код: %lu\n", GetLastError());
    }
}
```
```cpp
#include <windows.h>
#include <dbghelp.h>
#include <iostream>
#include <string>
#include <string_view>

std::string win32_undecorate(std::string_view decorated, DWORD flags = UNDNAME_COMPLETE) {
    if (decorated.empty()) {
        return {};
    }
    
    std::string result(1024, '\0');
    DWORD len = UnDecorateSymbolName(
        decorated.data(),
        result.data(),
        static_cast<DWORD>(result.size()),
        flags
    );
    
    if (len == 0 && GetLastError() == ERROR_INSUFFICIENT_BUFFER) {
        result.resize(4096);
        len = UnDecorateSymbolName(
            decorated.data(),
            result.data(),
            static_cast<DWORD>(result.size()),
            flags
        );
    }
    
    if (len > 0) {
        result.resize(len);
        return result;
    }
    return std::string(decorated);
}
```
:::

### 2.2. Повна матриця прапорців декодування (Flags)

На відміну від `__cxa_demangle`, функція `UnDecorateSymbolName` приймає 32-бітну бітову маску прапорців, яка дозволяє вибірково приховувати або показувати окремі компоненти сигнатури:

| Прапорець | Шістнадцяткове значення | Повна дія прапорця на вихідний рядок |
| :--- | :--- | :--- |
| `UNDNAME_COMPLETE` | `0x0000` | Повне декодування: повертає всі елементи, включаючи тип повернення, модифікатори доступу (`public:`, `private:`), конвенцію виклику (`__cdecl`), параметри та `this`-кваліфікатори. |
| `UNDNAME_NO_MS_KEYWORDS` | `0x0002` | Пригнічує специфічні ключові слова компілятора Microsoft (`__cdecl`, `__stdcall`, `__thiscall`, `__fastcall`, `__ptr64`). |
| `UNDNAME_NO_ACCESS_SPECIFIERS` | `0x0080` | Приховує модифікатори доступу членів класу (`public:`, `protected:`, `private:`). |
| `UNDNAME_NO_MEMBER_TYPE` | `0x0200` | Приховує службові модифікатори статичних та віртуальних функцій-членів (`static`, `virtual`). |
| `UNDNAME_NAME_ONLY` | `0x1000` | Повертає виключно кваліфіковану назву функції чи методу (`Namespace::Class::Method`) без аргументів, типу повернення та модифікаторів. |
| `UNDNAME_NO_ARGUMENTS` | `0x2000` | Приховує список типів параметрів у круглих дужках, залишаючи ім'я та тип повернення. |
| `UNDNAME_NO_SPECIAL_SYMS` | `0x4000` | Забороняє декодування внутрішніх службових символів компілятора (таблиць віртуальних методів `vftable` чи RTTI-дескрипторів). |
| `UNDNAME_NO_ALLOCATION_MODEL` | `0x0008` | Приховує модель розподілу пам'яті (ключові слова `__near`, `__far`). |
| `UNDNAME_NO_ALLOCATION_LANGUAGE` | `0x0010` | Приховує мовну модель виклику (`__pascal`, `__fortran`). |
| `UNDNAME_NO_THISTYPE` | `0x0060` | Пригнічує відображення константності покажчика `this` (`const` або `volatile` методи). |
| `UNDNAME_NO_RETURN_UDT_MODEL` | `0x0400` | Приховує специфікатори моделі повернення користувацьких типів даних (UDT). |
| `UNDNAME_32_BIT_DECODE` | `0x0800` | Примусово декодує 32-бітний контекст символу. |

### 2.3. Спеціальні символи компілятора Microsoft

MSVC ABI кодує не лише функції, а й службові конструкції мови. Символи, що починаються з подвійного знака питання `??`, мають спеціальне значення:
- `??_7...@@6B@`: Таблиця віртуальних функцій (`const Class::`vftable`'`).
- `??_G...@@QAEPAXI@Z`: Скалярний деструктор з видаленням (`Class::`scalar deleting destructor'`).
- `??_E...@@QAEPAXI@Z`: Векторний деструктор для масивів (`Class::`vector deleting destructor'`).
- `??_R0...`: Повний дескриптор типу RTTI (`Type `RTTI Type Descriptor'`).

### 2.4. Потокобезпека та ініціалізація контексту DbgHelp

Сама функція `UnDecorateSymbolName` є простою рядковою утилітою і не звертається до диска. Проте глобальний контекст налагодження Windows (функції `SymInitialize()`, `SymFromAddr()`, `SymCleanup()`) є **суворо однопотоковим**. Виклик `SymInitialize()` прив'язується до `HANDLE` процесу, і конкурентні виклики з різних потоків без використання зовнішнього `std::mutex` викликають пошкодження пам'яті та аварійне завершення `STATUS_ACCESS_VIOLATION`.

---

## 3. Системні консольні інструменти та автоматизація в конвеєрах

Під час збирання проєктів, налагодження бінарних релізів та аналізу дампів у CI/CD використовуються стандартні консольні утиліти.

### 3.1. Утиліти GNU Binutils c++filt та LLVM llvm-cxxfilt

Утиліта `c++filt` (входить до GNU Binutils) та `llvm-cxxfilt` (частина LLVM) здатні декодувати окремі аргументи або працювати як потоковий фільтр:

```bash
# Розшифрування окремого символу:
c++filt _ZN4math6Vector3addERKS0_

# Фільтрація експортованих символів динамічної бібліотеки ELF:
nm -D --defined-only libengine.so | c++filt

# Декодування списку символів із журналу падіння:
cat crash.log | c++filt > readable_crash.log

# Примусове декодування Windows-символів утилітою llvm-cxxfilt:
llvm-cxxfilt --format=msvc "?calculate@MathHelper@@QEAAHHN@Z"
```

Ключові прапорці запуску `c++filt`:
- `-_`, `--strip-underscore`: Ігнорувати початковий символ підкреслення (обов'язковий прапорець для об'єктних файлів Mach-O на macOS).
- `-p`, `--no-params`: Не друкувати типи параметрів функцій (лише назви просторів імен, класів та методів).
- `-t`, `--types`: Декодувати вхідний рядок як тип даних, а не як назву функції (необхідно для розбору RTTI).
- `-s FORMAT`, `--format=FORMAT`: Примусово вибрати схему манглінгу (`gnu-v3`, `msvc`, `arm`).

### 3.2. Утиліта Microsoft undname.exe

Постачається у складі Microsoft Visual Studio (доступна у командному рядку розробника Developer Command Prompt):

```cmd
undname ?calculate@MathHelper@@QEAAHHN@Z
```

Вивід містить детальну інформацію про конвенцію виклику, права доступу та типи:
```text
Undecoration of :- "?calculate@MathHelper@@QEAAHHN@Z"
is :- "public: int __cdecl MathHelper::calculate(int,double)"
```

---

## 4. Динамічна інтроспекція: RTTI та typeid(T).name()

Оператор мови C++ `typeid(T).name()` повертає внутрішній рядок назви типу. Проте стандарт ISO C++ свідомо не стандартизує формат цього рядка, залишаючи його на розсуд розробників компілятора.

:::tabs
```cpp
#include <iostream>
#include <typeinfo>
#include <vector>
#include <string>

#if defined(__GNUC__) || defined(__clang__)
#include <cxxabi.h>
#include <memory>

std::string demangled_typename(const std::type_info& ti) {
    int status = 0;
    std::unique_ptr<char, void(*)(void*)> res{
        abi::__cxa_demangle(ti.name(), nullptr, nullptr, &status),
        std::free
    };
    return (status == 0 && res) ? std::string(res.get()) : ti.name();
}
#else
std::string demangled_typename(const std::type_info& ti) {
    // На MSVC typeid().name() вже містить декодований людиночитабельний рядок
    return ti.name();
}
#endif

int main() {
    std::vector<int> numbers;
    std::cout << "Сире ім'я typeid:   " << typeid(numbers).name() << '\n';
    std::cout << "Людиночитабельне:  " << demangled_typename(typeid(numbers)) << '\n';
}
```
:::

### Відмінності поведінки RTTI між компіляторами

1. **GCC та Clang (Itanium ABI):** Метод `typeid(T).name()` повертає сирий спотворений тип (наприклад, `i` для `int`, `PKc` для `const char*`, `St6vectorIiSaIiEE` для `std::vector<int>`). Виклик `abi::__cxa_demangle` є обов'язковим для показу зрозумілого тексту користувачеві.
2. **MSVC (Windows):** Метод `typeid(T).name()` автоматично викликає внутрішній деманґлер середовища виконання під час звернення і повертає **вже декодований рядок** (наприклад, `class std::vector<int,class std::allocator<int> >`).

У сучасному стандарті C++23 стандартна бібліотека ввела компонент `std::stacktrace` у заголовку `<stacktrace>`. Метод `std::stacktrace_entry::description()` самостійно звертається до системних деманґлерів цільової операційної системи, надаючи розробнику готовий людиночитабельний опис кадру без необхідності ручного написання платформних обгорток.

### 4.1. Специфікація std::stacktrace у C++23

Тип `std::stacktrace` є стандартним контейнером елементів `std::stacktrace_entry`. Кожен запис інкапсулює інформацію про один стек-фрейм:

| Метод `std::stacktrace_entry` | Повертане значення | Опис поведінки |
| :--- | :--- | :--- |
| `description()` | `std::string` | Повертає деманґлене людиночитабельне ім'я функції або порожній рядок, якщо налагоджувальні символи недоступні. |
| `source_file()` | `std::string` | Повертає шлях до вихідного `.cpp` файлу (якщо скомпільовано з DWARF/PDB метаданими). |
| `source_line()` | `uint_least32_t` | Номер рядка вихідного файлу (1-індексований) або 0 у разі відсутності налагоджувальної інформації. |
| `native_handle()` | `native_handle_type` | Низькорівнева адреса інструкції процесора (`uintptr_t` або покажчик на машинний код). |

Використання C++23 `std::stacktrace` усуває необхідність прямої підтримки системних заголовків `<cxxabi.h>` та `<dbghelp.h>` у прикладному коді:

:::tabs
```cpp
#include <iostream>
#include <stacktrace>

void trigger_diagnostic() {
    auto trace = std::stacktrace::current();
    std::cout << "--- Діагностичний звіт C++23 ---\n";
    for (const auto& entry : trace) {
        std::cout << entry.description() << " ("
                  << entry.source_file() << ":" << entry.source_line() << ")\n";
    }
}

int main() {
    trigger_diagnostic();
    return 0;
}
```
:::
