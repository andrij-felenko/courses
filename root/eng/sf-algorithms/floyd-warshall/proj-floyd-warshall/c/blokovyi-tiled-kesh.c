#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define BLOCK_SZ 64
#define INF_VAL  (1LL << 60)

static inline int64_t min64(int64_t a, int64_t b) {
    return (a < b) ? a : b;
}

void fw_kernel_block(int64_t *d, int n, int bi, int bj, int bk) {
    int i_start = bi * BLOCK_SZ, i_end = min64(i_start + BLOCK_SZ, n);
    int j_start = bj * BLOCK_SZ, j_end = min64(j_start + BLOCK_SZ, n);
    int k_start = bk * BLOCK_SZ, k_end = min64(k_start + BLOCK_SZ, n);
    
    for (int k = k_start; k < k_end; ++k) {
        for (int i = i_start; i < i_end; ++i) {
            int64_t dik = d[i * n + k];
            if (dik >= INF_VAL) continue;
            
            for (int j = j_start; j < j_end; ++j) {
                int64_t alt = dik + d[k * n + j];
                if (alt < d[i * n + j]) {
                    d[i * n + j] = alt;
                }
            }
        }
    }
}

void tiled_floyd_warshall(int64_t *d, int n) {
    int num_blocks = (n + BLOCK_SZ - 1) / BLOCK_SZ;
    
    for (int bk = 0; bk < num_blocks; ++bk) {
        // Фаза 1: Діагональний блок
        fw_kernel_block(d, n, bk, bk, bk);
        
        // Фаза 2: Панелі хрестовини (горизонтальна та вертикальна)
        for (int b = 0; b < num_blocks; ++b) {
            if (b != bk) {
                fw_kernel_block(d, n, bk, b, bk); // горизонталь
                fw_kernel_block(d, n, b, bk, bk); // вертикаль
            }
        }
        
        // Фаза 3: Усі інші незалежні блоки (можуть обчислюватися паралельно)
        for (int bi = 0; bi < num_blocks; ++bi) {
            if (bi == bk) continue;
            for (int bj = 0; bj < num_blocks; ++bj) {
                if (bj == bk) continue;
                fw_kernel_block(d, n, bi, bj, bk);
            }
        }
    }
}
