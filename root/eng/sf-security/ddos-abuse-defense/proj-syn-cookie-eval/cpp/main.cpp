#include <cstdint>
#include <array>
#include <optional>
#include <string_view>
#include <algorithm>
#include <span>

class SynCookieEngine {
public:
    static constexpr uint32_t TimeShift = 6;          // 64 секунди на одне вікно
    static constexpr uint32_t TimeMask  = 0x07;       // 3 біти для часового індексу
    static constexpr uint32_t MssMask   = 0x07;       // 3 біти для індексу MSS
    static constexpr uint32_t HashMask  = 0x03FFFFFF; // 26 бітів для криптографічного MAC

    static constexpr std::array<uint16_t, 8> MssTable = {
        536, 1200, 1400, 1440, 1452, 1460, 8960, 9000
    };

    struct Endpoints {
        uint32_t src_ip;
        uint32_t dst_ip;
        uint16_t src_port;
        uint16_t dst_port;
        uint32_t client_isn;
    };

    explicit SynCookieEngine(std::span<const uint8_t, 16> secret_key) noexcept {
        std::copy(secret_key.begin(), secret_key.end(), secret_.begin());
    }

    [[nodiscard]] uint32_t generate(const Endpoints& ep, uint16_t client_mss, uint32_t now_sec) const noexcept {
        const uint32_t time_idx = (now_sec >> TimeShift) & TimeMask;
        const uint32_t mss_idx = select_mss_index(client_mss);
        const uint32_t mac = compute_mac(ep, time_idx);

        return (time_idx << 29) | (mss_idx << 26) | mac;
    }

    [[nodiscard]] std::optional<uint16_t> verify(uint32_t cookie, const Endpoints& ep, uint32_t now_sec) const noexcept {
        const uint32_t cookie_time = (cookie >> 29) & TimeMask;
        const uint32_t cookie_mss_idx = (cookie >> 26) & MssMask;
        const uint32_t cookie_mac = cookie & HashMask;

        const uint32_t current_time = (now_sec >> TimeShift) & TimeMask;
        const uint32_t diff = (current_time - cookie_time) & TimeMask;

        // Приймаємо лише поточне та попереднє вікно (термін валідності куки 64..128 с)
        if (diff > 1) {
            return std::nullopt;
        }

        if (compute_mac(ep, cookie_time) != cookie_mac) {
            return std::nullopt;
        }

        return MssTable[cookie_mss_idx];
    }

private:
    std::array<uint8_t, 16> secret_{};

    static uint32_t select_mss_index(uint16_t client_mss) noexcept {
        uint32_t best_idx = 0;
        for (size_t i = 0; i < MssTable.size(); ++i) {
            if (MssTable[i] <= client_mss) {
                best_idx = static_cast<uint32_t>(i);
            } else {
                break;
            }
        }
        return best_idx;
    }

    [[nodiscard]] uint32_t compute_mac(const Endpoints& ep, uint32_t time_idx) const noexcept {
        uint64_t k0 = 0, k1 = 0;
        for (int i = 0; i < 8; ++i) {
            k0 |= static_cast<uint64_t>(secret_[i]) << (i * 8);
            k1 |= static_cast<uint64_t>(secret_[i + 8]) << (i * 8);
        }

        uint64_t v0 = 0x736f6d6570736575ULL ^ k0;
        uint64_t v1 = 0x646f72616e646f6dULL ^ k1;
        uint64_t v2 = 0x6c7967656e657261ULL ^ k0;
        uint64_t v3 = 0x7465646279746573ULL ^ k1;

        const uint64_t m0 = (static_cast<uint64_t>(ep.src_ip) << 32) | ep.dst_ip;
        const uint64_t m1 = (static_cast<uint64_t>(ep.src_port) << 48) |
                            (static_cast<uint64_t>(ep.dst_port) << 32) |
                            (ep.client_isn ^ time_idx);

        auto round = [&](uint64_t m) {
            v3 ^= m;
            v0 += v1; v1 = (v1 << 13) | (v1 >> 51); v1 ^= v0; v0 = (v0 << 32) | (v0 >> 32);
            v2 += v3; v3 = (v3 << 16) | (v3 >> 48); v3 ^= v2;
            v0 += v3; v3 = (v3 << 21) | (v3 >> 43); v3 ^= v0;
            v2 += v1; v1 = (v1 << 17) | (v1 >> 47); v1 ^= v2; v2 = (v2 << 32) | (v2 >> 32);
            v0 ^= m;
        };

        round(m0);
        round(m1);

        v2 ^= 0xff;
        v0 += v1; v1 = (v1 << 13) | (v1 >> 51); v1 ^= v0; v0 = (v0 << 32) | (v0 >> 32);
        v2 += v3; v3 = (v3 << 16) | (v3 >> 48); v3 ^= v2;

        return static_cast<uint32_t>((v0 ^ v1 ^ v2 ^ v3) & HashMask);
    }
};
