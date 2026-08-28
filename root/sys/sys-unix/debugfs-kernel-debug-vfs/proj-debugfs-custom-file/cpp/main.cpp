// Modern Userspace Client in C++20 (RAII & std::filesystem)
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <string_view>
#include <system_error>

namespace fs = std::filesystem;

class DebugfsInspector {
public:
    static constexpr std::string_view base_path = "/sys/kernel/debug/inspector_demo";

    bool is_available() const noexcept {
        std::error_code ec;
        return fs::exists(base_path, ec);
    }

    void print_file(const fs::path& rel_path, std::string_view title) const {
        fs::path full_path = fs::path(base_path) / rel_path;
        std::ifstream file(full_path);
        
        if (!file.is_open()) {
            std::cerr << "Failed to open debugfs file: " << full_path << '\n';
            return;
        }

        std::cout << "=== " << title << " ===\n";
        std::string line;
        while (std::getline(file, line)) {
            std::cout << line << '\n';
        }
        std::cout << '\n';
    }

    void set_control(std::string_view value) const {
        fs::path control_path = fs::path(base_path) / "control";
        std::ofstream file(control_path);

        if (!file.is_open()) {
            std::cerr << "Failed to open control file for writing: " << control_path << '\n';
            return;
        }

        file << value;
        std::cout << "Successfully updated control state to: " << value << '\n';
    }
};

int main() {
    DebugfsInspector inspector;

    if (!inspector.is_available()) {
        std::cerr << "Error: /sys/kernel/debug/inspector_demo is inaccessible.\n"
                  << "Ensure the module is loaded and program runs with root privileges.\n";
        return 1;
    }

    inspector.print_file("event_count", "Current Event Count");
    inspector.set_control("1");
    inspector.print_file("events_log", "Kernel Events Log");

    return 0;
}
