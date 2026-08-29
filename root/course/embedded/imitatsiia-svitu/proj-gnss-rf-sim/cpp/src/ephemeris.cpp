#include "ephemeris.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <format>
#include <fstream>
#include <iostream>
#include <numbers>

namespace gnss {
namespace {

constexpr double kPi = std::numbers::pi;

// Поле фіксованої ширини у форматі Фортрана: показник степеня буває 'D'.
double field(std::string_view line, std::size_t col, std::size_t width)
{
    if (col >= line.size()) return 0.0;
    std::string text{line.substr(col, std::min(width, line.size() - col))};
    std::ranges::replace(text, 'D', 'E');
    std::ranges::replace(text, 'd', 'E');
    return std::strtod(text.c_str(), nullptr);
}

int int_field(std::string_view line, std::size_t col, std::size_t width)
{
    return static_cast<int>(field(line, col, width));
}

bool has_label(std::string_view line, std::string_view label)
{
    return line.size() >= 61 && line.substr(60).starts_with(label);
}

// Дні від 1970-01-01 (алгоритм Гінанта).
long days_from_civil(int y, int m, int d) noexcept
{
    y -= (m <= 2);
    const long era = (y >= 0 ? y : y - 399) / 400;
    const auto yoe = static_cast<unsigned>(y - era * 400);
    const auto doy = static_cast<unsigned>((153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1);
    const unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    return era * 146097 + static_cast<long>(doe) - 719468;
}

// Епоха навігаційного запису GPS подана вже у шкалі GPS.
GpsTime calendar_to_gps(int y, int mo, int d, int h, int mi, double s) noexcept
{
    constexpr long kGpsEpochDay = 3657;      // 1980-01-06
    const long days = days_from_civil(y, mo, d) - kGpsEpochDay;
    return {static_cast<int>(days / 7),
            static_cast<double>(days % 7) * 86400.0 + h * 3600.0 + mi * 60.0 + s};
}

int lines_of_record(char system) noexcept
{
    switch (system) {
    case 'G': case 'E': case 'C': case 'J': case 'I': return 7;
    case 'R': case 'S':                               return 3;
    default:                                          return -1;
    }
}

}  // namespace

std::string_view describe(RinexError e) noexcept
{
    switch (e) {
    case RinexError::NotFound:           return "файл не відкривається";
    case RinexError::TruncatedHeader:    return "шапка обірвана, END OF HEADER немає";
    case RinexError::UnsupportedVersion: return "потрібен RINEX 3 — у v2 інша розкладка колонок";
    case RinexError::NoUsableRecords:    return "жодного придатного запису GPS";
    }
    return "невідома помилка";
}

std::expected<Navigation, RinexError> Navigation::load(const std::string& path)
{
    std::ifstream file{path};
    if (!file) return std::unexpected(RinexError::NotFound);

    Navigation nav;
    std::array<double, 4> alpha{}, beta{};
    bool have_alpha = false, have_beta = false;
    double version = 0.0;
    bool header_done = false;

    std::string line;
    while (std::getline(file, line)) {
        if (has_label(line, "RINEX VERSION / TYPE")) {
            version = field(line, 0, 9);
        } else if (has_label(line, "IONOSPHERIC CORR")) {
            std::array<double, 4> v{};
            for (std::size_t i = 0; i < v.size(); ++i) v[i] = field(line, 5 + i * 12, 12);
            if (line.starts_with("GPSA")) { alpha = v; have_alpha = true; }
            else if (line.starts_with("GPSB")) { beta = v; have_beta = true; }
        } else if (has_label(line, "LEAP SECONDS")) {
            nav.leap_ = int_field(line, 0, 6);
        } else if (has_label(line, "END OF HEADER")) {
            header_done = true;
            break;
        }
    }

    if (!header_done) return std::unexpected(RinexError::TruncatedHeader);
    if (version < 3.0) return std::unexpected(RinexError::UnsupportedVersion);
    if (have_alpha && have_beta) nav.iono_.emplace(alpha, beta);

    while (std::getline(file, line)) {
        if (line.size() < 20) continue;

        const int body_lines = lines_of_record(line.front());
        if (body_lines < 0) {
            std::cerr << std::format("невідома система '{}', запис пропущено\n", line.front());
            continue;
        }

        std::vector<std::string> body;
        body.reserve(static_cast<std::size_t>(body_lines));
        for (int i = 0; i < body_lines; ++i) {
            std::string b;
            if (!std::getline(file, b)) break;
            body.push_back(std::move(b));
        }
        if (static_cast<int>(body.size()) != body_lines) {
            std::cerr << "запис обірвано посеред BROADCAST ORBIT\n";
            break;
        }
        if (line.front() != 'G') continue;         // стенд синтезує лише GPS L1 C/A

        Ephemeris e{};
        e.prn = int_field(line, 1, 2);
        if (e.prn < 1 || e.prn > 32) {
            std::cerr << std::format("PRN {} поза межами GPS, запис пропущено\n", e.prn);
            continue;
        }

        const GpsTime toc = calendar_to_gps(int_field(line, 4, 4), int_field(line, 9, 2),
                                            int_field(line, 12, 2), int_field(line, 15, 2),
                                            int_field(line, 18, 2), field(line, 21, 2));
        e.toc = toc.tow();
        e.af0 = field(line, 23, 19);
        e.af1 = field(line, 42, 19);
        e.af2 = field(line, 61, 19);

        std::array<std::array<double, 4>, 7> o{};
        for (std::size_t i = 0; i < o.size(); ++i)
            for (std::size_t j = 0; j < 4; ++j)
                o[i][j] = field(body[i], 4 + j * 19, 19);

        e.iode      = static_cast<int>(o[0][0]);
        e.crs       = o[0][1];
        e.delta_n   = o[0][2] * kPi;         // напівоберти/с → рад/с
        e.m0        = o[0][3] * kPi;
        e.cuc       = o[1][0];
        e.ecc       = o[1][1];
        e.cus       = o[1][2];
        e.sqrt_a    = o[1][3];
        e.toe       = o[2][0];
        e.cic       = o[2][1];
        e.omega0    = o[2][2] * kPi;
        e.cis       = o[2][3];
        e.i0        = o[3][0] * kPi;
        e.crc       = o[3][1];
        e.omega_arg = o[3][2] * kPi;
        e.omega_dot = o[3][3] * kPi;
        e.idot      = o[4][0] * kPi;
        e.week      = static_cast<int>(o[4][2]);
        e.accuracy  = o[5][0];
        e.health    = static_cast<int>(o[5][1]);
        e.tgd       = o[5][2];
        e.iodc      = static_cast<int>(o[5][3]);

        if (e.sqrt_a < 1000.0 || e.ecc < 0.0 || e.ecc > 0.1) {
            std::cerr << std::format("PRN {:02}: неправдоподібна орбіта (√A={:.1f} e={:.4f})\n",
                                     e.prn, e.sqrt_a, e.ecc);
            continue;
        }
        nav.ephemerides_.push_back(e);
    }

    if (nav.ephemerides_.empty()) return std::unexpected(RinexError::NoUsableRecords);
    return nav;
}

const Ephemeris* Navigation::select(int prn, GpsTime t) const noexcept
{
    const Ephemeris* best = nullptr;
    double best_age = 0.0;

    for (const auto& e : ephemerides_) {
        if (e.prn != prn || e.health != 0) continue;    // нездоровий апарат у сузір'я не йде

        const double age = std::abs(t - GpsTime{e.week, e.toe});
        if (age > 7200.0) continue;                     // поза інтервалом придатності
        if (best == nullptr || age < best_age) { best = &e; best_age = age; }
    }
    return best;
}

std::expected<SatelliteState, OrbitError> Ephemeris::state_at(GpsTime t) const noexcept
{
    const double tk = t - GpsTime{week, toe};
    if (std::abs(tk) > 7200.0) return std::unexpected(OrbitError::Expired);

    const double a  = sqrt_a * sqrt_a;
    const double n  = std::sqrt(kGm / (a * a * a)) + delta_n;
    const double mk = m0 + n * tk;

    // Рівняння Кеплера M = E − e·sin E, метод Ньютона.
    double ek = mk;
    bool converged = false;
    for (int i = 0; i < 20; ++i) {
        const double dek = (ek - ecc * std::sin(ek) - mk) / (1.0 - ecc * std::cos(ek));
        ek -= dek;
        if (std::abs(dek) < 1e-13) { converged = true; break; }
    }
    if (!converged) return std::unexpected(OrbitError::NoConvergence);

    const double sin_ek = std::sin(ek), cos_ek = std::cos(ek);
    const double one_e2 = std::sqrt(1.0 - ecc * ecc);
    const double vk   = std::atan2(one_e2 * sin_ek, cos_ek - ecc);
    const double phik = vk + omega_arg;
    const double s2 = std::sin(2.0 * phik), c2 = std::cos(2.0 * phik);

    const double uk = phik + cus * s2 + cuc * c2;
    const double rk = a * (1.0 - ecc * cos_ek) + crs * s2 + crc * c2;
    const double ik = i0 + cis * s2 + cic * c2 + idot * tk;

    const double xp = rk * std::cos(uk), yp = rk * std::sin(uk);
    const double omk = omega0 + (omega_dot - kEarthRate) * tk - kEarthRate * toe;
    const double sin_om = std::sin(omk), cos_om = std::cos(omk);
    const double sin_ik = std::sin(ik),  cos_ik = std::cos(ik);

    SatelliteState st{};
    st.position = {xp * cos_om - yp * cos_ik * sin_om,
                   xp * sin_om + yp * cos_ik * cos_om,
                   yp * sin_ik};

    // Швидкість — аналітичні похідні: числове диференціювання зашумило б доплер,
    // а доплер тут і є предметом.
    const double ek_dot = n / (1.0 - ecc * cos_ek);
    const double vk_dot = ek_dot * one_e2 / (1.0 - ecc * cos_ek);
    const double uk_dot = vk_dot * (1.0 + 2.0 * (cus * c2 - cuc * s2));
    const double rk_dot = a * ecc * sin_ek * ek_dot + 2.0 * vk_dot * (crs * c2 - crc * s2);
    const double ik_dot = idot + 2.0 * vk_dot * (cis * c2 - cic * s2);
    const double om_dot = omega_dot - kEarthRate;

    const double xp_dot = rk_dot * std::cos(uk) - rk * uk_dot * std::sin(uk);
    const double yp_dot = rk_dot * std::sin(uk) + rk * uk_dot * std::cos(uk);

    st.velocity = {xp_dot * cos_om - yp_dot * cos_ik * sin_om
                       + yp * sin_ik * sin_om * ik_dot - st.position.y * om_dot,
                   xp_dot * sin_om + yp_dot * cos_ik * cos_om
                       - yp * sin_ik * cos_om * ik_dot + st.position.x * om_dot,
                   yp_dot * sin_ik + yp * cos_ik * ik_dot};

    double dtc = t.tow() - toc;
    if (dtc >  302400.0) dtc -= kSecondsPerWeek;
    if (dtc < -302400.0) dtc += kSecondsPerWeek;

    st.clock_bias  = af0 + af1 * dtc + af2 * dtc * dtc
                   + kRelF * ecc * sqrt_a * sin_ek - tgd;
    st.clock_drift = af1 + 2.0 * af2 * dtc + kRelF * ecc * sqrt_a * cos_ek * ek_dot;
    return st;
}

}  // namespace gnss
