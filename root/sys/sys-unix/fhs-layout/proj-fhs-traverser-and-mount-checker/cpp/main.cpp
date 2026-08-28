#include <iostream>
#include <filesystem>
#include <vector>
#include <string>
#include <string_view>
#include <iomanip>
#include <sys/statvfs.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

struct FhsNodeInfo {
    std::string path;
    bool is_symlink{false};
    std::string symlink_target{};
    dev_t device_id{0};
    bool is_readonly{false};
    bool exists{false};
};

class FhsInspector {
public:
    static FhsNodeInfo inspect(std::string_view path_str) {
        FhsNodeInfo node;
        node.path = path_str;
        fs::path p(path_str);

        std::error_code ec;
        fs::file_status status = fs::symlink_status(p, ec);

        if (ec || status.type() == fs::file_type::not_found) {
            node.exists = false;
            return node;
        }

        node.exists = true;
        if (fs::is_symlink(status)) {
            node.is_symlink = true;
            fs::path target = fs::read_symlink(p, ec);
            node.symlink_target = ec ? "<invalid_link>" : target.string();
        }

        struct stat st{};
        if (::stat(node.path.c_str(), &st) == 0) {
            node.device_id = st.st_dev;
        }

        struct statvfs stfs{};
        if (::statvfs(node.path.c_str(), &stfs) == 0) {
            node.is_readonly = (stfs.f_flag & ST_RDONLY) != 0;
        }

        return node;
    }

    static void print_report(const std::vector<FhsNodeInfo>& nodes) {
        std::cout << "=== ЗВІТ ІНСПЕКЦІЇ ІЄРАРХІЇ FHS 3.0 (C++20 Impl) ===\n\n";

        bool usrmerge_detected = true;

        for (const auto& node : nodes) {
            if (!node.exists) {
                std::cout << "Каталог: " << std::left << std::setw(12) << node.path
                          << " | Стан: ВІДСУТНІЙ\n";
                continue;
            }

            std::cout << "Каталог: " << std::left << std::setw(12) << node.path << " | ";
            if (node.is_symlink) {
                std::cout << "Тип: SYMLINK -> " << std::left << std::setw(12) << node.symlink_target << " | ";
            } else {
                std::cout << "Тип: DIRECTORY           | ";
            }

            std::cout << "DevID: 0x" << std::hex << node.device_id << std::dec << " | "
                      << "Mode: " << (node.is_readonly ? "READ-ONLY" : "READ-WRITE") << "\n";

            if ((node.path == "/bin" || node.path == "/lib") && !node.is_symlink) {
                usrmerge_detected = false;
            }
        }

        std::cout << "\nСтатус usrmerge: " 
                  << (usrmerge_detected ? "АКТИВНО (успішно об'єднано)" : "ТРАДИЦІЙНИЙ (окремі каталоги)")
                  << "\n";
    }
};

int main() {
    const std::vector<std::string_view> target_paths = {
        "/", "/bin", "/sbin", "/lib", "/usr", "/usr/bin",
        "/var", "/var/log", "/etc", "/tmp", "/run"
    };

    std::vector<FhsNodeInfo> results;
    results.reserve(target_paths.size());

    for (auto path : target_paths) {
        results.push_back(FhsInspector::inspect(path));
    }

    FhsInspector::print_report(results);

    return 0;
}
