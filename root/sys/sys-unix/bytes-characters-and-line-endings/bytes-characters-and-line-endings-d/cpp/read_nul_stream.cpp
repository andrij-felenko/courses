// read_nul_stream.cpp — Безпечне читання NUL-потоку в C++20.
// Збірка: g++ -std=c++20 -Wall -Wextra -O2 read_nul_stream.cpp -o read_nul_stream

#include <iostream>
#include <string>
#include <vector>

int main() {
    // Вимикаємо синхронізацію з stdio для максимальної швидкості
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);

    std::string entry;
    size_t count = 0;

    // Читаємо стандартний ввід до кожного знайденого нульового байта '\0'
    while (std::getline(std::cin, entry, '\0')) {
        ++count;
        std::cout << '[' << count << "] Запис (" << entry.size() << " байтів): " 
                  << entry << '\n';
    }

    return 0;
}
