#include <string_view>
#include <cstdint>

namespace unsafe_log {

static std::string_view g_remaining{};
static uint64_t g_total_bytes = 0;
static uint64_t g_error_count = 0;

std::string_view next_token(std::string_view log_line, char delimiter) {
    if (!log_line.empty()) {
        g_remaining = log_line;
    }
    if (g_remaining.empty()) {
        return {};
    }

    auto pos = g_remaining.find(delimiter);
    if (pos != std::string_view::npos) {
        auto token = g_remaining.substr(0, pos);
        g_remaining.remove_prefix(pos + 1);
        return token;
    } else {
        auto token = g_remaining;
        g_remaining = {};
        return token;
    }
}

void record_metric(int status_code, uint64_t bytes) {
    g_total_bytes += bytes;
    if (status_code >= 400) {
        ++g_error_count;
    }
}

} // namespace unsafe_log
