#include <cstdio>

int main() {
    int  g_min   = 5;            // «minimum stable gain» з даташита (шумове!)
    // Неінвертуюче ввімкнення: сигнальне = шумове
    int  ni_min  = g_min;        // → не нижче ×5
    // Інвертуюче ввімкнення: шумове = 1 + Rf/Rg = Gmin,
    //   тож |сигнальне| = Rf/Rg = Gmin − 1
    int  inv_min = g_min - 1;    // → можна аж до ×4 за модулем

    std::printf("неінвертуюче: |A| >= %d\n", ni_min);   // 5
    std::printf("інвертуюче:   |A| >= %d\n", inv_min);   // 4
    return 0;
}
