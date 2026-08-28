// C++: Безпечна та небезпечна передача рядків у C-API
#include <cstdio>
#include <string>
#include <string_view>

void safe_c_api_usage(const std::string& path_str, std::string_view path_view) {
    // 1. Безпечно: c_str() завжди гарантує null-термінатор '\0'
    FILE* f1 = std::fopen(path_str.c_str(), "r");
    if (f1) std::fclose(f1);

    // 2. НЕБЕЗПЕЧНО: path_view.data() МЕНЕ МАТИ '\0' у кінці підрядка!
    // FILE* f2 = std::fopen(path_view.data(), "r"); // Помилка: Buffer Overread!

    // 3. Безпечна адаптація string_view для C-API:
    std::string null_term_path{path_view}; // Явна алокація тимчасового рядка
    FILE* f3 = std::fopen(null_term_path.c_str(), "r");
    if (f3) std::fclose(f3);
}
