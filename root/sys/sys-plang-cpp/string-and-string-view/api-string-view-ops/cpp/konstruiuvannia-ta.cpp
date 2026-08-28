#include <string>
#include <string_view>

void conversion_rules() {
    std::string str = "Hello C++ World";

    // 1. Неявне перетворення з std::string у std::string_view (O(1))
    std::string_view sv = str; // Неявно: sv.ptr_ = str.data(), sv.size_ = str.size()

    // 2. Неявне перетворення з C-рядка у std::string_view (O(N) через strlen)
    std::string_view sv_lit = "Literal Text";

    // 3. Спроба неявного перетворення з std::string_view у std::string — ПОМИЛКА КОМПІЛЯЦІЇ!
    // std::string str_err = sv; // Помилка: конструктор std::string(string_view) є EXPLICIT

    // 4. Явне конструювання std::string з std::string_view (O(N) алокація у купі)
    std::string str_copy{sv}; // Явно: виділяє новий буфер у купі
}
