#include <stdlib.h>   // для abs()

void block_match_naive(void)
{
    // межі: не виходимо за край ні вікном, ні зсувом диспаритету
    for (int y = HALF; y < H - HALF; ++y) {
        for (int x = HALF + DMAX; x < W - HALF; ++x) {

            uint32_t best_cost = UINT32_MAX;
            int      best_d    = 0;

            // перебір кандидатів-диспаритетів
            for (int d = DMIN; d <= DMAX; ++d) {
                uint32_t cost = 0;

                // SAD по вікну (2·HALF+1)×(2·HALF+1)
                for (int j = -HALF; j <= HALF; ++j) {
                    for (int i = -HALF; i <= HALF; ++i) {
                        int lv = L[y + j][x + i];
                        int rv = R[y + j][x - d + i];
                        cost += abs(lv - rv);
                    }
                }

                if (cost < best_cost) {
                    best_cost = cost;
                    best_d    = d;
                }
            }
            disp[y][x] = (uint8_t)best_d;
        }
    }
}
