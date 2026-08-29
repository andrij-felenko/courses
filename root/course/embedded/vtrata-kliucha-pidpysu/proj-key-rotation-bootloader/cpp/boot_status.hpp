#pragma once

#include <cstdint>
#include <string_view>

namespace boot {

// Причина, з якої образ не можна виконувати. Успіх у std::expected несе сам
// тип значення, тож «Ok» у переліку немає — і забути перевірити результат
// стає складніше, ніж перевірити.
enum class Status : std::uint8_t {
    // Розбір маніфесту
    InvalidMagic,        // немає "SFWM" або не збігся CRC-32 заголовка
    InvalidSlot,         // індекс слота ключа поза 0..3
    BadImageLayout,      // образ не вміщується у розділ або порожній

    // Ланцюг довіри
    KeyRevoked,          // біт відкликання цього слота вже спалено
    RootMismatch,        // хеш ключа не збігся з еталоном у eFuse
    RollbackDetected,    // версія нижча за апаратний лічильник
    SignatureInvalid,    // підпис не пройшов математичну перевірку
    CryptoEngineFailure, // сам крипторушій повернув помилку

    // Драйвер eFuse
    EfuseBrownout,       // напруга просіла — палити перемичку не можна
    EfuseTimeout,        // контролер не зняв BUSY
    EfuseMarginal,       // комірка не підтвердилась у режимі Marginal Read
    EfuseRange,          // лічильник вичерпав розрядність рядка

    // Стан завантаження
    StateWriteFailed,    // сторінка стану не записалась
    NotTesting           // підтвердження прийшло не з пробного запуску
};

[[nodiscard]] constexpr std::string_view toString(Status status) noexcept
{
    switch (status) {
    case Status::InvalidMagic:        return "MAGIC/CRC";
    case Status::InvalidSlot:         return "INVALID_SLOT";
    case Status::BadImageLayout:      return "IMAGE_LAYOUT";
    case Status::KeyRevoked:          return "KEY_REVOKED";
    case Status::RootMismatch:        return "ROOT_MISMATCH";
    case Status::RollbackDetected:    return "ROLLBACK";
    case Status::SignatureInvalid:    return "SIGNATURE";
    case Status::CryptoEngineFailure: return "CRYPTO_ENGINE";
    case Status::EfuseBrownout:       return "EFUSE_BROWNOUT";
    case Status::EfuseTimeout:        return "EFUSE_TIMEOUT";
    case Status::EfuseMarginal:       return "EFUSE_MARGINAL";
    case Status::EfuseRange:          return "EFUSE_RANGE";
    case Status::StateWriteFailed:    return "STATE_WRITE";
    case Status::NotTesting:          return "NOT_TESTING";
    }
    return "UNKNOWN";
}

} // namespace boot
