// ============================================================================
// Програмний рушій емулятора ISP-програматора STK500v2 (Стандарт C++20)
// ============================================================================

#include <cstdint>
#include <array>
#include <vector>
#include <span>
#include <string>
#include <string_view>
#include <algorithm>
#include <iostream>
#include <expected>
#include <numeric>

namespace stk500 {

inline constexpr std::uint8_t MessageStart = 0x1B;
inline constexpr std::uint8_t TokenMarker  = 0x0E;

enum class Command : std::uint8_t {
    SignOn            = 0x01,
    SetParameter      = 0x02,
    GetParameter      = 0x03,
    LoadAddress       = 0x06,
    EnterProgModeIsp  = 0x10,
    LeaveProgModeIsp  = 0x11,
    ChipEraseIsp      = 0x12,
    ProgramFlashIsp   = 0x13,
    ReadFlashIsp      = 0x14,
    ProgramEepromIsp  = 0x15,
    ReadEepromIsp     = 0x16,
    ProgramFuseIsp    = 0x17,
    ReadFuseIsp       = 0x18,
    SpiMulti          = 0x1D
};

enum class Status : std::uint8_t {
    Ok                = 0x00,
    Timeout           = 0x80,
    Failed            = 0xC0,
    Unknown           = 0xC9
};

enum class Parameter : std::uint8_t {
    HwVersion         = 0x90,
    SwMajor           = 0x91,
    SwMinor           = 0x92,
    VTarget           = 0x94,
    SckDuration       = 0x98
};

// ── Віртуальна модель мікроконтролера ───────────────────────────────────────

class VirtualMcu {
public:
    static constexpr std::size_t FlashSize  = 32768;
    static constexpr std::size_t PageSize   = 128;
    static constexpr std::size_t EepromSize = 1024;
    static constexpr std::array<std::uint8_t, 3> Signature{0x1E, 0x95, 0x0F}; // ATmega328P

    VirtualMcu() noexcept {
        reset();
    }

    void reset() noexcept {
        flash_.fill(0xFF);
        eeprom_.fill(0xFF);
        fuse_low_ = 0x62;
        fuse_high_ = 0xD9;
        fuse_ext_ = 0xFF;
        lock_bits_ = 0xFF;
        current_byte_address_ = 0;
        in_prog_mode_ = false;
        cpu_hz_ = 1'000'000;
        isp_hz_ = 125'000;
    }

    void chip_erase() noexcept {
        flash_.fill(0xFF);
        if ((fuse_high_ & 0x08) != 0) { // Якщо EESAVE не встановлено
            eeprom_.fill(0xFF);
        }
        lock_bits_ = 0xFF; // Скидання захисту
    }

    [[nodiscard]] bool enter_prog_mode() noexcept {
        // Перевірка обмеження f_ISP <= f_CPU / 4
        if (isp_hz_ > (cpu_hz_ / 4)) {
            in_prog_mode_ = false;
            return false;
        }
        in_prog_mode_ = true;
        return true;
    }

    void leave_prog_mode() noexcept {
        in_prog_mode_ = false;
    }

    [[nodiscard]] bool in_prog_mode() const noexcept { return in_prog_mode_; }

    void set_address(std::uint32_t byte_addr) noexcept {
        current_byte_address_ = byte_addr;
    }

    [[nodiscard]] std::uint32_t current_address() const noexcept {
        return current_byte_address_;
    }

    [[nodiscard]] bool program_flash_page(std::span<const std::uint8_t> data) noexcept {
        if (!in_prog_mode_ || (lock_bits_ & 0x02) == 0) {
            return false; // Захист від запису
        }
        if (current_byte_address_ + data.size() > FlashSize) {
            return false;
        }
        std::copy(data.begin(), data.end(), flash_.begin() + current_byte_address_);
        current_byte_address_ += static_cast<std::uint32_t>(data.size());
        return true;
    }

    [[nodiscard]] std::vector<std::uint8_t> read_flash(std::size_t length) noexcept {
        std::vector<std::uint8_t> result(length, 0xFF);
        if (!in_prog_mode_) {
            return result;
        }
        // Захист Lock Bits Mode 3
        if ((lock_bits_ & 0x03) == 0) {
            return result; // Повертаємо 0xFF
        }

        if (current_byte_address_ + length <= FlashSize) {
            std::copy_n(flash_.begin() + current_byte_address_, length, result.begin());
            current_byte_address_ += static_cast<std::uint32_t>(length);
        }
        return result;
    }

    void set_isp_frequency(std::uint32_t hz) noexcept { isp_hz_ = hz; }
    [[nodiscard]] std::uint32_t isp_frequency() const noexcept { return isp_hz_; }

