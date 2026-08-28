// Ідіоматичний C++ підхід з використанням std::locale та std::collate
#include <iostream>
#include <string>
#include <locale>

int main() {
    try {
        // Створення об'єкта локалі без зміни глобального стану процесу
        std::locale loc("uk_UA.UTF-8");
        
        // Витягування фасету сортування
        const auto& coll = std::use_facet<std::collate<char>>(loc);

        std::string s1 = "апельсин";
        std::string s2 = "банан";

        int res = coll.compare(s1.data(), s1.data() + s1.size(),
                               s2.data(), s2.data() + s2.size());
        if (res < 0) {
            std::cout << s1 << " передує " << s2 << "\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка локалі: " << e.what() << "\n";
    }
    return 0;
}
