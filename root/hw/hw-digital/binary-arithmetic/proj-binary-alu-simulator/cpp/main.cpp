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
