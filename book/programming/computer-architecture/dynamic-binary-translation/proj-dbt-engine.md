# ⚙️ Практична реалізація DBT-рушія: від JIT-генератора до Block Chaining

Створення динамічного двійкового транслятора (англ. *dynamic binary translation*, DBT) вимагає об'єднання кількох рівнів системного програмування: низькорівневого керування віртуальною пам'яттю операційної системи, побайтового кодування машинних інструкцій цільового процесора та динамічної модифікації коду безпосередньо під час виконання.

Головна мета динамічної трансляції полягає в подоланні прірви між гостьовим кодом (Guest ISA) та фізичним процесором (Host ISA) без катастрофічного падіння швидкодії, властивого класичним інтерпретаторам. Інтерпретатор змушений для кожної інструкції виконувати цикл вибірки, декодування через довгий оператор `switch` та програмне оновлення віртуального стану процесора. На цей диспетчерський оверхед витрачається від 40 до 120 тактів фізичного процесора на кожну гостьову інструкцію.

Динамічний двійковий транслятор кардинально змінює цей підхід:
1. Він зчитує потік гостьових байтів цілими базовими блоками (послідовностями інструкцій до першого розгалуження).
2. Транслює весь блок у нативні машинні інструкції цільового кристала за один прохід.
3. Записує скомпільований блок у виконуваний буфер пам'яті — кеш коду (*Code Cache*).
4. Зшиває згенеровані блоки між собою прямими переходами (*Direct Block Chaining*), дозволяючи процесору виконувати перекладений код на повній апаратній швидкості без повернення в керівний диспетчер.

## Архітектура мінімального транслятора

Щоб простежити роботу механізму без зайвого шуму сотень інструкцій та префіксів промислового x86, ми спроєктуємо цілісний DBT-рушій для компактної 32-розрядної гостьової регістрової машини **ToyVM** і транслюватимемо її код у нативні 64-розрядні інструкції **x86-64**.

### Гостьова архітектура (Guest ISA)
Гостьова машина ToyVM побудована за канонічною регістровою схемою RISC і містить:
* Чотири 32-розрядні регістри загального призначення: `R0`, `R1`, `R2`, `R3`;
* 32-розрядний лічильник команд: `PC` (Program Counter);
* Один прапорець нуля: `ZF` (Zero Flag — встановлюється в `1`, якщо результат останньої арифметичної операції чи порівняння дорівнює нулю, і в `0` в іншому разі);
* Фіксоване 4-байтне бінарне кодування інструкцій, зручне для швидкого декодування.

Формат бінарного слова інструкції:
```
+------------+------------+------------+------------+
| Байт 0     | Байт 1     | Байт 2     | Байт 3     |
| Опкод (Op) | Регістр D  | Операнд 1  | Операнд 2  |
+------------+------------+------------+------------+
```

| Опкод | Мнемоніка | Формат | Семантика |
| :--- | :--- | :--- | :--- |
| `0x01` | `MOV_IMM` | `MOV_IMM Rd, imm16` | Запис 16-бітної константи в регістр: `Rd = imm16` |
| `0x02` | `ADD` | `ADD Rd, Rs` | Додавання регістрів: `Rd = Rd + Rs; ZF = (Rd == 0)` |
| `0x03` | `SUB` | `SUB Rd, Rs` | Віднімання регістрів: `Rd = Rd - Rs; ZF = (Rd == 0)` |
| `0x04` | `CMP_IMM` | `CMP_IMM Rd, imm16` | Порівняння з константою: `ZF = (Rd == imm16)` |
| `0x05` | `JMP` | `JMP target_pc` | Безумовний стрибок: `PC = target_pc` |
| `0x06` | `JZ` | `JZ target_pc` | Умовний стрибок: `if (ZF == 1) PC = target_pc` |
| `0xFF` | `HALT` | `HALT` | Зупинка виконання програми |

### Структура віртуального контексту CPU
Віртуальний стан процесора описується структурою пам'яті, вказівник на яку передається в згенерований нативний код як перший параметр функції.

Під час проєктування транслятора постає вибір: відобразити віртуальні регістри гостя на фізичні регістри процесора хоста чи тримати їх у структурі контексту в оперативній пам'яті. У повноцінних оптимізуючих JIT-компіляторах застосовують глобальний розподіл регістрів (*Register Allocation*). Проте для базового транслятора значно надійнішим і простішим є закріплення одного фізичного регістра хоста (наприклад, `rdi` у конвенції System V AMD64 ABI або `rcx` у Microsoft x64 ABI) як базового вказівника на контекст `GuestContext`. Усі звернення до гостьових регістрів транслюються в інструкції непрямої адресації зі зміщенням: `mov eax, [rdi + offset]`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct {
    uint32_t regs[4]; // R0, R1, R2, R3
    uint32_t pc;      // Guest Program Counter
    uint32_t zf;      // Zero Flag (1 або 0)
    bool     halted;  // Прапорець завершення роботи
} GuestContext;
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>

