//
// kvm_mmu_tracer.cpp — сучасний ідіоматичний моніторинг KVM MMU на C++20
// Компіляція: g++ -std=c++20 -O2 -Wall kvm_mmu_tracer.cpp -o kvm_mmu_tracer_cpp
//
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <chrono>
#include <csignal>
#include <filesystem>
#include <memory>
#include <system_error>

namespace fs = std::filesystem;
using namespace std::chrono_literals;

namespace {
volatile std::sig_atomic_t g_running = 1;

void handle_signal(int) noexcept {
    g_running = 0;
}

class TracepointGuard {
public:
    explicit TracepointGuard(fs::path root_path)
        : root_(std::move(root_path)) {
        set_enabled("kvm/kvm_exit", true);
        set_enabled("kvm/kvm_page_fault", true);
    }

    ~TracepointGuard() {
        try {
            set_enabled("kvm/kvm_exit", false);
            set_enabled("kvm/kvm_page_fault", false);
        } catch (...) {
            // Деструктор не повинен викидати винятки
        }
    }

    TracepointGuard(const TracepointGuard&) = delete;
    TracepointGuard& operator=(const TracepointGuard&) = delete;

private:
    void set_enabled(std::string_view event, bool enable) {
        fs::path p = root_ / "events" / event / "enable";
        std::ofstream ofs(p);
        if (ofs.is_open()) {
            ofs << (enable ? "1\n" : "0\n");
        }
    }

    fs::path root_;
};

fs::path find_tracefs() {
    const fs::path primary = "/sys/kernel/tracing";
    const fs::path fallback = "/sys/kernel/debug/tracing";

    if (fs::exists(primary / "trace_pipe")) {
        return primary;
    }
    if (fs::exists(fallback / "trace_pipe")) {
        return fallback;
    }
    throw std::runtime_error("tracefs не знайдено (перевірте монтування та права sudo)");
}

struct MMUStats {
    uint64_t ept_violations = 0;
    uint64_t ept_misconfigs = 0;
    uint64_t page_faults = 0;
    uint64_t other_exits = 0;

    void reset() noexcept {
        ept_violations = 0;
        ept_misconfigs = 0;
        page_faults = 0;
        other_exits = 0;
    }
};
} // namespace

int main() {
    std::signal(SIGINT, handle_signal);
    std::signal(SIGTERM, handle_signal);

    try {
        const fs::path root = find_tracefs();
        TracepointGuard guard(root);

        std::ifstream pipe(root / "trace_pipe");
        if (!pipe.is_open()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити trace_pipe");
        }

        std::cout << "Трасування KVM MMU подій запущено. Очікування виходів...\n";

        MMUStats stats;
        std::string line;
        auto last_tick = std::chrono::steady_clock::now();

        while (g_running && std::getline(pipe, line)) {
            const std::string_view sv(line);

            if (sv.find("kvm_exit:") != std::string_view::npos) {
                if (sv.find("reason 0x30") != std::string_view::npos ||
                    sv.find("reason EPT_VIOLATION") != std::string_view::npos) {
                    stats.ept_violations++;
                } else if (sv.find("reason 0x31") != std::string_view::npos ||
                           sv.find("reason EPT_MISCONFIG") != std::string_view::npos) {
                    stats.ept_misconfigs++;
                } else {
                    stats.other_exits++;
                }
            } else if (sv.find("kvm_page_fault:") != std::string_view::npos) {
                stats.page_faults++;
            }

            const auto now = std::chrono::steady_clock::now();
            if (now - last_tick >= 1s) {
                std::cout << "\r[KVM MMU C++] EPT Violations: " << stats.ept_violations
                          << "/s | Page Faults: " << stats.page_faults
                          << "/s | Misconfigs: " << stats.ept_misconfigs
                          << "/s | Інші VM-exits: " << stats.other_exits << std::flush;
                stats.reset();
                last_tick = now;
            }
        }

        std::cout << "\nЗупинка трасування...\n";
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
