#include <new>
#include <iostream>
#include <cstdlib>

// Резервний буфер пам'яті для екстрених ситуацій
char* emergency_reserve = new char[1024 * 1024 * 16]; // 16 МБ

void out_of_memory_handler() {
    if (emergency_reserve) {
        delete[] emergency_reserve;
        emergency_reserve = nullptr;
        std::cerr << "[ПОПЕРЕДЖЕННЯ] Вичерпано пам'ять! Звільнено аварійний резерв.\n";
        return; // Повернення: operator new спробує виділити пам'ять ще раз!
    }
    std::cerr << "[КРИТИЧНО] Аварійний резерв вичерпано. Зупинка процесу.\n";
    std::set_new_handler(nullptr); // Видалення обробника -> наступний крок кидає bad_alloc
}

int main() {
    std::set_new_handler(out_of_memory_handler);
    // Робота програми...
}
