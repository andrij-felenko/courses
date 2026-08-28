#include <iostream>
#include <vector>
#include <functional>
#include <algorithm>

// Генерація всіх розбиттів n-елементної множини у форматі RGS
void generate_all_partitions(std::size_t n,
                             const std::function<void(const std::vector<int>&)>& callback) {
    if (n == 0) return;

    std::vector<int> a(n, 0);
    std::vector<int> m(n, 0);

    auto backtrack = [&](auto& self, std::size_t idx) -> void {
        if (idx == n) {
            callback(a);
            return;
        }

        int max_prev = m[idx - 1];
        for (int v = 0; v <= max_prev + 1; ++v) {
            a[idx] = v;
            m[idx] = std::max(v, max_prev);
            self(self, idx + 1);
        }
    };

    backtrack(backtrack, 1);
}

int main() {
    std::size_t count = 0;
    constexpr std::size_t N = 4;

    std::cout << "Усі розбиття для n = 4 (усього B_4 = 15):\n";
    generate_all_partitions(N, [&](const std::vector<int>& rgs) {
        ++count;
        std::cout << "[" << count << "] RGS: (";
        for (std::size_t i = 0; i < rgs.size(); ++i) {
            std::cout << rgs[i] << (i + 1 < rgs.size() ? ", " : "");
        }
        std::cout << ")\n";
    });

    return 0;
}
