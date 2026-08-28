#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <optional>
#include <openssl/sha.h>

namespace fs = std::filesystem;

class ContentAddressableStore {
public:
    explicit ContentAddressableStore(fs::path root_dir) 
        : root_dir_(std::move(root_dir)) {
        fs::create_directories(root_dir_ / "tmp");
    }

    // Обчислення SHA-256 у шістнадцятковий рядок
    static std::string compute_sha256(std::string_view data) {
        unsigned char hash[SHA256_DIGEST_LENGTH];
        SHA256(reinterpret_cast<const unsigned char*>(data.data()), data.size(), hash);
        
        std::ostringstream oss;
        for (unsigned char byte : hash) {
            oss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
        }
        return oss.str();
    }

    // Отримання відносного шляху блобу за префіксом (2 символи на підкаталог)
    [[nodiscard]] fs::path blob_path(std::string_view digest) const {
        return root_dir_ / digest.substr(0, 2) / digest.substr(2);
    }

    // Збереження блобу з гарантією атомарності та дедуплікації
    std::string put(std::string_view data) {
        const std::string digest = compute_sha256(data);
        const fs::path target = blob_path(digest);

        if (fs::exists(target)) {
            return digest; // Уже збережено — дедуплікація
        }

        fs::create_directories(target.parent_path());

        // Атомарний запис через тимчасовий файл у тій самій файловій системі
        const fs::path temp_file = root_dir_ / "tmp" / (digest + ".tmp." + std::to_string(rand()));
        {
            std::ofstream out(temp_file, std::ios::binary | std::ios::trunc);
            out.write(data.data(), static_cast<std::streamsize>(data.size()));
            out.flush();
        }

        fs::rename(temp_file, target);
        return digest;
    }

    // Читання блобу із самоперевіркою цілісності на льоту
    std::optional<std::string> get(std::string_view digest) const {
        const fs::path path = blob_path(digest);
        if (!fs::exists(path)) {
            return std::nullopt;
        }

        std::ifstream in(path, std::ios::binary);
        std::stringstream buffer;
        buffer << in.rdbuf();
        std::string content = buffer.str();

        // Верифікація інваріанта: захист від апаратного пошкодження диска
        if (compute_sha256(content) != digest) {
            std::cerr << "[КРИТИЧНО] Пошкодження даних для блобу: " << digest << std::endl;
            return std::nullopt;
        }

        return content;
    }

private:
    fs::path root_dir_;
};

int main() {
    ContentAddressableStore store("./cas_repository");

    std::string payload = "console.log('Production static asset payload');";
    std::string digest = store.put(payload);

    std::cout << "Збережено блоб з відбитком: " << digest << std::endl;

    auto retrieved = store.get(digest);
    if (retrieved) {
        std::cout << "Успішно прочитано та верифіковано: " << *retrieved << std::endl;
    }
    return 0;
}
