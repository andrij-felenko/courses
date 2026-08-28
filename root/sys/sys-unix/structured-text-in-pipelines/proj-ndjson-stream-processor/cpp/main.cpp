#include <iostream>
#include <string>
#include <string_view>
#include <charconv>
#include <optional>
#include <vector>
#include <csignal>
#include <unistd.h>

struct LogRecord {
    std::string_view timestamp;
    std::string_view path;
    long status_code{0};
    double latency_ms{0.0};
};

class NdjsonStreamFilter {
public:
    static std::optional<LogRecord> parse_line(std::string_view line) noexcept {
        LogRecord rec;
        bool has_ts = false, has_path = false, has_status = false, has_latency = false;

        size_t pos = 0;
        const size_t len = line.size();

        while (pos < len) {
            if (line[pos] != '"') { ++pos; continue; }
            ++pos;
            const size_t k_start = pos;
            while (pos < len && line[pos] != '"') ++pos;
            if (pos >= len) break;
            const std::string_view key = line.substr(k_start, pos - k_start);
            ++pos;

            while (pos < len && (line[pos] == ' ' || line[pos] == '\t' || line[pos] == ':')) {
                if (line[pos] == ':') { ++pos; break; }
                ++pos;
            }
            while (pos < len && (line[pos] == ' ' || line[pos] == '\t')) ++pos;
            if (pos >= len) break;

            if (key == "timestamp") {
                if (line[pos] == '"') {
                    ++pos;
                    const size_t v_start = pos;
                    while (pos < len && line[pos] != '"') ++pos;
                    rec.timestamp = line.substr(v_start, pos - v_start);
                    has_ts = true;
                    if (pos < len) ++pos;
                }
            } else if (key == "path") {
                if (line[pos] == '"') {
                    ++pos;
                    const size_t v_start = pos;
                    while (pos < len && line[pos] != '"') ++pos;
                    rec.path = line.substr(v_start, pos - v_start);
                    has_path = true;
                    if (pos < len) ++pos;
                }
            } else if (key == "status") {
                const size_t v_start = pos;
                while (pos < len && (std::isdigit(line[pos]) || line[pos] == '-')) ++pos;
                const auto val_str = line.substr(v_start, pos - v_start);
                long val = 0;
                if (auto [ptr, ec] = std::from_chars(val_str.data(), val_str.data() + val_str.size(), val); ec == std::errc{}) {
                    rec.status_code = val;
                    has_status = true;
                }
            } else if (key == "latency_ms") {
                const size_t v_start = pos;
                while (pos < len && (std::isdigit(line[pos]) || line[pos] == '.' || line[pos] == '-')) ++pos;
                const auto val_str = line.substr(v_start, pos - v_start);
                try {
                    rec.latency_ms = std::stod(std::string(val_str));
                    has_latency = true;
                } catch (...) {
                    // Ігноруємо некоректне числове перетворення
                }
            } else {
                if (line[pos] == '"') {
                    ++pos;
                    while (pos < len && line[pos] != '"') {
                        if (line[pos] == '\\' && pos + 1 < len) ++pos;
                        ++pos;
                    }
                    if (pos < len) ++pos;
                } else {
                    while (pos < len && line[pos] != ',' && line[pos] != '}' && line[pos] != '\n') ++pos;
                }
            }
        }

        if (has_ts && has_path && has_status && has_latency) {
            return rec;
        }
        return std::nullopt;
    }
};

int main() {
    // Прискорюємо синхронізацію стандартних потоків C++
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);

    // Ігноруємо SIGPIPE на рівні процесу, щоб обробляти обрив каналу через статус запису
    std::signal(SIGPIPE, SIG_IGN);

    std::string line;
    line.reserve(4096); // Фіксована місткість буфера, запобігає алокаціям у циклі

    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;

        const auto rec_opt = NdjsonStreamFilter::parse_line(line);
        if (!rec_opt) {
            std::cerr << "[WARN] Некоректний запис ndjson: " << line << '\n';
            continue;
        }

        const auto& rec = *rec_opt;
        if (rec.status_code >= 500 || rec.latency_ms > 1000.0) {
            std::cout << "{\"ts\":\"" << rec.timestamp
                      << "\",\"endpoint\":\"" << rec.path
                      << "\",\"err\":" << rec.status_code
                      << ",\"dur\":" << rec.latency_ms << "}\n";

            if (!std::cout) {
                // Вихідний потік закрито (наприклад, конвеєр перервано командою head)
                break;
            }
        }
    }

    return 0;
}
