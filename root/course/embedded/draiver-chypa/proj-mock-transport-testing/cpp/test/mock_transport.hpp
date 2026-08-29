// mock_transport.hpp — віртуальний чип у пам'яті комп'ютера.
//
// Це модель кремнію, а не заглушка «поверни щось». У неї є адресний простір,
// реакція на біт автоінкременту, регістри лише для читання, прапорець
// готовності, що гасне після забирання відліку, — і важелі, якими тест
// зумисне ламає шину. Поблажливий мок зеленить набір і вбиває плату.
#pragma once

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>
#include <vector>

#include "chip/registers.hpp"
#include "chip/status.hpp"

namespace chip::testing {

struct WriteLogEntry {
    std::uint32_t seq{};   // наскрізний номер транзакції
    std::uint8_t  reg{};
    std::uint8_t  value{};
    bool          applied{}; // false — адреса лише для читання, байт зник
};

class MockTransport {
public:
    MockTransport() { reset(); }

    // --- Стан кремнію ------------------------------------------------------

    void reset()
    {
        registers_.fill(0);
        writeLog_.clear();
        seq_               = 0;
        readTransactions_  = 0;
        writeTransactions_ = 0;
        failReads_         = 0;
        failWrites_        = 0;
        deviceAbsent_      = false;
        breakReadAtByte_   = 0;
        registers_[reg::WhoAmI] = reg::WhoAmIValue;
    }

    // Прямий доступ повз шину: так тест грає роль фізики.
    void poke(std::uint8_t address, std::uint8_t value) noexcept
    {
        registers_[address & 0x7FU] = value;
    }

    [[nodiscard]] std::uint8_t peek(std::uint8_t address) const noexcept
    {
        return registers_[address & 0x7FU];
    }

    // --- Генератор синтетичних даних ---------------------------------------

    void setRawXyz(std::int16_t x, std::int16_t y, std::int16_t z) noexcept
    {
        const std::array<std::int16_t, 3> axes{x, y, z};
        for (std::size_t i = 0; i < axes.size(); ++i) {
            const auto word = static_cast<std::uint16_t>(axes[i]);
            registers_[reg::OutXL + i * 2 + 0] = static_cast<std::uint8_t>(word & 0xFFU);
            registers_[reg::OutXL + i * 2 + 1] = static_cast<std::uint8_t>(word >> 8);
        }

        // Не забраний вчасно відлік лишає слід перезапису — на цьому тримається
        // перевірка пропущених даних.
        if ((registers_[reg::Status] & reg::StatusZyxda) != 0) {
            registers_[reg::Status] |= reg::StatusZyxor;
        }
        registers_[reg::Status] |= reg::StatusZyxda;
    }

    // Ті самі дані, але задані фізично: скільки g лежить на кожній осі.
    void setAcceleration(Range range, float gx, float gy, float gz) noexcept
    {
        const float countsPerG = 32768.0F / static_cast<float>(fullScaleG(range));
        const std::array<float, 3> input{gx, gy, gz};
        std::array<std::int16_t, 3> raw{};

        for (std::size_t i = 0; i < input.size(); ++i) {
            // Насичення, а не мовчазне загортання: реальний чип впирається
            // в край шкали, а не міняє знак.
            const float counts = std::clamp(input[i] * countsPerG, -32768.0F, 32767.0F);
            raw[i] = static_cast<std::int16_t>(counts);
        }
        setRawXyz(raw[0], raw[1], raw[2]);
    }

    // --- Генератор апаратних збоїв -----------------------------------------

    void injectReadFailures(unsigned count) noexcept { failReads_ = count; }
    void injectWriteFailures(unsigned count) noexcept { failWrites_ = count; }
    void setDeviceAbsent(bool absent) noexcept { deviceAbsent_ = absent; }

    // Одноразовий обрив пакетного читання рівно на заданому байті (1 — на
    // першому). Частина буфера вже заповнена, і драйвер не має права цим
    // скористатися.
    void breakReadAtByte(std::size_t index) noexcept { breakReadAtByte_ = index; }

