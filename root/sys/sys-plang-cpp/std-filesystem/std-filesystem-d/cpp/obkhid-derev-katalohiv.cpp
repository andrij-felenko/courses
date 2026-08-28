#include <iostream>
#include <filesystem>

namespace fs = std::filesystem;

void scan_with_options(const fs::path& root_dir) {
    std::error_code ec;
    // Пропускати каталоги без прав доступу замість генерації винятку
    auto options = fs::directory_options::skip_permission_denied;

    fs::recursive_directory_iterator it(root_dir, options, ec);
    fs::recursive_directory_iterator end_it;

    while (it != end_it) {
        const fs::directory_entry& entry = *it;

        // Приклад: не заходити у приховані каталоги (наприклад, .git)
        if (entry.is_directory() && entry.path().filename().string().starts_with(".")) {
            it.disable_recursion_pending(); // Пропустити занурення
        } else {
            std::cout << "Глибина [" << it.depth() << "]: " << entry.path() << "\n";
        }

        it.increment(ec); // Безпечний крок без винятків
    }
}
