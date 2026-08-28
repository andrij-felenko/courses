#include <filesystem>
namespace fs = std::filesystem;

void clean_logs(const fs::path& log_dir) {
    if (!fs::exists(log_dir) || !fs::is_directory(log_dir)) return;

    // Кросплатформна рекурсивна ітерація по каталогу
    for (const auto& entry : fs::recursive_directory_iterator(log_dir)) {
        if (entry.is_regular_file() && entry.path().extension() == ".tmp") {
            std::error_code ec;
            fs::remove(entry.path(), ec); // Видалення без викидання винятків
            if (ec) {
                std::cerr << "Помилка видалення: " << ec.message() << "\n";
            }
        }
    }
}
