# ⚙️ Програмне моделювання двійкового АЛУ: схемотехнічна емуляція та прапорці стану

Програмна емуляція арифметико-логічного пристрою (АЛУ) на рівні побітових операцій дозволяє дослідити роботу логічних вентилів безпосередньо в коді та зрозуміти механіку виставлення прапорців стану процесора (`Z`, `N`, `C`, `V`). У цьому проєкті ми створимо повноцінний симулятор 8-бітного АЛУ, що імітує апаратний тракт обчислень: вентилі однобітних суматорів, керований інвертор операнда для віднімання, схему паралельного формування переносів та блок декодування прапорців.

### Архітектура та принципи побудови емулятора

Реальне кремнієве АЛУ не використовує високорівневі математичні інструкції, а оперує виключно бітовими лініями. Щоб відтворити поведінку апаратного блоку, симулятор розбивається на окремі функціональні вузли:

1. **Комбінаційний однобітний повний суматор (Full Adder Cell):** реалізує базові булеві рівняння `S = A ⊕ B ⊕ Cin` та `Cout = (A · B) + Cin · (A ⊕ B)`. Усі проміжні значення обчислюються суто логічними операціями XOR, AND та OR.
2. **Керований інвертор знака (Subtractor Stage):** операнд `B` проходить через побітовий XOR із сигналом операції `SubMode`. Якщо `SubMode = 1`, біти `B` інвертуються, а на молодший вхідний перенос `Cin[0]` подається 1, що реалізує доповняльний код `A + (~B) + 1 = A - B`. Це усуває потребу в окремій схемі віднімання.
3. **Блок паралельного переносу (Lookahead Carry Generator):** заздалегідь обчислює вектори генерації `G` та розповсюдження `P` для всіх розрядів, дозволяючи простежити формування переносу між бітовими зрізами.
4. **Логічно-зсувний тракт:** паралельно з суматором виконує побітові операції AND, OR, XOR, NOT, а також логічний та арифметичний зсуви (LSL, LSR, ASR). В арифметичному зсуві вправо (ASR) старший біт дублюється для збереження математичного знака від'ємного числа.
5. **Мультиплексор вихідних даних:** за кодом операції (Opcode) комутує відповідний результат на вихідну шину, блокуючи неактивні результати.
6. **Детектор прапорців стану (Condition Flags Unit):** аналізує проміжні переноси та фінальний результат для формування прапорців процесорного регістра `EFLAGS/APSR`.

### Схемотехнічне формування прапорців стану

Кожна арифметична операція супроводжується оновленням регістра прапорців, на основі яких процесор виконує інструкції умовних переходів:

- **Zero Flag (`Z`):** встановлюється в 1, якщо всі 8 бітів вихідного результату дорівнюють нулю. Апаратно це реалізується багатовходовим елементом NOR над усіма лініями вихідної шини результату: `Z = ~(S[7] | S[6] | ... | S[0])`.
- **Negative Flag (`N`):** копіює старший знаковий біт результату: `N = S[7]`. Якщо `N = 1`, число інтерпретується як від'ємне у форматі доповняльного коду.
- **Carry Flag (`C`):** фіксує перенос із найстаршого 7-го розряду суматора: `C = Cout[7]`. Для беззнакових чисел `C = 1` сигналізує про вихід за межі діапазону `[0, 255]`. При відніманні прапорець показує факт позики (Borrow). В архітектурі x86 прапорець переносу інвертується при відніманні для індикації позики (`Borrow = ~Cout`), тоді як в архітектурі ARM прапорець `C` напряму зберігає `Cout` (де `1` означає відсутність позики).
- **Overflow Flag (`V`):** сигналізує про переповнення розрядної сітки знакових чисел (діапазон `[-128, +127]`). Знакове переповнення виникає тоді й лише тоді, коли перенос на вході старшого біта `Cin[7]` не збігається з переносом на його виході `Cout[7]`. Апаратна схема детектора переповнення складається лише з одного двовходового елемента XOR: `V = Cin[7] ⊕ Cout[7]`.

### Порівняння беззнакового (Carry) та знакового (Overflow) переповнення

Фундаментальний принцип архітектури процесорів полягає в тому, що АЛУ виконує абсолютно ідентичні побітові операції незалежно від того, якими даними оперує програміст — знаковими (`int8_t`) чи беззнаковими (`uint8_t`). Кремнієві вентилі не знають типу даних змінної: вони просто додають біти й одночасно виставляють обидва прапорці `C` та `V`.

