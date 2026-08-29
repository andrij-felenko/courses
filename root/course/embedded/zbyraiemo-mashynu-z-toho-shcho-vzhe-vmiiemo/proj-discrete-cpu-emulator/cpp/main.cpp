// main.cpp — складач прошивок і запуск сценаріїв емуляції.
//
// Прошивки тут не набирають стовпчиком байтів: крихітний асемблер із мітками
// коштує півсотні рядків і знімає найпротивнішу помилку ручного асемблювання —
// адресу переходу, порахувану на око. Мітка, якої немає, зупиняє складання,
// а не дає ядру стрибнути в середину чужої інструкції.
#include <cstdint>
#include <exception>
#include <format>
#include <iostream>
#include <map>
#include <span>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include "cpu.hpp"
#include "isa.hpp"
#include "system_bus.hpp"

namespace {

using namespace emu;

class Assembler {
public:
    Assembler& op(Opcode opcode)
    {
        code_.push_back(std::to_underlying(opcode));
        return *this;
    }

    Assembler& imm(std::uint8_t value)
    {
        code_.push_back(value);
        return *this;
    }

    Assembler& addr(std::uint16_t address)
    {
        code_.push_back(static_cast<std::uint8_t>(address & 0x00FF));
        code_.push_back(static_cast<std::uint8_t>(address >> 8));
        return *this;
    }

    Assembler& label(std::string name)
    {
        const auto [it, inserted] = labels_.emplace(std::move(name), here());
        if (!inserted) {
            throw std::runtime_error(std::format("мітку '{}' оголошено двічі", it->first));
        }
        return *this;
    }

    // Опкод переходу разом із порожнім місцем під адресу: справжнє значення
    // підставить link(), коли всі мітки вже відомі.
    Assembler& jump(Opcode opcode, std::string target)
    {
        op(opcode);
        fixups_.emplace_back(code_.size(), std::move(target));
        code_.push_back(0x00);
        code_.push_back(0x00);
        return *this;
    }

    [[nodiscard]] std::uint16_t here() const noexcept
    {
        return static_cast<std::uint16_t>(code_.size());
    }

