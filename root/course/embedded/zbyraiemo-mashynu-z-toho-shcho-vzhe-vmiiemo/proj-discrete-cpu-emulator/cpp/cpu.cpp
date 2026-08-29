#include "cpu.hpp"

#include <format>
#include <iostream>
#include <string>

#include "isa.hpp"

namespace emu {

void Cpu::reset() noexcept
{
    regs_         = Registers{};
    halted_       = false;
    faulted_      = false;
    instructions_ = 0;
    bus_errors_   = 0;
}

void Cpu::report(BusFault fault, std::uint16_t addr)
{
    ++bus_errors_;
    std::cout << std::format("  [BUS ERROR] 0x{:04X}: {} — цикл проігноровано\n",
                             addr, describe(fault));
}

std::uint8_t Cpu::read_data(std::uint16_t addr)
{
    const auto value = bus_.read(addr);
    if (!value) {
        report(value.error(), addr);
        // Кристала немає, шина лишається підтягнутою: ядро прочитає одиниці
        // й піде далі, бо зупиняти його нема кому.
        return kOpenBus;
    }
    return *value;
}

void Cpu::write_data(std::uint16_t addr, std::uint8_t data)
{
    if (const auto result = bus_.write(addr, data); !result) {
        report(result.error(), addr);
    }
}

std::uint8_t Cpu::fetch_byte()
{
    return read_data(regs_.pc++);
}

std::uint16_t Cpu::fetch_address()
{
    const std::uint8_t lo = fetch_byte();
    const std::uint8_t hi = fetch_byte();
    return static_cast<std::uint16_t>(lo | (hi << 8));
}

void Cpu::alu_store(std::uint16_t raw_result, bool carry_out) noexcept
{
    regs_.acc    = static_cast<std::uint8_t>(raw_result & 0xFF);
    regs_.flag_z = (regs_.acc == 0);
    regs_.flag_c = carry_out;
}

void Cpu::logic_store(std::uint8_t result) noexcept
{
    // Логіка прапорця перенесення не чіпає: вихід переносу підключений
    // лише до суматора АЛП.
    regs_.acc    = result;
    regs_.flag_z = (regs_.acc == 0);
}

void Cpu::trace_instruction() const
{
    const std::uint8_t opcode   = bus_.peek(regs_.pc);
    const unsigned     operands = operand_bytes_of(opcode);

    std::string args;
    if (operands == 1) {
        args = std::format("0x{:02X}", bus_.peek(static_cast<std::uint16_t>(regs_.pc + 1)));
    } else if (operands == 2) {
        const unsigned lo = bus_.peek(static_cast<std::uint16_t>(regs_.pc + 1));
        const unsigned hi = bus_.peek(static_cast<std::uint16_t>(regs_.pc + 2));
        args = std::format("0x{:04X}", lo | (hi << 8));
    }

    std::cout << std::format("TICK {:3} | PC:0x{:04X} | {:<13} {:<6} | ACC:0x{:02X} R0:0x{:02X} Z:{:d} C:{:d}\n",
                             instructions_ + 1, regs_.pc, mnemonic_of(opcode), args,
                             regs_.acc, regs_.r0, regs_.flag_z, regs_.flag_c);
}

void Cpu::step()
{
    if (!running()) {
        return;
    }

    if (trace_) {
        trace_instruction();
    }

    // 1. Фаза вибірки (Fetch)
    const std::uint16_t instruction_pc = regs_.pc;
    regs_.ir = fetch_byte();
    ++instructions_;

    const auto instruction = decode_opcode(regs_.ir);
    if (!instruction) {
        // Дешифратор не має рядка під цей код операції.
        faulted_ = true;
        std::cout << std::format("  [CPU FAULT] Невідомий опкод 0x{:02X} за адресою 0x{:04X}\n",
                                 regs_.ir, instruction_pc);
        return;
    }

    // 2. Фази декодування та виконання (Decode & Execute)
    switch (instruction->opcode) {
        case Opcode::Nop:
            break;

        case Opcode::LoadImmAcc:
            regs_.acc = fetch_byte();
            break;

        case Opcode::LoadImmR0:
            regs_.r0 = fetch_byte();
            break;

        case Opcode::LoadMemAcc: {
            const std::uint16_t addr = fetch_address();
            regs_.acc = read_data(addr);   // третій шинний цикл — уже за даними
            break;
        }

        case Opcode::StoreMemAcc: {
            const std::uint16_t addr = fetch_address();
            write_data(addr, regs_.acc);
            break;
        }

        case Opcode::AddAccR0: {
            const std::uint16_t sum = static_cast<std::uint16_t>(regs_.acc + regs_.r0);
            alu_store(sum, sum > 0xFF);
            break;
        }

        case Opcode::SubAccR0: {
            // Позичка виникає, коли від'ємник більший за зменшуване: саме цей
            // сигнал дозволяє зшивати багаторозрядне віднімання з байтів.
            const bool          borrow = regs_.r0 > regs_.acc;
            const std::uint16_t diff   = static_cast<std::uint16_t>(regs_.acc - regs_.r0);
            alu_store(diff, borrow);
            break;
        }

        case Opcode::AndAccR0:
            logic_store(static_cast<std::uint8_t>(regs_.acc & regs_.r0));
            break;

        case Opcode::XorAccR0:
            logic_store(static_cast<std::uint8_t>(regs_.acc ^ regs_.r0));
            break;

        case Opcode::Jmp:
            regs_.pc = fetch_address();
            break;

        case Opcode::Jz: {
            // Операнд вибирається завжди — навіть коли перехід не відбувся:
            // інакше PC зупинився б посеред інструкції.
            const std::uint16_t target = fetch_address();
            if (regs_.flag_z) {
                regs_.pc = target;
                if (trace_) {
                    std::cout << std::format("  [BRANCH] Z=1, перехід на 0x{:04X}\n", target);
                }
            }
            break;
        }

        case Opcode::Halt:
            halted_ = true;
            if (trace_) {
                std::cout << "  [CPU] HALT: тактовий генератор ядра зупинено\n";
            }
            break;
    }
}

StopReason Cpu::run(unsigned long max_steps)
{
    for (unsigned long steps = 0; running(); ++steps) {
        if (steps >= max_steps) {
            // Прошивка з нескінченним циклом опитування — нормальний стан
            // залізяки, але емулятор мусить із нього вийти, а не висіти.
            std::cout << std::format("  [WATCHDOG] Вичерпано ліміт у {} інструкцій\n", max_steps);
            return StopReason::StepLimit;
        }
        step();
    }

    return faulted_ ? StopReason::Fault : StopReason::Halted;
}

}  // namespace emu
