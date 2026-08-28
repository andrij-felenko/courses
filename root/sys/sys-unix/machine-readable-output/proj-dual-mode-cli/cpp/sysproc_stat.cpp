// sysproc_stat.cpp — Ідіоматична реалізація дуального CLI мовою C++20
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <format>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <csignal>

namespace {

constexpr std::string_view ANSI_RESET  = "\033[0m";
constexpr std::string_view ANSI_BOLD   = "\033[1m";
constexpr std::string_view ANSI_GREEN  = "\033[32m";
constexpr std::string_view ANSI_CYAN   = "\033[36m";

enum class OutputMode {
    Auto,
    Human,
    Json,
    Tsv
};

struct ProcessMetric {
    pid_t pid;
    std::string name;
    char state;
    uint64_t rss_bytes;
    uint64_t vsz_bytes;
};

struct Config {
    OutputMode mode = OutputMode::Auto;
    bool enable_color = false;
    bool null_delimited = false;
    bool no_heading = false;
};

[[nodiscard]] bool detect_color_support(int fd) noexcept {
    if (const char *no_color = std::getenv("NO_COLOR"); no_color && no_color[0] != '\0') {
        return false;
    }
    if (const char *force = std::getenv("CLICOLOR_FORCE"); force && std::string_view(force) != "0") {
        return true;
    }
    if (const char *term = std::getenv("TERM"); term && std::string_view(term) == "dumb") {
        return false;
    }
    if (const char *clicolor = std::getenv("CLICOLOR"); clicolor && std::string_view(clicolor) == "0") {
        return false;
    }
    return isatty(fd) == 1;
}

[[nodiscard]] std::string format_human_bytes(uint64_t bytes) {
    constexpr std::string_view units[] = {"B", "KiB", "MiB", "GiB", "TiB"};
    auto size = static_cast<double>(bytes);
    size_t unit_idx = 0;
    while (size >= 1024.0 && unit_idx < 4) {
        size /= 1024.0;
        unit_idx++;
    }
    if (unit_idx == 0) {
        return std::format("{} B", bytes);
    }
    return std::format("{:.1f} {}", size, units[unit_idx]);
}

void print_human(const std::vector<ProcessMetric> &procs, bool color, bool no_heading) {
    if (!no_heading) {
        if (color) {
            std::cout << std::format("{}{:<8} {:<20} {:<8} {:<12} {:<12}{}\n",
                                     ANSI_BOLD, "PID", "NAME", "STATE", "RSS", "VSZ", ANSI_RESET);
        } else {
            std::cout << std::format("{:<8} {:<20} {:<8} {:<12} {:<12}\n",
                                     "PID", "NAME", "STATE", "RSS", "VSZ");
        }
    }

    for (const auto &p : procs) {
        const auto rss_str = format_human_bytes(p.rss_bytes);
        const auto vsz_str = format_human_bytes(p.vsz_bytes);

        if (color) {
            const auto state_col = (p.state == 'R') ? ANSI_GREEN : ANSI_CYAN;
            std::cout << std::format("{:<8} {:<20} {}{:<8}{} {:<12} {:<12}\n",
                                     p.pid, p.name, state_col, p.state, ANSI_RESET, rss_str, vsz_str);
        } else {
            std::cout << std::format("{:<8} {:<20} {:<8} {:<12} {:<12}\n",
                                     p.pid, p.name, p.state, rss_str, vsz_str);
        }
    }
}

void print_tsv(const std::vector<ProcessMetric> &procs, bool no_heading, bool null_delim) {
    const char term = null_delim ? '\0' : '\n';
    if (!no_heading && !null_delim) {
        std::cout << "pid\tname\tstate\trss_bytes\tvsz_bytes\n";
    }
    for (const auto &p : procs) {
        std::cout << std::format("{}\t{}\t{}\t{}\t{}{}",
                                 p.pid, p.name, p.state, p.rss_bytes, p.vsz_bytes, term);
    }
}

void print_json(const std::vector<ProcessMetric> &procs) {
    const auto now = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
    std::cout << std::format("{{\n  \"timestamp\": {},\n  \"processes\": [\n", now);
    for (size_t i = 0; i < procs.size(); ++i) {
        const auto &p = procs[i];
        std::cout << std::format("    {{\n"
                                 "      \"pid\": {},\n"
                                 "      \"name\": \"{}\",\n"
                                 "      \"state\": \"{}\",\n"
                                 "      \"rss_bytes\": {},\n"
                                 "      \"vsz_bytes\": {}\n"
                                 "    }}{}\n",
                                 p.pid, p.name, p.state, p.rss_bytes, p.vsz_bytes,
                                 (i + 1 < procs.size()) ? "," : "");
    }
    std::cout << "  ]\n}\n";
}

} // namespace

int main(int argc, char **argv) {
    std::signal(SIGPIPE, SIG_DFL);
    std::ios_base::sync_with_stdio(false);

    Config cfg;
    for (int i = 1; i < argc; ++i) {
        const std::string_view arg(argv[i]);
        if (arg == "--json" || arg == "-j") {
            cfg.mode = OutputMode::Json;
        } else if (arg == "--raw" || arg == "--tsv") {
            cfg.mode = OutputMode::Tsv;
        } else if (arg == "--human" || arg == "-H") {
            cfg.mode = OutputMode::Human;
        } else if (arg == "-z" || arg == "--null") {
            cfg.null_delimited = true;
            cfg.mode = OutputMode::Tsv;
        } else if (arg == "--no-heading" || arg == "-n") {
            cfg.no_heading = true;
        }
    }

    const bool is_terminal = isatty(STDOUT_FILENO) == 1;
    if (cfg.mode == OutputMode::Auto) {
        cfg.mode = is_terminal ? OutputMode::Human : OutputMode::Tsv;
    }

    cfg.enable_color = (cfg.mode == OutputMode::Human) && detect_color_support(STDOUT_FILENO);

    const std::vector<ProcessMetric> sample_procs = {
        {1, "systemd", 'S', 12451840, 168427520},
        {412, "dbus-daemon", 'S', 4890624, 25165824},
        {1024, "nginx", 'S', 34078720, 142606336},
        {2048, "rust-worker", 'R', 268435456, 1073741824}
    };

    switch (cfg.mode) {
        case OutputMode::Json:
            print_json(sample_procs);
            break;
        case OutputMode::Tsv:
            print_tsv(sample_procs, cfg.no_heading, cfg.null_delimited);
            break;
        case OutputMode::Human:
        case OutputMode::Auto:
            print_human(sample_procs, cfg.enable_color, cfg.no_heading);
            break;
    }

    return 0;
}
