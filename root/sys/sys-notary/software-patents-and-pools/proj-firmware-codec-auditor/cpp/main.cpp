#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <filesystem>
#include <span>
#include <algorithm>

namespace fs = std::filesystem;

enum class PatentRisk {
    None,
    AVC,
    HEVC,
    AAC,
    MPEG2
};

struct CodecSignature {
    std::string_view signature;
    std::string_view codec_name;
    std::string_view pool_name;
    PatentRisk risk;
};

class FirmwareCodecAuditor {
public:
    FirmwareCodecAuditor() {
        signatures_ = {
            {"libx264",    "H.264 / AVC",   "Via LA (MPEG LA)",       PatentRisk::AVC},
            {"libgstx264", "H.264 / AVC",   "Via LA (MPEG LA)",       PatentRisk::AVC},
            {"libx265",    "H.265 / HEVC",  "Access Advance / Via",   PatentRisk::HEVC},
            {"libgstx265", "H.265 / HEVC",  "Access Advance / Via",   PatentRisk::HEVC},
            {"libfaac",    "AAC Audio",     "Via LA (Via Licensing)",  PatentRisk::AAC},
            {"libfdk_aac", "AAC Audio",     "Via LA (Via Licensing)",  PatentRisk::AAC},
            {"libmpeg2",   "MPEG-2 Video",  "MPEG LA (Expired in US)", PatentRisk::MPEG2},
            {"libgstaac",  "AAC Audio",     "Via LA (Via Licensing)",  PatentRisk::AAC}
        };
    }

    void audit_file(const fs::path& target_path) const {
        if (!fs::exists(target_path) || !fs::is_regular_file(target_path)) {
            std::cerr << "Помилка: файл " << target_path << " не існує або не є файлом.\n";
            return;
        }

        std::ifstream file(target_path, std::ios::binary | std::ios::ate);
        if (!file.is_open()) {
            std::cerr << "Не вдалося відкрити файл: " << target_path << "\n";
            return;
        }

        const auto file_size = file.tellg();
        file.seekg(0, std::ios::beg);

        std::vector<char> buffer(static_cast<size_t>(file_size));
        if (!file.read(buffer.data(), file_size)) {
            std::cerr << "Помилка зчитування вмісту файлу: " << target_path << "\n";
            return;
        }

        std::string_view content(buffer.data(), buffer.size());
        std::cout << "[*] Аудит файлу: " << target_path.filename().string() 
                  << " (" << buffer.size() << " байтів)\n";

        bool risk_found = false;
        for (const auto& entry : signatures_) {
            if (content.find(entry.signature) != std::string_view::npos) {
                std::cout << "  [!] ВИЯВЛЕНО ПАТЕНТНИЙ РИЗИК:\n";
                std::cout << "      - Сигнатура: " << entry.signature << "\n";
                std::cout << "      - Технологія: " << entry.codec_name << "\n";
                std::cout << "      - Патентний пул: " << entry.pool_name << "\n";
                risk_found = true;
            }
        }

        if (!risk_found) {
            std::cout << "  [+] Чисто: запатентованих кодеків не виявлено.\n";
        }
    }

private:
    std::vector<CodecSignature> signatures_;
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях до файлу або каталогу>\n";
        return 1;
    }

    const fs::path input_path(argv[1]);
    const FirmwareCodecAuditor auditor;

    if (fs::is_directory(input_path)) {
        for (const auto& entry : fs::recursive_directory_iterator(input_path)) {
            if (entry.is_regular_file()) {
                auditor.audit_file(entry.path());
            }
        }
    } else {
        auditor.audit_file(input_path);
    }

    return 0;
}
