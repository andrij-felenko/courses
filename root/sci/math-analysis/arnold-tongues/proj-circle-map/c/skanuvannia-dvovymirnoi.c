#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

void render_ascii_arnold_tongues(int grid_w, int grid_h, size_t steps) {
    const double two_pi = 2.0 * M_PI;

    for (int y = grid_h - 1; y >= 0; --y) {
        double k = 1.2 * ((double)y / (double)(grid_h - 1));
        printf("%4.1f |", k);

        for (int x = 0; x < grid_w; ++x) {
            double omega = (double)x / (double)(grid_w - 1);
            double phase = 0.1;

            /* Ітерації відображення */
            for (size_t i = 0; i < steps; ++i) {
                phase = phase + omega - (k / two_pi) * sin(two_pi * phase);
            }

            double start_p = phase;
            size_t m_steps = steps;
            for (size_t i = 0; i < m_steps; ++i) {
                phase = phase + omega - (k / two_pi) * sin(two_pi * phase);
            }

            double w = (phase - start_p) / (double)m_steps;
            w = w - floor(w);

            /* Символьне позначення резонансів */
            char symbol = '.';
            if (fabs(w - 0.0) < 0.02 || fabs(w - 1.0) < 0.02) symbol = '0';
            else if (fabs(w - 0.5) < 0.02) symbol = 'H'; // 1/2
            else if (fabs(w - 1.0/3.0) < 0.015 || fabs(w - 2.0/3.0) < 0.015) symbol = '3';
            else if (fabs(w - 1.0/4.0) < 0.01 || fabs(w - 3.0/4.0) < 0.01) symbol = '4';
            else if (fabs(w - 1.0/5.0) < 0.008 || fabs(w - 2.0/5.0) < 0.008 ||
                     fabs(w - 3.0/5.0) < 0.008 || fabs(w - 4.0/5.0) < 0.008) symbol = '5';

            putchar(symbol);
        }
        putchar('\n');
    }

    printf("     +");
    for (int x = 0; x < grid_w; ++x) putchar('-');
    printf("\n      0.0");
    for (int x = 0; x < grid_w - 8; ++x) putchar(' ');
    printf("1.0 (Omega)\n");
}

int main(void) {
    printf("=== Двовимірна карта язиків Арнольда (ASCII) ===\n");
    render_ascii_arnold_tongues(60, 20, 2000);
    return 0;
}