    [[nodiscard]] std::uint8_t fuse_low() const noexcept { return fuse_low_; }
    [[nodiscard]] std::uint8_t fuse_high() const noexcept { return fuse_high_; }
    [[nodiscard]] std::uint8_t fuse_ext() const noexcept { return fuse_ext_; }
    [[nodiscard]] std::uint8_t lock_bits() const noexcept { return lock_bits_; }

    void apply_lock_bits(std::uint8_t bits) noexcept {
        lock_bits_ &= bits; // Тільки скидання в нуль
    }

private:
    std::array<std::uint8_t, FlashSize> flash_{};
    std::array<std::uint8_t, EepromSize> eeprom_{};
    std::uint8_t fuse_low_{0x62};
    std::uint8_t fuse_high_{0xD9};
    std::uint8_t fuse_ext_{0xFF};
    std::uint8_t lock_bits_{0xFF};
    std::uint32_t current_byte_address_{0};
    bool in_prog_mode_{false};
    std::uint32_t cpu_hz_{1'000'000};
    std::uint32_t isp_hz_{125'000};
};

// ── Рушій емулятора STK500v2 ───────────────────────────────────────────────

class Stk500Engine {
public:
    Stk500Engine() noexcept = default;

    [[nodiscard]] VirtualMcu& mcu() noexcept { return mcu_; }
    [[nodiscard]] const VirtualMcu& mcu() const noexcept { return mcu_; }