    // --- Контракт chip::Transport ------------------------------------------

    std::expected<void, Error> read(std::uint8_t address, std::span<std::uint8_t> out)
    {
        ++seq_;
        ++readTransactions_;
        if (deviceAbsent_) {
            return std::unexpected(Error::Comm);
        }
        if (failReads_ > 0) {
            --failReads_;
            return std::unexpected(Error::Comm);
        }

        for (std::size_t i = 0; i < out.size(); ++i) {
            if (breakReadAtByte_ != 0 && i + 1 == breakReadAtByte_) {
                breakReadAtByte_ = 0;
                return std::unexpected(Error::Comm);
            }
            out[i] = registers_[nextAddress(address, i)];
        }

        if ((address & 0x7FU) == reg::OutXL && out.size() >= 6) {
            registers_[reg::Status] &=
                static_cast<std::uint8_t>(~(reg::StatusZyxda | reg::StatusZyxor));
        }
        return {};
    }

    std::expected<void, Error> write(std::uint8_t address,
                                     std::span<const std::uint8_t> in)
    {
        ++seq_;
        ++writeTransactions_;
        if (deviceAbsent_) {
            return std::unexpected(Error::Comm);
        }
        if (failWrites_ > 0) {
            --failWrites_;
            return std::unexpected(Error::Comm);
        }

        for (std::size_t i = 0; i < in.size(); ++i) {
            const std::uint8_t target  = nextAddress(address, i);
            const bool         applied = !isReadOnly(target);
            if (applied) {
                registers_[target] = in[i];
            }
            writeLog_.push_back(WriteLogEntry{seq_, target, in[i], applied});
        }
        return {};
    }

    void delay(std::chrono::milliseconds) noexcept
    {
        // Час на ПК не витрачаємо: увесь сенс у тому, що набір іде мілісекунди.
        // Політику пауз перевіряють за лічильниками спроб, не за годинником.
    }

    // --- Розбір журналу -----------------------------------------------------

    [[nodiscard]] const std::vector<WriteLogEntry>& writeLog() const noexcept
    {
        return writeLog_;
    }

    [[nodiscard]] std::optional<std::uint8_t> lastWrite(std::uint8_t address) const
    {
        for (auto it = writeLog_.rbegin(); it != writeLog_.rend(); ++it) {
            if (it->reg == address) {
                return it->value;
            }
        }
        return std::nullopt;
    }

    [[nodiscard]] std::size_t writesTo(std::uint8_t address) const
    {
        return static_cast<std::size_t>(
            std::ranges::count_if(writeLog_, [address](const WriteLogEntry& entry) {
                return entry.reg == address;
            }));
    }

    [[nodiscard]] std::uint32_t readTransactions() const noexcept
    {
        return readTransactions_;
    }

    [[nodiscard]] unsigned pendingReadFailures() const noexcept { return failReads_; }

private:
    static bool isReadOnly(std::uint8_t address) noexcept
    {
        return address == reg::WhoAmI || address == reg::Status ||
               (address >= reg::OutXL && address <= reg::OutZH);
    }

    // Без біта автоінкременту чип не рухає внутрішній вказівник.
    static std::uint8_t nextAddress(std::uint8_t address, std::size_t index) noexcept
    {
        if ((address & reg::AutoIncrement) == 0) {
            return static_cast<std::uint8_t>(address & 0x7FU);
        }
        return static_cast<std::uint8_t>(((address & 0x7FU) + index) & 0x7FU);
    }

    std::array<std::uint8_t, 128> registers_{};
    std::vector<WriteLogEntry>    writeLog_{};
    std::uint32_t                 seq_{};
    std::uint32_t                 readTransactions_{};
    std::uint32_t                 writeTransactions_{};
    unsigned                      failReads_{};
    unsigned                      failWrites_{};
    bool                          deviceAbsent_{};
    std::size_t                   breakReadAtByte_{};
};

} // namespace chip::testing
