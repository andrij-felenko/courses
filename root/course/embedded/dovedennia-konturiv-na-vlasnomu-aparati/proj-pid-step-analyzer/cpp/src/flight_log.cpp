#include "flight_log.hpp"

#include <cctype>
#include <charconv>
#include <format>
#include <fstream>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>

namespace pid {
namespace {

constexpr std::size_t kMinSamples = 32;

std::string_view trim(std::string_view s) noexcept {
    while (!s.empty() && (s.front() == ' ' || s.front() == '\t')) s.remove_prefix(1);
    while (!s.empty() && (s.back() == ' ' || s.back() == '\t' || s.back() == '\r')) s.remove_suffix(1);
    return s;
}

/// Відрізає наступне поле; std::nullopt — полів більше немає.
std::optional<std::string_view> nextField(std::string_view& rest) noexcept {
    if (rest.empty()) return std::nullopt;
    const auto pos = rest.find(',');
    if (pos == std::string_view::npos) {
        const auto field = rest;
        rest = {};
        return trim(field);
    }
    const auto field = rest.substr(0, pos);
    rest.remove_prefix(pos + 1);
    return trim(field);
}

template <typename T>
T parseField(std::string_view& rest, std::string_view name, std::size_t lineno) {
    const auto field = nextField(rest);
    if (!field || field->empty()) {
        throw std::runtime_error(
            std::format("рядок {}: бракує поля {} (чекали п'ять стовпчиків)", lineno, name));
    }
    T value{};
    const auto* first = field->data();
    const auto* last = first + field->size();
    const auto [ptr, ec] = std::from_chars(first, last, value);
    if (ec != std::errc{} || ptr != last) {
        throw std::runtime_error(std::format("рядок {}: поле {} = «{}» не число", lineno, name, *field));
    }
    return value;
}

bool looksLikeNumber(std::string_view s) noexcept {
    return !s.empty() && (std::isdigit(static_cast<unsigned char>(s.front())) || s.front() == '-' ||
                          s.front() == '+' || s.front() == '.');
}

} // namespace

FlightLog FlightLog::loadCsv(const std::filesystem::path& path) {
    std::ifstream in(path);
    if (!in) {
        throw std::runtime_error(std::format("не вдалося відкрити «{}»", path.string()));
    }

    std::vector<Sample> samples;
    std::string line;
    std::size_t lineno = 0;

    while (std::getline(in, line)) {
        ++lineno;
        std::string_view rest = trim(line);
        if (rest.empty() || rest.front() == '#') continue;   // порожній рядок або коментар
        if (!looksLikeNumber(rest)) {
            if (samples.empty()) continue;                   // шапка CSV
            throw std::runtime_error(std::format("рядок {}: перше поле не схоже на час", lineno));
        }

        Sample s;
        s.t = std::chrono::microseconds{parseField<std::uint64_t>(rest, "t_us", lineno)};
        s.setpoint = parseField<double>(rest, "setpoint", lineno);
        s.gyro = parseField<double>(rest, "gyro", lineno);
        s.dTerm = parseField<double>(rest, "d_term", lineno);
        s.vbat = parseField<double>(rest, "vbat", lineno);

        // Час мусить зростати строго: склеєний із двох сесій лог дав би
        // від'ємні затримки, і жодна метрика нижче не мала б сенсу.
        if (!samples.empty() && s.t <= samples.back().t) {
            throw std::runtime_error(std::format("рядок {}: час {} не більший за попередній {}",
                                                 lineno, s.t.count(), samples.back().t.count()));
        }
        samples.push_back(s);
    }

    if (in.bad()) {
        throw std::runtime_error(std::format("помилка читання «{}»", path.string()));
    }
    if (samples.size() < kMinSamples) {
        throw std::runtime_error(std::format("у лозі лише {} відліків, потрібно щонайменше {}",
                                             samples.size(), kMinSamples));
    }
    return FlightLog{std::move(samples)};
}

Micros FlightLog::meanPeriod() const {
    if (samples_.size() < 2) return Micros{0.0};
    const auto span = samples_.back().t - samples_.front().t;
    return Micros{static_cast<double>(span.count()) / static_cast<double>(samples_.size() - 1)};
}

} // namespace pid