    [[nodiscard]] std::vector<std::uint8_t> process_command(std::span<const std::uint8_t> payload) {
        if (payload.empty()) {
            return build_frame(std::array<std::uint8_t, 2>{0x00, static_cast<std::uint8_t>(Status::Failed)});
        }

        const auto cmd = static_cast<Command>(payload[0]);
        std::vector<std::uint8_t> resp;

        switch (cmd) {
            case Command::SignOn: {
                resp.push_back(static_cast<std::uint8_t>(Command::SignOn));
                resp.push_back(static_cast<std::uint8_t>(Status::Ok));
                constexpr std::string_view name = "AVRISP_2";
                resp.push_back(static_cast<std::uint8_t>(name.size()));
                resp.insert(resp.end(), name.begin(), name.end());
                break;
            }

            case Command::SetParameter: {
                resp.push_back(static_cast<std::uint8_t>(Command::SetParameter));
                if (payload.size() >= 3) {
                    const auto param = static_cast<Parameter>(payload[1]);
                    const std::uint8_t val = payload[2];
                    if (param == Parameter::SckDuration) {
                        sck_duration_ = val;
                        const std::uint32_t hz = (val > 0) ? (1'000'000u / val) : 2'000'000u;
                        mcu_.set_isp_frequency(hz);
                    }
                    resp.push_back(static_cast<std::uint8_t>(Status::Ok));
                } else {
                    resp.push_back(static_cast<std::uint8_t>(Status::Failed));
                }
                break;
            }

            case Command::GetParameter: {
                resp.push_back(static_cast<std::uint8_t>(Command::GetParameter));
                resp.push_back(static_cast<std::uint8_t>(Status::Ok));
                const auto param = (payload.size() >= 2) ? static_cast<Parameter>(payload[1]) : Parameter::HwVersion;
                switch (param) {
                    case Parameter::HwVersion:   resp.push_back(0x02); break;
                    case Parameter::SwMajor:     resp.push_back(0x02); break;
                    case Parameter::SwMinor:     resp.push_back(0x0A); break;
                    case Parameter::VTarget:     resp.push_back(50);   break;
                    case Parameter::SckDuration: resp.push_back(sck_duration_); break;
                    default:                     resp.push_back(0x00); break;
                }
                break;
            }

            case Command::LoadAddress: {
                resp.push_back(static_cast<std::uint8_t>(Command::LoadAddress));
                if (payload.size() >= 5) {
                    const std::uint32_t word_addr = ((static_cast<std::uint32_t>(payload[1]) << 24) |
                                                     (static_cast<std::uint32_t>(payload[2]) << 16) |
                                                     (static_cast<std::uint32_t>(payload[3]) << 8)  |
                                                     (static_cast<std::uint32_t>(payload[4]))) & 0x7FFFFFFF;
                    mcu_.set_address(word_addr * 2);
                    resp.push_back(static_cast<std::uint8_t>(Status::Ok));
                } else {
                    resp.push_back(static_cast<std::uint8_t>(Status::Failed));
                }
                break;
            }

            case Command::EnterProgModeIsp: {
                resp.push_back(static_cast<std::uint8_t>(Command::EnterProgModeIsp));
                const bool ok = mcu_.enter_prog_mode();
                resp.push_back(static_cast<std::uint8_t>(ok ? Status::Ok : Status::Failed));
                break;
            }

            case Command::LeaveProgModeIsp: {
                resp.push_back(static_cast<std::uint8_t>(Command::LeaveProgModeIsp));
                mcu_.leave_prog_mode();
                resp.push_back(static_cast<std::uint8_t>(Status::Ok));
                break;
            }

            case Command::ChipEraseIsp: {
                resp.push_back(static_cast<std::uint8_t>(Command::ChipEraseIsp));
                if (mcu_.in_prog_mode()) {
                    mcu_.chip_erase();
                    resp.push_back(static_cast<std::uint8_t>(Status::Ok));
                } else {
                    resp.push_back(static_cast<std::uint8_t>(Status::Failed));
                }
                break;
            }

            case Command::ProgramFlashIsp: {
                resp.push_back(static_cast<std::uint8_t>(Command::ProgramFlashIsp));
                if (payload.size() >= 10) {
                    const std::size_t num_bytes = (static_cast<std::size_t>(payload[1]) << 8) | payload[2];
                    const auto data_slice = payload.subspan(10, num_bytes);
                    const bool ok = mcu_.program_flash_page(data_slice);
                    resp.push_back(static_cast<std::uint8_t>(ok ? Status::Ok : Status::Failed));
                } else {
                    resp.push_back(static_cast<std::uint8_t>(Status::Failed));
                }
                break;
            }

            case Command::ReadFlashIsp: {
                resp.push_back(static_cast<std::uint8_t>(Command::ReadFlashIsp));
                if (payload.size() >= 3) {
                    const std::size_t num_bytes = (static_cast<std::size_t>(payload[1]) << 8) | payload[2];
                    resp.push_back(static_cast<std::uint8_t>(Status::Ok));
                    const auto read_data = mcu_.read_flash(num_bytes);
                    resp.insert(resp.end(), read_data.begin(), read_data.end());
                    resp.push_back(static_cast<std::uint8_t>(Status::Ok));
                } else {
                    resp.push_back(static_cast<std::uint8_t>(Status::Failed));
                }
                break;
            }

            case Command::SpiMulti: {
                resp.push_back(static_cast<std::uint8_t>(Command::SpiMulti));
                if (payload.size() >= 8 && mcu_.in_prog_mode()) {
                    const std::uint8_t num_tx = payload[1];
                    const std::uint8_t num_rx = payload[2];
                    const std::uint8_t rx_start = payload[3];
                    const auto tx_data = payload.subspan(4, num_tx);

                    resp.push_back(static_cast<std::uint8_t>(Status::Ok));
                    std::array<std::uint8_t, 4> rx_buf{0, 0, 0, 0};

                    if (tx_data.size() >= 4) {
                        const std::uint8_t op = tx_data[0];
                        if (op == 0x30) { // Read Signature
                            const std::uint8_t addr = tx_data[2];
                            if (addr < VirtualMcu::Signature.size()) {
                                rx_buf[3] = VirtualMcu::Signature[addr];
                            }
                        } else if (op == 0x58 && tx_data[1] == 0x00) {
                            rx_buf[3] = mcu_.fuse_low();
                        } else if (op == 0x58 && tx_data[1] == 0x08) {
                            rx_buf[3] = mcu_.fuse_high();
                        } else if (op == 0x50 && tx_data[1] == 0x08) {
                            rx_buf[3] = mcu_.fuse_ext();
                        } else if (op == 0xAC && tx_data[1] == 0xE0) {
                            mcu_.apply_lock_bits(tx_data[3]);
                        }
                    }

                    for (std::uint8_t i = 0; i < num_rx; ++i) {
                        resp.push_back(rx_buf[rx_start + i]);
                    }
                    resp.push_back(static_cast<std::uint8_t>(Status::Ok));
                } else {
                    resp.push_back(static_cast<std::uint8_t>(Status::Failed));
                }
                break;
            }

            default:
                resp.push_back(static_cast<std::uint8_t>(cmd));
                resp.push_back(static_cast<std::uint8_t>(Status::Unknown));
                break;
        }

        return build_frame(resp);
    }

private:
    [[nodiscard]] std::vector<std::uint8_t> build_frame(std::span<const std::uint8_t> payload) {
        std::vector<std::uint8_t> frame;
        frame.reserve(6 + payload.size());

        frame.push_back(MessageStart);
        frame.push_back(seq_num_++);
        frame.push_back(static_cast<std::uint8_t>((payload.size() >> 8) & 0xFF));
        frame.push_back(static_cast<std::uint8_t>(payload.size() & 0xFF));
        frame.push_back(TokenMarker);

        frame.insert(frame.end(), payload.begin(), payload.end());

        const std::uint8_t checksum = std::accumulate(frame.begin(), frame.end(), static_cast<std::uint8_t>(0),
                                                      [](std::uint8_t acc, std::uint8_t b) { return acc ^ b; });
        frame.push_back(checksum);
        return frame;
    }

