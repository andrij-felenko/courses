# ⚙️ Практичний проєкт: Кросплатформний деманґлер та стек-трейсер

У системному програмуванні на C++ виникнення критичних помилок (збоїв сегментації пам'яті, необроблених винятків або порушень інваріантів) вимагає негайного формування діагностичного звіту. Операційна система в момент переривання потоку надає лише масив числових адрес інструкцій процесора (`RIP`/`EIP`).

Щоб перетворити ці адреси на інформативний стек-трейс, необхідно виконати складний трирівневий конвеєр: розкрутити стек викликів (Stack Unwinding), знайти за адресою інструкції назву двійкового модуля та спотворене ім'я функції в таблицях динамічного компонувальника, а потім виконати деманґлінг імені відповідно до ABI цільової платформи.

Цей практичний проєкт демонструє проектування та реалізацію надійної кросплатформної підсистеми інтроспекції на C++20, яка уніфікує деманґлінг для систем Unix (Itanium ABI) та Windows (MSVC ABI), забезпечує високу швидкодію завдяки повторному використанню буферів пам'яті та захищає процес від дедлоків під час обробки асинхронних сигналів.

---

## 1. Постановка інженерної задачі

Розробити модульну бібліотеку зняття стек-трейсів та деманґлінгу символів, яка задовольняє таким вимогам:

1. **Єдиний кросплатформний інтерфейс:** Надати високорівневий клас `SymbolDemangler` із методом `std::string demangle(std::string_view)`, який автоматично адаптується до середовища компіляції (`<cxxabi.h>` у POSIX та `DbgHelp.dll` у Windows).
2. **Швидкий шлях без алокацій (Zero-Allocation Fast Path):** Якщо вхідний ідентифікатор є звичайним неспотвореним символом мови C (наприклад, `main` або системний виклик `read`), деманґлер не повинен виконувати жодних звернень до купи, миттєво повертаючи вихідний рядок.
3. **Пакетне перевикористання пам'яті:** Під час обробки глибоких стеків викликів (30–60 кадрів) алокатор не повинен виділяти окремий блок пам'яті під кожен кадр. Буфер має розширюватися одноразово й повторно використовуватися для всієї пачки символів.
4. **Повна інформація про кадр стеку:** Захоплювати не лише ім'я функції, а й числову адресу інструкції, назву скомпільованого двійкового файлу (`.so`, `.dylib`, `.dll`, `.exe`) та зміщення від початку функції в байтах.
5. **Архітектурний захист від дедлоків:** Розділити збір аварійної діагностики на асинхронно-безпечну фазу (усередині обробника `SIGSEGV`) та фазу повного деманґлінгу.

---

## 2. Архітектура та механіка розкручування стеку

Розкручування стеку (Stack Unwinding) залежить від архітектури процесора та моделі компіляції:

- **Кадрове розкручування (Frame Pointer Unwinding):** Історичний підхід, де регістр `RBP`/`EBP` вказує на початок кадру поточної функції. Кожен кадр зберігає вказівник на попередній кадр та адресу повернення. За увімкненої оптимізації `-fomit-frame-pointer` цей ланцюжок відсутній.
- **Табличне розкручування (Table-driven Unwinding):** Сучасний підхід, де компілятор генерує метадані розгортання стеку: секцію `.eh_frame` (формат DWARF) у Linux/macOS або секції `.pdata`/`.xdata` (Structured Exception Handling, SEH) у 64-бітній системі Windows. Системні функції `backtrace()` та `RtlCaptureStackBackTrace()` читають ці таблиці, дозволяючи точно відновити стек викликів навіть для повністю оптимізованого коду.

Отримані адреси інструкцій передаються системному розпізнавачу символів:
- У POSIX функція `dladdr()` переглядає заголовки ELF/Mach-O завантажених у пам'ять динамічних бібліотек і повертає ім'я найближчого експортованого символу з таблиці `.dynsym`.
- У Windows функція `SymFromAddr()` звертається до модуля `DbgHelp.dll`, який зчитує відлагоджувальну інформацію з файлів символів PDB.

---

## 3. Реалізація ядра деманґлера

Нижче наведено код базового модуля деманґлінгу. Для розуміння системних відмінностей реалізацію наведено мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#include <windows.h>
#include <dbghelp.h>
#pragma comment(lib, "dbghelp.lib")
#else
#include <cxxabi.h>
#endif

// C-версія: ручне керування покажчиком на буфер та його ємністю
char* demangle_symbol_c(const char* mangled, char* buffer, size_t* capacity) {
    if (!mangled || mangled[0] == '\0') {
        return NULL;
    }

#if defined(_WIN32)
    char win_buf[1024];
    DWORD flags = UNDNAME_NO_MS_KEYWORDS | UNDNAME_NO_ACCESS_SPECIFIERS;
    DWORD res = UnDecorateSymbolName(mangled, win_buf, sizeof(win_buf), flags);
    
    if (res > 0) {
        if (!buffer || *capacity < res + 1) {
            buffer = (char*)realloc(buffer, res + 1);
            *capacity = res + 1;
        }
        memcpy(buffer, win_buf, res + 1);
        return buffer;
    }
#else
    const char* target = mangled;
    // Обробка специфіки Mach-O на macOS: видалення зайвого початкового підкреслення
    if (target[0] == '_' && target[1] == '_') {
        target++;
    }

    int status = 0;
    char* demangled = abi::__cxa_demangle(target, buffer, capacity, &status);
    if (status == 0 && demangled != NULL) {
        return demangled; // Покажчик міг змінитися в результаті роботи realloc
    }
#endif

    // Якщо деманґлінг не дав результату, повертаємо незмінений вхідний рядок
    size_t len = strlen(mangled);
    if (!buffer || *capacity < len + 1) {
        buffer = (char*)realloc(buffer, len + 1);
        *capacity = len + 1;
    }
    memcpy(buffer, mangled, len + 1);
    return buffer;
}
```
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <utility>

#if defined(_WIN32)
#include <windows.h>
#include <dbghelp.h>
#pragma comment(lib, "dbghelp.lib")
#else
#include <cxxabi.h>
#endif

class SymbolDemangler {
public:
    explicit SymbolDemangler(size_t initial_capacity = 512)
        : capacity_(initial_capacity),
          buffer_(static_cast<char*>(std::malloc(initial_capacity)), std::free) {}

    SymbolDemangler(const SymbolDemangler&) = delete;
    SymbolDemangler& operator=(const SymbolDemangler&) = delete;
    SymbolDemangler(SymbolDemangler&&) noexcept = default;
    SymbolDemangler& operator=(SymbolDemangler&&) noexcept = default;

    std::string demangle(std::string_view mangled) {
        if (mangled.empty()) {
            return {};
        }

#if defined(_WIN32)
        std::string result(1024, '\0');
        DWORD flags = UNDNAME_NO_MS_KEYWORDS | UNDNAME_NO_ACCESS_SPECIFIERS;
        DWORD len = UnDecorateSymbolName(
            mangled.data(),
            result.data(),
            static_cast<DWORD>(result.size()),
            flags
        );
        if (len > 0) {
            result.resize(len);
            return result;
        }
#else
        std::string_view target = mangled;
        if (target.starts_with("__Z")) {
            target.remove_prefix(1);
        }

        // Швидкий шлях: якщо символ не починається з _Z, це не Itanium C++
        if (!target.starts_with("_Z")) {
            return std::string(mangled);
        }

        int status = 0;
        char* raw_ptr = buffer_.release();
        char* demangled = abi::__cxa_demangle(target.data(), raw_ptr, &capacity_, &status);
        buffer_.reset(demangled ? demangled : raw_ptr);

        if (status == 0 && buffer_) {
            return std::string(buffer_.get());
        }
#endif
        return std::string(mangled);
    }

private:
    size_t capacity_;
    std::unique_ptr<char, void(*)(void*)> buffer_;
};
```
:::

---

## 4. Повний модуль захоплення стеку та формування звіту

Тепер об'єднаємо деманґлер у повноцінний трасувальник викликів `StackTracer`. Програма імітує реальну архітектуру фізичного рушія: створюються вкладені простори імен, шаблонні конвеєри та класи обчислень, після чого виконується захоплення кадрів та їхній вивід у термінал.

:::tabs
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <sstream>
#include <iomanip>

#if defined(_WIN32)
#include <windows.h>
#include <dbghelp.h>
#else
#include <execinfo.h>
#include <dlfcn.h>
#include <cxxabi.h>
#endif

namespace diagnostics {

struct StackFrame {
    size_t index = 0;
    void* address = nullptr;
    std::string symbol_name;
    std::string module_name;
    uintptr_t offset = 0;

    std::string to_string() const {
        std::ostringstream ss;
        ss << "#" << std::setw(2) << std::left << index << " ["
           << address << "] " << symbol_name;
        if (!module_name.empty()) {
            ss << " (файл: " << module_name;
            if (offset > 0) {
                ss << " + 0x" << std::hex << offset;
            }
            ss << ")";
        }
        return ss.str();
    }
};

class StackTracer {
public:
    static std::vector<StackFrame> capture(size_t max_frames = 64) {
        std::vector<StackFrame> frames;
        std::vector<void*> raw_addresses(max_frames);
        SymbolDemangler demangler(1024);

#if defined(_WIN32)
        HANDLE process = GetCurrentProcess();
        SymInitialize(process, NULL, TRUE);

        USHORT captured = RtlCaptureStackBackTrace(
            0,
            static_cast<DWORD>(max_frames),
            raw_addresses.data(),
            NULL
        );

        SYMBOL_INFO_PACKAGE sip;
        sip.si.SizeOfStruct = sizeof(SYMBOL_INFO);
        sip.si.MaxNameLen = sizeof(sip.name);

        for (USHORT i = 0; i < captured; ++i) {
            DWORD64 addr = reinterpret_cast<DWORD64>(raw_addresses[i]);
            DWORD64 displacement = 0;
            std::string sym = "<невідомий символ>";
            std::string mod = "<головний модуль>";

            if (SymFromAddr(process, addr, &displacement, &sip.si)) {
                sym = demangler.demangle(sip.si.Name);
            }

            IMAGEHLP_MODULE64 mod_info;
            mod_info.SizeOfStruct = sizeof(IMAGEHLP_MODULE64);
            if (SymGetModuleInfo64(process, addr, &mod_info)) {
                mod = mod_info.ModuleName;
            }

            frames.push_back(StackFrame{
                .index = i,
                .address = raw_addresses[i],
                .symbol_name = std::move(sym),
                .module_name = std::move(mod),
                .offset = static_cast<uintptr_t>(displacement)
            });
        }
#else
        int captured = backtrace(raw_addresses.data(), static_cast<int>(max_frames));

        for (int i = 0; i < captured; ++i) {
            Dl_info info;
            std::string sym = "<невідомий символ>";
            std::string mod = "<динамічний об'єкт>";
            uintptr_t offset = 0;

            if (dladdr(raw_addresses[i], &info)) {
                if (info.dli_sname) {
                    sym = demangler.demangle(info.dli_sname);
                    offset = reinterpret_cast<uintptr_t>(raw_addresses[i]) -
                             reinterpret_cast<uintptr_t>(info.dli_saddr);
                }
                if (info.dli_fname) {
                    mod = info.dli_fname;
                }
            }

            frames.push_back(StackFrame{
                .index = static_cast<size_t>(i),
                .address = raw_addresses[i],
                .symbol_name = std::move(sym),
                .module_name = std::move(mod),
                .offset = offset
            });
        }
#endif
        return frames;
    }
};

} // namespace diagnostics

// Ієрархія бізнес-логіки для демонстрації стек-трейсу
namespace core::engine {

template <typename PhysicsModel>
class SimulationPipeline {
public:
    void execute_step(double delta_time) {
        process_collisions(delta_time);
    }

private:
    void process_collisions(double dt) {
        PhysicsModel model;
        model.calculate_forces(dt);
    }
};

class RigidBodySolver {
public:
    void calculate_forces(double dt) {
        solve_constraints(dt);
    }

private:
    void solve_constraints([[maybe_unused]] double dt) {
        auto trace = diagnostics::StackTracer::capture();
        std::cout << "\n=== ЗАХОПЛЕНИЙ СТЕК-ТРЕЙС ВИКЛИКІВ ===\n";
        for (const auto& frame : trace) {
            std::cout << frame.to_string() << '\n';
        }
        std::cout << "======================================\n\n";
    }
};

} // namespace core::engine

int main() {
    core::engine::SimulationPipeline<core::engine::RigidBodySolver> pipeline;
    pipeline.execute_step(0.0166);
    return 0;
}
```
:::

---

## 5. Кешування та оптимізація високонавантаженого деманґлінгу

У системах безперервного моніторингу або вибіркового профілювання (Sampling Profiler), де зняття стеку відбувається тисячі разів на секунду, повторний деманґлінг одних і тих самих символів стає головним джерелом затримок.

Розв'язанням є багаторівневий кеш адрес і символів:

:::tabs
```cpp
#include <unordered_map>
#include <shared_mutex>
#include <string>
#include <string_view>
#include <mutex>

class SymbolCache {
public:
    std::string lookup_or_demangle(void* address, const char* mangled_name) {
        {
            // Швидке неблоковане читання з кешу
            std::shared_lock<std::shared_mutex> read_lock(mutex_);
            auto it = cache_.find(address);
            if (it != cache_.end()) {
                return it->second;
            }
        }

        // Якщо адреси немає в кеші — виконуємо деманґлінг
        std::string demangled = demangler_.demangle(mangled_name ? mangled_name : "");

        {
            // Ексклюзивний запис у кеш
            std::unique_lock<std::shared_mutex> write_lock(mutex_);
            cache_[address] = demangled;
        }

        return demangled;
    }

private:
    std::shared_mutex mutex_;
    std::unordered_map<void*, std::string> cache_;
    SymbolDemangler demangler_;
};
```
:::

---

## 6. Інженерні пастки та аналіз крайових випадків

### 6.1. Пастка обробників сигналів аварійного завершення (Signal Safety)

Найпоширеніша і найнебезпечніша помилка під час написання обробників асинхронних сигналів (`SIGSEGV`, `SIGABRT`, `SIGBUS`, `SIGFPE`) — спроба виконати деманґлінг або відформатувати рядок за допомогою `std::ostringstream`/`printf` безпосередньо в тілі функції-обробника.

Стандарт POSIX суворо обмежує функції, які дозволено викликати зсередини обробника сигналів (Async-Signal-Safe Functions). Функція `abi::__cxa_demangle` не входить до цього переліку, оскільки вона звертається до C-алокатора пам'яті `malloc()` та `realloc()`.

Якщо потік виконання зазнає збою в той момент, коли він сам (або будь-який інший потік процесу) виконував виділення пам'яті в купі (тримаючи внутрішній м'ютекс `ptmalloc` у системній бібліотеці glibc), переривання сигналу призведе до спроби повторного захоплення того самого замка. Результат — **миттєвий вічний дедлок (Deadlock)**. Процес зависає назавжди, перестає відповідати операційній системі, блокує створення файлу Core Dump і перешкоджає автоматичному перезапуску сервісу в контейнерах Docker або оркестраторі Kubernetes.

**Правильна архітектура краш-репортингу:**
- Всередині обробника сигналу дозволено виконувати лише асинхронно-безпечні дії: зберегти масив числових адрес через `backtrace()` та скинути їх у дескриптор файлу журналу через системний виклик `write(2)`.
- Повне декодування адрес і деманґлінг імен виконується у фоновому допоміжному процесі (Out-of-Process Crash Reporter) або офлайн під час аналізу дампу.

### 6.2. Багатопотокова синхронізація DbgHelp у Windows

Бібліотека `DbgHelp.dll` на платформі Windows є внутрішньо несинхронізованою. Виклик `SymInitialize()` ініціалізує контекст для всього процесу. Одночасні виклики функцій `SymFromAddr()` або `SymGetModuleInfo64()` із кількох робочих потоків без явного блокування викликають пошкодження внутрішніх структур пам'яті бібліотеки та призводять до винятку `STATUS_ACCESS_VIOLATION`.

Усі операції з DbgHelp у багатопотокових програмах необхідно захищати глобальним м'ютексом:

```cpp
#include <mutex>

std::mutex g_dbghelp_mutex;

void safe_symbol_lookup(HANDLE process, DWORD64 addr, PSYMBOL_INFO sym_info) {
    std::lock_guard<std::mutex> lock(g_dbghelp_mutex);
    DWORD64 displacement = 0;
    SymFromAddr(process, addr, &displacement, sym_info);
}
```

### 6.3. Очищення префіксів об'єктних форматів на macOS

Формат двійкових файлів Mach-O на платформі Apple Darwin (macOS, iOS) додає одне підкреслення `_` перед усіма глобальними символами під час компіляції. Через це функція, яка в стандарті Itanium ABI має спотворене ім'я `_ZN4math6Vector3addEv`, у таблиці символів записується як `__ZN4math6Vector3addEv` (з двома підкресленнями).

Пряма передача `__ZN4math6Vector3addEv` у функцію `abi::__cxa_demangle` повертає код помилки `-2` (Invalid Mangled Name), оскільки граматика стандарту очікує рівно одне підкреслення перед літерою `Z`. Реалізація деманґлера повинна перевіряти наявність префікса `__Z` і зсувати покажчик на один символ праворуч перед передачею в системну функцію.
