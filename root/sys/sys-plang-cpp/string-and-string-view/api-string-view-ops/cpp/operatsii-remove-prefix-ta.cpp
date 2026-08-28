#include <iostream>
#include <string_view>

void trim_demo() {
    std::string_view sv = "   [DATA_PAYLOAD]   ";

    // Видалення пробілів зліва: пересуває ptr_ уперед на 3 байти
    sv.remove_prefix(3); // sv тепер "[DATA_PAYLOAD]   "

    // Видалення пробілів справа: зменшує size_ на 3 байти
    sv.remove_suffix(3); // sv тепер "[DATA_PAYLOAD]"

    std::cout << "Очищений рядок: " << sv << " (довжина: " << sv.size() << ")\n";
}
