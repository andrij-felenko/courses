// custom-generator.cpp - Ідіоматичний системний генератор systemd мовою C++
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <system_error>

namespace fs = std::filesystem;

constexpr std::string_view kConfigPath = "/etc/custom-app.conf";
constexpr std::string_view kDefaultExec = "/usr/local/bin/custom-app";
constexpr std::string_view kDefaultPort = "8080";

struct Config {
    std::string exec_path{kDefaultExec};
    std::string port{kDefaultPort};
};

static Config parse_config(const fs::path& config_path) {
    Config cfg;
    std::ifstream file(config_path);
    if (!file.is_open()) return cfg;

    std::string line;
    while (std::getline(file, line)) {
        if (line.empty() || line.starts_with('#')) continue;

        if (line.starts_with("EXEC=")) {
            cfg.exec_path = line.substr(5);
        } else if (line.starts_with("PORT=")) {
            cfg.port = line.substr(5);
        }
    }
    return cfg;
}

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Помилка: генератор вимагає 3 аргументи (normal, early, late dirs)\n";
        return EXIT_FAILURE;
    }

    const fs::path normal_dir = argv[1];
    const fs::path config_path = kConfigPath;

    std::error_code ec;
    if (!fs::exists(config_path, ec)) {
        return EXIT_SUCCESS;
    }

    const auto config = parse_config(config_path);
    const fs::path service_path = normal_dir / "custom-app.service";

    {
        std::ofstream sf(service_path);
        if (!sf.is_open()) {
            std::cerr << "Не вдалося створити unit-файл " << service_path << "\n";
            return EXIT_FAILURE;
        }

        sf << "[Unit]\n"
           << "Description=Динамічна служба Custom App (порт " << config.port << ")\n"
           << "After=network.target\n\n"
           << "[Service]\n"
           << "Type=simple\n"
           << "ExecStart=" << config.exec_path << " --port " << config.port << "\n"
           << "Restart=on-failure\n\n"
           << "[Install]\n"
           << "WantedBy=multi-user.target\n";
    }

    const fs::path wants_dir = normal_dir / "multi-user.target.wants";
    fs::create_directories(wants_dir, ec);
    if (ec) {
        std::cerr << "Не вдалося створити каталог " << wants_dir << ": " << ec.message() << "\n";
        return EXIT_FAILURE;
    }

    const fs::path symlink_path = wants_dir / "custom-app.service";
    fs::remove(symlink_path, ec);

    fs::create_relative_symlink(service_path, symlink_path, ec);
    if (ec) {
        std::cerr << "Не вдалося створити symlink " << symlink_path << ": " << ec.message() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