Компілятор обирає, який саме прапорець перевіряти, відповідно до типів змінних у вихідному коді:
- Для беззнакового порівняння `if (a < b)` генеруються інструкції `CMP` та `JB` (Jump if Below), які перевіряють стан прапорця `C`.
- Для знакового порівняння `if (a < b)` генеруються інструкції `CMP` та `JL` (Jump if Less), які перевіряють логічну умову `N ⊕ V = 1`.

### Реалізація симулятора

Нижче наведено повні та взаємно еквівалентні реалізації симулятора мовами C та C++. У версії C++ використано сучасні ідіоми: інкапсуляцію в клас, структуровані типи з ініціалізаторами полів, строгу типізацію переліків `enum class`, форматований вивід через `<iostream>` та метод вичерпної верифікації (Exhaustive Self-Test). У версії C використано чистий процедурний стиль зі структурами, явним передаванням вказівників і функціями з `printf`.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    ALU_OP_ADD = 0,
    ALU_OP_SUB = 1,
    ALU_OP_AND = 2,
    ALU_OP_OR  = 3,
    ALU_OP_XOR = 4,
    ALU_OP_NOT = 5,
    ALU_OP_LSL = 6,
    ALU_OP_LSR = 7,
    ALU_OP_ASR = 8
} alu_opcode_t;

typedef struct {
    bool C; /* Carry / Borrow */
    bool Z; /* Zero */
    bool N; /* Negative / Sign */
    bool V; /* Overflow */
} alu_flags_t;

typedef struct {
    alu_flags_t flags;
} alu_t;

void alu_init(alu_t *alu) {
    alu->flags.C = false;
    alu->flags.Z = false;
    alu->flags.N = false;
    alu->flags.V = false;
}

/* Однобітний повний суматор на вентилях */
static inline void full_adder_bit(bool a, bool b, bool cin, bool *sum, bool *cout) {
    *sum = a ^ b ^ cin;
    *cout = (a & b) | (cin & (a ^ b));
}

uint8_t alu_execute(alu_t *alu, alu_opcode_t op, uint8_t a, uint8_t b) {
    uint8_t result = 0;
    alu->flags.C = false;
    alu->flags.V = false;

    if (op == ALU_OP_ADD || op == ALU_OP_SUB) {
        bool is_sub = (op == ALU_OP_SUB);
        bool carry = is_sub; /* Cin[0] = 1 при відніманні для доповняльного коду */
        bool last_cin = false;

        for (int i = 0; i < 8; ++i) {
            bool a_bit = (a >> i) & 1;
            bool b_bit = (b >> i) & 1;
            bool b_effective = b_bit ^ is_sub; /* Керований інвертор B */

            if (i == 7) {
                last_cin = carry; /* Зберігаємо вхідний перенос у старший 7-й біт */
            }

            bool s_bit, cout_bit;
            full_adder_bit(a_bit, b_effective, carry, &s_bit, &cout_bit);
            result |= (s_bit << i);
            carry = cout_bit;
        }

        /* Обчислення апаратних прапорців */
        alu->flags.C = carry;                     /* Беззнаковий перенос / вихід із 7-го біта */
        alu->flags.V = last_cin ^ carry;          /* V = Cin[7] XOR Cout[7] */
    } else {
        switch (op) {
            case ALU_OP_AND: result = a & b; break;
            case ALU_OP_OR:  result = a | b; break;
            case ALU_OP_XOR: result = a ^ b; break;
            case ALU_OP_NOT: result = ~a;    break;
            case ALU_OP_LSL:
                alu->flags.C = (a & 0x80) != 0;
                result = (uint8_t)(a << 1);
                break;
            case ALU_OP_LSR:
                alu->flags.C = (a & 0x01) != 0;
                result = (uint8_t)(a >> 1);
                break;
            case ALU_OP_ASR:
                alu->flags.C = (a & 0x01) != 0;
                result = (uint8_t)(((int8_t)a) >> 1);
                break;
            default: break;
        }
    }

    /* Прапорці Zero та Negative визначаються для всіх операцій */
    alu->flags.Z = (result == 0);
    alu->flags.N = (result & 0x80) != 0;

    return result;
}

void print_alu_state(const char *name, uint8_t a, uint8_t b, uint8_t res, const alu_flags_t *f) {
    printf("%-5s: A=0x%02X (%4d) | B=0x%02X (%4d) -> RES=0x%02X (%4d) | Flags: [Z=%d N=%d C=%d V=%d]\n",
           name, a, (int8_t)a, b, (int8_t)b, res, (int8_t)res, f->Z, f->N, f->C, f->V);
}

