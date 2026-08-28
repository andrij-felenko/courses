#include <stdio.h>

typedef struct { float v_node, i, p1, p2; } Divider;

/* Vin — живлення; r1 — верхнє плече, r2 — нижнє (на землю). */
static Divider solve_divider(float vin, float r1, float r2) {
    Divider d;
    d.i      = vin / (r1 + r2);   /* спільний струм гілки  */
    d.v_node = vin * r2 / (r1 + r2); /* напруга у вузлі = спад на R2 */
    d.p1     = d.i * d.i * r1;     /* P = I²·R на кожному плечі */
    d.p2     = d.i * d.i * r2;
    return d;
}

int main(void) {
    Divider d = solve_divider(12.0f, 100.0f, 200.0f);
    printf("V(вузол) = %.2f В\n", d.v_node);  /* 8.00 В  */
    printf("I        = %.1f мА\n", d.i * 1e3f); /* 40.0 мА */
    printf("P(R1)    = %.3f Вт\n", d.p1);      /* 0.160 Вт */
    printf("P(R2)    = %.3f Вт\n", d.p2);      /* 0.320 Вт */
    return 0;
}
