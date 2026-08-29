#include "twi.hpp"

#include <avr/io.h>
#include <util/delay.h>
#include <util/twi.h>

namespace gimbal {
namespace {

constexpr std::uint8_t kSdaBit = PC4;
constexpr std::uint8_t kSclBit = PC5;

}  // namespace

void Twi::begin(std::uint32_t scl_hz) noexcept {
    // Внутрішні підтяжки — лише страховка; на платі стоять зовнішні 2.2…4.7 кОм.
    PORTC |= static_cast<std::uint8_t>((1u << kSdaBit) | (1u << kSclBit));

    TWSR = 0;  // дільник 1
    TWBR = static_cast<std::uint8_t>(((F_CPU / scl_hz) - 16UL) / 2UL);
    TWCR = (1 << TWEN);
}

Result<void, TwiError> Twi::wait_flag() noexcept {
    for (std::uint16_t us = 0; us < kTimeoutUs; ++us) {
        if (TWCR & (1 << TWINT)) {
            return Result<void, TwiError>::ok();
        }
        _delay_us(1);
    }
    return Result<void, TwiError>::fail(TwiError::Timeout);
}

void Twi::stop() noexcept {
    TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWSTO);

    // На побитій шині не завершується навіть STOP — і тут із межею.
    for (std::uint16_t us = 0; us < kTimeoutUs; ++us) {
        if (!(TWCR & (1 << TWSTO))) {
            return;
        }
        _delay_us(1);
    }
}

Result<void, TwiError> Twi::start(std::uint8_t expected_status) noexcept {
    TWCR = (1 << TWINT) | (1 << TWSTA) | (1 << TWEN);

    if (auto waited = wait_flag(); !waited) {
        return waited;
    }
    if (TW_STATUS != expected_status) {
        return Result<void, TwiError>::fail(TwiError::BusState);
    }
    return Result<void, TwiError>::ok();
}

Result<void, TwiError> Twi::write_byte(std::uint8_t data,
                                        std::uint8_t expected_status) noexcept {
    TWDR = data;
    TWCR = (1 << TWINT) | (1 << TWEN);

    if (auto waited = wait_flag(); !waited) {
        return waited;
    }
    if (TW_STATUS != expected_status) {
        // Найчастіше — веденого просто немає на цій адресі.
        return Result<void, TwiError>::fail(TwiError::Nack);
    }
    return Result<void, TwiError>::ok();
}

Result<std::uint8_t, TwiError> Twi::read_byte(bool ack) noexcept {
    using R = Result<std::uint8_t, TwiError>;

    TWCR = static_cast<std::uint8_t>((1 << TWINT) | (1 << TWEN) | (ack ? (1 << TWEA) : 0));

    if (auto waited = wait_flag(); !waited) {
        return R::fail(waited.error());
    }

    const std::uint8_t expected = ack ? TW_MR_DATA_ACK : TW_MR_DATA_NACK;
    if (TW_STATUS != expected) {
        return R::fail(TwiError::BusState);
    }
    return R::ok(TWDR);
}

Result<void, TwiError> Twi::write_register(DeviceAddress dev,
                                            std::uint8_t reg,
                                            std::uint8_t value) noexcept {
    Transaction guard{*this};  // STOP вилетить із будь-якого return нижче

    if (auto r = start(TW_START); !r) return r;
    if (auto r = write_byte(dev.write_byte(), TW_MT_SLA_ACK); !r) return r;
    if (auto r = write_byte(reg, TW_MT_DATA_ACK); !r) return r;
    if (auto r = write_byte(value, TW_MT_DATA_ACK); !r) return r;

    return Result<void, TwiError>::ok();
}

Result<void, TwiError> Twi::read_registers(DeviceAddress dev,
                                            std::uint8_t reg,
                                            std::span<std::uint8_t> dst) noexcept {
    if (dst.empty()) {
        return Result<void, TwiError>::ok();
    }

    Transaction guard{*this};

    // Фаза запису: називаємо ведному регістр, з якого читати.
    if (auto r = start(TW_START); !r) return r;
    if (auto r = write_byte(dev.write_byte(), TW_MT_SLA_ACK); !r) return r;
    if (auto r = write_byte(reg, TW_MT_DATA_ACK); !r) return r;

    // Повторний START без відпускання шини: інакше між фазами вклиниться
    // чужий майстер і лічильник регістра з'їде.
    if (auto r = start(TW_REP_START); !r) return r;
    if (auto r = write_byte(dev.read_byte(), TW_MR_SLA_ACK); !r) return r;

    for (std::size_t i = 0; i < dst.size(); ++i) {
        const bool ack = (i + 1 < dst.size());  // останній байт квитуємо NACK
        auto byte = read_byte(ack);
        if (!byte) {
            return Result<void, TwiError>::fail(byte.error());
        }
        dst[i] = byte.value();
    }

    return Result<void, TwiError>::ok();
}

void Twi::recover_bus() noexcept {
    TWCR = 0;  // відпускаємо апарат, далі смикаємо ніжки руками

    DDRC  = static_cast<std::uint8_t>(DDRC | (1u << kSclBit));
    DDRC  = static_cast<std::uint8_t>(DDRC & ~(1u << kSdaBit));
    PORTC = static_cast<std::uint8_t>(PORTC | (1u << kSdaBit) | (1u << kSclBit));

    // Дев'ять тактів — байт плюс квитанція: скільки б бітів ведений не
    // недоговорив, за дев'ять він договорить усі й відпустить SDA.
    for (std::uint8_t i = 0; i < 9; ++i) {
        if (PINC & (1u << kSdaBit)) {
            break;  // лінія вже вільна
        }
        PORTC = static_cast<std::uint8_t>(PORTC & ~(1u << kSclBit));
        _delay_us(5);
        PORTC = static_cast<std::uint8_t>(PORTC | (1u << kSclBit));
        _delay_us(5);
    }

    // Ручний STOP: на високому SCL переводимо SDA знизу вгору.
    DDRC  = static_cast<std::uint8_t>(DDRC | (1u << kSdaBit));
    PORTC = static_cast<std::uint8_t>(PORTC & ~(1u << kSdaBit));
    _delay_us(5);
    PORTC = static_cast<std::uint8_t>(PORTC | (1u << kSclBit));
    _delay_us(5);
    PORTC = static_cast<std::uint8_t>(PORTC | (1u << kSdaBit));
    _delay_us(5);

    DDRC = static_cast<std::uint8_t>(DDRC & ~((1u << kSdaBit) | (1u << kSclBit)));

    begin();
}

}  // namespace gimbal
