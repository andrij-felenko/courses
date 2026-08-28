#include <cstdio>

int main() {
    int g_min = 10;          // мінімальне стійке (шумове) підсилення з даташита

    // Хочемо інвертор із сигнальним підсиленням ×2  →  Rf/Rg = 2
    float rf_rg = 2.0f;
    float ng1   = 1.0f + rf_rg;          // низькочастотне шумове = сигнальне+1 = 3

    // 3 < 10  →  без компенсації петля сяде на круте −40, зрив.
    // Піднімаємо ВЧ-шумове конденсаторами до NG2 ≥ Gmin:
    float ng2_target = (float)g_min;     // ціль: 10 (з невеликим запасом — більше)

    // NG2 = 1 + Cs/Cf  →  Cs/Cf = NG2 − 1
    float cs_cf = ng2_target - 1.0f;     // = 9  →  напр. Cf = 2 пФ, Cs = 18 пФ

    std::printf("сигнальне |A| = %.0f (інверсне)\n", rf_rg);          // 2
    std::printf("NG1 (НЧ шумове) = %.0f  -> само по собі < Gmin\n", ng1);  // 3
    std::printf("ціль NG2 (ВЧ шумове) = %.0f >= Gmin\n", ng2_target);  // 10
    std::printf("потрібне Cs/Cf = %.0f\n", cs_cf);                    // 9
    return 0;
}
