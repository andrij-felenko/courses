#include <cstdint>
#include <cstddef>
#include <array>
#include <chrono>
#include <algorithm>
#include <iostream>
#include <cassert>

enum class AuthResult : uint8_t {
    Ok = 0,
    TimestampSkew = 1,
    ReplayDetected = 2,
    InvalidSignature = 3
};

template <size_t CacheCapacity = 1024, size_t NonceSize = 16, size_t DigestSize = 32>
class ReplayGuard {
public:
    using Nonce = std::array<uint8_t, NonceSize>;
    using Digest = std::array<uint8_t, DigestSize>;

    explicit constexpr ReplayGuard(std::chrono::seconds tolerance = std::chrono::seconds(300)) noexcept
        : tolerance_(tolerance) {}

    [[nodiscard]] AuthResult verify_and_record(
        const Nonce& nonce,
        std::chrono::system_clock::time_point req_time,
        std::chrono::system_clock::time_point now,
        const Digest& expected_sig,
        const Digest& provided_sig
    ) noexcept {
        // 1. Перевірка вікна допустимої часової розсинхронізації
        const auto diff = std::chrono::duration_cast<std::chrono::seconds>(now - req_time);
        if (diff < -tolerance_ || diff > tolerance_) {
            return AuthResult::TimestampSkew;
        }

        // 2. Перевірка кешу одноразових чисел
        for (const auto& entry : entries_) {
            if (entry.occupied && entry.expires_at >= now) {
                if (entry.nonce == nonce) {
                    return AuthResult::ReplayDetected;
                }
            }
        }

        // 3. Порівняння підпису в константному часі
        if (!constant_time_equals(expected_sig, provided_sig)) {
            return AuthResult::InvalidSignature;
        }

        // 4. Запис Nonce у кільцевий буфер
        auto& entry = entries_[next_idx_];
        entry.nonce = nonce;
        entry.expires_at = now + (tolerance_ * 2);
        entry.occupied = true;

        next_idx_ = (next_idx_ + 1) % CacheCapacity;
        return AuthResult::Ok;
    }

private:
    struct CacheEntry {
        Nonce nonce{};
        std::chrono::system_clock::time_point expires_at{};
        bool occupied{false};
    };

    static bool constant_time_equals(const Digest& a, const Digest& b) noexcept {
        uint8_t diff = 0;
        for (size_t i = 0; i < DigestSize; ++i) {
            diff |= (a[i] ^ b[i]);
        }
        return diff == 0;
    }

    std::chrono::seconds tolerance_{300};
    std::array<CacheEntry, CacheCapacity> entries_{};
    size_t next_idx_{0};
};
