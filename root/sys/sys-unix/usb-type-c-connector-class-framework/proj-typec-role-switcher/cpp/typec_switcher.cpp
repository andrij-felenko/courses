// typec_switcher.cpp — Idiomatic C++20 implementation with std::filesystem
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <string_view>
#include <system_error>

namespace fs = std::filesystem;

class TypeCPortInspector {
public:
    explicit TypeCPortInspector(fs::path sysfs_base = "/sys/class/typec")
        : base_path_(std::move(sysfs_base)) {}

    void scan_all_ports() const {
        if (!fs::exists(base_path_)) {
            std::cerr << "Error: " << base_path_ << " does not exist on this kernel.\n";
            return;
        }

        for (const auto& entry : fs::directory_iterator(base_path_)) {
            const auto filename = entry.path().filename().string();
            if (filename.rfind("port", 0) == 0 && filename.find('-') == std::string::npos) {
                print_port_status(entry.path());
            }
        }
    }

    [[nodiscard]] bool request_role_swap(std::string_view port_name, std::string_view target_role) const {
        fs::path target_file;
        if (target_role == "host" || target_role == "device") {
            target_file = base_path_ / port_name / "data_role";
        } else if (target_role == "source" || target_role == "sink") {
            target_file = base_path_ / port_name / "power_role";
        } else {
            std::cerr << "Error: Invalid target role '" << target_role << "'\n";
            return false;
        }

        std::ofstream ofs(target_file);
        if (!ofs.is_open()) {
            std::cerr << "Error: Failed to open " << target_file << " for writing.\n";
            return false;
        }

        ofs << target_role;
        if (ofs.fail()) {
            std::cerr << "Error: Kernel rejected role swap request.\n";
            return false;
        }

        std::cout << "Role swap request to '" << target_role << "' on " << port_name << " accepted by kernel.\n";
        return true;
    }

private:
    fs::path base_path_;

    static std::string read_attribute(const fs::path& attr_path) {
        std::ifstream ifs(attr_path);
        if (!ifs.is_open()) {
            return "unknown";
        }
        std::string val;
        std::getline(ifs, val);
        return val;
    }

    void print_port_status(const fs::path& port_path) const {
        const auto port_name = port_path.filename().string();
        const auto data_role = read_attribute(port_path / "data_role");
        const auto power_role = read_attribute(port_path / "power_role");
        const auto port_type = read_attribute(port_path / "port_type");
        const bool partner_attached = fs::exists(port_path / (port_name + "-partner"));

        std::cout << "=== Port: " << port_name << " ===\n"
                  << "  Port Type:  " << port_type << "\n"
                  << "  Data Role:  " << data_role << "\n"
                  << "  Power Role: " << power_role << "\n"
                  << "  Partner:    " << (partner_attached ? "CONNECTED" : "DISCONNECTED") << "\n\n";
    }
};

int main(int argc, char* argv[]) {
    TypeCPortInspector inspector;

    if (argc >= 4 && std::string_view(argv[1]) == "--swap") {
        const std::string_view port = argv[2];
        const std::string_view role = argv[3];
        return inspector.request_role_swap(port, role) ? EXIT_SUCCESS : EXIT_FAILURE;
    }

    inspector.scan_all_ports();
    return EXIT_SUCCESS;
}
