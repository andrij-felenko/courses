# ⚙️ Практична реалізація емулятора мікропроцесорного ядра на C та C++

Емуляція процесорного ядра на рівні архітектури системи команд (Instruction Set Architecture, ISA) є головним інженерним інструментом для перевірки правильності функціонування обчислювального тракту, налагодження компіляторів і тестування вбудованого програмного забезпечення до моменту появи фізичного кремнієвого кристала.

Програмний емулятор точно моделює поведінку апаратних тригерів, регістрового файлу, комбінаційного АЛП, лічильника команд `PC` та пам'яті на кожному дискретному тактовому імпульсі.

У цьому проекті реалізовано повноцінний 16-бітний процесорний емулятор із гарвардською організацією шин (роздільна пам'ять програм і даних), 8 регістрами загального призначення (`R0`–`R7`, де `R0` апаратно зафіксований на нульовому значенні), прапорцями стану (`Z`, `N`, `C`, `V`) та детермінованим циклом вибірки, декодування й виконання інструкцій.

### Формат двійкових інструкцій і система команд

Процесор використовує 16-бітні інструкції фіксованої довжини. Фіксована довжина спрощує апаратний декодер, оскільки позиції номерів регістрів і коду операції залишаються незмінними у двійковому слові.

Система команд поділяється на два базові формати:

```
Формат R-типу (Register-to-Register):
 15  14  13  12 | 11  10   9 | 8   7   6 | 5   4   3 | 2   1   0
[    Opcode    ] [    Rd    ] [   Rs1   ] [   Rs2   ] [ Unused  ]

Формат I-типу (Immediate / Memory / Branch):
 15  14  13  12 | 11  10   9 | 8   7   6   5   4   3   2   1   0
[    Opcode    ] [ Rd / Rs1 ] [      Immediate / Offset 9-bit     ]
```

Призначення полів:
- `Opcode` (біти `15:12`) — 4-бітний код операції (до 16 унікальних інструкцій).
- `Rd` (біти `11:9`) — 3-бітний номер цільового регістра запису результату (`0`..`7`).
- `Rs1` (біти `8:6`) — 3-бітний номер першого регістра-операнда (`0`..`7`).
- `Rs2` (біти `5:3`) — 3-бітний номер другого регістра-операнда (`0`..`7`).
- `Immediate / Offset` (біти `8:0`) — 9-бітна знакова або беззнакова числова константа.

Набір операцій охоплює всі базові класи дій процесорного ядра:
1. `ADD Rd, Rs1, Rs2` (Opcode `0x1`) — арифметичне додавання `Rd = Rs1 + Rs2` з оновленням усіх прапорців.
2. `SUB Rd, Rs1, Rs2` (Opcode `0x2`) — арифметичне віднімання `Rd = Rs1 - Rs2` з оновленням усіх прапорців.
3. `AND Rd, Rs1, Rs2` (Opcode `0x3`) — побітове логічне `І`: `Rd = Rs1 & Rs2`, оновлює прапорці `Z` та `N`.
4. `OR  Rd, Rs1, Rs2` (Opcode `0x4`) — побітове логічне `АБО`: `Rd = Rs1 | Rs2`, оновлює прапорці `Z` та `N`.
5. `LDI Rd, Imm9`     (Opcode `0x5`) — завантаження безпосередньої константи зі знаковим розширенням: `Rd = SignExtend(Imm9)`.
6. `LD  Rd, [Rs1]`    (Opcode `0x6`) — зчитування 16-бітного слова з оперативної пам'яті даних за адресою в `Rs1`: `Rd = DataMem[Rs1]`.
7. `ST  Rs2, [Rs1]`   (Opcode `0x7`) — запис 16-бітного слова з `Rs2` в оперативну пам'ять даних за адресою в `Rs1`: `DataMem[Rs1] = Rs2`.
8. `BEQ Rd, Rs1, Off` (Opcode `0x8`) — умовний перехід за рівністю: якщо `Reg[Rd] == Reg[Rs1]`, то `PC = PC + 1 + SignExtend(Off)`.
9. `HLT`              (Opcode `0xF`) — зупинка тактового генератора процесора.

### Програмна реалізація емулятора на C та C++

У реалізації мовою C стан ядра представлено явною структурою `CpuCore`, а кожна фаза циклу інструкції реалізована через прямі бітові маски та зрушення. У реалізації на C++ стан інкапсульовано в клас із суворим контролем типів (`enum class Opcode`), стандартними контейнерами `std::array` фіксованого розміру та інтерфейсом завантаження двійкового коду через `std::span`.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define REG_COUNT 8
#define MEM_SIZE 256

typedef enum {
    OP_NOP = 0x0,
    OP_ADD = 0x1,
    OP_SUB = 0x2,
    OP_AND = 0x3,
    OP_OR  = 0x4,
    OP_LDI = 0x5,
    OP_LD  = 0x6,
    OP_ST  = 0x7,
    OP_BEQ = 0x8,
    OP_HLT = 0xF
} Opcode;

typedef struct {
    bool z; /* Zero flag: результат операції дорівнює нулю */
    bool n; /* Negative flag: старший знаковий біт результату дорівнює 1 */
    bool c; /* Carry flag: перенос із 16-го біта / беззнакове переповнення */
    bool v; /* Overflow flag: знакове арифметичне переповнення */
} Flags;

typedef struct {
    uint16_t regs[REG_COUNT];
    uint16_t pc;
    Flags flags;
    bool halted;
    uint16_t prog_mem[MEM_SIZE];
    uint16_t data_mem[MEM_SIZE];
} CpuCore;

void cpu_init(CpuCore *cpu) {
    for (int i = 0; i < REG_COUNT; ++i) cpu->regs[i] = 0;
    cpu->pc = 0;
    cpu->flags = (Flags){ .z = false, .n = false, .c = false, .v = false };
    cpu->halted = false;
    for (int i = 0; i < MEM_SIZE; ++i) {
        cpu->prog_mem[i] = 0;
        cpu->data_mem[i] = 0;
    }
}

static int16_t sign_extend_9(uint16_t val) {
    if (val & 0x0100) {
        return (int16_t)(val | 0xFE00);
    }
    return (int16_t)(val & 0x01FF);
}

void cpu_step(CpuCore *cpu) {
    if (cpu->halted) return;

    /* 1. Фаза Fetch: вибірка слова інструкції та інкремент PC */
    uint16_t instr = cpu->prog_mem[cpu->pc % MEM_SIZE];
    cpu->pc++;

    /* 2. Фаза Decode: виділення бітових полів команди */
    uint8_t opcode = (instr >> 12) & 0x0F;
    uint8_t rd     = (instr >> 9)  & 0x07;
    uint8_t rs1    = (instr >> 6)  & 0x07;
    uint8_t rs2    = (instr >> 3)  & 0x07;
    uint16_t imm9  = instr & 0x01FF;

    /* 3. Фаза Execute / Memory / Write-Back */
    switch (opcode) {
        case OP_NOP:
            break;

        case OP_ADD: {
            uint32_t a = cpu->regs[rs1];
            uint32_t b = cpu->regs[rs2];
            uint32_t res = a + b;
            uint16_t res16 = (uint16_t)res;

            if (rd != 0) cpu->regs[rd] = res16;

            cpu->flags.z = (res16 == 0);
            cpu->flags.n = (res16 & 0x8000) != 0;
            cpu->flags.c = (res > 0xFFFF);
            cpu->flags.v = (!((a ^ b) & 0x8000) && ((a ^ res) & 0x8000));
            break;
        }

        case OP_SUB: {
            uint32_t a = cpu->regs[rs1];
            uint32_t b = cpu->regs[rs2];
            uint32_t res = a - b;
            uint16_t res16 = (uint16_t)res;

            if (rd != 0) cpu->regs[rd] = res16;

            cpu->flags.z = (res16 == 0);
            cpu->flags.n = (res16 & 0x8000) != 0;
            cpu->flags.c = (a >= b);
            cpu->flags.v = (((a ^ b) & 0x8000) && ((a ^ res) & 0x8000));
            break;
        }

        case OP_AND: {
            uint16_t res = cpu->regs[rs1] & cpu->regs[rs2];
            if (rd != 0) cpu->regs[rd] = res;
            cpu->flags.z = (res == 0);
            cpu->flags.n = (res & 0x8000) != 0;
            break;
        }

        case OP_OR: {
            uint16_t res = cpu->regs[rs1] | cpu->regs[rs2];
            if (rd != 0) cpu->regs[rd] = res;
            cpu->flags.z = (res == 0);
            cpu->flags.n = (res & 0x8000) != 0;
            break;
        }

        case OP_LDI: {
            int16_t ext = sign_extend_9(imm9);
            if (rd != 0) cpu->regs[rd] = (uint16_t)ext;
            break;
        }

        case OP_LD: {
            uint16_t addr = cpu->regs[rs1] % MEM_SIZE;
            if (rd != 0) cpu->regs[rd] = cpu->data_mem[addr];
            break;
        }

        case OP_ST: {
            uint16_t addr = cpu->regs[rs1] % MEM_SIZE;
            cpu->data_mem[addr] = cpu->regs[rs2];
            break;
        }

        case OP_BEQ: {
            if (cpu->regs[rd] == cpu->regs[rs1]) {
                int16_t offset = sign_extend_9(imm9);
                cpu->pc = (uint16_t)((int16_t)cpu->pc + offset);
            }
            break;
        }

        case OP_HLT:
            cpu->halted = true;
            break;

        default:
            cpu->halted = true;
            break;
    }

    cpu->regs[0] = 0; /* R0 апаратно підключений до землі (незмінний 0) */
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <cstdint>
#include <iomanip>

enum class Opcode : uint8_t {
    Nop = 0x0,
    Add = 0x1,
    Sub = 0x2,
    And = 0x3,
    Or  = 0x4,
    Ldi = 0x5,
    Ld  = 0x6,
    St  = 0x7,
    Beq = 0x8,
    Hlt = 0xF
};

struct Flags {
    bool z{false};
    bool n{false};
    bool c{false};
    bool v{false};
};

class CpuCore {
public:
    static constexpr size_t RegCount = 8;
    static constexpr size_t MemSize = 256;

    CpuCore() {
        reset();
    }

    void reset() noexcept {
        registers_.fill(0);
        pc_ = 0;
        flags_ = Flags{};
        halted_ = false;
        program_mem_.fill(0);
        data_mem_.fill(0);
    }

    void load_program(std::span<const uint16_t> binary, uint16_t start_addr = 0) {
        for (size_t i = 0; i < binary.size() && (start_addr + i) < MemSize; ++i) {
            program_mem_[start_addr + i] = binary[i];
        }
        pc_ = start_addr;
        halted_ = false;
    }

    void step() {
        if (halted_) return;

        // 1. Fetch
        const uint16_t instr = program_mem_[pc_ % MemSize];
        pc_++;

        // 2. Decode
        const auto op   = static_cast<Opcode>((instr >> 12) & 0x0F);
        const uint8_t rd  = (instr >> 9) & 0x07;
        const uint8_t rs1 = (instr >> 6) & 0x07;
        const uint8_t rs2 = (instr >> 3) & 0x07;
        const uint16_t imm9 = instr & 0x01FF;

        // 3. Execute & Write-Back
        switch (op) {
            case Opcode::Nop:
                break;

            case Opcode::Add: {
                const uint32_t a = registers_[rs1];
                const uint32_t b = registers_[rs2];
                const uint32_t res = a + b;
                const auto res16 = static_cast<uint16_t>(res);

                if (rd != 0) registers_[rd] = res16;

                flags_.z = (res16 == 0);
                flags_.n = (res16 & 0x8000) != 0;
                flags_.c = (res > 0xFFFF);
                flags_.v = (!((a ^ b) & 0x8000) && ((a ^ res) & 0x8000));
                break;
            }

            case Opcode::Sub: {
                const uint32_t a = registers_[rs1];
                const uint32_t b = registers_[rs2];
                const uint32_t res = a - b;
                const auto res16 = static_cast<uint16_t>(res);

                if (rd != 0) registers_[rd] = res16;

                flags_.z = (res16 == 0);
                flags_.n = (res16 & 0x8000) != 0;
                flags_.c = (a >= b);
                flags_.v = (((a ^ b) & 0x8000) && ((a ^ res) & 0x8000));
                break;
            }

            case Opcode::And: {
                const uint16_t res = registers_[rs1] & registers_[rs2];
                if (rd != 0) registers_[rd] = res;
                flags_.z = (res == 0);
                flags_.n = (res & 0x8000) != 0;
                break;
            }

            case Opcode::Or: {
                const uint16_t res = registers_[rs1] | registers_[rs2];
                if (rd != 0) registers_[rd] = res;
                flags_.z = (res == 0);
                flags_.n = (res & 0x8000) != 0;
                break;
            }

            case Opcode::Ldi: {
                if (rd != 0) registers_[rd] = static_cast<uint16_t>(sign_extend_9(imm9));
                break;
            }

            case Opcode::Ld: {
                const size_t addr = registers_[rs1] % MemSize;
                if (rd != 0) registers_[rd] = data_mem_[addr];
                break;
            }

            case Opcode::St: {
                const size_t addr = registers_[rs1] % MemSize;
                data_mem_[addr] = registers_[rs2];
                break;
            }

            case Opcode::Beq: {
                if (registers_[rd] == registers_[rs1]) {
                    const int16_t offset = sign_extend_9(imm9);
                    pc_ = static_cast<uint16_t>(static_cast<int16_t>(pc_) + offset);
                }
                break;
            }

            case Opcode::Hlt:
                halted_ = true;
                break;

            default:
                halted_ = true;
                break;
        }

        registers_[0] = 0; // R0 завжди нульовий
    }

    [[nodiscard]] bool is_halted() const noexcept { return halted_; }
    [[nodiscard]] uint16_t reg(size_t idx) const noexcept { return registers_.at(idx); }
    [[nodiscard]] uint16_t pc() const noexcept { return pc_; }
    [[nodiscard]] const Flags& flags() const noexcept { return flags_; }
    [[nodiscard]] uint16_t read_data(size_t addr) const noexcept { return data_mem_.at(addr % MemSize); }

private:
    static constexpr int16_t sign_extend_9(uint16_t val) noexcept {
        if (val & 0x0100) {
            return static_cast<int16_t>(val | 0xFE00);
        }
        return static_cast<int16_t>(val & 0x01FF);
    }

    std::array<uint16_t, RegCount> registers_{};
    uint16_t pc_{0};
    Flags flags_{};
    bool halted_{false};
    std::array<uint16_t, MemSize> program_mem_{};
    std::array<uint16_t, MemSize> data_mem_{};
};
```
:::

### Покрокове трасування тестової програми

Розглянемо виконання бінарної програми, що реалізує алгоритм циклічного обчислення суми натуральних чисел від `1` до `5` (математичний вираз `1 + 2 + 3 + 4 + 5 = 15`):

```
Адреса | Інструкція         | Бінарний код | Призначення
0x0000 | LDI R1, 5          | 0x5205       | R1 = 5 (лічильник циклу)
0x0001 | LDI R2, 0          | 0x5400       | R2 = 0 (акумулятор суми)
0x0002 | LDI R3, 1          | 0x5601       | R3 = 1 (декремент)
0x0003 | ADD R2, R2, R1     | 0x1490       | [Мітка LOOP]: R2 = R2 + R1
0x0004 | SUB R1, R1, R3     | 0x2258       | R1 = R1 - 1
0x0005 | BEQ R1, R0, 1      | 0x8201       | Якщо R1 == 0, перейти вперед на 1 інструкцію
0x0006 | BEQ R0, R0, -4     | 0x80FC       | Безумовний перехід назад на LOOP (зміщення -4)
0x0007 | ST  R2, [R0]       | 0x7010       | [Мітка END]: DataMem[0] = R2 (запис результату)
0x0008 | HLT                | 0xF000       | Зупинка ядра
```

Простежимо стан регістрів у часі:
- **Такт 1 (PC = 0x0000):** виконується `LDI R1, 5`. Стан: `R1 = 5`, `PC = 0x0001`.
- **Такт 2 (PC = 0x0001):** виконується `LDI R2, 0`. Стан: `R2 = 0`, `PC = 0x0002`.
- **Такт 3 (PC = 0x0002):** виконується `LDI R3, 1`. Стан: `R3 = 1`, `PC = 0x0003`.
- **Такт 4 (PC = 0x0003):** `ADD R2, R2, R1` → `R2 = 0 + 5 = 5`, `PC = 0x0004`.
- **Такт 5 (PC = 0x0004):** `SUB R1, R1, R3` → `R1 = 5 - 1 = 4`, `Z = 0`, `PC = 0x0005`.
- **Такт 6 (PC = 0x0005):** `BEQ R1, R0, 1` → умова хибна (`R1 != 0`), стрибок не відбувається, `PC = 0x0006`.
- **Такт 7 (PC = 0x0006):** `BEQ R0, R0, -4` → `R0 == R0` (істина), `PC = 0x0007 + (-4) = 0x0003` (повернення на `LOOP`).

Цикл повторюється 5 разів. На останній ітерації `R1` стає `0`, прапорець `Z` встановлюється в `1`, інструкція за адресою `0x0005` виконує стрибок через інструкцію повернення на адресу `0x0007`. Інструкція `ST` зберігає значення `15` у комірку оперативної пам'яті `DataMem[0]`, після чого команда `HLT` зупиняє процесор.

### Інженерні пастки та граничні умови реалізації ядра

1. **Апаратне знакове розширення від'ємних зміщень (Sign Extension Trap):**
   У 9-бітному полі `Immediate` число `-4` кодується як двійкове `1_1111_1100` (`0x01FC`). Якщо програмно помістити це число в 16-бітне беззнакове поле без тиражування 8-го біта знака, воно перетвориться на число `+508`. Замість стрибка назад на 4 інструкції процесор стрибне вперед на 508 слів, вийшовши за межі пам'яті коду. Функція `sign_extend_9` зобов'язана перевірити старший 8-й біт (`val & 0x0100`) і заповнити всі старші біти з 9 по 15 логічними одиницями (`val | 0xFE00`).

2. **Захист жорстко заземленого нульового регістра (`R0`):**
   В архітектурах RISC (MIPS, RISC-V, дане навчальне ядро) регістр `R0` виконує роль постійного джерела нуля для операцій безумовного переходу (`BEQ R0, R0, offset`), копіювання (`ADD Rd, Rs, R0`) та очищення пам'яті. Якщо дешифратор дозволить будь-якій арифметичній команді записати ненульове значення в `R0`, уся подальша логіка порівнянь і безумовних переходів миттєво зламається.

3. **Розмежування прапорців перенесення `C` та арифметичного переповнення `V`:**
   - Прапорець `C` (Carry) фіксує переповнення **беззнакової** арифметики: якщо сума двох 16-бітних чисел перевищує `65535`, виникає 17-й біт переносу (`res > 0xFFFF`). Під час віднімання `A - B` прапорець `C` свідчить про відсутність позики (`A >= B`).
   - Прапорець `V` (Overflow) фіксує переповнення **знакової** арифметики у форматі доповняльного коду (діапазон `-32768`..`+32767`). Додавання двох додатних чисел `0x4000 + 0x4000 = 0x8000` дає від'ємне число (`-32768`), що є знаковою помилкою переповнення (`V = 1`), хоча беззнакового переносу немає (`C = 0`).

### Методика верифікації та автоматизованого тестування

Для надійної перевірки поведінки емулятора створюють набір граничних тестів (*Corner Case Suite*), які перевіряють граничні переходи знакової сітки:
- **Перевірка переповнення додавання:** додавання чисел `0x7FFF + 0x0001 = 0x8000` повинно активувати прапорець `V = 1`, `N = 1` та скинути `C = 0`, `Z = 0`.
- **Перевірка перенесення беззнакових чисел:** операція `0xFFFF + 0x0001 = 0x0000` повинна сформувати прапорці `Z = 1`, `C = 1` та скинути `V = 0`, `N = 0`.
- **Перевірка знакової позики при відніманні:** віднімання `0x0000 - 0x0001 = 0xFFFF` повинно встановити `N = 1`, скинути `C = 0` (виникла позика) та `V = 0`.

Утиліти налагодження компілюються стандартними прапорцями компілятора GCC або Clang:
- Для версії C: `gcc -std=c11 -Wall -Wextra -O2 cpu_emulator.c -o cpu_emulator`
- Для версії C++: `g++ -std=c++20 -Wall -Wextra -O2 cpu_emulator.cpp -o cpu_emulator`

Такий тестовий стенд гарантує, що програмна модель процесора повністю повторює поведінку фізичної кремнієвої схеми з точністю до окремого розряду прапорців стану на кожному такті.
