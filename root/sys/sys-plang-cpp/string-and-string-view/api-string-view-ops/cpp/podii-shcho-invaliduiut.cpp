#include <iostream>
#include <string>
#include <string_view>

void invalidation_example() {
    std::string source = "Base Text";
    std::string_view view = source;

    // Всі читання через view безпечні
    std::cout << view << "\n"; // Друк "Base Text"

    // МОДИФІКАЦІЯ ДЖЕРЕЛА: Викликає реалокацію пам'яті в купі!
    source.append(" with a very long appended string that forces reallocation");

    // КАТАСТРОФА: view.data() вказує на стару звільнену адресу в купі!
    // std::cout << view << "\n"; // UB: Use-After-Free!
}
