#include <iostream>
#include <string_view>
#include <optional>
#include <charconv>
#include <cstdint>
#include <vector>
#include <iomanip>

enum class RegStatus : uint8_t {
    NotRegistered = 0,
    Home          = 1,
    Searching     = 2,
    Denied        = 3,
    Unknown       = 4,
    Roaming       = 5
};

enum class AccessTech : uint8_t {
    Gsm    = 0,
    Utran  = 2,
    Eutran = 7,
    Nr5G   = 12
};

struct CellMetrics {
    bool valid{false};
    int16_t rsrp_dbm{-140};
    float rsrq_db{-20.0f};
    uint32_t cell_id{0};
    uint16_t tac{0};
    RegStatus reg{RegStatus::NotRegistered};
    AccessTech act{AccessTech::Eutran};
    std::string operator_name{};
};

class CellMonitor {
public:
    CellMonitor() = default;

    void processLine(std::string_view line) {
        if (line.starts_with("+CESQ: ")) {
            parseCesq(line.substr(7));
        } else if (line.starts_with("+CEREG: ")) {
            parseCereg(line.substr(8));
        } else if (line.starts_with("+COPS: ")) {
            parseCops(line.substr(7));
        }
    }

    [[nodiscard]] const CellMetrics& metrics() const noexcept { return metrics_; }
    [[nodiscard]] bool checkAndClearHandover() noexcept {
        const bool flag = handover_flag_;
        handover_flag_ = false;
        return flag;
    }

private:
    CellMetrics metrics_{};
    uint32_t previous_cell_id_{0};
    bool handover_flag_{false};

    static std::vector<std::string_view> split(std::string_view s, char delim) {
        std::vector<std::string_view> tokens;
        size_t start = 0;
        while (start < s.size()) {
            const size_t end = s.find(delim, start);
            if (end == std::string_view::npos) {
                tokens.push_back(s.substr(start));
                break;
            }
            tokens.push_back(s.substr(start, end - start));
            start = end + 1;
        }
        return tokens;
    }

    void parseCesq(std::string_view payload) {
        const auto parts = split(payload, ',');
        if (parts.size() < 6) return;

        int rsrq_raw = 255;
        int rsrp_raw = 255;
        std::from_chars(parts[4].data(), parts[4].data() + parts[4].size(), rsrq_raw);
        std::from_chars(parts[5].data(), parts[5].data() + parts[5].size(), rsrp_raw);

        if (rsrp_raw >= 0 && rsrp_raw <= 97) {
            metrics_.rsrp_dbm = static_cast<int16_t>(-140 + rsrp_raw);
            metrics_.valid = true;
        }
        if (rsrq_raw >= 0 && rsrq_raw <= 34) {
            metrics_.rsrq_db = -19.5f + static_cast<float>(rsrq_raw) * 0.5f;
        }

        std::cout << "[METRICS] RSRP: " << metrics_.rsrp_dbm << " dBm, RSRQ: " 
                  << std::fixed << std::setprecision(1) << metrics_.rsrq_db << " dB\n";
    }

    void parseCereg(std::string_view payload) {
        const auto parts = split(payload, ',');
        if (parts.empty()) return;

        size_t idx = (parts.size() >= 4 && parts[0].size() == 1) ? 1 : 0;
        int stat_int = 0;
        std::from_chars(parts[idx].data(), parts[idx].data() + parts[idx].size(), stat_int);
        metrics_.reg = static_cast<RegStatus>(stat_int);

        if (parts.size() >= idx + 3) {
            auto clean_hex = [](std::string_view sv) -> std::string_view {
                if (sv.size() >= 2 && sv.front() == '"' && sv.back() == '"') {
                    return sv.substr(1, sv.size() - 2);
                }
                return sv;
            };

            const auto tac_sv = clean_hex(parts[idx + 1]);
            const auto ci_sv = clean_hex(parts[idx + 2]);

            uint32_t parsed_tac = 0;
            uint32_t parsed_ci = 0;
            std::from_chars(tac_sv.data(), tac_sv.data() + tac_sv.size(), parsed_tac, 16);
            std::from_chars(ci_sv.data(), ci_sv.data() + ci_sv.size(), parsed_ci, 16);

            metrics_.tac = static_cast<uint16_t>(parsed_tac);
            if (previous_cell_id_ != 0 && parsed_ci != 0 && parsed_ci != previous_cell_id_) {
                handover_flag_ = true;
                std::cout << "[EVENT] Handover detected: 0x" << std::hex << previous_cell_id_ 
                          << " -> 0x" << parsed_ci << std::dec << "\n";
            }
            metrics_.cell_id = parsed_ci;
            previous_cell_id_ = parsed_ci;
        }
    }

    void parseCops(std::string_view payload) {
        const auto parts = split(payload, ',');
        if (parts.size() >= 3) {
            std::string_view oper = parts[2];
            if (oper.size() >= 2 && oper.front() == '"' && oper.back() == '"') {
                oper = oper.substr(1, oper.size() - 2);
            }
            metrics_.operator_name = std::string(oper);
            std::cout << "[OPERATOR] Registered network: " << metrics_.operator_name << "\n";
        }
    }
};
