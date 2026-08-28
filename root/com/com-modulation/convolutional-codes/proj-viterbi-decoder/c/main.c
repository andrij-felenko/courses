#include <limits.h>

// Наступний стан і пара виходів (v1<<1)|v2 для коду (7,5), K=3.
static const int NXT[4][2] = {{0,2},{0,2},{1,3},{1,3}};
static const int OUT[4][2] = {{0b00,0b11},{0b11,0b00},{0b10,0b01},{0b01,0b10}};

// Один такт add-compare-select. pm — метрики зараз, npm — нові;
// back[s′] = (попередник<<1)|вхід. r0,r1 — прийнята пара (0/1).
void acs_step(const int pm[4], int npm[4], int back[4], int r0, int r1) {
    for (int ns = 0; ns < 4; ns++) npm[ns] = INT_MAX;
    for (int s = 0; s < 4; s++) {
        if (pm[s] == INT_MAX) continue;
        for (int u = 0; u < 2; u++) {
            int o    = OUT[s][u];
            int bm   = ((o >> 1) ^ r0) + ((o & 1) ^ r1);   // відстань Геммінга
            int cand = pm[s] + bm;                         // ADD
            int ns   = NXT[s][u];
            if (cand < npm[ns]) {                          // COMPARE + SELECT
                npm[ns]  = cand;
                back[ns] = (s << 1) | u;
            }
        }
    }
}
