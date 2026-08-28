#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <filesystem>
#include <expected>

namespace fs = std::filesystem;

struct PackageInfo {
    std::string name;
    std::string version;
    std::string license;
    std::string license_file;
};

class NoticesGenerator {
public:
    static std::expected<void, std::string> build_notices(
        const fs::path& csv_manifest,
        const fs::path& licenses_dir,
        const fs::path& output_file) 
    {
        std::ifstream csv(csv_manifest);
        if (!csv.is_open()) {
            return std::unexpected("Не вдалося відкрити CSV-маніфест: " + csv_manifest.string());
        }

        std::ofstream out(output_file);
        if (!out.is_open()) {
            return std::unexpected("Не вдалося створити вихідний файл: " + output_file.string());
        }

        out << "================================================================================\n"
            << "                    OPEN SOURCE SOFTWARE NOTICES & LICENSES\n"
            << "================================================================================\n\n";

        std::string line;
        bool is_header = true;

        while (std::getline(csv, line)) {
            if (is_header) {
                is_header = false;
                continue;
            }
            if (line.empty()) continue;

            auto pkg = parse_csv_line(line);
            if (!pkg) continue;

            out << "--------------------------------------------------------------------------------\n"
                << "Package: " << pkg->name << " (version: " << pkg->version << ")\n"
                << "SPDX License: " << pkg->license << "\n"
                << "--------------------------------------------------------------------------------\n\n";

            auto lic_path = licenses_dir / (pkg->name + "-" + pkg->version) / pkg->license_file;
            if (!fs::exists(lic_path)) {
                lic_path = licenses_dir / pkg->name / pkg->license_file;
            }

            if (fs::exists(lic_path)) {
                std::ifstream lic_stream(lic_path);
                out << lic_stream.rdbuf() << "\n\n";
            } else {
                out << "[Текст ліцензії відсутній за шляхом: " << lic_path.string() << "]\n\n";
            }
        }

        return {};
    }

private:
    static std::optional<PackageInfo> parse_csv_line(const std::string& line) {
        std::stringstream ss(line);
        std::string item;
        std::vector<std::string> fields;

        while (std::getline(ss, item, ',')) {
            // Видаляємо лапки навколо полів CSV
            if (item.size() >= 2 && item.front() == '"' && item.back() == '"') {
                item = item.substr(1, item.size() - 2);
            }
            fields.push_back(item);
        }

        if (fields.size() < 4) return std::nullopt;
        return PackageInfo{fields[0], fields[1], fields[2], fields[3]};
    }
};