int main(void) {
    alu_t alu;
    alu_init(&alu);

    printf("=== Демонстрація роботи 8-бітного симулятора АЛУ (C) ===\n\n");

    /* Тест 1: Звичайне додавання без прапорців */
    uint8_t r1 = alu_execute(&alu, ALU_OP_ADD, 0x14, 0x1E); /* 20 + 30 = 50 */
    print_alu_state("ADD", 0x14, 0x1E, r1, &alu.flags);

    /* Тест 2: Беззнакове переповнення (Carry) */
    uint8_t r2 = alu_execute(&alu, ALU_OP_ADD, 0xFF, 0x01); /* 255 + 1 = 0, C=1, Z=1 */
    print_alu_state("ADD", 0xFF, 0x01, r2, &alu.flags);

    /* Тест 3: Знакове переповнення (Overflow) */
    uint8_t r3 = alu_execute(&alu, ALU_OP_ADD, 0x7F, 0x01); /* +127 + 1 = -128, V=1, N=1 */
    print_alu_state("ADD", 0x7F, 0x01, r3, &alu.flags);

    /* Тест 4: Віднімання з позикою */
    uint8_t r4 = alu_execute(&alu, ALU_OP_SUB, 0x05, 0x0A); /* 5 - 10 = -5 (0xFB) */
    print_alu_state("SUB", 0x05, 0x0A, r4, &alu.flags);

    /* Тест 5: Логічний зсув вліво */
    uint8_t r5 = alu_execute(&alu, ALU_OP_LSL, 0x85, 0x00); /* 10000101 << 1 = 00001010, C=1 */
    print_alu_state("LSL", 0x85, 0x00, r5, &alu.flags);

    return 0;
}
```
```cpp
#include <iostream>
#include <cstdint>
#include <iomanip>
#include <string_view>

enum class AluOpcode {
    Add = 0,
    Sub = 1,
    And = 2,
    Or  = 3,
    Xor = 4,
    Not = 5,
    Lsl = 6,
    Lsr = 7,
    Asr = 8
};

struct AluFlags {
    bool C{false}; // Carry / Borrow
    bool Z{false}; // Zero
    bool N{false}; // Negative
    bool V{false}; // Overflow
};

class BinaryAlu {
public:
    AluFlags flags{};

    // Однобітний вентильний повний суматор
    static constexpr std::pair<bool, bool> fullAdderBit(bool a, bool b, bool cin) noexcept {
        bool sum = a ^ b ^ cin;
        bool cout = (a & b) | (cin & (a ^ b));
        return {sum, cout};
    }

    uint8_t execute(AluOpcode op, uint8_t a, uint8_t b) noexcept {
        uint8_t result = 0;
        flags.C = false;
        flags.V = false;

        if (op == AluOpcode::Add || op == AluOpcode::Sub) {
            const bool isSub = (op == AluOpcode::Sub);
            bool carry = isSub; // Cin[0] = 1 при відніманні для доповняльного коду
            bool lastCin = false;

            for (int i = 0; i < 8; ++i) {
                const bool aBit = (a >> i) & 1;
                const bool bBit = (b >> i) & 1;
                const bool bEffective = bBit ^ isSub; // Інверсія B при Sub

                if (i == 7) {
                    lastCin = carry; // Вхідний перенос у старший знаковий розряд
                }

                const auto [sBit, coutBit] = fullAdderBit(aBit, bEffective, carry);
                result |= (static_cast<uint8_t>(sBit) << i);
                carry = coutBit;
            }

            flags.C = carry;              // Вихідний перенос із 7-го розряду
            flags.V = lastCin ^ carry;    // Апаратне переповнення V = Cin[7] XOR Cout[7]
        } else {
            switch (op) {
                case AluOpcode::And: result = a & b; break;
                case AluOpcode::Or:  result = a | b; break;
                case AluOpcode::Xor: result = a ^ b; break;
                case AluOpcode::Not: result = static_cast<uint8_t>(~a); break;
                case AluOpcode::Lsl:
                    flags.C = (a & 0x80) != 0;
                    result = static_cast<uint8_t>(a << 1);
                    break;
                case AluOpcode::Lsr:
                    flags.C = (a & 0x01) != 0;
                    result = static_cast<uint8_t>(a >> 1);
                    break;
                case AluOpcode::Asr:
                    flags.C = (a & 0x01) != 0;
                    result = static_cast<uint8_t>(static_cast<int8_t>(a) >> 1);
                    break;
            }
        }

        flags.Z = (result == 0);
        flags.N = (result & 0x80) != 0;

        return result;
    }
};

