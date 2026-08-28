#include <stdio.h>

int main(void)
{
    // кабель: пасивна втрата 2 дБ → NF = 2 дБ, підсилення = −2 дБ (від'ємне!)
    float nf_db[]   = {  2.0f,  1.0f,  8.0f,  5.0f };
    float gain_db[] = { -2.0f, 20.0f,  6.0f, 30.0f };

    float total = cascade_nf_db(nf_db, gain_db, 4);
    printf("повний NF = %.2f дБ\n", total);   // ≈ 3.20 дБ
    return 0;
}
