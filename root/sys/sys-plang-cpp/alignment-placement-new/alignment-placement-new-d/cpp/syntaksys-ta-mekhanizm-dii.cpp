#include <new>
#include <cstddef>
#include <string>
#include <iostream>

int main() {
    // 1. Виділяємо сирий буфер пам'яті з ПРАВИЛЬНИМ вирівнюванням
    alignas(std::string) std::byte storage[sizeof(std::string)];

    // На цьому етапі в storage лежать неініціалізовані байти.
    // Об'єкта std::string ще НЕ існує. Викликати його методи — це грубе UB.

    // 2. Конструюємо об'єкт у підготовленому буфері через розміщувальний new
    std::string* str_ptr = ::new (storage) std::string("Привіт, розміщувальний new!");

    // Тепер час життя об'єкта почався. Використання методів законне.
    std::cout << *str_ptr << " (довжина: " << str_ptr->length() << ")\n";

    // 3. Завершення часу життя об'єкта
    str_ptr->~basic_string();
}
