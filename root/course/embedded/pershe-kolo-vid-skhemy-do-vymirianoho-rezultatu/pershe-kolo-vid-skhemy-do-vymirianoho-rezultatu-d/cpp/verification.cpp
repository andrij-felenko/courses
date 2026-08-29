#include "verification.hpp"

#include <algorithm>
#include <cmath>
#include <format>
#include <ostream>

namespace bench {
namespace {

constexpr std::size_t kTableWidth = 92;

// Продовжувальні байти 10xxxxxx окремої літери не утворюють.
[[nodiscard]] std::size_t glyphs(std::string_view s) noexcept
{
    std::size_t n = 0;
    for (const unsigned char c : s) {
        if ((c & 0xC0) != 0x80) {
            ++n;
        }
    }
    return n;
}

[[nodiscard]] double relative_error(double calc, double meas) noexcept
{
    if (std::abs(calc) < 1e-12) {
        return 0.0;
    }
    return (meas - calc) / calc * 100.0;
}

}  // namespace

std::string_view to_string(Verdict v) noexcept
{
    switch (v) {
    case Verdict::Pass: return "PASS";
    case Verdict::Warn: return "WARN";
    case Verdict::Fail: return "FAIL";
    }
    return "????";
}

Verdict verdict_of(double calc, double meas, double tol_pct) noexcept
{
    if (std::abs(calc) < 1e-12) {
        // Розрахунковий нуль: відносної похибки не існує, судимо абсолютно.
        return (std::abs(meas) < 1e-12) ? Verdict::Pass : Verdict::Fail;
    }
    const double dev = std::abs(relative_error(calc, meas));
    if (dev <= tol_pct) {
        return Verdict::Pass;
    }
    // Такий порядок відхилення ще пояснюється навантаженням приладу —
    // рядок вимагає корекції, а не пошуку дефекту монтажу.
    if (dev <= 5.0 * tol_pct) {
        return Verdict::Warn;
    }
    return Verdict::Fail;
}

Verdict rule_of_hundred(double ratio) noexcept
{
    if (ratio >= 100.0) {
        return Verdict::Pass;
    }
    if (ratio >= 10.0) {
        return Verdict::Warn;
    }
    return Verdict::Fail;
}

Verdict contact_verdict(double r_per_contact) noexcept
{
    if (r_per_contact <= 0.3) {
        return Verdict::Pass;
    }
    if (r_per_contact <= 0.5) {
        return Verdict::Warn;
    }
    return Verdict::Fail;
}

std::string align_left(std::string_view s, std::size_t width)
{
    std::string out{s};
    const std::size_t w = glyphs(s);
    if (w < width) {
        out.append(width - w, ' ');
    }
    return out;
}

std::string align_right(std::string_view s, std::size_t width)
{
    const std::size_t w = glyphs(s);
    std::string out;
    if (w < width) {
        out.assign(width - w, ' ');
    }
    out.append(s);
    return out;
}

void VerificationLog::add(std::string_view name, std::string_view unit,
                          double calc, double meas, double tol_pct)
{
    rows_.push_back(Row{
        .name = std::string{name},
        .unit = std::string{unit},
        .calc = calc,
        .meas = meas,
        .tol_pct = tol_pct
    });
}

void VerificationLog::note(Verdict v) noexcept
{
    extra_ = std::max(extra_, v);
}

Verdict VerificationLog::overall() const noexcept
{
    Verdict worst = extra_;
    for (const auto& r : rows_) {
        worst = std::max(worst, verdict_of(r.calc, r.meas, r.tol_pct));
    }
    return worst;
}

void VerificationLog::render(std::ostream& os) const
{
    os << align_left("Параметр", 36)
       << align_left("Од.", 5)
       << align_right("Розрах.", 11)
       << align_right("Виміряно", 12)
       << align_right("Δ", 11)
       << align_right("δ, %", 9)
       << "  Статус\n"
       << std::string(kTableWidth, '-') << '\n';

    for (const auto& r : rows_) {
        os << align_left(r.name, 36)
           << align_left(r.unit, 5)
           << std::format("{:>11.4f}{:>12.4f}{:>11.4f}{:>9.2f}  {}\n",
                          r.calc, r.meas, r.meas - r.calc,
                          relative_error(r.calc, r.meas),
                          to_string(verdict_of(r.calc, r.meas, r.tol_pct)));
    }
}

}  // namespace bench
