#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <chrono>
#include <thread>
#include <filesystem>
#include <system_error>

namespace fs = std::filesystem;

struct ProcessMemoryStats {
    unsigned long rss_kb{0};
    unsigned long referenced_kb{0};
};

class WorkingSetInspector {
public:
    explicit WorkingSetInspector(pid_t pid) : pid_(pid) {
        proc_dir_ = "/proc/" + std::to_string(pid_);
        if (!fs::exists(proc_dir_)) {
            throw std::runtime_error("Процес із PID " + std::to_string(pid_) + " не існує.");
        }
    }

    void reset_accessed_bits() const {
        const std::string clear_refs_path = proc_dir_ + "/clear_refs";
        std::ofstream file(clear_refs_path);
        if (!file.is_open()) {
            throw std::system_error(errno, std::generic_category(),
                                   "Не вдалося відкрити " + clear_refs_path + " для запису");
        }
        file << "1\n";
        if (!file.good()) {
            throw std::runtime_error("Помилка під час скидання бітів у " + clear_refs_path);
        }
    }

    [[nodiscard]] ProcessMemoryStats sample_stats() const {
        const std::string smaps_path = proc_dir_ + "/smaps_rollup";
        std::ifstream file(smaps_path);
        if (!file.is_open()) {
            throw std::system_error(errno, std::generic_category(),
                                   "Не вдалося відкрити " + smaps_path);
        }

        ProcessMemoryStats stats{};
        std::string line;
        while (std::getline(file, line)) {
            if (line.starts_with("Rss:")) {
                std::istringstream iss(line.substr(4));
                iss >> stats.rss_kb;
            } else if (line.starts_with("Referenced:")) {
                std::istringstream iss(line.substr(11));
                iss >> stats.referenced_kb;
            }
        }
        return stats;
    }

    [[nodiscard]] pid_t pid() const noexcept { return pid_; }

private:
    pid_t pid_;
    std::string proc_dir_;
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <pid> <вікно_сек>\n";
        return 1;
    }

    try {
        const pid_t pid = std::stoi(argv[1]);
        const int delta_sec = std::stoi(argv[2]);

        if (pid <= 0 || delta_sec <= 0) {
            std::cerr << "Помилка: PID та вікно мають бути додатними значеннями.\n";
            return 1;
        }

        WorkingSetInspector inspector(pid);
        std::cout << "=== Інспекція робочої множини PID=" << pid
                  << " (вікно Δ=" << delta_sec << " с) ===\n";

        inspector.reset_accessed_bits();
        std::cout << "Біти звернення скинуто. Очікування спостереження...\n";

        std::this_thread::sleep_for(std::chrono::seconds(delta_sec));

        const auto stats = inspector.sample_stats();
        const double ws_ratio = (stats.rss_kb > 0)
            ? (static_cast<double>(stats.referenced_kb) / static_cast<double>(stats.rss_kb)) * 100.0
            : 0.0;

        std::cout << "Загальний обсяг резидентної пам'яті (RSS): " << stats.rss_kb << " kB\n";
        std::cout << "Активна робоча множина W(t, Δ):           " << stats.referenced_kb << " kB\n";
        std::cout << "Частка активної пам'яті:                   " << ws_ratio << " %\n";

    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
