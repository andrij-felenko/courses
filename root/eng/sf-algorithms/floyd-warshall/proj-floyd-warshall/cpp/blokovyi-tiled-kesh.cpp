#include <vector>
#include <algorithm>
#include <cstdint>

class TiledFloydWarshall {
public:
    static constexpr int BLOCK_SIZE = 64;
    static constexpr int64_t INF_VAL = (1LL << 60);

    static void compute(std::vector<int64_t>& matrix, int n) {
        const int num_blocks = (n + BLOCK_SIZE - 1) / BLOCK_SIZE;

        for (int bk = 0; bk < num_blocks; ++bk) {
            // Фаза 1: Оновлення залежного діагонального блоку
            process_block(matrix, n, bk, bk, bk);

            // Фаза 2: Оновлення перехресних панелей
            for (int b = 0; b < num_blocks; ++b) {
                if (b != bk) {
                    process_block(matrix, n, bk, b, bk);
                    process_block(matrix, n, b, bk, bk);
                }
            }

            // Фаза 3: Повністю незалежне оновлення решти блоків
            for (int bi = 0; bi < num_blocks; ++bi) {
                if (bi == bk) continue;
                for (int bj = 0; bj < num_blocks; ++bj) {
                    if (bj == bk) continue;
                    process_block(matrix, n, bi, bj, bk);
                }
            }
        }
    }

private:
    static void process_block(std::vector<int64_t>& d, int n, int bi, int bj, int bk) {
        const int i_start = bi * BLOCK_SIZE, i_end = std::min(i_start + BLOCK_SIZE, n);
        const int j_start = bj * BLOCK_SIZE, j_end = std::min(j_start + BLOCK_SIZE, n);
        const int k_start = bk * BLOCK_SIZE, k_end = std::min(k_start + BLOCK_SIZE, n);

        for (int k = k_start; k < k_end; ++k) {
            for (int i = i_start; i < i_end; ++i) {
                const int64_t dik = d[static_cast<size_t>(i) * n + k];
                if (dik >= INF_VAL) continue;

                for (int j = j_start; j < j_end; ++j) {
                    const int64_t alt = dik + d[static_cast<size_t>(k) * n + j];
                    size_t ij = static_cast<size_t>(i) * n + j;
                    if (alt < d[ij]) {
                        d[ij] = alt;
                    }
                }
            }
        }
    }
};
