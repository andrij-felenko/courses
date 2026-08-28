#include <string_view>
#include <vector>
#include <algorithm>
#include <charconv>
#include <cstdint>

struct ByteRange {
    uint64_t start{0};
    uint64_t end{0};

    [[nodiscard]] constexpr uint64_t length() const noexcept {
        return end - start + 1;
    }
};

struct RangeResult {
    std::vector<ByteRange> ranges;
    bool unsatisfiable{false};
};

class RangeParser {
public:
    static constexpr size_t kMaxRangesLimit = 16;

    static RangeResult parse(std::string_view header, uint64_t fileSize) {
        RangeResult result;
        if (fileSize == 0) {
            result.unsatisfiable = true;
            return result;
        }

        header = trim(header);
        constexpr std::string_view kPrefix = "bytes=";
        if (!header.starts_with(kPrefix)) {
            return result; // Невідома одиниця: за стандартом повертаємо 200 OK
        }
        header.remove_prefix(kPrefix.size());

        while (!header.empty() && result.ranges.size() < kMaxRangesLimit) {
            auto commaPos = header.find(',');
            auto token = trim(header.substr(0, commaPos));
            header = (commaPos == std::string_view::npos) ? std::string_view{} : header.substr(commaPos + 1);

            if (token.empty()) continue;

            auto dashPos = token.find('-');
            if (dashPos == std::string_view::npos) continue;

            auto startPart = trim(token.substr(0, dashPos));
            auto endPart = trim(token.substr(dashPos + 1));

            if (startPart.empty()) {
                // Форма -suffix
                uint64_t suffix = 0;
                if (auto [p, ec] = std::from_chars(endPart.data(), endPart.data() + endPart.size(), suffix);
                    ec == std::errc{} && suffix > 0) {
                    uint64_t start = (suffix >= fileSize) ? 0 : (fileSize - suffix);
                    result.ranges.push_back({start, fileSize - 1});
                }
            } else if (endPart.empty()) {
                // Форма start-
                uint64_t start = 0;
                if (auto [p, ec] = std::from_chars(startPart.data(), startPart.data() + startPart.size(), start);
                    ec == std::errc{}) {
                    if (start < fileSize) {
                        result.ranges.push_back({start, fileSize - 1});
                    } else {
                        result.unsatisfiable = true;
                    }
                }
            } else {
                // Форма start-end
                uint64_t start = 0, end = 0;
                auto res1 = std::from_chars(startPart.data(), startPart.data() + startPart.size(), start);
                auto res2 = std::from_chars(endPart.data(), endPart.data() + endPart.size(), end);
                if (res1.ec == std::errc{} && res2.ec == std::errc{} && start <= end) {
                    if (start < fileSize) {
                        result.ranges.push_back({start, std::min(end, fileSize - 1)});
                    } else {
                        result.unsatisfiable = true;
                    }
                }
            }
        }

        if (!result.ranges.empty()) {
            result.unsatisfiable = false;
            coalesce(result.ranges);
        }
        return result;
    }

private:
    static std::string_view trim(std::string_view s) noexcept {
        while (!s.empty() && (s.front() == ' ' || s.front() == '\t')) s.remove_prefix(1);
        while (!s.empty() && (s.back() == ' ' || s.back() == '\t')) s.remove_suffix(1);
        return s;
    }

    static void coalesce(std::vector<ByteRange>& ranges) {
        if (ranges.size() <= 1) return;

        std::sort(ranges.begin(), ranges.end(), [](const auto& a, const auto& b) {
            return a.start < b.start;
        });

        std::vector<ByteRange> merged;
        merged.reserve(ranges.size());
        merged.push_back(ranges.front());

        for (size_t i = 1; i < ranges.size(); ++i) {
            auto& current = merged.back();
            if (ranges[i].start <= current.end + 1) {
                current.end = std::max(current.end, ranges[i].end);
            } else {
                merged.push_back(ranges[i]);
            }
        }
        ranges = std::move(merged);
    }
};
