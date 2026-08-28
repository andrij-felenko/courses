// oops_parser.cpp — Аналізатор адрес збою мовою C++20
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <regex>
#include <cstdlib>
#include <filesystem>

namespace fs = std::filesystem;

class OopsParser {
public:
    explicit OopsParser(fs::path vmlinux_path = {}) 
        : vmlinux_path_(std::move(vmlinux_path)) {}

    void process_log(const fs::path& log_path) const {
        std::ifstream file(log_path);
        if (!file.is_open()) {
            std::cerr << "Error: Cannot open log file: " << log_path << '\n';
            return;
        }

        const std::regex rip_regex(R"(RIP:\s+[0-9a-fA-F]+:([a-zA-Z0-9_]+)\+0x([0-9a-fA-F]+)/0x([0-9a-fA-F]+))");
        std::string line;

        while (std::getline(file, line)) {
            std::smatch match;
            if (std::regex_search(line, match, rip_regex)) {
                const std::string func = match[1].str();
                const std::string offset_hex = match[2].str();
                const unsigned long offset = std::stoul(offset_hex, nullptr, 16);

                std::cout << "[+] Found Faulting RIP:\n    " << line << '\n';
                std::cout << "[+] Extracted Symbol: " << func << " + 0x" << std::hex << offset << std::dec << '\n';

                if (!vmlinux_path_.empty() && fs::exists(vmlinux_path_)) {
                    resolve_with_gdb(func, offset);
                }
            }
        }
    }

private:
    fs::path vmlinux_path_;

    void resolve_with_gdb(std::string_view func, unsigned long offset) const {
        char offset_buf[32];
        snprintf(offset_buf, sizeof(offset_buf), "%lx", offset);

        const std::string cmd = "gdb -batch -ex 'info line *" + std::string(func) + 
                                "+0x" + std::string(offset_buf) + "' " + vmlinux_path_.string() + " 2>/dev/null";
        
        std::cout << "[+] Resolving via GDB:\n";
        std::clog.flush();
        std::system(cmd.c_str());
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <dmesg_oops.txt> [vmlinux_path]\n";
        return 1;
    }

    const fs::path log_path = argv[1];
    const fs::path vmlinux_path = (argc > 2) ? argv[2] : "";

    OopsParser parser(vmlinux_path);
    parser.process_log(log_path);
    return 0;
}
