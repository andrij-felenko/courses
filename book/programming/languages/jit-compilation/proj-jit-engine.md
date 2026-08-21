# ⚙️ Реалізація мініатюрного JIT-рушія з W^X та динамічною генерацією x86-64

Найкращий спосіб до кінця зрозуміти, як центральний процесор виконує згенерований на льоту код, — створити мінімальний робочий JIT-рушій без сторонніх бібліотек та залежностей. Задача: взяти математичний вираз `f(a, b) = (a * b) + c`, перетворити його у двійкові інструкції процесора x86-64 безпосередньо під час виконання програми, завантажити в пам'ять за суворими правилами безпеки W^X (*Write XOR Execute*) і викликати як звичайну функцію мов C або C++.

## Задача та архітектура рушія

Звичайний компілятор створює виконуваний файл на диску (ELF у Linux, PE у Windows, Mach-O в macOS), який завантажувач операційної системи монтує у фіксовані сегменти віртуальної пам'яті. JIT-рушій працює принципово інакше: він виступає мініатюрним компілятором, що живе всередині адресного простору процесу, виділяє сторінки пам'яті, генерує машинний код і одразу передає йому керування.

Щоб операційна система дозволила процесору стрибнути за адресою динамічно створеного буфера, потрібно пройти чотири обов'язкові інженерні фази:

```
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│ 1. Виділення пам'яті    │ ──► │ 2. Емісія інструкцій    │ ──► │ 3. Захист W^X + I-Cache │ ──► │ 4. Виклик функції       │
│ mmap / VirtualAlloc     │     │ Запис машинних байтів   │     │ mprotect (R|X)          │     │ fn = (jit_func_t)code   │
│ Права: PROT_READ|WRITE  │     │ x86-64 у буфер          │     │ __builtin___clear_cache │     │ int64_t res = fn(a, b)  │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

1. **Виділення віртуальної сторінки.** Звичайна купа (`malloc`/`new`) розміщується ядром операційної системи з правами `PROT_READ | PROT_WRITE` без права виконання. Спроба виконати код із такого буфера буде перехоплена блоком керування пам'яттю (MMU), і операційна система негайно вб'є процес сигналом `SIGSEGV` (або `STATUS_ACCESS_VIOLATION`). Тому пам'ять запитується безпосередньо в ядра через системний виклик `mmap()` (у POSIX) або `VirtualAlloc()` (у Windows).
2. **Генерація двійкового коду (Emitter).** Запис послідовності двійкових байтів інструкцій x86-64 у виділений буфер.
3. **Зміна прав захисту сторінки (W^X) та очищення кешу.** Сторінка перемикається в режим `PROT_READ | PROT_EXEC` викликом `mprotect()`. Будь-який подальший запис у цю область блокується апаратно. Одночасно виконується скидання конвеєра інструкцій процесора (`I-Cache`).
4. **Виклик через покажчик на функцію.** Вказівник на початок буфера зводиться до типу сигнатури функції згідно з угодою про виклики ([ABI та calling convention](book:programming/abi-calling-convention)), після чого викликається як звичайна функція.

## Кодування інструкцій x86-64 та угода про виклики

Центральний процесор архітектури x86-64 інтерпретує команди як послідовність байтів змінної довжини. Щоб виконати операцію над 64-бітними регістрами, інструкція містить спеціальний префікс **REX.W** (`0x48`), байт коду операції (*Opcode*) та байт адресації **ModR/M**, який визначає регістри джерела й призначення.

Для кросплатформної сумісності врахуємо конвенцію передачі аргументів:
- У **System V AMD64 ABI** (Linux, macOS, BSD): перший аргумент передається в регістрі `RDI`, другий — у `RSI`, а повернене значення очікується в `RAX`.
- У **Microsoft x64 ABI** (Windows): перший аргумент у `RCX`, другий — у `RDX`, результат — у `RAX`.

Розберемо двійкове кодування кожної інструкції для виразу `f(a, b) = a * b + constant`:

1. **Множення `imul rdi, rsi` (System V) або `imul rcx, rdx` (Windows):**
   - Префікс `0x48` (REX.W — 64-бітні операнди).
   - Опкод `0x0F 0xAF` — інструкція знакового множення двох 64-бітних регістрів.
   - Байт ModR/M: для `rdi` та `rsi` це `0xFE` (двійкове `11 111 110`), для `rcx` та `rdx` це `0xCA` (двійкове `11 001 010`).
2. **Додавання константи `add rdi, constant` (System V) або `add rcx, constant` (Windows):**
   - Префікс `0x48`.
   - Опкод `0x81` — операція з безпосереднім 32-бітним операндом (*immediate*).
   - Байт ModR/M: `0xC7` для `rdi` або `0xC1` для `rcx`.
   - 4 байти константи `constant` у порядку від молодшого байта до старшого (*Little-Endian*).
3. **Переміщення результату `mov rax, rdi` / `mov rax, rcx`:**
   - Префікс `0x48`.
   - Опкод `0x89` — копіювання регістр-регістр.
   - Байт ModR/M: `0xF8` для `rax = rdi` або `0xC8` для `rax = rcx`.
4. **Повернення з функції `ret`:**
   - Байт `0xC3` — зняття адреси повернення зі стека та стрибок назад до викликаючого коду.

## Реалізація мовами C та C++

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#if defined(_WIN32) || defined(_WIN64)
#include <windows.h>
#else
#include <sys/mman.h>
#include <unistd.h>
#endif

/* Сигнатура функції, яку генерує JIT */
typedef int64_t (*jit_func_t)(int64_t, int64_t);

/* Структура для керування виконуваною сторінкою */
typedef struct {
    uint8_t *code;
    size_t size;
} jit_buffer_t;

/* 1. Виділення пам'яті (W=1, X=0) */
int jit_buffer_init(jit_buffer_t *buf, size_t size) {
    buf->size = size;
#if defined(_WIN32) || defined(_WIN64)
    buf->code = (uint8_t *)VirtualAlloc(NULL, size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (!buf->code) return -1;
#else
    buf->code = (uint8_t *)mmap(NULL, size, PROT_READ | PROT_WRITE,
                                MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
    if (buf->code == MAP_FAILED) {
        buf->code = NULL;
        return -1;
    }
#endif
    return 0;
}

/* 2. Генерація байтів x86-64 для f(a, b) = a * b + constant */
size_t jit_emit_mul_add(jit_buffer_t *buf, int32_t constant) {
    uint8_t *p = buf->code;

#if defined(_WIN32) || defined(_WIN64)
    /* imul rcx, rdx */
    *p++ = 0x48; *p++ = 0x0F; *p++ = 0xAF; *p++ = 0xCA;
    /* add rcx, constant (imm32) */
    *p++ = 0x48; *p++ = 0x81; *p++ = 0xC1;
    memcpy(p, &constant, sizeof(int32_t));
    p += sizeof(int32_t);
    /* mov rax, rcx */
    *p++ = 0x48; *p++ = 0x89; *p++ = 0xC8;
#else
    /* imul rdi, rsi */
    *p++ = 0x48; *p++ = 0x0F; *p++ = 0xAF; *p++ = 0xFE;
    /* add rdi, constant (imm32) */
    *p++ = 0x48; *p++ = 0x81; *p++ = 0xC7;
    memcpy(p, &constant, sizeof(int32_t));
    p += sizeof(int32_t);
    /* mov rax, rdi */
    *p++ = 0x48; *p++ = 0x89; *p++ = 0xF8;
#endif
    /* ret */
    *p++ = 0xC3;

    return (size_t)(p - buf->code);
}

/* 3. Перемикання прав на виконання (W=0, X=1) згідно з W^X */
int jit_buffer_protect(jit_buffer_t *buf) {
#if defined(_WIN32) || defined(_WIN64)
    DWORD old_protect;
    if (!VirtualProtect(buf->code, buf->size, PAGE_EXECUTE_READ, &old_protect)) {
        return -1;
    }
#else
    if (mprotect(buf->code, buf->size, PROT_READ | PROT_EXEC) != 0) {
        return -1;
    }
    /* Скидання кешу інструкцій (Instruction Cache flush) */
    __builtin___clear_cache((char *)buf->code, (char *)buf->code + buf->size);
#endif
    return 0;
}

/* 4. Звільнення виконуваної сторінки */
void jit_buffer_free(jit_buffer_t *buf) {
    if (!buf->code) return;
#if defined(_WIN32) || defined(_WIN64)
    VirtualFree(buf->code, 0, MEM_RELEASE);
#else
    munmap(buf->code, buf->size);
#endif
    buf->code = NULL;
}

int main(void) {
    jit_buffer_t jit;
    const size_t page_size = 4096;

    if (jit_buffer_init(&jit, page_size) != 0) {
        perror("Не вдалося виділити JIT-пам'ять");
        return 1;
    }

    /* Емітуємо код обчислення: f(a, b) = a * b + 42 */
    jit_emit_mul_add(&jit, 42);

    /* Захищаємо пам'ять від запису й дозволяємо виконання */
    if (jit_buffer_protect(&jit) != 0) {
        perror("mprotect помилка");
        jit_buffer_free(&jit);
        return 1;
    }

    /* Викликаємо згенеровану функцію через покажчик */
    jit_func_t fn = (jit_func_t)(uintptr_t)jit.code;
    int64_t a = 7, b = 8;
    int64_t result = fn(a, b);

    printf("JIT f(%lld, %lld) = %lld (очікувано 7 * 8 + 42 = 98)\n",
           (long long)a, (long long)b, (long long)result);

    jit_buffer_free(&jit);
    return 0;
}
```
```cpp
#include <iostream>
#include <span>
#include <vector>
#include <cstdint>
#include <cstring>
#include <system_error>

#if defined(_WIN32) || defined(_WIN64)
#include <windows.h>
#else
#include <sys/mman.h>
#include <unistd.h>
#endif

// RAII-клас для суворого контролю стану та прав віртуальної сторінки
class ExecutableMemory {
public:
    enum class State {
        Writable,    // W=1, X=0 (дозволено генерацію коду)
        Executable,  // W=0, X=1 (дозволено виконання, запис заборонено)
        Freed        // Пам'ять повернуто операційній системі
    };

    explicit ExecutableMemory(size_t size = 4096) : size_(size), state_(State::Writable) {
#if defined(_WIN32) || defined(_WIN64)
        ptr_ = static_cast<uint8_t*>(VirtualAlloc(nullptr, size_, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));
        if (!ptr_) {
            throw std::system_error(static_cast<int>(GetLastError()), std::system_category(), "VirtualAlloc failed");
        }
#else
        void* p = mmap(nullptr, size_, PROT_READ | PROT_WRITE, MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
        if (p == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "mmap failed");
        }
        ptr_ = static_cast<uint8_t*>(p);
#endif
    }

    ~ExecutableMemory() noexcept {
        release();
    }

    ExecutableMemory(const ExecutableMemory&) = delete;
    ExecutableMemory& operator=(const ExecutableMemory&) = delete;

    ExecutableMemory(ExecutableMemory&& other) noexcept 
        : ptr_(other.ptr_), size_(other.size_), state_(other.state_) {
        other.ptr_ = nullptr;
        other.state_ = State::Freed;
    }

    ExecutableMemory& operator=(ExecutableMemory&& other) noexcept {
        if (this != &other) {
            release();
            ptr_ = other.ptr_;
            size_ = other.size_;
            state_ = other.state_;
            other.ptr_ = nullptr;
            other.state_ = State::Freed;
        }
        return *this;
    }

    void make_executable() {
        if (state_ != State::Writable) {
            throw std::logic_error("Сторінка не перебуває в стані запису");
        }

#if defined(_WIN32) || defined(_WIN64)
        DWORD old_prot;
        if (!VirtualProtect(ptr_, size_, PAGE_EXECUTE_READ, &old_prot)) {
            throw std::system_error(static_cast<int>(GetLastError()), std::system_category(), "VirtualProtect failed");
        }
#else
        if (mprotect(ptr_, size_, PROT_READ | PROT_EXEC) != 0) {
            throw std::system_error(errno, std::generic_category(), "mprotect failed");
        }
        __builtin___clear_cache(reinterpret_cast<char*>(ptr_), reinterpret_cast<char*>(ptr_) + size_);
#endif
        state_ = State::Executable;
    }

    [[nodiscard]] uint8_t* data() {
        if (state_ != State::Writable) {
            throw std::logic_error("Спроба запису у виконувану або звільнену пам'ять");
        }
        return ptr_;
    }

    [[nodiscard]] size_t size() const noexcept { return size_; }
    [[nodiscard]] State state() const noexcept { return state_; }

    template<typename FuncType>
    [[nodiscard]] FuncType as_function() const {
        if (state_ != State::Executable) {
            throw std::logic_error("Спроба виклику коду зі сторінки, яка не має прав PROT_EXEC");
        }
        return reinterpret_cast<FuncType>(reinterpret_cast<uintptr_t>(ptr_));
    }

private:
    void release() noexcept {
        if (!ptr_) return;
#if defined(_WIN32) || defined(_WIN64)
        VirtualFree(ptr_, 0, MEM_RELEASE);
#else
        munmap(ptr_, size_);
#endif
        ptr_ = nullptr;
        state_ = State::Freed;
    }

    uint8_t* ptr_{nullptr};
    size_t size_{0};
    State state_{State::Freed};
};

// Емітер інструкцій x86-64
class SimpleJitEmitter {
public:
    static void emit_mul_add(std::span<uint8_t> buffer, int32_t constant) {
        std::vector<uint8_t> bytes;

#if defined(_WIN32) || defined(_WIN64)
        // imul rcx, rdx
        bytes.insert(bytes.end(), {0x48, 0x0F, 0xAF, 0xCA});
        // add rcx, imm32
        bytes.insert(bytes.end(), {0x48, 0x81, 0xC1});
        append_int32(bytes, constant);
        // mov rax, rcx
        bytes.insert(bytes.end(), {0x48, 0x89, 0xC8});
#else
        // imul rdi, rsi
        bytes.insert(bytes.end(), {0x48, 0x0F, 0xAF, 0xFE});
        // add rdi, imm32
        bytes.insert(bytes.end(), {0x48, 0x81, 0xC7});
        append_int32(bytes, constant);
        // mov rax, rdi
        bytes.insert(bytes.end(), {0x48, 0x89, 0xF8});
#endif
        // ret
        bytes.push_back(0xC3);

        if (bytes.size() > buffer.size()) {
            throw std::runtime_error("JIT-буфер замалий для емітованого коду");
        }
        std::memcpy(buffer.data(), bytes.data(), bytes.size());
    }

private:
    static void append_int32(std::vector<uint8_t>& vec, int32_t val) {
        const auto* raw = reinterpret_cast<const uint8_t*>(&val);
        vec.insert(vec.end(), raw, raw + sizeof(int32_t));
    }
};

int main() {
    try {
        ExecutableMemory mem(4096);

        // Генерація коду для f(a, b) = a * b + 42
        SimpleJitEmitter::emit_mul_add(std::span<uint8_t>(mem.data(), mem.size()), 42);

        // Перемикання в режим виконання (W^X)
        mem.make_executable();

        // Отримання покажчика на функцію
        using JitSignature = int64_t (*)(int64_t, int64_t);
        auto fn = mem.as_function<JitSignature>();

        int64_t a = 7, b = 8;
        int64_t res = fn(a, b);

        std::cout << "JIT f(" << a << ", " << b << ") = " << res
                  << " (очікувано 7 * 8 + 42 = 98)\n";

    } catch (const std::exception& ex) {
        std::cerr << "Помилка JIT: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

## Налагодження та типові підводні камені

Створення динамічного компілятора пов'язане зі специфічними низькорівневими пастками, яких не буває у звичайному прикладному програмуванні:

1. **Когерентність кешу інструкцій (I-Cache / D-Cache).** У сучасних процесорах із суперскалярним конвеєром кеш інструкцій L1I та кеш даних L1D фізично розділені. Коли JIT-компілятор записує нові байти коду в пам'ять через звичайні інструкції `MOV`, ці зміни оновлюють L1D та системну оперативну пам'ять, але не потрапляють у L1I автоматично. Якщо не виконати інструкцію інвалідації черги команд (виклик `__builtin___clear_cache()` у GCC/Clang або інструкцію `ISB` на ARM), процесор виконає старі байти, що випадково залишилися в L1I, що призведе до невизначеної поведінки або збою `SIGILL` (*Illegal Instruction*).
2. **Вимога вирівнювання сторінок для `mprotect`.** Системний виклик `mprotect()` вимагає, щоб передана адреса була строго кратна розміру системної сторінки віртуальної пам'яті (зазвичай 4096 байтів). Якщо передати вказівник зі зміщенням усередині сторінки, виклик поверне помилку `-1` із кодом `EINVAL`.
3. **Вбудовування точок зупинки для налагодження (Software Breakpoints).** Щоб дослідити згенерований машинний код у зневаджувачі GDB або LLDB, на початок JIT-буфера можна записати байт `0xCC` (асемблерна інструкція `INT 3`). Коли процесор дійде до цього байта, він згенерує сигнал `SIGTRAP` і передасть керування налагоджувачу. У командному рядку GDB можна переглянути дизасембльований код командою `disassemble /r $rip` або увімкнути покрокове виконання машинних інструкцій через `stepi`.
4. **Релокації 32-бітних відносних адрес.** Інструкції умовних і безумовних переходів x86-64 (наприклад, `CALL rel32` чи `JMP rel32`) оперують 32-бітними знаковими зміщеннями відносно регістра `RIP` (діапазон ±2 ГБ). Якщо згенерований JIT-код розташований у виділеному пулі пам'яті за адресою `0x7FFF10000000`, а runtime-функція C знаходиться в пам'яті за межами 2 ГБ, прямий відносний виклик переповнить 32-бітне поле. У такому разі JIT зобов'язаний завантажувати абсолютну 64-бітну адресу в регістр (наприклад, `MOV RAX, 0x123456789ABCDEF0`) і викликати її через непрямий перехід `CALL RAX`.