void printState(std::string_view opName, uint8_t a, uint8_t b, uint8_t res, const AluFlags& f) {
    std::cout << std::left << std::setw(5) << opName << ": "
              << "A=0x" << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(a)
              << " (" << std::dec << std::setw(4) << std::setfill(' ') << static_cast<int>(static_cast<int8_t>(a)) << ") | "
              << "B=0x" << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(b)
              << " (" << std::dec << std::setw(4) << std::setfill(' ') << static_cast<int>(static_cast<int8_t>(b)) << ") -> "
              << "RES=0x" << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(res)
              << " (" << std::dec << std::setw(4) << std::setfill(' ') << static_cast<int>(static_cast<int8_t>(res)) << ") | "
              << "Flags: [Z=" << f.Z << " N=" << f.N << " C=" << f.C << " V=" << f.V << "]\n";
}

int main() {
    BinaryAlu alu;

    std::cout << "=== Демонстрація роботи 8-бітного симулятора АЛУ (C++) ===\n\n";

    // Тест 1: Звичайне додавання без прапорців
    uint8_t r1 = alu.execute(AluOpcode::Add, 0x14, 0x1E); // 20 + 30 = 50
    printState("ADD", 0x14, 0x1E, r1, alu.flags);

    // Тест 2: Беззнакове переповнення (Carry)
    uint8_t r2 = alu.execute(AluOpcode::Add, 0xFF, 0x01); // 255 + 1 = 0, C=1, Z=1
    printState("ADD", 0xFF, 0x01, r2, alu.flags);

    // Тест 3: Знакове переповнення (Overflow)
    uint8_t r3 = alu.execute(AluOpcode::Add, 0x7F, 0x01); // +127 + 1 = -128, V=1, N=1
    printState("ADD", 0x7F, 0x01, r3, alu.flags);

    // Тест 4: Віднімання з позикою
    uint8_t r4 = alu.execute(AluOpcode::Sub, 0x05, 0x0A); // 5 - 10 = -5 (0xFB)
    printState("SUB", 0x05, 0x0A, r4, alu.flags);

    // Тест 5: Логічний зсув вліво
    uint8_t r5 = alu.execute(AluOpcode::Lsl, 0x85, 0x00); // 10000101 << 1 = 00001010, C=1
    printState("LSL", 0x85, 0x00, r5, alu.flags);

    // Вичерпна верифікація: перевірка всіх 65 536 комбінацій для ADD
    bool allValid = true;
    for (int a = 0; a <= 255; ++a) {
        for (int b = 0; b <= 255; ++b) {
            uint8_t res = alu.execute(AluOpcode::Add, static_cast<uint8_t>(a), static_cast<uint8_t>(b));
            bool expectedCarry = (a + b) > 255;
            int signedA = static_cast<int8_t>(a);
            int signedB = static_cast<int8_t>(b);
            int signedSum = signedA + signedB;
            bool expectedOverflow = (signedSum < -128) || (signedSum > 127);

            if (alu.flags.C != expectedCarry || alu.flags.V != expectedOverflow) {
                allValid = false;
                break;
            }
        }
    }

    std::cout << "\n[Верифікація] 65536 тестових векторів ADD: "
              << (allValid ? "УСПІШНО ПРОЙДЕНО" : "ПОМИЛКА") << "\n";

    return 0;
}
```
:::

### Результати тестування та інтерпретація станів

Тестовий прогін наочно демонструє ключові сценарії цифрової арифметики:

1. **Додавання `0x14 + 0x1E = 0x32` (20 + 30 = 50):** результат лежить у межах обох числових діапазонів (знакового та беззнакового). Усі прапорці залишаються в стані `0`.
2. **Беззнакове переповнення `0xFF + 0x01 = 0x00` (255 + 1 = 256 → 0):** результат обнуляється в 8-бітній сітці, тому встановлюються прапорці `Z = 1` та `C = 1`. Проте знакового переповнення немає (`V = 0`), оскільки для знакових чисел операція відповідала `-1 + 1 = 0`, що є математично коректним результатом.
3. **Знакове переповнення `0x7F + 0x01 = 0x80` (+127 + 1 = 128 → -128):** результат у двійковому вигляді має старшу одиницю (`0b10000000`), що у форматі доповняльного коду інтерпретується як число `-128`. Відбулося додавання двох додатних операндів, яке дало від'ємний результат. Апаратний детектор фіксує це через невідповідність переносів `Cin[7] = 1` та `Cout[7] = 0`, встановлюючи прапорець `V = 1` (разом із `N = 1`). Беззнакового переносу немає (`C = 0`), оскільки `128 < 256`.
4. **Вичерпна валідація:** автоматичний тестовий цикл перевіряє всі 65 536 комбінацій вхідних байтів, порівнюючи результат обчислення за формулою `V = Cin[7] ⊕ Cout[7]` з еталонним математичним діапазоном `[-128, 127]`. Це на 100% підтверджує строгу математичну еквівалентність одновентильного XOR-детектора переповнення.
