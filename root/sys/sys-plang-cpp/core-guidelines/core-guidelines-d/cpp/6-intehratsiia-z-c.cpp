#include <memory>
#include <cstdio>

// Спеціальний функтор-видаляч для файлового дескриптора C
struct FileCloser {
    void operator()(std::FILE* fp) const noexcept {
        if (fp) {
            std::fclose(fp);
        }
    }
};

// Зручний аліас типу безпечного файлового дескриптора
using UniqueFile = std::unique_ptr<std::FILE, FileCloser>;

[[nodiscard]] UniqueFile open_secure_config(const char* path) {
    std::FILE* raw_file = std::fopen(path, "re");
    // Негайно передаємо володіння розумному вказівнику:
    // деструктор гарантовано викличе std::fclose при будь-якому виході або винятку
    return UniqueFile(raw_file);
}
