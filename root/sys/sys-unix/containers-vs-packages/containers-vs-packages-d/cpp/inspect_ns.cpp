// inspect_ns.cpp — Ідіоматична перевірка просторів імен мовою C++20
#include <iostream>
#include <filesystem>
#include <string_view>
#include <system_error>
#include <vector>

namespace fs = std::filesystem;

class NamespaceInspector {
public:
    explicit NamespaceInspector(std::string_view pid)
        : proc_ns_path_(fs::path("/proc") / pid / "ns") {}

    void print_namespaces() const {
        std::error_code ec;
        if (!fs::exists(proc_ns_path_, ec)) {
            std::cerr << "Каталог процесу " << proc_ns_path_ << " не існує або недоступний\n";
            return;
        }

        std::cout << "=== [C++ Inspector] Inspecting namespaces for PID " << proc_ns_path_ << " ===\n";
        for (const auto& entry : fs::directory_iterator(proc_ns_path_, ec)) {
            std::error_code symlink_ec;
            auto target = fs::read_symlink(entry.path(), symlink_ec);
            if (!symlink_ec) {
                std::cout << "  * " << entry.path().filename().string() 
                          << " -> " << target.string() << "\n";
            }
        }
    }

private:
    fs::path proc_ns_path_;
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: inspect_ns <PID>\n";
        return EXIT_FAILURE;
    }

    NamespaceInspector inspector(argv[1]);
    inspector.print_namespaces();
    return EXIT_SUCCESS;
}
