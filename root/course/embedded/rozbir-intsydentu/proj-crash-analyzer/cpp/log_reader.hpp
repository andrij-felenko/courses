#pragma once

// Читання зведеного CSV, який лишають утиліти розпакування ULog/DataFlash
// (pyulog, mavlogdump). Колонки шукаються ЗА ІМЕНЕМ у шапці, порядок довільний.

#include "telemetry.hpp"

#include <charconv>
#include <expected>
#include <fstream>
#include <limits>
#include <string>
#include <string_view>
#include <vector>

namespace postmortem {

struct LoadError {
    std::size_t line{0}; // 0 — біда з файлом загалом, не з конкретним рядком
    std::string message;
};

namespace detail {

struct Column {
    std::string_view name;
    bool required;
    void (*apply)(Frame&, float);
};

// Маски здоров'я в старих записах DataFlash немає — вважаємо IMU справним,
// тому imu_status єдина необов'язкова колонка.
inline constexpr std::array<Column, 13> kColumns{{
    {"roll_des",   true,  [](Frame& f, float v) { f.roll_des_deg = v; }},
    {"roll",       true,  [](Frame& f, float v) { f.roll_deg = v; }},
    {"yaw_des",    true,  [](Frame& f, float v) { f.yaw_des_deg = v; }},
    {"yaw",        true,  [](Frame& f, float v) { f.yaw_deg = v; }},
    {"mot0",       true,  [](Frame& f, float v) { f.motor[0] = v; }},
    {"mot1",       true,  [](Frame& f, float v) { f.motor[1] = v; }},
    {"mot2",       true,  [](Frame& f, float v) { f.motor[2] = v; }},
    {"mot3",       true,  [](Frame& f, float v) { f.motor[3] = v; }},
    {"bat_v",      true,  [](Frame& f, float v) { f.bat_voltage_v = v; }},
    {"bat_a",      true,  [](Frame& f, float v) { f.bat_current_a = v; }},
    {"mag_innov",  true,  [](Frame& f, float v) { f.mag_innov = v; }},
    {"gyro_x",     true,  [](Frame& f, float v) { f.gyro_x_rads = v; }},
    {"imu_status", false, [](Frame& f, float v) {
                              f.sensor_status = static_cast<std::uint32_t>(v);
                          }},
}};

inline constexpr std::string_view kTimestampColumn = "timestamp_us";

[[nodiscard]] inline std::string_view trim(std::string_view s) noexcept
{
    constexpr std::string_view space = " \t\r\n";
    const auto first = s.find_first_not_of(space);
    if (first == std::string_view::npos) {
        return {};
    }
    return s.substr(first, s.find_last_not_of(space) - first + 1);
}

[[nodiscard]] inline std::vector<std::string_view> split(std::string_view line)
{
    std::vector<std::string_view> out;
    while (true) {
        const auto comma = line.find(',');
        if (comma == std::string_view::npos) {
            out.push_back(trim(line));
            return out;
        }
        out.push_back(trim(line.substr(0, comma)));
        line.remove_prefix(comma + 1);
    }
}

template <typename T>
[[nodiscard]] std::optional<T> parse(std::string_view token)
{
    T value{};
    const auto* last = token.data() + token.size();
    const auto [ptr, ec] = std::from_chars(token.data(), last, value);
    if (ec != std::errc{} || ptr != last) {
        return std::nullopt;
    }
    return value;
}

} // namespace detail

[[nodiscard]] inline std::expected<std::vector<Frame>, LoadError>
read_csv(const std::string& path)
{
    std::ifstream in(path);
    if (!in) {
        return std::unexpected(LoadError{0, "не вдалося відкрити файл журналу"});
    }

    std::vector<Frame> frames;
    std::vector<int> mapping; // колонка CSV -> індекс у kColumns, -1 чужа
    int timestamp_col = -1;
    bool header_done = false;
    std::size_t lineno = 0;
    std::string line;

    while (std::getline(in, line)) {
        ++lineno;
        const std::string_view body = detail::trim(line);
        if (body.empty() || body.front() == '#') {
            continue;
        }
        const auto tokens = detail::split(body);

        if (!header_done) {
            std::array<bool, detail::kColumns.size()> seen{};
            mapping.assign(tokens.size(), -1);
            for (std::size_t c = 0; c < tokens.size(); ++c) {
                if (tokens[c] == detail::kTimestampColumn) {
                    timestamp_col = static_cast<int>(c);
                    continue;
                }
                for (std::size_t k = 0; k < detail::kColumns.size(); ++k) {
                    if (tokens[c] == detail::kColumns[k].name) {
                        mapping[c] = static_cast<int>(k);
                        seen[k] = true;
                        break;
                    }
                }
            }
            if (timestamp_col < 0) {
                return std::unexpected(LoadError{
                    lineno, std::string("у шапці немає колонки ") +
                                std::string(detail::kTimestampColumn)});
            }
            for (std::size_t k = 0; k < detail::kColumns.size(); ++k) {
                if (detail::kColumns[k].required && !seen[k]) {
                    return std::unexpected(LoadError{
                        lineno, "у шапці немає обов'язкової колонки '" +
                                    std::string(detail::kColumns[k].name) + "'"});
                }
            }
            header_done = true;
            continue;
        }

        if (tokens.size() != mapping.size()) {
            return std::unexpected(LoadError{
                lineno, "колонок " + std::to_string(tokens.size()) + ", а в шапці " +
                            std::to_string(mapping.size())});
        }

        Frame frame;
        const auto ts = detail::parse<std::uint64_t>(tokens[timestamp_col]);
        if (!ts) {
            return std::unexpected(LoadError{
                lineno, "нечитабельна мітка часу '" +
                            std::string(tokens[timestamp_col]) + "'"});
        }
        frame.timestamp_us = *ts;

        for (std::size_t c = 0; c < tokens.size(); ++c) {
            if (mapping[c] < 0) {
                continue;
            }
            const auto& column = detail::kColumns[static_cast<std::size_t>(mapping[c])];
            if (tokens[c].empty()) {
                // Порожня клітинка — поле в цьому кадрі не оновлювалося.
                // Кладемо NaN: аналізатор такий кадр просто відкине. Для маски
                // здоров'я NaN не має сенсу, тож там лишаємо усталене значення.
                if (column.required) {
                    column.apply(frame, std::numeric_limits<float>::quiet_NaN());
                }
                continue;
            }
            const auto value = detail::parse<float>(tokens[c]);
            if (!value) {
                return std::unexpected(LoadError{
                    lineno, "нечитабельне число '" + std::string(tokens[c]) +
                                "' у колонці '" + std::string(column.name) + "'"});
            }
            column.apply(frame, *value);
        }
        frames.push_back(frame);
    }

    if (in.bad()) {
        return std::unexpected(LoadError{lineno, "помилка читання файлу"});
    }
    if (!header_done) {
        return std::unexpected(
            LoadError{0, "файл порожній: немає навіть шапки з іменами колонок"});
    }
    return frames;
}

} // namespace postmortem
