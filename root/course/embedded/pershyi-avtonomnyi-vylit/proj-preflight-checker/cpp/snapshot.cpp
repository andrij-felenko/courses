#include "snapshot.hpp"

#include <algorithm>
#include <cctype>
#include <charconv>
#include <cmath>
#include <format>
#include <functional>
#include <istream>
#include <map>
#include <set>
#include <string_view>
#include <type_traits>
#include <vector>

namespace {

using SetResult = std::expected<void, std::string>;
using Setter    = std::function<SetResult(TelemetrySnapshot&, std::string_view)>;

std::string_view trim(std::string_view text)
{
    constexpr std::string_view space = " \t\r\n";
    const auto begin = text.find_first_not_of(space);
    if (begin == std::string_view::npos) {
        return {};
    }
    return text.substr(begin, text.find_last_not_of(space) - begin + 1);
}

bool iequals(std::string_view a, std::string_view b)
{
    return a.size() == b.size() &&
           std::equal(a.begin(), a.end(), b.begin(), [](char x, char y) {
               return std::tolower(static_cast<unsigned char>(x)) ==
                      std::tolower(static_cast<unsigned char>(y));
           });
}

// Один шаблон замість таблиці зсувів: вказівник на член сам несе і тип
// поля, і місце запису, тож перевірка діапазону дістається від from_chars.
template <class T>
Setter field(T TelemetrySnapshot::*member)
{
    return [member](TelemetrySnapshot& snapshot, std::string_view text) -> SetResult {
        if constexpr (std::is_same_v<T, bool>) {
            for (std::string_view yes : {"true", "1", "yes", "on"}) {
                if (iequals(text, yes)) {
                    snapshot.*member = true;
                    return {};
                }
            }
            for (std::string_view no : {"false", "0", "no", "off"}) {
                if (iequals(text, no)) {
                    snapshot.*member = false;
                    return {};
                }
            }
            return std::unexpected(std::format("очікується true/false, отримано «{}»", text));
        } else {
            T value{};
            const char* first = text.data();
            const char* last  = first + text.size();
            const auto [stop, ec] = std::from_chars(first, last, value);

            if (ec == std::errc::result_out_of_range) {
                return std::unexpected(std::format("значення «{}» поза діапазоном поля", text));
            }
            if (ec != std::errc{} || stop != last) {
                return std::unexpected(std::format("«{}» не є числом потрібного типу", text));
            }
            if constexpr (std::is_floating_point_v<T>) {
                // from_chars радо приймає inf і nan, а вони проходять будь-який поріг
                if (!std::isfinite(value)) {
                    return std::unexpected(std::format("«{}» не є скінченним числом", text));
                }
            }
            snapshot.*member = value;
            return {};
        }
    };
}

// Упорядкована мапа: перелік відсутніх полів виходить сталим і читабельним.
const std::map<std::string_view, Setter>& fields()
{
    static const std::map<std::string_view, Setter> table{
        { "acc_vibe_floor",   field(&TelemetrySnapshot::acc_vibe_floor)   },
        { "battery_temp_c",   field(&TelemetrySnapshot::battery_temp_c)   },
        { "battery_voltage",  field(&TelemetrySnapshot::battery_voltage)  },
        { "cell_delta_v",     field(&TelemetrySnapshot::cell_delta_v)     },
        { "ekf_pos_innov",    field(&TelemetrySnapshot::ekf_pos_innov)    },
        { "ekf_vel_innov",    field(&TelemetrySnapshot::ekf_vel_innov)    },
        { "ekf_yaw_innov",    field(&TelemetrySnapshot::ekf_yaw_innov)    },
        { "geofence_action",  field(&TelemetrySnapshot::geofence_action)  },
        { "geofence_enabled", field(&TelemetrySnapshot::geofence_enabled) },
        { "geofence_points",  field(&TelemetrySnapshot::geofence_points)  },
        { "gps_fix_type",     field(&TelemetrySnapshot::gps_fix_type)     },
        { "gps_hdop",         field(&TelemetrySnapshot::gps_hdop)         },
        { "gps_satellites",   field(&TelemetrySnapshot::gps_satellites)   },
        { "rc_kill_channel",  field(&TelemetrySnapshot::rc_kill_channel)  },
        { "rc_rssi_dbm",      field(&TelemetrySnapshot::rc_rssi_dbm)      }
    };
    return table;
}

std::string join(const std::vector<std::string_view>& items, std::size_t limit)
{
    std::string out;
    for (std::size_t i = 0; i < items.size() && i < limit; ++i) {
        if (!out.empty()) {
            out += ", ";
        }
        out += items[i];
    }
    if (items.size() > limit) {
        out += ", …";
    }
    return out;
}

} // namespace

std::expected<TelemetrySnapshot, std::string> parse_snapshot(std::istream& in)
{
    TelemetrySnapshot snapshot{};
    std::set<std::string_view> seen;   // тримає ключі таблиці, а не рядка-буфера
    std::string line;
    unsigned lineno = 0;

    while (std::getline(in, line)) {
        ++lineno;

        std::string_view text{line};
        if (const auto hash = text.find('#'); hash != std::string_view::npos) {
            text = text.substr(0, hash);
        }
        text = trim(text);
        if (text.empty()) {
            continue;
        }

        const auto eq = text.find('=');
        if (eq == std::string_view::npos) {
            return std::unexpected(
                std::format("рядок {}: очікується «ключ=значення», маємо «{}»", lineno, text));
        }

        const auto key   = trim(text.substr(0, eq));
        const auto value = trim(text.substr(eq + 1));

        const auto it = fields().find(key);
        if (it == fields().end()) {
            return std::unexpected(std::format("рядок {}: невідоме поле «{}»", lineno, key));
        }
        if (!seen.insert(it->first).second) {
            // Двічі задане поле — ознака склеєних дампів із різних бортів
            return std::unexpected(std::format("рядок {}: поле «{}» задано двічі", lineno, key));
        }
        if (const auto stored = it->second(snapshot, value); !stored) {
            return std::unexpected(
                std::format("рядок {}: поле «{}»: {}", lineno, key, stored.error()));
        }
    }

    if (in.bad()) {
        return std::unexpected("помилка читання потоку зі зліпком");
    }

    std::vector<std::string_view> missing;
    for (const auto& [name, setter] : fields()) {
        if (!seen.contains(name)) {
            missing.push_back(name);
        }
    }
    if (!missing.empty()) {
        return std::unexpected(std::format("у зліпку бракує {} полів: {}",
                                           missing.size(), join(missing, 5)));
    }

    return snapshot;
}
