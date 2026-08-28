#include <stop_token>
#include <iostream>
#include <vector>

void process_matrix_blocks(std::stop_token stoken, const std::vector<double>& matrix) {
    for (size_t block = 0; block < matrix.size(); ++block) {
        // Періодична атомарна перевірка запиту на скасування
        if (stoken.stop_requested()) {
            std::cout << "Обчислення перервано на блоці " << block << "\n";
            return;
        }
        // Виконання ресурсомісткого математичного кроку
    }
}
