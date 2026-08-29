#include "release_verifier.hpp"

#include "board.hpp"
#include "sha256.hpp"

/* Ed25519 бере Monocypher 4.x: crypto_ed25519_check() повертає 0, коли підпис
   дійсний, і -1 інакше. Арифметику кривої Edwards25519 у проєкт не тягнемо —
   це окрема тема, а не предмет завантажувача. */
extern "C" {
#include "monocypher-ed25519.h"
}

namespace fw {
namespace {

/* Порівняння за сталий час: підсумовуємо різницю всіх байтів і лише потім
   дивимось на результат. Ранній вихід на першому розбіжному байті зливає
   зловмиснику, скільки байтів гешу він уже вгадав. */
[[nodiscard]] bool equal_constant_time(const Digest& a, const Digest& b) noexcept
{
    std::byte diff{0};
    for (std::size_t i = 0; i < a.size(); ++i) {
        diff |= a[i] ^ b[i];
    }
    return diff == std::byte{0};
}

/* Потокове обчислення гешу тіла: згодовуємо Flash шматками по 256 байтів.
   Тіло буває на сотні кілобайтів, і жоден проміжний буфер тут не потрібен. */
[[nodiscard]] Digest hash_payload(std::span<const std::byte> payload) noexcept
{
    Sha256 hasher;
    while (!payload.empty()) {
        const std::size_t take = std::min<std::size_t>(payload.size(), 256);
        hasher.update(payload.first(take));
        payload = payload.subspan(take);
    }
    return hasher.finish();
}

[[nodiscard]] const std::uint8_t* raw(std::span<const std::byte> bytes) noexcept
{
    return reinterpret_cast<const std::uint8_t*>(bytes.data());
}

}  // namespace

std::expected<void, VerifyError> verify_release(const Descriptor& descriptor) noexcept
{
    /* 1. Магічне число й версія формату. Стерта Flash — це 0xFFFFFFFF,
          і саме тут вона відсікається, ще до будь-якої математики. */
    if (!descriptor.magic_ok()) {
        return std::unexpected(VerifyError::BadMagic);
    }

    /* 2. Сумісність із залізом: спершу виріб, потім ревізія плати. */
    if (descriptor.target_hw_id != board::hw_platform_id) {
        return std::unexpected(VerifyError::HardwareIncompatible);
    }
    if (!descriptor.accepts_revision(board::pcb_revision())) {
        return std::unexpected(VerifyError::HardwareIncompatible);
    }

    /* 3. Anti-rollback. Підпис старого релізу бездоганний — і саме тому
          порівняння з апаратним лічильником іде ДО перевірки підпису:
          відкликану версію ми не приймаємо навіть дійсно підписану. */
    if (descriptor.security_version < board::security_counter()) {
        return std::unexpected(VerifyError::Rollback);
    }

    /* 4. Підпис над першими 64 байтами заголовка. */
    const auto key = board::root_public_key();
    if (!key) {
        return std::unexpected(VerifyError::NoRootKey);
    }
    const auto prefix = descriptor.signed_prefix();
    if (crypto_ed25519_check(raw(std::span{descriptor.signature}), raw(*key),
                             raw(prefix), prefix.size()) != 0) {
        return std::unexpected(VerifyError::BadSignature);
    }

    /* Геометрія. Поля вже засвідчені підписом, але перш ніж читати
       payload_size байтів, переконуємось, що вони лежать там, де ми їх
       чекаємо: образ під іншу карту пам'яті впаде в HardFault на першій же
       абсолютній адресації. */
    if (descriptor.load_address != board::app_payload_address ||
        descriptor.payload_size == 0u ||
        descriptor.payload_size > board::app_max_payload) {
        return std::unexpected(VerifyError::BadGeometry);
    }
    const auto payload = board::flash_window(descriptor.load_address, descriptor.payload_size);
    if (payload.empty()) {
        return std::unexpected(VerifyError::FlashIo);
    }

    /* 5. Геш тіла. Підпис засвідчив поле payload_sha256; тепер лишилось
          довести, що байти у Flash йому відповідають. */
    if (!equal_constant_time(hash_payload(payload), descriptor.payload_sha256)) {
        return std::unexpected(VerifyError::HashMismatch);
    }

    return {};
}

}  // namespace fw
