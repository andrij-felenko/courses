/* Обгортка розв'язання задачі рюкзака на C++ */
std::optional<std::vector<int>> solve_knapsack(std::span<const int64_t> weights, int64_t target_sum) {
    const auto n = static_cast<int>(weights.size());
    const int dim = n + 1;
    const auto N = static_cast<int64_t>(std::ceil(0.5 * std::sqrt(n))) + 10;

    std::vector<std::vector<int64_t>> matrix(dim, std::vector<int64_t>(dim, 0));

    for (int i = 0; i < n; i++) {
        matrix[i][i] = 2;
        matrix[i][n] = 2 * N * weights[i];
    }
    for (int j = 0; j < n; j++) {
        matrix[n][j] = 1;
    }
    matrix[n][n] = 2 * N * target_sum;

    Lattice lattice(std::move(matrix));
    lattice.reduce(0.75);

    for (int row = 0; row < dim; row++) {
        if (lattice[row][n] == 0) {
            bool valid = true;
            for (int j = 0; j < n; j++) {
                if (std::abs(lattice[row][j]) != 1) {
                    valid = false;
                    break;
                }
            }
            if (valid) {
                std::vector<int> solution(n);
                const bool invert = (lattice[row][0] < 0);
                for (int j = 0; j < n; j++) {
                    const int64_t val = invert ? -lattice[row][j] : lattice[row][j];
                    solution[j] = (val > 0) ? 1 : 0;
                }
                return solution;
            }
        }
    }
    return std::nullopt;
}

int main() {
    const std::vector<int64_t> weights = {102, 205, 412, 825, 1653, 3310, 6625, 13254};
    const int64_t target_sum = 17903; // 102 + 412 + 825 + 3310 + 13254

    std::cout << "Криптоаналіз рюкзака Меркля — Геллмана через LLL (C++):\n";
    std::cout << "Цільова сума S = " << target_sum << "\n";

    if (auto result = solve_knapsack(weights, target_sum)) {
        std::cout << "Знайдено секретний бітовий вектор x: [ ";
        for (int bit : *result) {
            std::cout << bit << " ";
        }
        std::cout << "]\n";
    } else {
        std::cout << "Розв'язок не знайдено.\n";
    }

    return 0;
}
