// isa.hpp — система команд синтезованого 8-бітного ядра.
//
// Таблиця інструкцій constexpr: дешифратор у Cpu і складач прошивки в main
// беруть з неї одні й ті самі дані, а компілятор розгортає пошук ще на етапі
// збірки — рівно як матриця вентилів дешифратора «розгорнута» в кремнії.
#pragma once

#include <array>
#include <cstdint>
#include <optional>
#include <string_view>

namespace emu {

enum class Opcode : std::uint8_t {
    Nop         = 0x00,
    LoadImmAcc  = 0x01,
    LoadImmR0   = 0x02,
    LoadMemAcc  = 0x10,
    StoreMemAcc = 0x20,
    AddAccR0    = 0x30,
    SubAccR0    = 0x31,
    AndAccR0    = 0x32,
    XorAccR0    = 0x33,
    Jmp         = 0x40,
    Jz          = 0x41,
    Halt        = 0xFF
};

struct Instruction {
    Opcode           opcode;
    std::string_view mnemonic;
    unsigned         operand_bytes;   // 0, 1 або 2 байти одразу за опкодом
};

inline constexpr std::array<Instruction, 12> kIsa{{
    { Opcode::Nop,         "NOP",           0 },
    { Opcode::LoadImmAcc,  "LOAD_IMM_ACC",  1 },
    { Opcode::LoadImmR0,   "LOAD_IMM_R0",   1 },
    { Opcode::LoadMemAcc,  "LOAD_MEM_ACC",  2 },
    { Opcode::StoreMemAcc, "STORE_MEM_ACC", 2 },
    { Opcode::AddAccR0,    "ADD_ACC_R0",    0 },
    { Opcode::SubAccR0,    "SUB_ACC_R0",    0 },
    { Opcode::AndAccR0,    "AND_ACC_R0",    0 },
    { Opcode::XorAccR0,    "XOR_ACC_R0",    0 },
    { Opcode::Jmp,         "JMP",           2 },
    { Opcode::Jz,          "JZ",            2 },
    { Opcode::Halt,        "HALT",          0 }
}};

// Байт із шини — це ще не інструкція: дешифратор може й не знайти рядка.
[[nodiscard]] constexpr std::optional<Instruction> decode_opcode(std::uint8_t byte) noexcept
{
    for (const Instruction& entry : kIsa) {
        if (static_cast<std::uint8_t>(entry.opcode) == byte) {
            return entry;
        }
    }
    return std::nullopt;
}

[[nodiscard]] constexpr std::string_view mnemonic_of(std::uint8_t byte) noexcept
{
    const auto entry = decode_opcode(byte);
    return entry ? entry->mnemonic : std::string_view{"???"};
}

[[nodiscard]] constexpr unsigned operand_bytes_of(std::uint8_t byte) noexcept
{
    const auto entry = decode_opcode(byte);
    return entry ? entry->operand_bytes : 0u;
}

}  // namespace emu
