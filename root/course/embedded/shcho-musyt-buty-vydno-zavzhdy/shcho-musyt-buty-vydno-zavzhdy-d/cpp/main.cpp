// Обчислення актуальності та семантичного статусу телеметрії (C++20)
#include <cstdint>
#include <string_view>
#include <cstdio>
#include <array>

namespace gcs::ui {

enum class Severity : uint8_t { Normal, Warning, Critical, Stale };

struct StalenessResult {
    Severity severity{Severity::Normal};
    std::array<char, 24> text{};

    [[nodiscard]] constexpr std::string_view view() const noexcept {
        return std::string_view(text.data());
    }
};

[[nodiscard]] StalenessResult evaluate_staleness(uint32_t now_ms, uint32_t last_packet_ms) noexcept {
    StalenessResult res{};
    const uint32_t age_ms = now_ms - last_packet_ms;

    if (age_ms >= 3000) {
        res.severity = Severity::Critical;
        std::snprintf(res.text.data(), res.text.size(), "[X LOST: %.1fs]", static_cast<float>(age_ms) / 1000.0f);
    } else if (age_ms >= 1000) {
        res.severity = Severity::Stale;
        std::snprintf(res.text.data(), res.text.size(), "[⧗ STALE: %.1fs]", static_cast<float>(age_ms) / 1000.0f);
    } else {
        res.severity = Severity::Normal;
        std::snprintf(res.text.data(), res.text.size(), "[OK ONLINE]");
    }

    return res;
}

} // namespace gcs::ui
