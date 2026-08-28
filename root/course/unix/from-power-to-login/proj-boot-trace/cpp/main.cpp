#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <filesystem>
#include <chrono>
#include <cstring>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

namespace fs = std::filesystem;
using namespace std::chrono_literals;

struct BootMetrics {
    std::optional<std::chrono::microseconds> firmware_time;
    std::optional<std::chrono::microseconds> loader_time;
    std::string root_device = "не вказано (вбудований)";
    std::string init_process = "/sbin/init (типовий)";
    std::string target_unit = "default.target";
    bool is_uefi = false;
    double uptime_seconds = 0.0;
};

class BootTelemetryAnalyzer {
public:
    static constexpr std::string_view EFIVARS_DIR = "/sys/firmware/efi/efivars";
    static constexpr std::string_view CMDLINE_FILE = "/proc/cmdline";
    static constexpr std::string_view UPTIME_FILE  = "/proc/uptime";

    BootMetrics collect() {
        BootMetrics metrics;
        check_firmware_mode(metrics);
        parse_kernel_cmdline(metrics);
        read_system_uptime(metrics);
        return metrics;
    }

private:
    void check_firmware_mode(BootMetrics& m) {
        if (!fs::exists(EFIVARS_DIR) || !fs::is_directory(EFIVARS_DIR)) {
            m.is_uefi = false;
            return;
        }

        m.is_uefi = true;
        m.firmware_time = read_efivar_microseconds("LoaderTimeFirmwareUSec-");
        m.loader_time = read_efivar_microseconds("LoaderTimeExecUSec-");
    }

    std::optional<std::chrono::microseconds> read_efivar_microseconds(std::string_view prefix) {
        try {
            for (const auto& entry : fs::directory_iterator(EFIVARS_DIR)) {
                const auto filename = entry.path().filename().string();
                if (filename.rfind(prefix, 0) == 0) {
                    int fd = ::open(entry.path().c_str(), O_RDONLY | O_CLOEXEC);
                    if (fd < 0) {
                        return std::nullopt;
                    }

                    struct FileCloser {
                        int desc;
                        ~FileCloser() { if (desc >= 0) ::close(desc); }
                    } closer{fd};

                    uint8_t buffer[12] = {0};
                    ssize_t bytes = ::read(fd, buffer, sizeof(buffer));
                    if (bytes >= 12) {
                        uint64_t val = 0;
                        std::memcpy(&val, buffer + 4, sizeof(uint64_t));
                        return std::chrono::microseconds(val);
                    }
                }
            }
        } catch (const std::exception&) {
            return std::nullopt;
        }
        return std::nullopt;
    }

    void parse_kernel_cmdline(BootMetrics& m) {
        std::ifstream file(CMDLINE_FILE.data());
        if (!file.is_open()) {
            return;
        }

        std::string token;
        while (file >> token) {
            if (token.rfind("root=", 0) == 0) {
                m.root_device = token.substr(5);
            } else if (token.rfind("init=", 0) == 0) {
                m.init_process = token.substr(5);
            } else if (token.rfind("systemd.unit=", 0) == 0) {
                m.target_unit = token.substr(13);
            }
        }
    }

    void read_system_uptime(BootMetrics& m) {
        std::ifstream file(UPTIME_FILE.data());
        if (file.is_open()) {
            file >> m.uptime_seconds;
        }
    }
};

int main() {
    BootTelemetryAnalyzer analyzer;
    BootMetrics metrics = analyzer.collect();

    std::cout << "====================================================\n";
    std::cout << "    АНАЛІЗАТОР ТЕЛЕМЕТРІЇ ЗАВАНТАЖЕННЯ (C++20)      \n";
    std::cout << "====================================================\n\n";

    if (metrics.is_uefi) {
        std::cout << "[+] Режим прошивки: UEFI (знайдено інтерфейс efivars)\n";
        if (metrics.firmware_time) {
            const double fw_s = metrics.firmware_time->count() / 1'000'000.0;
            std::cout << "    * Час прошивки UEFI (SEC/PEI/DXE): " << fw_s << " с\n";
        }
        if (metrics.loader_time) {
            const double ld_s = metrics.loader_time->count() / 1'000'000.0;
            std::cout << "    * Час завантажувача: " << ld_s << " с\n";
        }
    } else {
        std::cout << "[-] Режим прошивки: Legacy BIOS або efivars не змонтовано\n";
    }

    std::cout << "\n[+] Параметри старту (/proc/cmdline):\n";
    std::cout << "    * Кореневий пристрій (root):  " << metrics.root_device << "\n";
    std::cout << "    * Первинний процес (init):    " << metrics.init_process << "\n";
    std::cout << "    * Цільовий юніт (target):     " << metrics.target_unit << "\n";
    std::cout << "\n[+] Поточний системний Uptime: " << metrics.uptime_seconds << " с\n";

    return 0;
}