struct GuestContext {
    std::array<uint32_t, 4> regs{0, 0, 0, 0}; // R0, R1, R2, R3
    uint32_t                pc{0};            // Guest Program Counter
    uint32_t                zf{0};            // Zero Flag (1 або 0)
    bool                    halted{false};    // Прапорець завершення роботи
};
```
:::

## Керування виконуваною пам'яттю: Code Cache

Сучасні операційні системи суворо контролюють захист сторінок віртуальної пам'яті на апаратному рівні за допомогою таблиць сторінок MMU. Звичайна динамічна пам'ять, виділена стандартними функціями `malloc` чи оператором `new`, розміщується на сторінках із правами читання й запису (`PROT_READ | PROT_WRITE`), але з вимкненим бітом виконання (`PROT_EXEC` або `PAGE_NOACCESS`). Ця політика безпеки, відома як **W^X** (англ. *Write XOR Execute* — пиши або виконуй, але ніколи одночасно), запобігає виконанню шкідливого коду, записаного через переповнення буфера на купі або в стеку.

Якщо процесор спробує виконати інструкцію за адресою сторінки, де відсутній дозвіл на виконання, апаратний блок MMU згенерує виключення `Page Fault`, і операційна система аварійно зупинить процес (сигнал `SIGSEGV` в Linux/macOS або виключення `STATUS_ACCESS_VIOLATION` у Windows).

Для розміщення згенерованого нативного машинного коду транслятор виділяє спеціальний анонімний буфер пам'яті через системні виклики `mmap` у POSIX-системах або `VirtualAlloc` у Windows, явно запитуючи права читання, запису та виконання (`PROT_READ | PROT_WRITE | PROT_EXEC` або `PAGE_EXECUTE_READWRITE`).

На сучасних системах macOS Apple Silicon з увімкненим Hardened Runtime політика W^X контролюється ще суворіше: сторінка може мати комбіновані права `MAP_JIT`, але потік зобов'язаний явно перемикати права між записом і виконанням через виклик `pthread_jit_write_protect_np()`. 

Для керування розміром та фрагментацією кешу коду промислові DBT застосовують дві стратегії:
1. **Лінійний буфер зі скиданням (Flush on Overflow):** пам'ять виділяється простим зсувом вказівника (*Bump Allocator*). Коли буфер заповнюється, транслятор повністю очищає кеш, скидає всі таблиці трансляцій і починає компіляцію з чистого аркуша. Це найпростіша і найшвидша стратегія для коротких задач.
2. **Кільцевий буфер (Ring Buffer Code Cache):** пам'ять розглядається як циклічна черга. Коли вільне місце закінчується, транслятор перезаписує найстаріші базові блоки, обов'язково розриваючи всі вхідні зв'язки зшивання.

Для нашого рушія ми реалізуємо клас `ExecutableBuffer`, що виділяє суміжний блок пам'яті та забезпечує захищене виділення байтів під нові блоки.

:::tabs
```c
#include <stdlib.h>
#include <stdio.h>

#if defined(_WIN32)
#include <windows.h>
#else
#include <sys/mman.h>
#include <unistd.h>
#endif

typedef struct {
    uint8_t* buffer;
    size_t   capacity;
    size_t   size;
} ExecutableBuffer;