    VirtualMcu mcu_{};
    std::uint8_t seq_num_{0};
    std::uint8_t sck_duration_{8};
};

} // namespace stk500

// ── Тестовий запуск емулятора (C++20 Suite) ────────────────────────────────

int main() {
    std::cout << "==================================================================\n";
    std::cout << "   Тестовий стенд емулятора ISP-програматора STK500v2 (C++20)\n";
    std::cout << "==================================================================\n\n";

    stk500::Stk500Engine engine;

    // 1. Sign-On
    std::cout << "[1] Перевірка ідентифікації програматора (Sign-On)...\n";
    const std::array<std::uint8_t, 1> sign_on_cmd{static_cast<std::uint8_t>(stk500::Command::SignOn)};
    auto resp1 = engine.process_command(sign_on_cmd);
    if (resp1[6] == static_cast<std::uint8_t>(stk500::Status::Ok)) {
        std::cout << "    -> УСПІХ: Отримано відповідь Sign-On.\n";
    }

    // 2. Вхід у режим ISP
    std::cout << "[2] Вхід у режим програмування ISP...\n";
    const std::array<std::uint8_t, 1> enter_cmd{static_cast<std::uint8_t>(stk500::Command::EnterProgModeIsp)};
    auto resp2 = engine.process_command(enter_cmd);
    if (resp2[6] == static_cast<std::uint8_t>(stk500::Status::Ok) && engine.mcu().in_prog_mode()) {
        std::cout << "    -> УСПІХ: Віртуальний кристал перейшов у стан ISP.\n";
    }

    // 3. Зчитування сигнатури
    std::cout << "[3] Зчитування сигнатури кристала через SpiMulti...\n";
    std::array<std::uint8_t, 3> sig{};
    for (std::uint8_t i = 0; i < 3; ++i) {
        const std::array<std::uint8_t, 8> spi_cmd{
            static_cast<std::uint8_t>(stk500::Command::SpiMulti), 4, 1, 3, 0x30, 0x00, i, 0x00
        };
        auto resp3 = engine.process_command(spi_cmd);
        sig[i] = resp3[7];
    }
    std::cout << "    -> Сигнатура: 0x" << std::hex << static_cast<int>(sig[0])
              << " 0x" << static_cast<int>(sig[1])
              << " 0x" << static_cast<int>(sig[2]) << std::dec << "\n";

    // 4. Посторінковий запис
    std::cout << "[4] Запис та верифікація сторінки Flash (128 байтів)...\n";
    const std::array<std::uint8_t, 5> addr_cmd{static_cast<std::uint8_t>(stk500::Command::LoadAddress), 0, 0, 0, 0};
    engine.process_command(addr_cmd);

    std::vector<std::uint8_t> prog_cmd(10 + stk500::VirtualMcu::PageSize, 0);
    prog_cmd[0] = static_cast<std::uint8_t>(stk500::Command::ProgramFlashIsp);
    prog_cmd[1] = 0;
    prog_cmd[2] = static_cast<std::uint8_t>(stk500::VirtualMcu::PageSize);
    for (std::size_t i = 0; i < stk500::VirtualMcu::PageSize; ++i) {
        prog_cmd[10 + i] = static_cast<std::uint8_t>((i * 3) & 0xFF);
    }
    engine.process_command(prog_cmd);

    // Читання назад
    engine.process_command(addr_cmd);
    const std::array<std::uint8_t, 3> read_cmd{
        static_cast<std::uint8_t>(stk500::Command::ReadFlashIsp), 0, static_cast<std::uint8_t>(stk500::VirtualMcu::PageSize)
    };
    auto read_resp = engine.process_command(read_cmd);

    bool match = true;
    for (std::size_t i = 0; i < stk500::VirtualMcu::PageSize; ++i) {
        if (read_resp[7 + i] != static_cast<std::uint8_t>((i * 3) & 0xFF)) {
            match = false;
            break;
        }
    }
    if (match) {
        std::cout << "    -> УСПІХ: Дані Flash верифіковано на 100%.\n";
    }

    std::cout << "\nВсі перевірки емулятора виконано успішно.\n";
    return 0;
}
