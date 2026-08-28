#include <format>
#include <vector>
#include <iterator>
#include <iostream>

int main() {
    std::vector<char> buffer;
    
    // Запис символів безпосередньо у кінець вектора через back_inserter
    std::format_to(std::back_inserter(buffer), "X: {}, Y: {}", 100, 200);

    // Буфер тепер містить символи без додаткових тимчасових std::string у купі
    std::cout << std::string_view(buffer.data(), buffer.size()) << "\n";
}