ExecutableBuffer* exec_buffer_create(size_t capacity) {
    ExecutableBuffer* eb = (ExecutableBuffer*)malloc(sizeof(ExecutableBuffer));
    if (!eb) return NULL;

    eb->capacity = capacity;
    eb->size = 0;

#if defined(_WIN32)
    eb->buffer = (uint8_t*)VirtualAlloc(NULL, capacity, 
                                        MEM_COMMIT | MEM_RESERVE, 
                                        PAGE_EXECUTE_READWRITE);
#else
    eb->buffer = (uint8_t*)mmap(NULL, capacity, 
                                PROT_READ | PROT_WRITE | PROT_EXEC, 
                                MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
    if (eb->buffer == MAP_FAILED) {
        free(eb);
        return NULL;
    }
#endif
    return eb;
}

void exec_buffer_free(ExecutableBuffer* eb) {
    if (!eb) return;
#if defined(_WIN32)
    VirtualFree(eb->buffer, 0, MEM_RELEASE);
#else
    munmap(eb->buffer, eb->capacity);
#endif
    free(eb);
}

uint8_t* exec_buffer_alloc_block(ExecutableBuffer* eb, size_t block_bytes) {
    if (eb->size + block_bytes > eb->capacity) {
        return NULL; // Переповнення буфера кешу коду
    }
    uint8_t* ptr = eb->buffer + eb->size;
    eb->size += block_bytes;
    return ptr;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <memory>
#include <stdexcept>
#include <span>

#if defined(_WIN32)
#include <windows.h>
#else
#include <sys/mman.h>
#include <unistd.h>
#endif

class ExecutableBuffer {
public:
    explicit ExecutableBuffer(std::size_t capacity)
        : capacity_(capacity), size_(0), buffer_(nullptr) {
#if defined(_WIN32)
        buffer_ = static_cast<uint8_t*>(VirtualAlloc(
            nullptr, capacity_, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE));
        if (!buffer_) {
            throw std::runtime_error("VirtualAlloc failed to allocate executable memory");
        }
#else
        void* ptr = mmap(nullptr, capacity_, 
                         PROT_READ | PROT_WRITE | PROT_EXEC, 
                         MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
        if (ptr == MAP_FAILED) {
            throw std::runtime_error("mmap failed to allocate executable memory");
        }
        buffer_ = static_cast<uint8_t*>(ptr);
#endif
    }

    ~ExecutableBuffer() noexcept {
        if (buffer_) {
#if defined(_WIN32)
            VirtualFree(buffer_, 0, MEM_RELEASE);
#else
            munmap(buffer_, capacity_);
#endif
        }
    }

    ExecutableBuffer(const ExecutableBuffer&) = delete;
    ExecutableBuffer& operator=(const ExecutableBuffer&) = delete;

    ExecutableBuffer(ExecutableBuffer&& other) noexcept
        : capacity_(other.capacity_), size_(other.size_), buffer_(other.buffer_) {
        other.buffer_ = nullptr;
        other.size_ = 0;
    }

    uint8_t* allocate_block(std::size_t bytes) {
        if (size_ + bytes > capacity_) {
            throw std::runtime_error("Code cache memory overflow");
        }
        uint8_t* ptr = buffer_ + size_;
        size_ += bytes;
        return ptr;
    }

    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] std::size_t capacity() const noexcept { return capacity_; }

private:
    std::size_t capacity_;
    std::size_t size_;
    uint8_t*    buffer_;
};
```
:::

## JIT-генератор нативних інструкцій x86-64

Кодогенератор (*JIT Emitter*) перетворює гостьовий базовий блок у послідовність бінарних байтів, що утворюють валідні нативні інструкції архітектури x86-64.

### Побайтове кодування інструкцій x86-64
В архітектурі x86-64 інструкції мають змінну довжину. Розглянемо точну структуру байтів, які ми генеруємо для кожної операції:

1. **`mov dword ptr [rdi + offset], imm32`** (запис 32-розрядної константи в пам'ять за вказівником):
   * Байт опкоду: `0xC7` (MOV r/m32, imm32);
   * Байт ModR/M: `0x47` (двійкове `01 000 111` — адресація `[rdi + disp8]`);
   * Байт зміщення: `offset` (зміщення поля регістра в структурі `GuestContext`);
   * 4 байти безпосереднього значення `imm32` у форматі little-endian.
   * Разом: 7 байтів.

2. **`mov eax, [rdi + rs_offset]`** (завантаження гостьового регістра у фізичний акумулятор):
   * Опкод: `0x8B 0x47 <rs_offset>`. Разом: 3 байти.

3. **`add [rdi + rd_offset], eax`** (додавання акумулятора до гостьового регістра в пам'яті):
   * Опкод: `0x01 0x47 <rd_offset>`. Разом: 3 байти.

4. **`sub [rdi + rd_offset], eax`** (віднімання значення з регістра):
   * Опкод: `0x29 0x47 <rd_offset>`. Разом: 3 байти.

5. **`cmp [rdi + rd_offset], imm32`** (порівняння регістра з константою):
   * Опкод: `0x81 0x7F <rd_offset> <imm32 (4 байти)>`. Разом: 7 байтів.

6. **Оновлення прапорця `ZF`:**
   Після арифметичної операції чи порівняння апаратні прапорці процесора хоста містять точний результат операції. Щоб зберегти значення прапорця нуля у віртуальний контекст:
   * `sete al` (`0x0F 0x94 0xC0`) — записує `1` у регістр `al`, якщо прапорець `ZF` встановлено, або `0` в іншому разі;
   * `movzx eax, al` (`0x0F 0xB6 0xC0`) — розширює байт нулями до 32-бітного слова `eax`;
   * `mov [rdi + ZF_OFFSET], eax` (`0x89 0x47 <ZF_OFFSET>`) — зберігає результат у структуру контексту.

7. **`jmp rel32`** (прямий відносний перехід):
   * Опкод: `0xE9 <4 байти signed int32 relative offset>`. Разом: 5 байтів.

8. **`je rel32`** (умовний відносний перехід):
   * Опкод: `0x0F 0x84 <4 байти signed int32 relative offset>`. Разом: 6 байтів.

9. **`ret`** (повернення з нативної функції блоку):
   * Опкод: `0xC3`. Разом: 1 байт.

### Математика відносного зміщення (Relative Jump Offset)
В архітектурі x86-64 операнд відносного стрибка `rel32` відлічується не від початку інструкції переходу, а від адреси **наступної** за переходом інструкції (тобто від кінця самого переходу).

Якщо інструкція безумовного переходу `jmp rel32` (довжиною 5 байтів) починається за адресою `src_addr`, а цільовий блок розташований за адресою `target_addr`, то відносне зміщення розраховується за формулою:

```
offset = target_addr - (src_addr + 5)
```

Для інструкції умовного переходу `je rel32` (довжиною 6 байтів `0x0F 0x84 xx xx xx xx`):

```
offset = target_addr - (src_addr + 6)
```

Ця відносна арифметика дозволяє нативному коду залишатися позиційно-незалежним у межах 32-розрядного адресного вікна (±2 Гігабайти від точки стрибка).

Нижче наведено програмний клас емітера інструкцій x86-64.

:::tabs
```c
#include <string.h>

#define REG_OFFSET(idx) ((uint8_t)((idx) * sizeof(uint32_t)))
#define PC_OFFSET       ((uint8_t)(offsetof(GuestContext, pc)))
#define ZF_OFFSET       ((uint8_t)(offsetof(GuestContext, zf)))
#define HALT_OFFSET     ((uint8_t)(offsetof(GuestContext, halted)))

typedef struct {
    uint8_t* code;
    size_t   size;
} CodeEmitter;

static void emit_byte(CodeEmitter* e, uint8_t b) {
    e->code[e->size++] = b;
}

static void emit_u32(CodeEmitter* e, uint32_t val) {
    memcpy(e->code + e->size, &val, sizeof(uint32_t));
    e->size += sizeof(uint32_t);
}

// Запис константи: mov [rdi + reg_off], imm32
static void emit_mov_imm(CodeEmitter* e, uint8_t reg_idx, uint32_t imm) {
    emit_byte(e, 0xC7); // MOV r/m32, imm32
    emit_byte(e, 0x47); // ModR/M: [rdi + disp8]
    emit_byte(e, REG_OFFSET(reg_idx));
    emit_u32(e, imm);
}

// Додавання: mov eax, [rdi + rs]; add [rdi + rd], eax
static void emit_add(CodeEmitter* e, uint8_t rd, uint8_t rs) {
    emit_byte(e, 0x8B); emit_byte(e, 0x47); emit_byte(e, REG_OFFSET(rs));
    emit_byte(e, 0x01); emit_byte(e, 0x47); emit_byte(e, REG_OFFSET(rd));
    emit_byte(e, 0x0F); emit_byte(e, 0x94); emit_byte(e, 0xC0); // sete al
    emit_byte(e, 0x0F); emit_byte(e, 0xB6); emit_byte(e, 0xC0); // movzx eax, al
    emit_byte(e, 0x89); emit_byte(e, 0x47); emit_byte(e, ZF_OFFSET);
}

// Віднімання: mov eax, [rdi + rs]; sub [rdi + rd], eax
static void emit_sub(CodeEmitter* e, uint8_t rd, uint8_t rs) {
    emit_byte(e, 0x8B); emit_byte(e, 0x47); emit_byte(e, REG_OFFSET(rs));
    emit_byte(e, 0x29); emit_byte(e, 0x47); emit_byte(e, REG_OFFSET(rd));
    emit_byte(e, 0x0F); emit_byte(e, 0x94); emit_byte(e, 0xC0); // sete al
    emit_byte(e, 0x0F); emit_byte(e, 0xB6); emit_byte(e, 0xC0); // movzx eax, al
    emit_byte(e, 0x89); emit_byte(e, 0x47); emit_byte(e, ZF_OFFSET);
}

// Порівняння: cmp [rdi + rd], imm32
static void emit_cmp_imm(CodeEmitter* e, uint8_t rd, uint32_t imm) {
    emit_byte(e, 0x81); emit_byte(e, 0x7F); emit_byte(e, REG_OFFSET(rd));
    emit_u32(e, imm);
    emit_byte(e, 0x0F); emit_byte(e, 0x94); emit_byte(e, 0xC0); // sete al
    emit_byte(e, 0x0F); emit_byte(e, 0xB6); emit_byte(e, 0xC0); // movzx eax, al
    emit_byte(e, 0x89); emit_byte(e, 0x47); emit_byte(e, ZF_OFFSET);
}

// Завершення: mov byte ptr [rdi + HALT_OFFSET], 1; ret
static void emit_halt(CodeEmitter* e) {
    emit_byte(e, 0xC6); emit_byte(e, 0x47); emit_byte(e, HALT_OFFSET); emit_byte(e, 0x01);
    emit_byte(e, 0xC3); // ret
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <vector>
#include <cstring>

struct OffsetHelper {
    static constexpr uint8_t reg(uint8_t idx) noexcept {
        return static_cast<uint8_t>(idx * sizeof(uint32_t));
    }
    static constexpr uint8_t pc() noexcept {
        return static_cast<uint8_t>(offsetof(GuestContext, pc));
    }
    static constexpr uint8_t zf() noexcept {
        return static_cast<uint8_t>(offsetof(GuestContext, zf));
    }
    static constexpr uint8_t halt() noexcept {
        return static_cast<uint8_t>(offsetof(GuestContext, halted));
    }
};

class CodeEmitter {
public:
    explicit CodeEmitter(uint8_t* output_buffer) 
        : buffer_(output_buffer), size_(0) {}

    void emit_byte(uint8_t b) {
        buffer_[size_++] = b;
    }

    void emit_u32(uint32_t val) {
        std::memcpy(buffer_ + size_, &val, sizeof(uint32_t));
        size_ += sizeof(uint32_t);
    }

    void emit_mov_imm(uint8_t reg_idx, uint32_t imm) {
        emit_byte(0xC7); // MOV r/m32, imm32
        emit_byte(0x47); // [rdi + disp8]
        emit_byte(OffsetHelper::reg(reg_idx));
        emit_u32(imm);
    }

    void emit_add(uint8_t rd, uint8_t rs) {
        emit_byte(0x8B); emit_byte(0x47); emit_byte(OffsetHelper::reg(rs)); // mov eax, [rdi + rs]
        emit_byte(0x01); emit_byte(0x47); emit_byte(OffsetHelper::reg(rd)); // add [rdi + rd], eax
        emit_update_zf();
    }

    void emit_sub(uint8_t rd, uint8_t rs) {
        emit_byte(0x8B); emit_byte(0x47); emit_byte(OffsetHelper::reg(rs)); // mov eax, [rdi + rs]
        emit_byte(0x29); emit_byte(0x47); emit_byte(OffsetHelper::reg(rd)); // sub [rdi + rd], eax
        emit_update_zf();
    }

    void emit_cmp_imm(uint8_t rd, uint32_t imm) {
        emit_byte(0x81); emit_byte(0x7F); emit_byte(OffsetHelper::reg(rd)); // cmp [rdi + rd], imm
        emit_u32(imm);
        emit_update_zf();
    }

    void emit_halt() {
        emit_byte(0xC6); emit_byte(0x47); emit_byte(OffsetHelper::halt()); emit_byte(0x01);
        emit_byte(0xC3); // ret
    }

    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] uint8_t* buffer() const noexcept { return buffer_; }

private:
    void emit_update_zf() {
        emit_byte(0x0F); emit_byte(0x94); emit_byte(0xC0); // sete al
        emit_byte(0x0F); emit_byte(0xB6); emit_byte(0xC0); // movzx eax, al
        emit_byte(0x89); emit_byte(0x47); emit_byte(OffsetHelper::zf()); // mov [rdi + zf], eax
    }

    uint8_t*    buffer_;
    std::size_t size_;
};
```
:::

## Механізм Direct Block Chaining

У базовому трансляторі без зшивання кожен базовий блок наприкінці зберігає новий `Guest PC` у пам'ять і повертає керування інструкцією `ret` у центральний диспетчер. Диспетчер бере цей `PC`, обчислює хеш-функцію, шукає відповідний блок у хеш-таблиці та виконує непрямий виклик функції через вказівник.

Такий цикл повернення коштує дорого:
* Збереження та відновлення регістрів конвенції викликів C ABI (наприклад, `rbx`, `rsp`, `rbp`, `r12`–`r15`);
* Промах апаратного блоку передбачення непрямих переходів (англ. *Branch Target Buffer*, BTB), оскільки адреса стрибка в диспетчері постійно змінюється від блоку до блоку;
* Накладні витрати на пошук у таблиці трансляцій.

Сумарно кожне повернення в диспетчер спалює від 40 до 70 машинних тактів процесора на кожні 4–6 корисних інструкцій.

### Архітектура трамплінів (Stubs / Trampolines)
Для усунення повернення в диспетчер застосовують **пряме зшивання блоків** (Direct Block Chaining). Механізм працює так:

1. Коли базовий блок тільки компілюється, цільові блоки, на які він посилається, ще можуть бути не скомпільовані (або взагалі невідомі).
2. Тому транслятор генерує наприкінці блоку відносний перехід не на пряму адресу цілі, а на локальну службову заглушку — **трамплін** (*Trampoline*).
3. Трамплін містить мінімальний код: запис цільового гостьового `Guest PC` у структуру `GuestContext` та інструкцію `ret`.
4. Адреса інструкції переходу та адреса її 4-байтного поля зміщення запам'ятовуються в структурі метаданих блоку `JumpPatchInfo`.

```
[Згенерований Блок A]
    ... арифметичні інструкції блоку ...
    cmp dword ptr [rdi + zf], 1
    je  trampoline_taken       <-- 6 байтів: 0x0F 0x84 [offset_taken]
    jmp trampoline_fallthrough <-- 5 байтів: 0xE9     [offset_fall]

[Трамплін Taken]
    mov dword ptr [rdi + pc_offset], TARGET_GUEST_PC
    ret

[Трамплін Fallthrough]
    mov dword ptr [rdi + pc_offset], FALLTHROUGH_GUEST_PC
    ret
```

### Динамічний патчинг коду (Code Patching)
Коли цільовий блок `B` за адресою `TARGET_GUEST_PC` вперше викликається і компілюється в нативну пам'ять за адресою `host_addr_B`:
1. Диспетчер реєструє блок `B` у таблиці трансляцій.
2. Диспетчер переглядає всі раніше скомпільовані блоки, що мають незакриті виходи на `TARGET_GUEST_PC`.
3. Для кожного такого виходу викликається функція `patch_jump()`: вона розраховує точне відносне зміщення від інструкції переходу в блоці `A` до початку блоку `B`:
   `offset = host_addr_B - (patch_site + insn_length)`.
4. Диспетчер перезаписує 4 байти зміщення прямо в пам'яті інструкції блоку `A`.
5. Викликається системна функція синхронізації кешу інструкцій (`FlushInstructionCache` або `__builtin___clear_cache`).

Наступного разу, коли процесор дійде до кінця блоку `A`, апаратний конвеєр перейде на блок `B` за **один машинний такт** за допомогою прямого передбаченого переходу, минаючи диспетчер, хеш-таблиці та збереження стекових кадрів.

:::tabs
```c
typedef struct {
    uint32_t guest_target_pc;
    uint8_t* patch_offset_addr; // Адреса 4-байтного зміщення rel32 для патчингу
    bool     is_conditional;    // true для je (довжина 6), false для jmp (довжина 5)
} JumpPatchInfo;

typedef struct {
    uint32_t      guest_pc;
    uint8_t*      host_addr;
    size_t        host_size;
    JumpPatchInfo exits[2];
    size_t        exit_count;
} TranslationBlock;

// Патчинг переходу: запис нової відносної адреси в машинний код
static void patch_jump(const JumpPatchInfo* patch, const uint8_t* target_host_addr) {
    size_t insn_len = patch->is_conditional ? 6 : 5;
    uint8_t* insn_start = patch->patch_offset_addr - (insn_len - 4);
    int32_t rel_offset = (int32_t)(target_host_addr - (insn_start + insn_len));

    memcpy(patch->patch_offset_addr, &rel_offset, sizeof(int32_t));

#if defined(_WIN32)
    FlushInstructionCache(GetCurrentProcess(), insn_start, insn_len);
#elif defined(__GNUC__) || defined(__clang__)
    __builtin___clear_cache((char*)insn_start, (char*)insn_start + insn_len);
#endif
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <array>

#if defined(_WIN32)
#include <windows.h>
#endif

struct JumpPatchInfo {
    uint32_t guest_target_pc{0};
    uint8_t* patch_offset_addr{nullptr};
    bool     is_conditional{false};

    void apply_patch(const uint8_t* target_host_addr) const noexcept {
        const std::size_t insn_len = is_conditional ? 6 : 5;
        uint8_t* insn_start = patch_offset_addr - (insn_len - 4);
        const auto rel_offset = static_cast<int32_t>(
            target_host_addr - (insn_start + insn_len));

        std::memcpy(patch_offset_addr, &rel_offset, sizeof(int32_t));

#if defined(_WIN32)
        FlushInstructionCache(GetCurrentProcess(), insn_start, insn_len);
#elif defined(__GNUC__) || defined(__clang__)
        __builtin___clear_cache(reinterpret_cast<char*>(insn_start), 
                                reinterpret_cast<char*>(insn_start + insn_len));
#endif
    }
};

struct TranslationBlock {
    uint32_t                      guest_pc{0};
    uint8_t*                      host_addr{nullptr};
    std::size_t                   host_size{0};
    std::array<JumpPatchInfo, 2>  exits{};
    std::size_t                   exit_count{0};
};
```
:::

## Повний робочий рушій та диспетчер

Нижче наведено закінчену реалізацію транслятора разом із тестовою гостьовою програмою, що реалізує ітеративний цикл обчислення факторіалу числа $5! = 120$ на гостьовій машині ToyVM.

Гостьова програма в пам'яті:
```
PC 0: MOV_IMM R0, 5    (початкове число N = 5)
PC 1: MOV_IMM R1, 1    (акумулятор результату fact = 1)
PC 2: MOV_IMM R2, 1    (константа 1 для віднімання)
PC 3: CMP_IMM R0, 1    (перевірка умови виходу: N == 1?)
PC 4: JZ 8             (якщо N == 1, виходимо з циклу на PC 8)
PC 5: ADD R1, R1       (імітація множення/накопичення в циклі)
PC 6: SUB R0, R2       (зменшуємо лічильник: N = N - 1)
PC 7: JMP 3            (перехід на початок перевірки циклу)
PC 8: HALT             (зупинка віртуального процесора)
```

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_GUEST_CODE 64
#define MAX_BLOCKS     64

typedef void (*JitFunction)(GuestContext* ctx);

typedef struct {
    uint8_t op;
    uint8_t rd;
    uint8_t rs;
    uint8_t imm8;
    uint16_t imm16;
} GuestInsn;

typedef struct {
    GuestInsn        program[MAX_GUEST_CODE];
    size_t           program_size;
    ExecutableBuffer* exec_mem;
    TranslationBlock blocks[MAX_BLOCKS];
    size_t           block_count;
} DbtEngine;

static TranslationBlock* find_block(DbtEngine* dbt, uint32_t gpc) {
    for (size_t i = 0; i < dbt->block_count; ++i) {
        if (dbt->blocks[i].guest_pc == gpc) return &dbt->blocks[i];
    }
    return NULL;
}

static TranslationBlock* compile_block(DbtEngine* dbt, uint32_t start_pc) {
    uint8_t* code_mem = exec_buffer_alloc_block(dbt->exec_mem, 256);
    if (!code_mem) return NULL;

    CodeEmitter e = { code_mem, 0 };
    TranslationBlock* tb = &dbt->blocks[dbt->block_count++];
    tb->guest_pc = start_pc;
    tb->host_addr = code_mem;
    tb->exit_count = 0;

    uint32_t pc = start_pc;
    bool block_ended = false;

    while (pc < dbt->program_size && !block_ended) {
        GuestInsn insn = dbt->program[pc];
        switch (insn.op) {
            case 0x01: emit_mov_imm(&e, insn.rd, insn.imm16); break;
            case 0x02: emit_add(&e, insn.rd, insn.rs); break;
            case 0x03: emit_sub(&e, insn.rd, insn.rs); break;
            case 0x04: emit_cmp_imm(&e, insn.rd, insn.imm16); break;
            case 0x05: { // JMP target
                uint32_t target = insn.imm16;
                emit_byte(&e, 0xE9); // jmp rel32
                uint8_t* patch_site = e.code + e.size;
                emit_u32(&e, 0);

                // Трамплін безумовного переходу:
                uint8_t* tramp_addr = e.code + e.size;
                int32_t tramp_offset = (int32_t)(tramp_addr - (patch_site + 4));
                memcpy(patch_site, &tramp_offset, sizeof(int32_t));

                emit_byte(&e, 0xC7); emit_byte(&e, 0x47); emit_byte(&e, PC_OFFSET); emit_u32(&e, target);
                emit_byte(&e, 0xC3); // ret

                tb->exits[tb->exit_count++] = (JumpPatchInfo){ target, patch_site, false };
                block_ended = true;
                break;
            }
            case 0x06: { // JZ target
                uint32_t target_taken = insn.imm16;
                uint32_t target_fall = pc + 1;

                // Перевірка прапорця: cmp dword ptr [rdi + ZF_OFFSET], 1
                emit_byte(&e, 0x83); emit_byte(&e, 0x7F); emit_byte(&e, ZF_OFFSET); emit_byte(&e, 0x01);

                // je trampoline_taken
                emit_byte(&e, 0x0F); emit_byte(&e, 0x84);
                uint8_t* patch_taken = e.code + e.size;
                emit_u32(&e, 0);

                // jmp trampoline_fall
                emit_byte(&e, 0xE9);
                uint8_t* patch_fall = e.code + e.size;
                emit_u32(&e, 0);

                // Трамплін Taken:
                uint8_t* tramp_taken = e.code + e.size;
                int32_t off_taken = (int32_t)(tramp_taken - (patch_taken + 4));
                memcpy(patch_taken, &off_taken, sizeof(int32_t));
                emit_byte(&e, 0xC7); emit_byte(&e, 0x47); emit_byte(&e, PC_OFFSET); emit_u32(&e, target_taken);
                emit_byte(&e, 0xC3);

                // Трамплін Fallthrough:
                uint8_t* tramp_fall = e.code + e.size;
                int32_t off_fall = (int32_t)(tramp_fall - (patch_fall + 4));
                memcpy(patch_fall, &off_fall, sizeof(int32_t));
                emit_byte(&e, 0xC7); emit_byte(&e, 0x47); emit_byte(&e, PC_OFFSET); emit_u32(&e, target_fall);
                emit_byte(&e, 0xC3);

                tb->exits[tb->exit_count++] = (JumpPatchInfo){ target_taken, patch_taken, true };
                tb->exits[tb->exit_count++] = (JumpPatchInfo){ target_fall, patch_fall, false };
                block_ended = true;
                break;
            }
            case 0xFF: // HALT
                emit_halt(&e);
                block_ended = true;
                break;
        }
        pc++;
    }

    tb->host_size = e.size;

    // Зшивання: якщо попередні блоки чекали на цей блок, патчимо їх
    for (size_t i = 0; i < dbt->block_count - 1; ++i) {
        for (size_t k = 0; k < dbt->blocks[i].exit_count; ++k) {
            if (dbt->blocks[i].exits[k].guest_target_pc == start_pc) {
                patch_jump(&dbt->blocks[i].exits[k], tb->host_addr);
            }
        }
    }

    // Зшивання виходів нового блоку, якщо цілі вже є в кеші
    for (size_t k = 0; k < tb->exit_count; ++k) {
        TranslationBlock* target_tb = find_block(dbt, tb->exits[k].guest_target_pc);
        if (target_tb) {
            patch_jump(&tb->exits[k], target_tb->host_addr);
        }
    }

    return tb;
}

void dbt_run(DbtEngine* dbt, GuestContext* ctx) {
    while (!ctx->halted) {
        TranslationBlock* tb = find_block(dbt, ctx->pc);
        if (!tb) {
            tb = compile_block(dbt, ctx->pc);
            if (!tb) {
                fprintf(stderr, "Помилка JIT-компіляції блоку\n");
                break;
            }
        }

        // Прямий виклик згенерованого нативного коду
        JitFunction fn = (JitFunction)tb->host_addr;
        fn(ctx);
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <unordered_map>
#include <functional>

using JitFunction = void (*)(GuestContext*);

struct GuestInsn {
    uint8_t  op{0};
    uint8_t  rd{0};
    uint8_t  rs{0};
    uint16_t imm16{0};
};

class DbtEngine {
public:
    explicit DbtEngine(std::size_t cache_size = 1024 * 1024)
        : exec_mem_(cache_size) {}

    void load_program(std::vector<GuestInsn> prog) {
        program_ = std::move(prog);
        blocks_.clear();
        block_map_.clear();
    }

    void run(GuestContext& ctx) {
        while (!ctx.halted) {
            TranslationBlock* tb = get_or_compile_block(ctx.pc);
            if (!tb) {
                std::cerr << "Compilation failed for PC " << ctx.pc << '\n';
                break;
            }

            auto fn = reinterpret_cast<JitFunction>(tb->host_addr);
            fn(&ctx);
        }
    }

private:
    TranslationBlock* get_or_compile_block(uint32_t gpc) {
        auto it = block_map_.find(gpc);
        if (it != block_map_.end()) {
            return &blocks_[it->second];
        }
        return compile_block(gpc);
    }

    TranslationBlock* compile_block(uint32_t start_pc) {
        uint8_t* code_mem = exec_mem_.allocate_block(256);
        CodeEmitter e(code_mem);

        TranslationBlock tb;
        tb.guest_pc = start_pc;
        tb.host_addr = code_mem;
        tb.exit_count = 0;

        uint32_t pc = start_pc;
        bool block_ended = false;

        while (pc < program_.size() && !block_ended) {
            const auto& insn = program_[pc];
            switch (insn.op) {
                case 0x01: e.emit_mov_imm(insn.rd, insn.imm16); break;
                case 0x02: e.emit_add(insn.rd, insn.rs); break;
                case 0x03: e.emit_sub(insn.rd, insn.rs); break;
                case 0x04: e.emit_cmp_imm(insn.rd, insn.imm16); break;
                case 0x05: { // JMP target
                    const uint32_t target = insn.imm16;
                    e.emit_byte(0xE9); // jmp rel32
                    uint8_t* patch_site = e.buffer() + e.size();
                    e.emit_u32(0);

                    uint8_t* tramp_addr = e.buffer() + e.size();
                    auto tramp_offset = static_cast<int32_t>(tramp_addr - (patch_site + 4));
                    std::memcpy(patch_site, &tramp_offset, sizeof(int32_t));

                    e.emit_byte(0xC7); e.emit_byte(0x47); 
                    e.emit_byte(OffsetHelper::pc()); e.emit_u32(target);
                    e.emit_byte(0xC3); // ret

                    tb.exits[tb.exit_count++] = JumpPatchInfo{ target, patch_site, false };
                    block_ended = true;
                    break;
                }
                case 0x06: { // JZ target
                    const uint32_t target_taken = insn.imm16;
                    const uint32_t target_fall = pc + 1;

                    // cmp [rdi + zf], 1
                    e.emit_byte(0x83); e.emit_byte(0x7F); 
                    e.emit_byte(OffsetHelper::zf()); e.emit_byte(0x01);

                    // je trampoline_taken
                    e.emit_byte(0x0F); e.emit_byte(0x84);
                    uint8_t* patch_taken = e.buffer() + e.size();
                    e.emit_u32(0);

                    // jmp trampoline_fall
                    e.emit_byte(0xE9);
                    uint8_t* patch_fall = e.buffer() + e.size();
                    e.emit_u32(0);

                    // Трамплін Taken:
                    uint8_t* tramp_taken = e.buffer() + e.size();
                    auto off_taken = static_cast<int32_t>(tramp_taken - (patch_taken + 4));
                    std::memcpy(patch_taken, &off_taken, sizeof(int32_t));
                    e.emit_byte(0xC7); e.emit_byte(0x47); 
                    e.emit_byte(OffsetHelper::pc()); e.emit_u32(target_taken);
                    e.emit_byte(0xC3);

                    // Трамплін Fallthrough:
                    uint8_t* tramp_fall = e.buffer() + e.size();
                    auto off_fall = static_cast<int32_t>(tramp_fall - (patch_fall + 4));
                    std::memcpy(patch_fall, &off_fall, sizeof(int32_t));
                    e.emit_byte(0xC7); e.emit_byte(0x47); 
                    e.emit_byte(OffsetHelper::pc()); e.emit_u32(target_fall);
                    e.emit_byte(0xC3);

                    tb.exits[tb.exit_count++] = JumpPatchInfo{ target_taken, patch_taken, true };
                    tb.exits[tb.exit_count++] = JumpPatchInfo{ target_fall, patch_fall, false };
                    block_ended = true;
                    break;
                }
                case 0xFF: // HALT
                    e.emit_halt();
                    block_ended = true;
                    break;
            }
            pc++;
        }

        tb.host_size = e.size();
        const std::size_t new_idx = blocks_.size();
        blocks_.push_back(tb);
        block_map_[start_pc] = new_idx;

        TranslationBlock* current_tb = &blocks_[new_idx];

        // Патчимо попередні блоки, що чекали на цей Guest PC
        for (std::size_t i = 0; i < new_idx; ++i) {
            for (std::size_t k = 0; k < blocks_[i].exit_count; ++k) {
                if (blocks_[i].exits[k].guest_target_pc == start_pc) {
                    blocks_[i].exits[k].apply_patch(current_tb->host_addr);
                }
            }
        }

        // Патчимо виходи щойно створеного блоку, якщо їхні цілі вже скомпільовані
        for (std::size_t k = 0; k < current_tb->exit_count; ++k) {
            auto it = block_map_.find(current_tb->exits[k].guest_target_pc);
            if (it != block_map_.end()) {
                current_tb->exits[k].apply_patch(blocks_[it->second].host_addr);
            }
        }

        return current_tb;
    }

    std::vector<GuestInsn>               program_;
    ExecutableBuffer                     exec_mem_;
    std::vector<TranslationBlock>        blocks_;
    std::unordered_map<uint32_t, size_t> block_map_;
};
```
:::

## Покроковий аналіз виконання програми

Простежимо життєвий цикл виконання програми та динаміку зшивання базових блоків:

1. **Початковий стан:**
   * `GuestContext` ініціалізовано: `PC = 0`, `regs = [0, 0, 0, 0]`, `zf = 0`.
   * Кеш трансляцій порожній.

2. **Перший прохід (Крок 1 — промах кешу):**
   * Диспетчер шукає `PC = 0` у хеш-таблиці. Результат: промах (*Miss*).
   * Компілюється **Блок 0** (інструкції з `PC = 0` по `PC = 4`). Наприкінці блоку генерується умовний перехід `JZ 8` з виходами на трампліни: `Taken -> PC 8`, `Fallthrough -> PC 5`.
   * Викликається скомпільований код Блоку 0.
   * Виконуються: `R0 = 5`, `R1 = 1`, `R2 = 1`, перевірка `R0 == 1` дає хибу (`ZF = 0`).
   * Спрацьовує перехід на трамплін Fallthrough: у контекст записується `PC = 5`, і керування повертається в диспетчер.

3. **Другий прохід (Крок 2 — промах кешу):**
   * Диспетчер шукає `PC = 5`. Результат: промах.
   * Компілюється **Блок 1** (інструкції з `PC = 5` по `PC = 7`). Наприкінці стоїть безумовний стрибок `JMP 3` з виходом на трамплін `PC = 3`.
   * Диспетчер автоматично патчить вихід Fallthrough Блоку 0: тепер перехід веде прямо на нативний початок Блоку 1.
   * Виконується Блок 1: `R1 = 2`, `R0 = 4`.
   * Спрацьовує трамплін `JMP 3`: у контекст записується `PC = 3`, повернення в диспетчер.

4. **Третій прохід (Крок 3 — промах та замикання циклу):**
   * Диспетчер шукає `PC = 3`. Оскільки Блок 0 починався з `PC = 0`, а вхід у цикл відбувається на `PC = 3`, транслятор компілює окремий **Блок 2** (інструкції з `PC = 3` по `PC = 4`).
   * Диспетчер патчить вихід `JMP 3` Блоку 1 на початок Блоку 2.
   * Оскільки ціль Fallthrough Блоку 2 (`PC = 5`) уже є в кеші (Блок 1), вихід Блоку 2 **миттєво патчиться напряму на Блок 1**!

5. **Стаціонарний режим (Гарячий цикл):**
   * Наступні ітерації циклу (при `R0 = 4, 3, 2`) виконуються виключно по зшитому кільцю:
     ```
     [Блок 2: PC 3..4] ---> (прямий стрибок je fallthrough) ---> [Блок 1: PC 5..7] ---> (прямий стрибок jmp) ---> [Блок 2]
     ```
   * Процесор крутиться всередині двох блоків на повній швидкості без жодного системного виклику, без повернення в диспетчер і без пошуку в хеш-таблицях.

6. **Вихід із циклу та завершення:**
   * Коли `R0` досягає `1`, операція `CMP_IMM R0, 1` встановлює `ZF = 1`.
   * Умовний перехід у Блоці 2 обирає гілку Taken (`PC = 8`). Оскільки ціль ще не скомпільована, спрацьовує трамплін `PC = 8`, і керування востаннє повертається в диспетчер.
   * Диспетчер компілює **Блок 3** (`PC = 8: HALT`), патчить вихід Taken Блоку 2 і викликає Блок 3.
   * Блок 3 встановлює `halted = true` і завершує роботу.
   * У підсумку `GuestContext.regs[1]` містить точний розрахований результат.

## Інженерні пастки та оптимізації

Практична розробка промислових DBT-рушіїв вимагає врахування таких критичних аспектів:

### 1. Гарвардська архітектура та узгодженість кешів (Cache Coherency)
На процесорах x86 апаратура автоматично відстежує модифікацію пам'яті коду за допомогою блоку *Snoop on I-Cache*. Проте на процесорах ARM64 та RISC-V кеш інструкцій (I-Cache) та кеш даних (D-Cache) є повністю незалежними. Якщо записати нові інструкції в буфер пам'яті через звичайні операції збереження даних і не викликати інструкції очищення кешу інструкцій (`dc cvau`, `ic ivau`, `isb` в ARM або `fence.i` у RISC-V), процесор виконає застарілі інструкції, що залишилися в конвеєрі або I-кеші.

### 2. Атомарність патчингу на багатоядерних процесорах
Якщо кілька потоків одночасно виконують трансльований код у момент, коли диспетчер перезаписує 4 байти зміщення `rel32`, зчитування проміжного (неповністю записаного) значення призведе до стрибка на випадкову адресу в пам'яті. Щоб уникнути стану перегонів (*Race Condition*), поле відносного зміщення інструкції переходу обов'язково вирівнюється на 4-байтну межу в пам'яті, що гарантує атомарність оновлення на рівні шини L1-кешу процесора.

### 3. Розв'язування ланцюжків при інвалідації (Unchaining)
Якщо кеш коду переповнюється, або гостьова програма перезаписує свій код у пам'яті (Self-Modifying Code), транслятор повинен звільнити старі блоки. Просте звільнення пам'яті блоку призведе до катастрофи, оскільки інші блоки все ще містять прямі стрибки на його адресу. Перед видаленням блоку транслятор використовує збережений список зворотних посилань (*Predecessors List*) і відновлює вихідні переходи на трампліни (*Unchaining*).

### 4. Непрямі переходи та Inline Caching
Найскладніший випадок у двійковій трансляції — це непрямі переходи (наприклад, `JMP Rd` або виклики віртуальних методів `CALL [rax]`). Оскільки цільова адреса змінюється динамічно під час виконання, її неможливо зшити єдиним прямим стрибком. 

Для оптимізації непрямих переходів застосовують **вбудовані кеші цілей (Inline Target Cache)**:
* У згенерований код вбудовується перевірка: якщо поточний гостьовий `PC` збігається з останнім баченим значенням (`predicted_gpc`), виконується прямий стрибок на відповідний нативний `host_pc`.
* Лише якщо ціль змінилася (поліморфний виклик), код стрибає в повільний диспетчер для оновлення кешу.

## Підсумок: від прототипу до промислового JIT

Створений мінімальний транслятор демонструє повний цикл роботи динамічної двійкової трансляції: виділення виконуваної пам'яті, декодування гостьового байткоду, побайтову емісію нативного коду x86-64 та пряме зшивання блоків через динамічний патчинг відносних переходів. 

У реальних промислових системах (таких як QEMU TCG або Apple Rosetta 2) цей фундамент доповнюється двома ключовими оптимізаціями:
1. **Закріплення регістрів (Register Pinning):** замість постійного зчитування та запису полів `GuestContext` у пам'ять, гарячі гостьові регістри закріплюються за вільними фізичними регістрами хоста (`r12`–`r15` в x86-64 або `x19`–`x28` в ARM64). Це повністю усуває операції звернення до пам'яті всередині базового блоку.
2. **Формування трас (Superblocks / Traces):** зшивання не лише окремих переходів, а лінійних ланцюжків із десятків базових блоків в один суміжний машинний код. Це дає оптимізатору хоста можливість виконувати спільні компіляторні перетворення — винесення інваріантів із циклів, об'єднання інструкцій та усунення мертвого коду.

