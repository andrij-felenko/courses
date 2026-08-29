#pragma once

#include <array>
#include <cstdint>
#include <span>

#include "firmware_descriptor.hpp"

namespace fw {

/* Потоковий SHA-256 (FIPS 180-4). Тримаємо реалізацію в проєкті свідомо:
   Monocypher, яким перевіряємо підпис, SHA-256 не має, а тягнути другу
   криптобібліотеку в завантажувач заради однієї функції — надмір.

   Клас, а не пара «контекст + функції»: стан живе рівно стільки, скільки
   об'єкт, і забути init() ніяк. */
class Sha256 {
public:
    void update(std::span<const std::byte> data) noexcept;

    /* Завершує обчислення й повертає дайджест. Об'єкт після цього
       непридатний до повторного вжитку — на це є assert у debug-збірці. */
    [[nodiscard]] Digest finish() noexcept;

private:
    void compress(const std::byte* block) noexcept;

    std::array<std::uint32_t, 8> state_{
        0x6a09e667u, 0xbb67ae85u, 0x3c6ef372u, 0xa54ff53au,
        0x510e527fu, 0x9b05688cu, 0x1f83d9abu, 0x5be0cd19u};
    std::array<std::byte, 64> block_{};
    std::size_t   used_{0};
    std::uint64_t total_bits_{0};
    bool          finished_{false};
};

}  // namespace fw
