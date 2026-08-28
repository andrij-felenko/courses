#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

int main(void) {
    build_dct_matrix();
    build(BITS_DC, VALS_DC, DC);
    build(BITS_AC, VALS_AC, AC);

    double f[8][8], F[8][8];
    int    Sq[8][8];
    for (int x = 0; x < 8; x++)
        for (int y = 0; y < 8; y++)
            f[x][y] = pix[x][y] - 128;      /* 0. зсув рівня */
    fdct(f, F);                             /* 1. пряме DCT   */
    quantize(F, Sq);                        /* 2. квантування */

    printf("DC F[0][0] = %.3f  ->  квант %d\n", F[0][0], Sq[0][0]);

    Bits b = { malloc(64), 0, 0, 0, 0 };
    encode_block(&b, Sq);                   /* 3-6. зигзаг + ентропія */
    flush(&b);

    printf("Потік блока: %ld біт -> %d байт\n", b.nbits, b.pos);
    for (int i = 0; i < b.pos; i++) printf("%02X ", b.out[i]);
    printf("\n");
    free(b.out);
    return 0;
}
