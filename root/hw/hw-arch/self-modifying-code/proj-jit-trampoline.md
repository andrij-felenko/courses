# ⚙️ Генератор JIT-трамплінів із синхронізацією кешу

Цей практичний проект демонструє проектування, побудову, низькорівневе простеження та тонке налагодження JIT-генератора (Just-In-Time) динамічних машинних функцій та викличних трамплінів для двох провідних сучасних архітектур — x86-64 та AArch64 (ARM64). Програма самостійно взаємодіє з підсистемою віртуальної пам'яті операційної системи, транслює високорівневі математичні вирази у бінарні опкоди під час виконання, забезпечує суворе дотримання політики безпеки `W^X` (Write XOR Execute), ініціює апаратну синхронізацію роздільних кешів мікропроцесора та демонструє механіку безпечного динамічного оновлення (гарячого латання) машинних інструкцій безпосередньо у процесі роботи.

---

## 1. Архітектурне завдання та мікроархітектурний контекст

У сучасних високопродуктивних системах динамічної компіляції (рушіях JavaScript V8, SpiderMonkey, віртуальних машинах Java JVM HotSpot, середовищах виконання WebAssembly Wasmtime, а також у бібліотеках динамічного зв'язування та створення замикань на зразок `libffi`) виникає фундаментальна потреба створювати або модифікувати машинний код у відповідь на події, що відбуваються під час виконання програми.

Звичайний статичний компілятор (GCC або Clang) транслює текст програми у бінарні файли формату ELF на Linux або Mach-O на macOS на етапі збірки проекту. Операційна система завантажує скомпільований код у захищений сегмент пам'яті `.text`, виставляє для відповідних сторінок біти захисту таблиць сторінок у режим виконання (`RX`, Read + Execute) і блокує будь-які спроби запису у цей простір.

На відміну від статичного бінарного файлу, JIT-компілятор зобов'язаний виділяти «чисту» пам'ять під час виконання, записувати в неї згенеровані послідовності машинних інструкцій і передавати на них апаратний лічильник команд процесора (`RIP` на x86-64 або `PC` на AArch64).

Ми збудуємо динамічний компілятор лінійної математичної функції з сигнатурою `int32_t (*jit_func_t)(int32_t x)`.

Ця функція приймає ціле 32-розрядне число `x` і виконує обчислення лінійного виразу:
```
f(x) = x · multiplier + addend
```

Головна відмінність цієї реалізації від звичайної скомпільованої функції полягає в тому, що коефіцієнти `multiplier` та `addend` не завантажуються зі змінних пам'яті чи глобальних структур даних. Вони безпосередньо кодуються в поля констант (Immediate Operands) самих машинних інструкцій процесора. Це дозволяє усунути зайві операції звернення до пам'яті через кеш даних, уникати промахів кешу першого рівня L1 D-Cache і досягати максимальної теоретичної швидкодії у гарячих обчислювальних циклах.

### Життєвий цикл пам'яті JIT-блоку
1. **Виділення сторінки пам'яті через `mmap`:** отримання нового анонімного відображення від ядра ОС із початковими правами на запис `PROT_READ | PROT_WRITE`.
2. **Емісія машинного коду:** послідовний розрахунок і запис байтів опкодів у виділений буфер.
3. **Застосування політики `W^X`:** виклик `mprotect` для блокування права на запис і надання прав на виконання `PROT_READ | PROT_EXEC`.
4. **Мікроархітектурна когерентність:** виконання інструкцій обслуговування кешу через `__builtin___clear_cache` (скидання D-Cache до точки PoU, інвалідація I-Cache та скидання конвеєра вибірки).
5. **Виконання:** виклик створеного машинного блоку за покажчиком на функцію та перевірка коректності обчислень.
6. **Гаряча модифікація (Live Patching):** безпечний перехід між станами `W^X`, зміна байтів коефіцієнта безпосередньо в тілі опкоду, повторна інвалідація кешів та перевірка оновленого результату.
7. **Звільнення ресурсів:** повернення сторінки віртуальної пам'яті ядру ОС через системний виклик `munmap`.

---

## 2. Бінарне кодування інструкцій для x86-64 та AArch64

### Машинне кодування для x86-64 (System V AMD64 ABI)
В архітектурі x86-64 інструкції мають змінну довжину від 1 до 15 байтів. Згідно зі стандартом викликів System V AMD64 ABI (Linux, BSD, macOS), перший 32-розрядний цілочисельний аргумент передається у регістрі `EDI`, а обчислене значення має повертатися в регістрі `EAX`.

Послідовність емітованих байтів формується так:

1. **Множення `IMUL EDI, EDI, <multiplier>` (6 байтів):**
   * Байт опкоду: `0x69` (знакове цілочисельне множення з 32-розрядним безпосереднім операндом).
   * Байт ModR/M: `0xFF` (двійкове значення `11 111 111`, що позначає режим регістр-регістр, де цільовим регістром і джерелом виступає `EDI`).
   * Чотири байти константи: значення `multiplier`, записане у форматі Little-Endian (молодший байт за меншою адресою).
2. **Додавання `ADD EDI, <addend>` (6 байтів):**
   * Байт опкоду: `0x81` (арифметична операція з 32-розрядним безпосереднім значенням).
   * Байт ModR/M: `0xC7` (двійкове `11 000 111`, де код операції `000` відповідає інструкції `ADD`, а цільовим регістром є `EDI`).
   * Чотири байти константи: значення `addend` у форматі Little-Endian.
3. **Переміщення результату `MOV EAX, EDI` (2 байти):**
   * Байти опкоду: `0x89`, `0xF8` (копіює молодші 32 біти обчисленого значення в регістр повернення `EAX`).
4. **Повернення з підпрограми `RET` (1 байт):**
   * Байт опкоду: `0xC3` (знімає адресу повернення зі стека та передає керування назад у викликач).

Сумарна довжина згенерованого тіла функції на x86-64 становить рівно 15 байтів.

### Машинне кодування для AArch64 (ARM64 AAPCS)
В архітектурі ARMv8-A/ARMv9-A всі інструкції мають суворо фіксовану довжину 4 байти (32 біти) і вимагають 4-байтного вирівнювання за адресою. За стандартом AAPCS64 аргумент передається у регістрі `W0`, результат повертається також у `W0`.

Послідовність інструкцій:

1. **Завантаження множника `MOVZ W1, #multiplier, LSL #0` (4 байти):**
   * Базовий опкод інструкції `MOVZ` для 32-розрядних регістрів: `0x52800000`.
   * Значення константи множника зсувається на 5 бітів ліворуч і об'єднується порозрядним «АБО» з індексом цільового регістра `W1` (індекс `1`).
2. **Множення `MUL W0, W0, W1` (4 байти):**
   * Машинне 32-розрядне слово `0x1B017C00` (перемножує вміст регістрів `W0` та `W1`, результат записує у `W0`).
3. **Завантаження доданка `MOVZ W1, #addend, LSL #0` (4 байти):**
   * Інструкція `MOVZ` із кодуванням константи `addend` у регістр `W1`.
4. **Додавання `ADD W0, W0, W1` (4 байти):**
   * Машинне слово `0x0B010000` (додає `W1` до `W0` без збереження прапорців стану).
5. **Повернення з підпрограми `RET` (4 байти):**
   * Машинне слово `0xD65F03C0` (виконує перехід за адресою зв'язку в регістрі `X30` / `LR`).

Сумарна довжина коду на AArch64 становить 20 байтів.

---

## 3. Програмна реалізація

Нижче наведено дві повні, самостійні та готові до компіляції реалізації: версію на чистому C (POSIX API) та версію на сучасній об'єктній мові C++20 із застосуванням ідіоми RAII для гарантованого автоматичного очищення пам'яті, типу `std::expected` для явної обробки помилок та контейнера `std::span` для безпечної роботи з діапазонами пам'яті.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

typedef int32_t (*jit_func_t)(int32_t);

// Перевірка цільової архітектури під час збірки
#if defined(__x86_64__) || defined(_M_X64)
#define ARCH_X86_64 1
#elif defined(__aarch64__) || defined(_M_ARM64)
#define ARCH_AARCH64 1
#else
#error "Непідтримувана процесорна архітектура для прямої генерації коду"
#endif

// Структура дескриптора виділеного блоку пам'яті JIT
typedef struct {
    uint8_t *buffer;
    size_t size;
    size_t code_len;
} jit_block_t;

// Виділення анонімної сторінки пам'яті
int jit_alloc(jit_block_t *block, size_t min_size) {
    long page_size = sysconf(_SC_PAGESIZE);
    if (page_size <= 0) page_size = 4096;

    // Округлення розміру до найближчого розміру цілої сторінки
    size_t alloc_size = (min_size + page_size - 1) & ~(page_size - 1);

    // Пам'ять спочатку виділяється як доступна на читання та запис (RW)
    void *ptr = mmap(NULL, alloc_size, PROT_READ | PROT_WRITE,
                     MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
    if (ptr == MAP_FAILED) {
        perror("mmap failed");
        return -1;
    }

    block->buffer = (uint8_t *)ptr;
    block->size = alloc_size;
    block->code_len = 0;
    return 0;
}

// Звільнення сторінки пам'яті
void jit_free(jit_block_t *block) {
    if (block->buffer && block->size > 0) {
        munmap(block->buffer, block->size);
        block->buffer = NULL;
        block->size = 0;
        block->code_len = 0;
    }
}

// Емісія машинного коду лінійної функції: f(x) = x * multiplier + addend
int jit_emit_linear(jit_block_t *block, int32_t multiplier, int32_t addend) {
#if defined(ARCH_X86_64)
    uint8_t code[] = {
        // IMUL EDI, EDI, imm32 (6 байтів)
        0x69, 0xFF,
        (uint8_t)(multiplier & 0xFF),
        (uint8_t)((multiplier >> 8) & 0xFF),
        (uint8_t)((multiplier >> 16) & 0xFF),
        (uint8_t)((multiplier >> 24) & 0xFF),

        // ADD EDI, imm32 (6 байтів)
        0x81, 0xC7,
        (uint8_t)(addend & 0xFF),
        (uint8_t)((addend >> 8) & 0xFF),
        (uint8_t)((addend >> 16) & 0xFF),
        (uint8_t)((addend >> 24) & 0xFF),

        // MOV EAX, EDI (2 байти)
        0x89, 0xF8,

        // RET (1 байт)
        0xC3
    };
    size_t len = sizeof(code);
#elif defined(ARCH_AARCH64)
    uint32_t imm_mul = (uint32_t)multiplier & 0xFFFF;
    uint32_t imm_add = (uint32_t)addend & 0xFFFF;

    uint32_t code[] = {
        // MOVZ W1, #multiplier
        0x52800000 | (imm_mul << 5) | 1,
        // MUL W0, W0, W1
        0x1B017C00,
        // MOVZ W1, #addend
        0x52800000 | (imm_add << 5) | 1,
        // ADD W0, W0, W1
        0x0B010000,
        // RET
        0xD65F03C0
    };
    size_t len = sizeof(code);
#endif

    if (len > block->size) return -1;
    memcpy(block->buffer, code, len);
    block->code_len = len;
    return 0;
}

// Захист пам'яті W^X та апаратна синхронізація кешів
int jit_finalize(jit_block_t *block) {
    // 1. Зміна прав сторінки на RX (Read + Execute)
    if (mprotect(block->buffer, block->size, PROT_READ | PROT_EXEC) != 0) {
        perror("mprotect RX failed");
        return -1;
    }

    // 2. Інвалідація кешів: D-Cache clean + I-Cache invalidate + ISB
    __builtin___clear_cache((char *)block->buffer,
                            (char *)block->buffer + block->code_len);
    return 0;
}

// Гаряча модифікація константи множника у згенерованому коді
int jit_patch_multiplier(jit_block_t *block, int32_t new_multiplier) {
    // 1. Відкриваємо права на запис RW
    if (mprotect(block->buffer, block->size, PROT_READ | PROT_WRITE) != 0) {
        perror("mprotect RW failed");
        return -1;
    }

    // 2. Модифікуємо байти константи
#if defined(ARCH_X86_64)
    // Зсув константи multiplier в інструкції IMUL дорівнює 2 байтам
    uint8_t *patch_ptr = block->buffer + 2;
    patch_ptr[0] = (uint8_t)(new_multiplier & 0xFF);
    patch_ptr[1] = (uint8_t)((new_multiplier >> 8) & 0xFF);
    patch_ptr[2] = (uint8_t)((new_multiplier >> 16) & 0xFF);
    patch_ptr[3] = (uint8_t)((new_multiplier >> 24) & 0xFF);
#elif defined(ARCH_AARCH64)
    // Інструкція MOVZ W1, #multiplier знаходиться за зсувом 0
    uint32_t *patch_ptr = (uint32_t *)block->buffer;
    uint32_t imm = (uint32_t)new_multiplier & 0xFFFF;
    patch_ptr[0] = 0x52800000 | (imm << 5) | 1;
#endif

    // 3. Закриваємо запис, повертаємо права RX та синхронізуємо кеші
    return jit_finalize(block);
}

int main(void) {
    jit_block_t jit;
    if (jit_alloc(&jit, 4096) != 0) {
        return EXIT_FAILURE;
    }

    printf("1. Генерація функції: f(x) = x * 10 + 7\n");
    if (jit_emit_linear(&jit, 10, 7) != 0 || jit_finalize(&jit) != 0) {
        jit_free(&jit);
        return EXIT_FAILURE;
    }

    jit_func_t func = (jit_func_t)jit.buffer;
    int32_t input = 5;
    int32_t res1 = func(input);
    printf("   Результат f(%d) = %d (очікувано: 57)\n", input, res1);

    printf("2. Гаряче латання коду на льоту: f(x) = x * 100 + 7\n");
    if (jit_patch_multiplier(&jit, 100) != 0) {
        jit_free(&jit);
        return EXIT_FAILURE;
    }

    int32_t res2 = func(input);
    printf("   Результат f(%d) після патчу = %d (очікувано: 507)\n", input, res2);

    jit_free(&jit);
    printf("3. Пам'ять успішно звільнено.\n");
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <string>
#include <cstdint>
#include <cstring>
#include <sys/mman.h>
#include <unistd.h>

#if defined(__x86_64__) || defined(_M_X64)
#define ARCH_X86_64 1
#elif defined(__aarch64__) || defined(_M_ARM64)
#define ARCH_AARCH64 1
#else
#error "Непідтримувана процесорна архітектура для прямої генерації коду"
#endif

// RAII обгортка для керування пам'яттю JIT-блоків
class JitMemoryBlock {
public:
    enum class Protection {
        ReadWrite,
        ReadExecute
    };

    static std::expected<JitMemoryBlock, std::string> allocate(size_t min_size) {
        long page_size = sysconf(_SC_PAGESIZE);
        if (page_size <= 0) page_size = 4096;

        size_t alloc_size = (min_size + page_size - 1) & ~(page_size - 1);
        void* ptr = mmap(nullptr, alloc_size, PROT_READ | PROT_WRITE,
                         MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);

        if (ptr == MAP_FAILED) {
            return std::unexpected("Не вдалося виділити пам'ять через mmap");
        }

        return JitMemoryBlock(static_cast<uint8_t*>(ptr), alloc_size);
    }

    ~JitMemoryBlock() noexcept {
        if (buffer_ && size_ > 0) {
            munmap(buffer_, size_);
        }
    }

    // Заборона копіювання об'єкта для запобігання подвійному звільненню
    JitMemoryBlock(const JitMemoryBlock&) = delete;
    JitMemoryBlock& operator=(const JitMemoryBlock&) = delete;

    // Підтримка семантики переміщення (Move Constructor / Move Assignment)
    JitMemoryBlock(JitMemoryBlock&& other) noexcept
        : buffer_(other.buffer_), size_(other.size_), code_len_(other.code_len_) {
        other.buffer_ = nullptr;
        other.size_ = 0;
        other.code_len_ = 0;
    }

    JitMemoryBlock& operator=(JitMemoryBlock&& other) noexcept {
        if (this != &other) {
            if (buffer_ && size_ > 0) munmap(buffer_, size_);
            buffer_ = other.buffer_;
            size_ = other.size_;
            code_len_ = other.code_len_;
            other.buffer_ = nullptr;
            other.size_ = 0;
            other.code_len_ = 0;
        }
        return *this;
    }

    std::expected<void, std::string> set_protection(Protection prot) noexcept {
        int flags = (prot == Protection::ReadWrite)
                    ? (PROT_READ | PROT_WRITE)
                    : (PROT_READ | PROT_EXEC);

        if (mprotect(buffer_, size_, flags) != 0) {
            return std::unexpected("Помилка зміни прав доступу сторінки mprotect");
        }
        return {};
    }

    void sync_cache() noexcept {
        __builtin___clear_cache(reinterpret_cast<char*>(buffer_),
                                reinterpret_cast<char*>(buffer_ + code_len_));
    }

    std::span<uint8_t> as_writable_span() noexcept {
        return std::span<uint8_t>(buffer_, size_);
    }

    template <typename FuncSignature>
    FuncSignature get_entry_point() const noexcept {
        return reinterpret_cast<FuncSignature>(buffer_);
    }

    void set_code_length(size_t len) noexcept { code_len_ = len; }
    size_t size() const noexcept { return size_; }
    size_t code_length() const noexcept { return code_len_; }

private:
    explicit JitMemoryBlock(uint8_t* buf, size_t sz) noexcept
        : buffer_(buf), size_(sz), code_len_(0) {}

    uint8_t* buffer_{nullptr};
    size_t size_{0};
    size_t code_len_{0};
};

// Типобезпечний клас генератора коду лінійних виразів
class LinearJitCompiler {
public:
    using FuncType = int32_t (*)(int32_t);

    static std::expected<void, std::string> compile(JitMemoryBlock& mem,
                                                   int32_t multiplier,
                                                   int32_t addend) {
        auto span = mem.as_writable_span();

#if defined(ARCH_X86_64)
        const uint8_t code[] = {
            0x69, 0xFF,
            static_cast<uint8_t>(multiplier & 0xFF),
            static_cast<uint8_t>((multiplier >> 8) & 0xFF),
            static_cast<uint8_t>((multiplier >> 16) & 0xFF),
            static_cast<uint8_t>((multiplier >> 24) & 0xFF),
            0x81, 0xC7,
            static_cast<uint8_t>(addend & 0xFF),
            static_cast<uint8_t>((addend >> 8) & 0xFF),
            static_cast<uint8_t>((addend >> 16) & 0xFF),
            static_cast<uint8_t>((addend >> 24) & 0xFF),
            0x89, 0xF8,
            0xC3
        };
        size_t len = sizeof(code);
#elif defined(ARCH_AARCH64)
        const uint32_t imm_mul = static_cast<uint32_t>(multiplier) & 0xFFFF;
        const uint32_t imm_add = static_cast<uint32_t>(addend) & 0xFFFF;

        const uint32_t code[] = {
            0x52800000 | (imm_mul << 5) | 1,
            0x1B017C00,
            0x52800000 | (imm_add << 5) | 1,
            0x0B010000,
            0xD65F03C0
        };
        size_t len = sizeof(code);
#endif

        if (len > span.size()) {
            return std::unexpected("Розмір виділеного буфера менший за довжину коду");
        }

        std::memcpy(span.data(), code, len);
        mem.set_code_length(len);

        auto prot_res = mem.set_protection(JitMemoryBlock::Protection::ReadExecute);
        if (!prot_res) return prot_res;

        mem.sync_cache();
        return {};
    }

    static std::expected<void, std::string> patch_multiplier(JitMemoryBlock& mem,
                                                            int32_t new_multiplier) {
        auto prot_rw = mem.set_protection(JitMemoryBlock::Protection::ReadWrite);
        if (!prot_rw) return prot_rw;

        auto span = mem.as_writable_span();
#if defined(ARCH_X86_64)
        span[2] = static_cast<uint8_t>(new_multiplier & 0xFF);
        span[3] = static_cast<uint8_t>((new_multiplier >> 8) & 0xFF);
        span[4] = static_cast<uint8_t>((new_multiplier >> 16) & 0xFF);
        span[5] = static_cast<uint8_t>((new_multiplier >> 24) & 0xFF);
#elif defined(ARCH_AARCH64)
        uint32_t* patch_ptr = reinterpret_cast<uint32_t*>(span.data());
        uint32_t imm = static_cast<uint32_t>(new_multiplier) & 0xFFFF;
        patch_ptr[0] = 0x52800000 | (imm << 5) | 1;
#endif

        auto prot_rx = mem.set_protection(JitMemoryBlock::Protection::ReadExecute);
        if (!prot_rx) return prot_rx;

        mem.sync_cache();
        return {};
    }
};

int main() {
    auto mem_alloc = JitMemoryBlock::allocate(4096);
    if (!mem_alloc) {
        std::cerr << "Помилка виділення пам'яті: " << mem_alloc.error() << '\n';
        return EXIT_FAILURE;
    }

    auto& jit_mem = *mem_alloc;

    std::cout << "1. C++ JIT: компіляція лінійної функції f(x) = x * 10 + 7\n";
    auto comp_res = LinearJitCompiler::compile(jit_mem, 10, 7);
    if (!comp_res) {
        std::cerr << "Помилка компіляції коду: " << comp_res.error() << '\n';
        return EXIT_FAILURE;
    }

    auto func = jit_mem.get_entry_point<LinearJitCompiler::FuncType>();
    int32_t x = 5;
    int32_t res1 = func(x);
    std::cout << "   Результат f(" << x << ") = " << res1 << " (очікувано: 57)\n";

    std::cout << "2. C++ JIT: гаряче латання коефіцієнта f(x) = x * 100 + 7\n";
    auto patch_res = LinearJitCompiler::patch_multiplier(jit_mem, 100);
    if (!patch_res) {
        std::cerr << "Помилка модифікації інструкцій: " << patch_res.error() << '\n';
        return EXIT_FAILURE;
    }

    int32_t res2 = func(x);
    std::cout << "   Результат f(" << x << ") після оновлення = " << res2 << " (очікувано: 507)\n";

    std::cout << "3. Пам'ять гарантовано звільняється автоматичним деструктором RAII.\n";
    return EXIT_SUCCESS;
}
```
:::

---

## 4. Глибокий аналіз мікроархітектурних пасток у реальному середовищі

### Пастка 1: Виконання старого коду через відсутність синхронізації I-Cache на ARM64
Якщо з наведеного вище коду повністю видалити виклик `__builtin___clear_cache` або виклик `mem.sync_cache()`, програма на архітектурі x86-64 продовжить успішно працювати завдяки апаратній схемі снупінгу. 

Проте на пристроях з процесорами ARM64 (наприклад, Raspberry Pi 4/5, серверах AWS Graviton або смартфонах на базі Android) результат виконання функції `func(input)` стане непередбачуваним:
1. Процесор виконає попередній стан кеш-лінії I-Cache (якщо за цією віртуальною адресою раніше вже виконувався код іншої підпрограми).
2. Якщо пам'ять була свіжовиділеною і заповненою нулями, конвеєр вибірки I-Cache зчитає опкод `0x00000000` (недійсна інструкція в ARM64), що призведе до негайного аварійного завершення програми сигналом `SIGILL` (Illegal Instruction).
3. Якщо код зазнав гарячого латання (заміна множника з `10` на `100`), виклик функції `func(5)` поверне старе значення `57` замість `507`, оскільки модифіковані байти збереглися лише в L1 D-Cache, тоді як ядро продовжить зчитувати старий опкод із L1 I-Cache.

### Пастка 2: Блокування виконання при суворому захисті `W^X`
Спроба спростити код шляхом одноразового виділення пам'яті з одночасними правами на запис і виконання через виклик `mmap(NULL, 4096, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_ANONYMOUS | MAP_PRIVATE, -1, 0)` завершиться аварійною відмовою на сучасних захищених операційних системах:
* На OpenBSD ядро негайно поверне помилку `MAP_FAILED` із кодом `ENOMEM` або `EPERM`.
* На дистрибутивах Linux з активним модулем безпеки SELinux або PaX/Grsecurity системний виклик буде заблокований правилом `deny_execmem`.
* На macOS для процесорів Apple Silicon виклик дозволений лише за наявності прапорця `MAP_JIT` та підписання бінарного файлу спеціальним дозволом (Entitlement `com.apple.security.cs.allow-jit`), а сам процес зобов'язаний динамічно перемикати права потоку через виклик `pthread_jit_write_protect_np`.

### Пастка 3: Багатопотоковий стан перегонів (Multithreaded Race Conditions)
У багатопотокових високонавантажених JIT-рушіях (наприклад, фоновому потоці компілятора V8 Turbofan або C2-компіляторі HotSpot) тимчасове переведення всієї сторінки у стан `PROT_READ | PROT_WRITE` під час оновлення однієї функції є неприпустимим: якщо робочий потік іншого ядра спробує виконати будь-яку сусідню функцію, розташовану на тій самій 4-кілобайтній сторінці, він отримає виключення `SIGSEGV` через відсутність біта `X` у таблиці сторінок.

Для вирішення цієї проблеми у промислових рушіях застосовують архітектуру **подвійного відображення (Dual Mapping)**:
1. Створюється спільний дескриптор анонімної пам'яті в спільній пам'яті (через системний виклик `memfd_create` на Linux або `shm_open` на POSIX).
2. За допомогою двох окремих викликів `mmap` один і той самий фізичний блок пам'яті відображається у дві різні віртуальні адреси:
   * Віртуальна адреса `V_write` мапується з правами `PROT_READ | PROT_WRITE`.
   * Віртуальна адреса `V_exec` мапується з правами `PROT_READ | PROT_EXEC`.
3. Потік компілятора записує машинні інструкції за адресою `V_write`, виконує операції скидання кешу, а всі робочі потоки безперервно й безпечно виконують код за адресою `V_exec` без жодного виклику `mprotect`.

---

## 5. Покрокове простеження та налагодження JIT-коду в GDB

При роботі з динамічно згенерованим машинним кодом звичайні інструменти статичного налагодження стикаються з відсутністю налагоджувальних символів (DWARF) та таблиць розкручування стека (CFI/Unwind Info). Розробник змушений безпосередньо контролювати стан регістрів, таблиці сторінок та дизасемблерний лістинг за адресою виконання.

### Крок 1: Встановлення апаратної точки зупину
Оскільки пам'ять виділяється динамічно, встановити точку зупину за іменем функції у вихідному файлі неможливо. У налагоджувачі GDB слід спочатку зупинити програму після повернення з функції `jit_alloc` або `jit_finalize` та отримати віртуальну адресу буфера `jit.buffer` (наприклад, `0x7ffff7fc0000`):

```
(gdb) break main
(gdb) run
(gdb) next 5
(gdb) print jit.buffer
$1 = (uint8_t *) 0x7ffff7fc0000
(gdb) hbreak *0x7ffff7fc0000
```
Команда `hbreak` встановлює апаратну точку зупину в регістрах налагодження процесора (`DR0`–`DR3` на x86-64), що дозволяє зупинити процесор у момент передачі керування на першу інструкцію динамічного блоку.

### Крок 2: Інспекція згенерованого машинного коду
Після зупинки процесора на точці входу можна перевірити стан інструкцій у пам'яті:

```
(gdb) continue
Continuing.
Breakpoint 1, 0x00007ffff7fc0000 in ?? ()
(gdb) x/5i $pc
=> 0x7ffff7fc0000:    imul   $0xa,%edi,%edi
   0x7ffff7fc0006:    add    $0x7,%edi
   0x7ffff7fc000c:    mov    %edi,%eax
   0x7ffff7fc000e:    ret
   0x7ffff7fc000f:    add    %al,(%rax)
```

Дизасемблер підтверджує, що опкоди `0x69 0xFF 0x0A 0x00 0x00 0x00` успішно розпізнаються процесором як команда `imul $10, %edi, %edi`, а константа додавання дорівнює `7`.

### Крок 3: Перевірка карти пам'яті та бітів захисту
У консолі операційної системи можна переглянути стан прав доступу виділеного блоку у псевдофайловій системі `procfs`:

```bash
cat /proc/$(pidof jit_trampoline)/maps | grep 7ffff7fc0000
```
Вивід показує перехід прав після виклику `mprotect`:
```
7ffff7fc0000-7ffff7fc1000 r-xp 00000000 00:00 0    [anon]
```
Прапорці `r-xp` підтверджують, що сторінка перебуває в режимі `Read + Execute` без права запису, що повністю задовольняє вимоги системної безпеки.

### Крок 4: Перевірка після гарячого латання
Після виконання кроку `jit_patch_multiplier` повторна інспекція інструкцій у GDB показує оновлений машинний код:

```
(gdb) x/5i 0x7ffff7fc0000
=> 0x7ffff7fc0000:    imul   $0x64,%edi,%edi
   0x7ffff7fc0006:    add    $0x7,%edi
   0x7ffff7fc000c:    mov    %edi,%eax
   0x7ffff7fc000e:    ret
```
Константа `0x64` (100 у десятковій системі) успішно замінила попереднє значення `0x0A`, а виклик `__builtin___clear_cache` гарантував, що конвеєр вибірки команд процесора обере саме нове значення без використання застарілих кешованих даних.

---

## 6. Продуктивність та оптимізація викликів у промислових рушіях

У промислових середовищах виконання частота створення та оновлення коду може досягати десятків тисяч функцій на секунду. Якщо на кожну згенеровану функцію викликати системний виклик `mprotect` і повний цикл інструкцій обслуговування кешу, накладні витрати на перемикання контексту ядра (Syscall Overhead) і скидання буферів TLB (Translation Lookaside Buffer) перевищать виграш від самої JIT-компіляції.

### Ціна системних викликів та перемикання прав
Зміна прав доступу сторінки через `mprotect` є однією з найдорожчих операцій в операційній системі:
1. **Зміна записів у таблиці сторінок (PTE):** ядро повинно знайти запис дескриптора віртуальної пам'яті (VMA), перевірити права процесу та оновити прапорці доступу в апаратних багаторівневих таблицях сторінок (Page Tables).
2. **Інвалідація буфера трансляції адрес (TLB Shootdown):** оскільки старі записи про права сторінки закешовані в апаратному буфері TLB кожного ядра процесора, ядро ОС надсилає міжпроцесорне переривання IPI всім іншим ядрам системи для примусового скидання відповідних записів TLB (інструкція `INVLPG` на x86).
3. **Загальна затримка:** виклик `mprotect` займає від 1500 до 8000 тактів процесора залежно від кількості ядер у системі.

### Амортизація та блокове виділення пам'яті (Code Slabs)
Щоб мінімізувати накладні витрати, сучасні віртуальні машини (зокрема Java HotSpot CodeCache та V8 Isolate Code Space) використовують стратегію **блокового розподілу коду**:
* Пам'ять виділяється великими неперервними блоками (Slabs) розміром від 64 КБ до 2 МБ (з використанням Huge Pages для зменшення кількості промахів TLB).
* Компілятор накопичує згенеровані тіла сотень функцій у локальному буфері пам'яті.
* Зміна прав через `mprotect` або запис через подвійне відображення здійснюється одноразово для всього пулу функцій.
* Інструкції скидання кешу `__builtin___clear_cache` викликаються один раз для всього діапазону адресної арени, суттєво амортизуючи вартість бар'єрів `DSB` та `ISB`.

### Патерн поліморфних вбудованих кешів (Polymorphic Inline Caching)
У динамічних мовах програмування звернення до поля об'єкта `obj.x` спочатку компілюється як виклик універсальної підпрограми пошуку за хеш-таблицею властивостей. Коли JIT-компілятор фіксує, що через точку виклику проходять об'єкти однієї фіксованої структури (Shape/Map), він виконує гаряче латання самої інструкції виклику (Callsite Patching):
1. Прямий виклик змінюється на компактний трамплін, який порівнює покажчик на форму об'єкта з зашитою константою.
2. Якщо форма збігається, здійснюється пряме читання зі зміщенням замість виклику підпрограми.
3. Якщо на ту саму інструкцію приходить об'єкт другої форми, трамплін динамічно перезаписується на бінарне дерево перевірок або мегаморфну таблицю переходів.

### Механізм деоптимізації (Deoptimization Trampolines)
Коли спекулятивне припущення високооптимізованого коду порушується (наприклад, у математичну операцію передано об'єкт неочікуваного типу чи відбулося переповнення цілого числа), JIT-рушій не може продовжувати виконання поточного бінарного блоку. Компілятор активує так звану пастку деоптимізації (Uncommon Trap):
1. Адреса повернення або точка розгалуження в машинному коді динамічно підміняється на адресу глобального деоптимізаційного трампліна.
2. Трамплін зберігає поточний стан усіх фізичних регістрів процесора (Register Spill) у системну структуру кадрів.
3. Спеціальний модуль відновлення стану (Frame Reconstructor) реконструює віртуальні стекові кадри інтерпретатора з фізичного кадру скомпільованого JIT-коду.
4. Керування безшовно повертається в інтерпретатор байт-коду з точного місця виникнення несумісності.

Усі ці промислові патерни — від інлайн-кешів до деоптимізації — спираються на фундамент атомарного перезапису інструкцій та обов'язкової мікроархітектурної синхронізації кешів даних та інструкцій.
