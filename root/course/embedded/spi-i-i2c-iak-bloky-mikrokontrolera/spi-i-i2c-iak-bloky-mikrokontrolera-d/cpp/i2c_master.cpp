#include "i2c_master.hpp"

namespace drv {

I2cMaster::I2cMaster(mcu::I2cRegs& regs, std::uint32_t pclk1Hz, std::uint32_t sclHz) noexcept
    : regs_{regs}
{
    constexpr unsigned sclPin = 6u;
    constexpr unsigned sdaPin = 7u;
    constexpr unsigned i2c1AltFunction = 4u;

    mcu::rcc().ahb1enr |= mcu::rcc_bits::gpiobEn;
    mcu::rcc().apb1enr |= mcu::rcc_bits::i2c1En;

    // Обидві ніжки — тільки відкритий стік: рівень "1" на шині створює
    // зовнішній підтягувальний резистор, а не вихідний каскад.
    mcu::configurePin(mcu::gpioB(), sclPin, mcu::PinMode::Alternate, true, i2c1AltFunction);
    mcu::configurePin(mcu::gpioB(), sdaPin, mcu::PinMode::Alternate, true, i2c1AltFunction);

    regs_.cr1 = mcu::i2c_cr1::swrst;  // знімаємо засувки автомата, зокрема BUSY
    regs_.cr1 = 0u;

    const std::uint32_t freqMHz = pclk1Hz / 1000000u;
    regs_.cr2 = freqMHz & 0x3Fu;  // блоку треба знати частоту своєї шини

    if (sclHz <= 100000u) {
        std::uint32_t ccr = pclk1Hz / (2u * sclHz);
        if (ccr < 4u) {
            ccr = 4u;
        }
        regs_.ccr = ccr;
        regs_.trise = freqMHz + 1u;  // 1000 нс на наростання фронту
    } else {
        std::uint32_t ccr = pclk1Hz / (3u * sclHz);  // швидкий режим, 1:2
        if (ccr < 1u) {
            ccr = 1u;
        }
        regs_.ccr = mcu::i2c_ccr::fastMode | ccr;
        regs_.trise = (freqMHz * 300u) / 1000u + 1u;
    }

    regs_.cr1 = mcu::i2c_cr1::pe | mcu::i2c_cr1::ack;
}

std::expected<void, I2cError> I2cMaster::waitFlag(std::uint32_t sr1Mask) noexcept
{
    std::uint32_t left = pollBudget;
    for (;;) {
        const std::uint32_t sr1 = regs_.sr1;

        if (sr1 & mcu::i2c_sr1::af) {
            regs_.sr1 &= ~mcu::i2c_sr1::af;
            return std::unexpected(I2cError::Nack);
        }
        if (sr1 & mcu::i2c_sr1::arlo) {
            // Шина вже не наша: блок сам перейшов у ведені, STOP не даємо
            regs_.sr1 &= ~mcu::i2c_sr1::arlo;
            return std::unexpected(I2cError::ArbitrationLost);
        }
        if (sr1 & mcu::i2c_sr1::berr) {
            regs_.sr1 &= ~mcu::i2c_sr1::berr;
            return std::unexpected(I2cError::BusError);
        }
        if (sr1 & sr1Mask) {
            return {};
        }
        if (--left == 0u) {
            return std::unexpected(I2cError::Timeout);
        }
    }
}

std::expected<void, I2cError> I2cMaster::waitStopDone() noexcept
{
    std::uint32_t left = pollBudget;
    while (regs_.cr1 & mcu::i2c_cr1::stop) {
        if (--left == 0u) {
            return std::unexpected(I2cError::Timeout);
        }
    }
    return {};
}

std::expected<void, I2cError> I2cMaster::sendStart(bool repeated) noexcept
{
    if (!repeated) {
        // Повторний START видається посеред власної транзакції, тому BUSY
        // перевіряємо лише перед першим.
        std::uint32_t left = pollBudget;
        while (regs_.sr2 & mcu::i2c_sr2::busy) {
            if (--left == 0u) {
                return std::unexpected(I2cError::BusBusy);
            }
        }
    }
    regs_.cr1 |= mcu::i2c_cr1::start;
    return waitFlag(mcu::i2c_sr1::sb);  // подія EV5
}

std::expected<void, I2cError> I2cMaster::sendAddress(std::uint8_t address7, bool read) noexcept
{
    regs_.dr = static_cast<std::uint32_t>(address7 << 1) | (read ? 1u : 0u);
    return waitFlag(mcu::i2c_sr1::addr);  // подія EV6
}

void I2cMaster::clearAddressFlag() noexcept
{
    // Саме пара читань SR1 -> SR2 відпускає притиснуту автоматом SCL
    [[maybe_unused]] volatile std::uint32_t sr1 = regs_.sr1;
    [[maybe_unused]] volatile std::uint32_t sr2 = regs_.sr2;
}

std::expected<void, I2cError> I2cMaster::writeBody(std::span<const std::uint8_t> data) noexcept
{
    for (std::uint8_t byte : data) {
        if (auto ready = waitFlag(mcu::i2c_sr1::txe); !ready) {  // подія EV8
            return ready;
        }
        regs_.dr = byte;
    }
    // BTF (EV8_2): буфер і зсувний регістр порожні — тепер STOP не обріже байт
    return waitFlag(mcu::i2c_sr1::btf);
}

std::expected<void, I2cError> I2cMaster::readBody(std::span<std::uint8_t> data) noexcept
{
    const std::size_t count = data.size();

    if (count == 1u) {
        // NACK треба поставити ДО зняття ADDR, інакше ведений почне другий байт
        regs_.cr1 &= ~mcu::i2c_cr1::ack;
        clearAddressFlag();
        regs_.cr1 |= mcu::i2c_cr1::stop;
        if (auto ready = waitFlag(mcu::i2c_sr1::rxne); !ready) {  // подія EV7
            return ready;
        }
        data[0] = static_cast<std::uint8_t>(regs_.dr);
    } else if (count == 2u) {
        regs_.cr1 &= ~mcu::i2c_cr1::ack;
        regs_.cr1 |= mcu::i2c_cr1::pos;  // NACK поїде на другий прийнятий байт
        clearAddressFlag();
        auto ready = waitFlag(mcu::i2c_sr1::btf);
        regs_.cr1 &= ~mcu::i2c_cr1::pos;
        if (!ready) {
            return ready;
        }
        regs_.cr1 |= mcu::i2c_cr1::stop;
        data[0] = static_cast<std::uint8_t>(regs_.dr);
        data[1] = static_cast<std::uint8_t>(regs_.dr);
    } else {
        regs_.cr1 |= mcu::i2c_cr1::ack;
        clearAddressFlag();

        std::size_t i = 0;
        while ((count - i) > 3u) {
            if (auto ready = waitFlag(mcu::i2c_sr1::rxne); !ready) {
                return ready;
            }
            data[i++] = static_cast<std::uint8_t>(regs_.dr);
        }

        // Лишилося рівно три байти: N-2 у буфері, N-1 у зсувному регістрі.
        // Ці п'ять дій мають пройти без пауз, інакше автомат устигне
        // підтвердити останній байт — у бойовому драйвері тут маскують NVIC.
        if (auto ready = waitFlag(mcu::i2c_sr1::btf); !ready) {
            return ready;
        }
        regs_.cr1 &= ~mcu::i2c_cr1::ack;
        data[i++] = static_cast<std::uint8_t>(regs_.dr);
        regs_.cr1 |= mcu::i2c_cr1::stop;
        data[i++] = static_cast<std::uint8_t>(regs_.dr);

        if (auto ready = waitFlag(mcu::i2c_sr1::rxne); !ready) {
            return ready;
        }
        data[i] = static_cast<std::uint8_t>(regs_.dr);
    }

    auto done = waitStopDone();
    regs_.cr1 |= mcu::i2c_cr1::ack;  // повертаємо стан за замовчуванням
    return done;
}

std::expected<void, I2cError> I2cMaster::write(std::uint8_t address7,
                                               std::span<const std::uint8_t> data) noexcept
{
    if (data.empty()) {
        return std::unexpected(I2cError::BadLength);
    }

    StopGuard guard{regs_};  // будь-який вихід нижче звільнить шину

    if (auto started = sendStart(false); !started) {
        return started;
    }
    if (auto addressed = sendAddress(address7, false); !addressed) {
        return addressed;
    }
    clearAddressFlag();
    if (auto sent = writeBody(data); !sent) {
        return sent;
    }

    regs_.cr1 |= mcu::i2c_cr1::stop;
    guard.dismiss();
    return waitStopDone();
}

std::expected<void, I2cError> I2cMaster::read(std::uint8_t address7,
                                              std::span<std::uint8_t> data) noexcept
{
    if (data.empty()) {
        return std::unexpected(I2cError::BadLength);
    }

    StopGuard guard{regs_};

    if (auto started = sendStart(false); !started) {
        return started;
    }
    if (auto addressed = sendAddress(address7, true); !addressed) {
        return addressed;
    }

    auto received = readBody(data);  // STOP усередині послідовності читання
    guard.dismiss();
    return received;
}

std::expected<void, I2cError> I2cMaster::writeRead(std::uint8_t address7,
                                                   std::span<const std::uint8_t> command,
                                                   std::span<std::uint8_t> data) noexcept
{
    if (command.empty() || data.empty()) {
        return std::unexpected(I2cError::BadLength);
    }

    StopGuard guard{regs_};

    if (auto started = sendStart(false); !started) {
        return started;
    }
    if (auto addressed = sendAddress(address7, false); !addressed) {
        return addressed;
    }
    clearAddressFlag();
    if (auto sent = writeBody(command); !sent) {
        return sent;
    }

    // Повторний START: шину не відпускаємо, щоб ніхто не вклинився між
    // адресою регістра і його читанням.
    if (auto restarted = sendStart(true); !restarted) {
        return restarted;
    }
    if (auto addressed = sendAddress(address7, true); !addressed) {
        return addressed;
    }

    auto received = readBody(data);
    guard.dismiss();
    return received;
}

}  // namespace drv
