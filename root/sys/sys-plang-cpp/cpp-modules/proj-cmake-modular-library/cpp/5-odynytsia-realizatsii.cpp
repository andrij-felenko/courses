module matrix;

import <iostream>;
import <iomanip>;

namespace math {

void print_matrix(const Matrix2x2& m, const std::string& label) {
    std::cout << "=== " << label << " ===\n";
    for (std::size_t r = 0; r < 2; ++r) {
        std::cout << "| ";
        for (std::size_t c = 0; c < 2; ++c) {
            std::cout << std::setw(8) << std::fixed << std::setprecision(3) << m.at(r, c) << " ";
        }
        std::cout << "|\n";
    }
}

} // namespace math