    [[nodiscard]] std::vector<std::uint8_t> link() const
    {
        std::vector<std::uint8_t> image = code_;
        for (const auto& [position, name] : fixups_) {
            const auto found = labels_.find(name);
            if (found == labels_.end()) {
                throw std::runtime_error(
                    std::format("невідома мітка '{}' у переході за зміщенням 0x{:04X}", name, position));
            }
            image[position]     = static_cast<std::uint8_t>(found->second & 0x00FF);
            image[position + 1] = static_cast<std::uint8_t>(found->second >> 8);
        }
        return image;
    }

private:
    std::vector<std::uint8_t>                         code_;
    std::map<std::string, std::uint16_t, std::less<>> labels_;
    std::vector<std::pair<std::size_t, std::string>>  fixups_;
};

// Сценарій 1: прошивка з покрокового розбору. Блимає світлодіодом через MMIO,
// віднімає й кладе результат у SRAM.
[[nodiscard]] std::vector<std::uint8_t> build_demo_firmware()
{
    Assembler asm_;
    asm_.op(Opcode::LoadImmR0).imm(0x01)              // R0 = 1
        .op(Opcode::LoadImmAcc).imm(0x01)             // ACC = 1
        .op(Opcode::StoreMemAcc).addr(kRegGpioOut)    // світлодіод УВІМКНЕНО
        .op(Opcode::LoadImmAcc).imm(0x00)             // ACC = 0
        .op(Opcode::StoreMemAcc).addr(kRegGpioOut)    // світлодіод ВИМКНЕНО
        .op(Opcode::LoadImmAcc).imm(0x03)             // ACC = 3
        .op(Opcode::SubAccR0)                         // ACC = 3 - 1 = 2
        .op(Opcode::StoreMemAcc).addr(0x4000)         // SRAM[0x4000] = 2
        .op(Opcode::Halt);
    return asm_.link();
}

// Сценарій 2: ядро крутиться в циклі опитування кнопки, а далі навмисно чіпає
// всі гострі кути карти адрес — переповнення суматора, запис у ROM, фантомну
// адресу периферії й порожнечу за межами підключених кристалів.
[[nodiscard]] std::vector<std::uint8_t> build_edge_firmware()
{
    Assembler asm_;
    asm_.op(Opcode::LoadImmR0).imm(0x01)              // маска біта кнопки
        .label("poll")
        .op(Opcode::LoadMemAcc).addr(kRegGpioIn)      // читаємо порт вводу
        .op(Opcode::AndAccR0)                         // лишаємо біт 0
        .jump(Opcode::Jz, "led_on")                   // нуль -> кнопку натиснуто
        .jump(Opcode::Jmp, "poll")                    // ні -> опитуємо далі
        .label("led_on")
        .op(Opcode::LoadImmAcc).imm(0x01)
        .op(Opcode::StoreMemAcc).addr(kRegGpioOut)    // світлодіод УВІМКНЕНО
        .op(Opcode::LoadImmAcc).imm(0xFF)
        .op(Opcode::AddAccR0)                         // 0xFF + 1: ACC = 0x00, C = 1
        .op(Opcode::StoreMemAcc).addr(0x4001)         // SRAM[0x4001] = 0x00
        .op(Opcode::XorAccR0)                         // ACC = 0x00 ^ 0x01 = 1
        .op(Opcode::StoreMemAcc).addr(0x0010)         // запис у ROM -> помилка шини
        .op(Opcode::LoadMemAcc).addr(0x8003)          // фантомна копія GPIO_IN
        .op(Opcode::LoadMemAcc).addr(0xC000)          // порожнеча -> 0xFF
        .op(Opcode::StoreMemAcc).addr(0x4002)         // SRAM[0x4002] = 0xFF
        .op(Opcode::Halt);
    return asm_.link();
}

StopReason run_scenario(std::string_view title, std::span<const std::uint8_t> image, unsigned button_press_after)
{
    std::cout << std::format("\n=== {} ===\n", title);

    SystemBus bus;
    bus.set_trace(true);
    bus.press_button_after(button_press_after);
    bus.load_rom(image);

    Cpu cpu{bus};
    cpu.reset();
    cpu.set_trace(true);
    std::cout << std::format("[RESET] PC=0x{:04X}, {} байтів прошивки в ROM\n\n",
                             cpu.registers().pc, image.size());

    const StopReason reason = cpu.run();
    const auto&      regs   = cpu.registers();

    std::cout << std::format("\n--- Підсумок: {} ---\n", describe(reason));
    std::cout << std::format("Інструкцій виконано : {}\n", cpu.instructions());
    std::cout << std::format("Шинних циклів       : {}\n", bus.cycles());
    std::cout << std::format("Помилок шини        : {}\n", cpu.bus_errors());
    std::cout << std::format("Прапорці            : Z={:d} C={:d}\n", regs.flag_z, regs.flag_c);
    std::cout << std::format("GPIO_OUT (засувка)  : 0x{:02X} (світлодіод {})\n",
                             bus.gpio_out_latch(), bus.led_on() ? "світить" : "згас");
    std::cout << std::format("SRAM[0x4000..0x4002]: 0x{:02X} 0x{:02X} 0x{:02X}\n",
                             bus.ram_at(0x4000), bus.ram_at(0x4001), bus.ram_at(0x4002));

    return reason;
}

}  // namespace

int main()
{
    try {
        const std::vector<std::uint8_t> demo_firmware = build_demo_firmware();
        const std::vector<std::uint8_t> edge_firmware = build_edge_firmware();

        const emu::StopReason demo =
            run_scenario("СЦЕНАРІЙ 1: блимання світлодіодом і запис у SRAM",
                         demo_firmware, /*button_press_after=*/~0u);

        // Кнопку натискають після третього опитування: до того цикл опитування
        // крутиться вхолосту, як і на справжній платі.
        const emu::StopReason edge =
            run_scenario("СЦЕНАРІЙ 2: кнопка, переповнення та гострі кути карти адрес",
                         edge_firmware, /*button_press_after=*/3u);

        const bool clean = demo == emu::StopReason::Halted && edge == emu::StopReason::Halted;
        return clean ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << std::format("[FATAL] {}\n", error.what());
        return 1;
    }
}
