#include <iostream>
#include <string_view>
#include <optional>
#include <charconv>
#include <vector>

struct RadioCellInfo {
    int16_t rsrp_dbm{-140};
    float rsrq_db{-20.0f};
    uint32_t cell_id{0};
    bool valid{false};
};

class CellMetricsParser {
public:
    static std::optional<RadioCellInfo> parseCesq(std::string_view response) {
        constexpr std::string_view tag = "+CESQ: ";
        const auto tag_pos = response.find(tag);
        if (tag_pos == std::string_view::npos) return std::nullopt;

        const auto payload = response.substr(tag_pos + tag.size());
        std::vector<std::string_view> tokens;
        size_t start = 0;
        while (start < payload.size()) {
            const size_t end = payload.find(',', start);
            if (end == std::string_view::npos) {
                tokens.push_back(payload.substr(start));
                break;
            }
            tokens.push_back(payload.substr(start, end - start));
            start = end + 1;
        }

        if (tokens.size() < 6) return std::nullopt;

        int rsrq_raw = 255, rsrp_raw = 255;
        std::from_chars(tokens[4].data(), tokens[4].data() + tokens[4].size(), rsrq_raw);
        std::from_chars(tokens[5].data(), tokens[5].data() + tokens[5].size(), rsrp_raw);

        RadioCellInfo info;
        if (rsrp_raw >= 0 && rsrp_raw <= 97) {
            info.rsrp_dbm = static_cast<int16_t>(-140 + rsrp_raw);
            info.valid = true;
        }
        if (rsrq_raw >= 0 && rsrq_raw <= 34) {
            info.rsrq_db = -19.5f + static_cast<float>(rsrq_raw) * 0.5f;
        }
        return info;
    }
};
