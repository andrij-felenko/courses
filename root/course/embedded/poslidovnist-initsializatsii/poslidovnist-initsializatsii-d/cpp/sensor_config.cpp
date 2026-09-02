#include <array>

#include "sensor.hpp"

namespace bringup {
namespace {

// Ієрархічний порядок: електрика виводів -> шкали -> фільтри -> переривання.
// Кожен запис несе власну маску значущих розрядів, бо в тих самих регістрах
// живуть RO-прапорці й фабричні константи.
constexpr std::array<RegField, 4> kConfigSequence{{
    // Крок 1: вивід INT об'єднаний Wired-OR, отже Open-Drain, активний нуль, latch
    {reg::IntCfg, 0x01 | 0x02 | 0x04, 0x07},
    // Крок 2: шкала ±8g і три осі — до вмикання цифрового тракту; біт 6 фабричний
    {reg::Range, 0x02 | (0x07 << 2), 0x1F},
    // Крок 3: ODR 104 Гц і DLPF 50 Гц — поки буфер фільтра ще порожній
    {reg::Filter, 0x04 | (0x02 << 4), 0x3F},
    // Крок 4: переривання за готовністю даних і кільцевий FIFO
    {reg::IntEnable, 0x01 | 0x02 | (0x02 << 2), 0x0F},
}};

constexpr RegField kStandby{reg::Power, PowerStandby, PowerModeMask};
constexpr RegField kActivate{reg::Power, PowerNormal, PowerModeMask};

}  // namespace

// ACK на 9-му такті підтверджує лише прийом байта зсувним регістром, а не запис
// у комірку конфігурації. Тому пишемо, читаємо назад і порівнюємо ТІЛЬКИ значущі
// розряди: пряме "==" зламав би перший же апаратний прапорець у тому ж регістрі.
std::expected<void, Fault> Sensor::write_verified(const RegField& field) {
    if (!bus_.write(addr_, field.reg, field.value)) {
        return std::unexpected(Fault{InitError::Bus, field.reg});
    }

    const auto read_back = bus_.read(addr_, field.reg);
    if (!read_back) {
        return std::unexpected(Fault{InitError::Bus, field.reg});
    }

    const auto target_masked = static_cast<std::uint8_t>(field.value & field.care);
    const auto read_masked = static_cast<std::uint8_t>(*read_back & field.care);
    if (target_masked != read_masked) {
        return std::unexpected(Fault{InitError::Verify, field.reg});
    }
    return {};
}

std::expected<void, Fault> Sensor::write_sequence(std::span<const RegField> fields) {
    for (const auto& field : fields) {
        if (auto result = write_verified(field); !result) {
            return result;
        }
    }
    return {};
}

std::expected<void, Fault> Sensor::apply_config() {
    // Нульовий крок: у робочому режимі конфігураційні регістри заблоковані
    if (auto result = write_verified(kStandby); !result) {
        return result;
    }
    if (auto result = write_sequence(kConfigSequence); !result) {
        return result;
    }
    // Крок 5: активація робочого режиму — останньою дією
    if (auto result = write_verified(kActivate); !result) {
        return result;
    }

    // Час прогріву: до його кінця відліки пливуть за нулем
    platform::sleep(SettlingTime);

    const auto filter = bus_.read(addr_, reg::Filter);
    if (!filter) {
        return std::unexpected(Fault{InitError::Bus, reg::Filter});
    }
    if ((*filter & bits::FilterReady) == 0) {
        return std::unexpected(Fault{InitError::Timeout, reg::Filter});
    }
    return {};
}

}  // namespace bringup
