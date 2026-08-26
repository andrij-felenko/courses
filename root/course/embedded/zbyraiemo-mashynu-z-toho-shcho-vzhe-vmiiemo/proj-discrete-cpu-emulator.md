# ⚙️ Програмна модель 8-бітного процесора: покроковий емулятор на C та C++

Найкращий спосіб зняти серпанок «магії» з роботи процесорного ядра — створити його повну програмну модель у коді. Коли кожен апаратний регістр стає звичайною числовою змінною, системна шина — парою функцій читання й запису, а дешифратор інструкцій — оператором вибору `switch`, абстрактні поняття тактового синхронізму, шинних циклів та Memory-Mapped I/O стають абсолютно прозорими.

Нижче наведено повнофункціональний покроковий емулятор нашої синтезованої 8-бітної архітектури. Емулятор моделює роботу кремнієвого ядра на рівні машинних тактів: реалізує канонічний трифазний цикл (Fetch-Decode-Execute), підтримує 16-бітний адресний простір (64 КіБ), розділяє пам'ять на секції ROM, SRAM та MMIO, містить повноцінний адресний дешифратор і емулює апаратний порт вводу-виводу (GPIO), що керує фізичним станом віртуального світлодіода.

---

### Архітектурний контракт емульованої системи

Модель спирається на гарвардсько-нейманівський компроміс: фізично простір пам'яті спільний (єдина шина адреси та даних), але адресний дешифратор жорстко розмежовує області виконання коду та збереження змінних:

1. **Регістри процесорного ядра**:
   - `PC` (16 біт) — лічильник команд, що вказує на адресу поточної вибірки;
   - `IR` (8 біт) — регістр інструкцій, що фіксує код операції на час його декодування;
   - `ACC` (8 біт) — головний робочий акумулятор, куди спрямовуються результати більшості операцій АЛП;
   - `R0` (8 біт) — допоміжний регістр загального призначення для другого операнда;
   - `FLAGS` — регістр ознак результату операцій АЛП (прапорець нуля `Z` та прапорець перенесення/позички `C`).

