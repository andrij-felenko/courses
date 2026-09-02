#include "ardupilot.hpp"

#include <algorithm>

namespace ap {

StatusText::StatusText(Severity severity, std::string_view text) noexcept : severity_{severity}
{
    // Довший текст прошивка просто зрізає до 50 байтів.
    const std::size_t len = std::min(text.size(), kTextLen);
    std::copy_n(text.begin(), len, text_.begin());
}

std::string_view StatusText::text() const noexcept
{
    const auto end = std::find(text_.begin(), text_.end(), '\0');
    return std::string_view{text_.data(), static_cast<std::size_t>(end - text_.begin())};
}

std::vector<StatusText> prearmReport(CheckMask enabled, std::span<const Check> failing)
{
    std::vector<StatusText> report;
    for (const Check check : failing) {
        if (check == Check::All || check >= Check::Count) {
            continue;                        // біт 0 — не підсистема
        }
        if (!enabled.enabled(check)) {
            continue;                        // перевірку вимкнено параметром
        }
        report.emplace_back(Severity::Critical, info(check).failure);
    }
    return report;
}

}  // namespace ap
