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