2. **Організація адресного простору (64 КіБ)**:
   - `0x0000 – 0x3FFF` (16 КіБ): ROM / Flash (пам'ять програм, спроба запису викликає апаратну помилку шини `BUS ERROR`);
   - `0x4000 – 0x7FFF` (16 КіБ): SRAM (оперативна пам'ять для збереження динамічних даних та змінних);
   - `0x8000`: Регістр `GPIO_OUT` (MMIO, біт 0 підключений до віртуального світлодіода);
   - `0x8001`: Регістр `GPIO_IN` (MMIO, біт 0 зчитує стан віртуальної кнопки з підтяжкою до живлення).

3. **Система команд (ISA)**:

| Опкод | Мнемоніка | Операнди | Кількість байтів | Опис апаратної дії |
|---|---|---|---|---|
| `0x00` | `NOP` | — | 1 | Пропуск такту без зміни регістрів |
| `0x01` | `LOAD_IMM_ACC` | `val` (8 біт) | 2 | Завантажити константу `val` в `ACC` |
| `0x02` | `LOAD_IMM_R0` | `val` (8 біт) | 2 | Завантажити константу `val` в `R0` |
| `0x10` | `LOAD_MEM_ACC` | `[addr]` (16 біт) | 3 | Прочитати байт із пам'яті/MMIO `[addr]` в `ACC` |
| `0x20` | `STORE_MEM_ACC` | `[addr]` (16 біт) | 3 | Записати вміст `ACC` у пам'ять/MMIO `[addr]` |
| `0x30` | `ADD_ACC_R0` | — | 1 | `ACC = ACC + R0`, оновити прапорці Z та C |
| `0x31` | `SUB_ACC_R0` | — | 1 | `ACC = ACC - R0`, оновити прапорці Z та C |
| `0x32` | `AND_ACC_R0` | — | 1 | `ACC = ACC & R0`, оновити прапорець Z |
| `0x33` | `XOR_ACC_R0` | — | 1 | `ACC = ACC ^ R0`, оновити прапорець Z |
| `0x40` | `JMP` | `addr` (16 біт) | 3 | Безумовний перехід: `PC = addr` |
| `0x41` | `JZ` | `addr` (16 біт) | 3 | Перехід за нульовим прапорцем: якщо `Z == 1`, то `PC = addr` |
| `0xFF` | `HALT` | — | 1 | Апаратний зупин тактового генератора ядра |

---

### Програмна реалізація емулятора

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MEMORY_SIZE 65536
#define MMIO_GPIO_OUT 0x8000
#define MMIO_GPIO_IN  0x8001

/* Опкоди інструкцій нашої ISA */
enum Opcode {
    OP_NOP           = 0x00,
    OP_LOAD_IMM_ACC  = 0x01,
    OP_LOAD_IMM_R0   = 0x02,
    OP_LOAD_MEM_ACC  = 0x10,
    OP_STORE_MEM_ACC = 0x20,
    OP_ADD_ACC_R0    = 0x30,
    OP_SUB_ACC_R0    = 0x31,
    OP_AND_ACC_R0    = 0x32,
    OP_XOR_ACC_R0    = 0x33,
    OP_JMP           = 0x40,
    OP_JZ            = 0x41,
    OP_HALT          = 0xFF
};

/* Стан процесорного ядра */
typedef struct {
    uint16_t pc;
    uint8_t  ir;
    uint8_t  acc;
    uint8_t  r0;
    bool     flag_z;
    bool     flag_c;
    bool     halted;
} CpuState;

/* Фізична пам'ять та стан периферійного заліза */
static uint8_t g_memory[MEMORY_SIZE];
static uint8_t g_gpio_out_latch = 0x00;
static uint8_t g_gpio_in_pins   = 0x01; /* кнопка відпущена (підтяжка до 1) */

/* Імітація системної шини та адресного дешифратора (Address Decoding) */
static uint8_t bus_read(uint16_t addr) {
    if (addr == MMIO_GPIO_IN) {
        printf("  [BUS RD] Читання MMIO 0x%04X (GPIO IN) = 0x%02X\n", addr, g_gpio_in_pins);
        return g_gpio_in_pins;
    }
    if (addr == MMIO_GPIO_OUT) {
        return g_gpio_out_latch;
    }
    return g_memory[addr];
}

static void bus_write(uint16_t addr, uint8_t data) {
    if (addr == MMIO_GPIO_OUT) {
        g_gpio_out_latch = data;
        bool led_state = (data & 0x01) != 0;
        printf("  [BUS WR] Запис MMIO 0x%04X (GPIO OUT) = 0x%02X -> Світлодіод: %s\n",
               addr, data, led_state ? "УВІМКНЕНО (3.3 В)" : "ВИМКНЕНО (0 В)");
        return;
    }
    if (addr < 0x4000) {
        printf("  [BUS ERROR] Спроба запису в ROM за адресою 0x%04X!\n", addr);
        return;
    }
    g_memory[addr] = data;
}

/* Оновлення прапорців стану АЛП */
static void update_flags_alu(CpuState *cpu, uint16_t raw_result) {
    cpu->acc = (uint8_t)(raw_result & 0xFF);
    cpu->flag_z = (cpu->acc == 0);
    cpu->flag_c = (raw_result > 0xFF);
}

/* Один повний цикл Fetch-Decode-Execute */
static void cpu_step(CpuState *cpu) {
    if (cpu->halted) return;

    /* 1. ФАЗА ВИБІРКИ (FETCH) */
    uint16_t current_pc = cpu->pc;
    cpu->ir = bus_read(cpu->pc++);

    printf("TICK | PC:0x%04X | IR:0x%02X | ACC:0x%02X | R0:0x%02X | Z:%d C:%d\n",
           current_pc, cpu->ir, cpu->acc, cpu->r0, cpu->flag_z, cpu->flag_c);

    /* 2. ФАЗА ДЕКОДУВАННЯ ТА ВИКОНАННЯ (DECODE & EXECUTE) */
    switch (cpu->ir) {
        case OP_NOP:
            break;

        case OP_LOAD_IMM_ACC:
            cpu->acc = bus_read(cpu->pc++);
            break;

        case OP_LOAD_IMM_R0:
            cpu->r0 = bus_read(cpu->pc++);
            break;

        case OP_LOAD_MEM_ACC: {
            uint8_t lo = bus_read(cpu->pc++);
            uint8_t hi = bus_read(cpu->pc++);
            uint16_t addr = (uint16_t)(lo | (hi << 8));
            cpu->acc = bus_read(addr);
            break;
        }

        case OP_STORE_MEM_ACC: {
            uint8_t lo = bus_read(cpu->pc++);
            uint8_t hi = bus_read(cpu->pc++);
            uint16_t addr = (uint16_t)(lo | (hi << 8));
            bus_write(addr, cpu->acc);
            break;
        }

        case OP_ADD_ACC_R0: {
            uint16_t res = (uint16_t)cpu->acc + (uint16_t)cpu->r0;
            update_flags_alu(cpu, res);
            break;
        }

        case OP_SUB_ACC_R0: {
            uint16_t res = (uint16_t)cpu->acc - (uint16_t)cpu->r0;
            update_flags_alu(cpu, res);
            break;
        }

        case OP_AND_ACC_R0:
            cpu->acc &= cpu->r0;
            cpu->flag_z = (cpu->acc == 0);
            break;

        case OP_XOR_ACC_R0:
            cpu->acc ^= cpu->r0;
            cpu->flag_z = (cpu->acc == 0);
            break;

        case OP_JMP: {
            uint8_t lo = bus_read(cpu->pc++);
            uint8_t hi = bus_read(cpu->pc++);
            cpu->pc = (uint16_t)(lo | (hi << 8));
            break;
        }

        case OP_JZ: {
            uint8_t lo = bus_read(cpu->pc++);
            uint8_t hi = bus_read(cpu->pc++);
            if (cpu->flag_z) {
                cpu->pc = (uint16_t)(lo | (hi << 8));
                printf("  [BRANCH TAKEN] Стрибок на адресу 0x%04X (Z=1)\n", cpu->pc);
            }
            break;
        }

        case OP_HALT:
            cpu->halted = true;
            printf("  [CPU] Сигнал HALT отримано. Ядро зупинено.\n");
            break;

        default:
            printf("  [CPU ERROR] Невідомий опкод 0x%02X за адресою 0x%04X!\n", cpu->ir, current_pc);
            cpu->halted = true;
            break;
    }
}

int main(void) {
    memset(g_memory, 0, sizeof(g_memory));

    /* Записуємо тестову бінарну прошивку в ROM (з адреси 0x0000):
       Програма двічі блимає світлодіодом через MMIO, обчислює різницю і записує в RAM. */
    uint8_t firmware[] = {
        /* 0x0000: Ініціалізація лічильника циклів: R0 = 1 */
        OP_LOAD_IMM_R0, 0x01,
        
        /* 0x0002: Увімкнути світлодіод (ACC = 0x01 -> MMIO 0x8000) */
        OP_LOAD_IMM_ACC, 0x01,
        OP_STORE_MEM_ACC, 0x00, 0x80,

        /* 0x0007: Вимкнути світлодіод (ACC = 0x00 -> MMIO 0x8000) */
        OP_LOAD_IMM_ACC, 0x00,
        OP_STORE_MEM_ACC, 0x00, 0x80,

        /* 0x000C: Зберегти поточний лічильник у RAM [0x4000] */
        OP_LOAD_IMM_ACC, 0x03,
        OP_SUB_ACC_R0,               /* ACC = 3 - 1 = 2 */
        OP_STORE_MEM_ACC, 0x00, 0x40,/* RAM[0x4000] = 2 */

        /* 0x0013: Зупинка */
        OP_HALT
    };

    memcpy(g_memory, firmware, sizeof(firmware));

    /* Ініціалізація процесора (Power-On Reset) */
    CpuState cpu = {
        .pc = 0x0000,
        .ir = 0x00,
        .acc = 0x00,
        .r0 = 0x00,
        .flag_z = false,
        .flag_c = false,
        .halted = false
    };

    printf("=== СТАРТ ЕМУЛЯЦІЇ ПРОЦЕСОРА (RESET PC=0x0000) ===\n\n");
    while (!cpu.halted) {
        cpu_step(&cpu);
    }
    printf("\n=== ЕМУЛЯЦІЮ ЗАВЕРШЕНО ===\n");
    printf("Фінальний стан RAM[0x4000] = 0x%02X\n", g_memory[0x4000]);
    printf("Фінальний стан GPIO Latch = 0x%02X\n", g_gpio_out_latch);

    return 0;
}
```
```cpp
#include <iostream>
#include <array>
#include <span>
#include <cstdint>
#include <iomanip>

namespace emu {

inline constexpr std::size_t MemorySize = 65536;
inline constexpr uint16_t MmioGpioOut   = 0x8000;
inline constexpr uint16_t MmioGpioIn    = 0x8001;

enum class Opcode : uint8_t {
    Nop          = 0x00,
    LoadImmAcc   = 0x01,
    LoadImmR0    = 0x02,
    LoadMemAcc   = 0x10,
    StoreMemAcc  = 0x20,
    AddAccR0     = 0x30,
    SubAccR0     = 0x31,
    AndAccR0     = 0x32,
    XorAccR0     = 0x33,
    Jmp          = 0x40,
    Jz           = 0x41,
    Halt         = 0xFF
};

class SystemBus {
public:
    SystemBus() {
        memory_.fill(0);
    }

    void load_rom(std::span<const uint8_t> firmware, uint16_t base_addr = 0x0000) {
        for (std::size_t i = 0; i < firmware.size() && (base_addr + i) < MemorySize; ++i) {
            memory_[base_addr + i] = firmware[i];
        }
    }

    [[nodiscard]] uint8_t read(uint16_t addr) const {
        if (addr == MmioGpioIn) {
            std::cout << "  [BUS RD] Читання MMIO 0x" << std::hex << std::uppercase
                      << std::setw(4) << std::setfill('0') << addr
                      << " (GPIO IN) = 0x" << std::setw(2) << static_cast<int>(gpio_in_pins_) << "\n";
            return gpio_in_pins_;
        }
        if (addr == MmioGpioOut) {
            return gpio_out_latch_;
        }
        return memory_[addr];
    }

    void write(uint16_t addr, uint8_t data) {
        if (addr == MmioGpioOut) {
            gpio_out_latch_ = data;
            const bool led_state = (data & 0x01) != 0;
            std::cout << "  [BUS WR] Запис MMIO 0x" << std::hex << std::uppercase
                      << std::setw(4) << std::setfill('0') << addr
                      << " (GPIO OUT) = 0x" << std::setw(2) << static_cast<int>(data)
                      << " -> Світлодіод: " << (led_state ? "УВІМКНЕНО (3.3 В)" : "ВИМКНЕНО (0 В)") << "\n";
            return;
        }
        if (addr < 0x4000) {
            std::cout << "  [BUS ERROR] Спроба запису в ROM за адресою 0x"
                      << std::hex << std::setw(4) << addr << "!\n";
            return;
        }
        memory_[addr] = data;
    }

    [[nodiscard]] uint8_t inspect_ram(uint16_t addr) const noexcept { return memory_[addr]; }
    [[nodiscard]] uint8_t inspect_gpio() const noexcept { return gpio_out_latch_; }

private:
    std::array<uint8_t, MemorySize> memory_{};
    uint8_t gpio_out_latch_{0x00};
    uint8_t gpio_in_pins_{0x01};
};

class Cpu {
public:
    explicit Cpu(SystemBus& bus) : bus_(bus) {}

    void step() {
        if (halted_) return;

        // 1. Fetch
        const uint16_t current_pc = pc_;
        ir_ = bus_.read(pc_++);

        std::cout << "TICK | PC:0x" << std::hex << std::uppercase << std::setw(4) << std::setfill('0') << current_pc
                  << " | IR:0x" << std::setw(2) << static_cast<int>(ir_)
                  << " | ACC:0x" << std::setw(2) << static_cast<int>(acc_)
                  << " | R0:0x" << std::setw(2) << static_cast<int>(r0_)
                  << " | Z:" << flag_z_ << " C:" << flag_c_ << "\n";

        // 2. Decode & Execute
        switch (static_cast<Opcode>(ir_)) {
            case Opcode::Nop:
                break;

            case Opcode::LoadImmAcc:
                acc_ = bus_.read(pc_++);
                break;

            case Opcode::LoadImmR0:
                r0_ = bus_.read(pc_++);
                break;

            case Opcode::LoadMemAcc: {
                const uint8_t lo = bus_.read(pc_++);
                const uint8_t hi = bus_.read(pc_++);
                acc_ = bus_.read(static_cast<uint16_t>(lo | (hi << 8)));
                break;
            }

            case Opcode::StoreMemAcc: {
                const uint8_t lo = bus_.read(pc_++);
                const uint8_t hi = bus_.read(pc_++);
                bus_.write(static_cast<uint16_t>(lo | (hi << 8)), acc_);
                break;
            }

            case Opcode::AddAccR0: {
                const uint16_t res = static_cast<uint16_t>(acc_) + static_cast<uint16_t>(r0_);
                acc_ = static_cast<uint8_t>(res & 0xFF);
                flag_z_ = (acc_ == 0);
                flag_c_ = (res > 0xFF);
                break;
            }

            case Opcode::SubAccR0: {
                const uint16_t res = static_cast<uint16_t>(acc_) - static_cast<uint16_t>(r0_);
                acc_ = static_cast<uint8_t>(res & 0xFF);
                flag_z_ = (acc_ == 0);
                flag_c_ = (res > 0xFF);
                break;
            }

            case Opcode::AndAccR0:
                acc_ &= r0_;
                flag_z_ = (acc_ == 0);
                break;

            case Opcode::XorAccR0:
                acc_ ^= r0_;
                flag_z_ = (acc_ == 0);
                break;

            case Opcode::Jmp: {
                const uint8_t lo = bus_.read(pc_++);
                const uint8_t hi = bus_.read(pc_++);
                pc_ = static_cast<uint16_t>(lo | (hi << 8));
                break;
            }

            case Opcode::Jz: {
                const uint8_t lo = bus_.read(pc_++);
                const uint8_t hi = bus_.read(pc_++);
                if (flag_z_) {
                    pc_ = static_cast<uint16_t>(lo | (hi << 8));
                    std::cout << "  [BRANCH TAKEN] Стрибок на 0x" << std::hex << pc_ << " (Z=1)\n";
                }
                break;
            }

            case Opcode::Halt:
                halted_ = true;
                std::cout << "  [CPU] Сигнал HALT отримано. Ядро зупинено.\n";
                break;

            default:
                std::cout << "  [CPU ERROR] Невідомий опкод 0x" << std::hex << static_cast<int>(ir_) << "!\n";
                halted_ = true;
                break;
        }
    }

    [[nodiscard]] bool is_halted() const noexcept { return halted_; }

private:
    SystemBus& bus_;
    uint16_t pc_{0x0000};
    uint8_t  ir_{0x00};
    uint8_t  acc_{0x00};
    uint8_t  r0_{0x00};
    bool     flag_z_{false};
    bool     flag_c_{false};
    bool     halted_{false};
};

} // namespace emu

int main() {
    emu::SystemBus bus;

    // Бінарна прошивка: блимання світлодіодом через MMIO і запис у RAM
    constexpr std::array<uint8_t, 20> firmware = {
        static_cast<uint8_t>(emu::Opcode::LoadImmR0), 0x01,
        static_cast<uint8_t>(emu::Opcode::LoadImmAcc), 0x01,
        static_cast<uint8_t>(emu::Opcode::StoreMemAcc), 0x00, 0x80, // MMIO 0x8000
        static_cast<uint8_t>(emu::Opcode::LoadImmAcc), 0x00,
        static_cast<uint8_t>(emu::Opcode::StoreMemAcc), 0x00, 0x80, // MMIO 0x8000
        static_cast<uint8_t>(emu::Opcode::LoadImmAcc), 0x03,
        static_cast<uint8_t>(emu::Opcode::SubAccR0),
        static_cast<uint8_t>(emu::Opcode::StoreMemAcc), 0x00, 0x40, // RAM 0x4000
        static_cast<uint8_t>(emu::Opcode::Halt)
    };

    bus.load_rom(firmware);

    emu::Cpu cpu(bus);
    std::cout << "=== СТАРТ ЕМУЛЯЦІЇ ПРОЦЕСОРА (RESET PC=0x0000) ===\n\n";
    while (!cpu.is_halted()) {
        cpu.step();
    }
    std::cout << "\n=== ЕМУЛЯЦІЮ ЗАВЕРШЕНО ===\n";
    std::cout << "Фінальний стан RAM[0x4000] = 0x" << std::hex << static_cast<int>(bus.inspect_ram(0x4000)) << "\n";
    std::cout << "Фінальний стан GPIO Latch = 0x" << std::hex << static_cast<int>(bus.inspect_gpio()) << "\n";

    return 0;
}
```
:::

---

### Покроковий розбір виконання прошивки в емуляторі

Простежмо, як тестова програма виконується ядром крок за кроком, зіставляючи лог емулятора з апаратними процесами:

1. **Ініціалізація скидання (POR)**:
   При створенні структури `CpuState` лічильник `pc` встановлюється в `0x0000`. Це програмний еквівалент апаратного сигналу `RESET`, який заземлює входи паралельного завантаження лічильників 74HC161 на платі.

2. **Крок 1 (`PC = 0x0000`) — `OP_LOAD_IMM_R0, 0x01`**:
   - Ядро зчитує байт `0x02` з адреси `0x0000` в регістр `IR`, інкрементує `PC` до `0x0001`.
   - Дешифратор бачить команду негайного завантаження й робить другий цикл вибірки з адреси `0x0001`, записуючи значення `0x01` у регістр `R0`. `PC` стає `0x0002`.

3. **Кроки 2 та 3 — Вмикання та вимикання світлодіода через MMIO**:
   - Команда `LOAD_IMM_ACC, 0x01` завантажує одиницю в робочий акумулятор `ACC`.
   - Команда `STORE_MEM_ACC, 0x00, 0x80` вимагає трьох звернень до пам'яті: спочатку зчитується молодший байт адреси (`0x00`), потім старший (`0x80`), формуючи 16-бітну адресу `0x8000`.
   - На фазі виконання викликається функція `bus_write(0x8000, 0x01)`. Програмний дешифратор розпізнає діапазон MMIO і оновлює змінну `g_gpio_out_latch`. Лог фіксує перемикання лінії у високий рівень: `Світлодіод: УВІМКНЕНО (3.3 В)`.
   - Наступна пара інструкцій завантажує в `ACC` нуль і записує його за тією ж адресою `0x8000` — на ніжці формується спадний фронт напруги, світлодіод гасне.

4. **Крок 4 — Арифметична дія та запис в оперативну пам'ять**:
   - Інструкція `LOAD_IMM_ACC, 0x03` заносить число 3 в акумулятор.
   - Інструкція `SUB_ACC_R0` активує блок віднімання в АЛП: обчислюється вираз `3 - 1 = 2`. Результат записується назад в `ACC`, прапорець нуля `Z` скидається в 0, оскільки результат не дорівнює нулю.
   - Інструкція `STORE_MEM_ACC, 0x00, 0x40` виставляє на шину адресу `0x4000`. Адресний дешифратор ідентифікує діапазон SRAM і зберігає байт `0x02` у масиві `g_memory`.

5. **Крок 5 — Апаратний зупин (`OP_HALT`)**:
   - Опкод `0xFF` переводить прапорець `halted` у значення `true`. Це відповідає вимкненню тактового генератора процесора (переведенню в режим глибокого сну `WFI` / `SLEEP`).

---

### Крайові випадки та апаратні пастки

Реальне кремнієве ядро щомиті стикається з нештатними ситуаціями, які програмна модель повинна відпрацьовувати детерміновано:

1. **Спроба запису в область ROM (Flash)**:
   Зверніть увагу на перевірку `if (addr < 0x4000)` у функції `bus_write()`. У фізичній схемі лінія запису `/WR` взагалі не підводиться до мікросхеми ROM — там є лише вхід читання `/RD` та вибору `/CS0`. Якщо прошивка через помилку покажчика спробує записати дані за адресою `0x0010`, мікросхема ROM просто проігнорує цей цикл, а в мікроконтролерах із захистом пам'яті (MPU) апаратний дешифратор згенерує виняток `BusFault` або `HardFault`.

2. **Неповна адресна дешифрація (Address Aliasing)**:
   У нашому простому дешифраторі регістр `GPIO_OUT` розташований за адресою `0x8000`. Якщо дешифратор аналізує лише старші біти `A[15:14]`, то звернення до адрес `0x8001`, `0x8002` чи `0x8FFF` без додаткових логічних вентилів потраплятимуть на той самий чіп. Це створює «фантомні копії» (англ. *ghost memory*) одного й того самого фізичного регістра по всьому адресному простору — класична пастка апаратних помилок у ранніх 8-бітних комп'ютерах.

3. **Арифметичне переповнення та прапорець перенесення (Carry)**:
   При додаванні `0xFF + 0x01` 8-бітний акумулятор містить `0x00`. Якщо аналізувати лише значення `ACC`, неможливо зрозуміти: чи це справжній нуль, чи результат переповнення розрядної сітки. Прапорець `C` (Carry) фіксує перенос дев'ятого біта за межі байта, дозволяючи прошивці будувати 16- та 32-бітну багаторозрядну арифметику з кількох послідовних 8-бітних інструкцій додавання з переносом (`ADC`).
