#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>

int main(void) {
    int32_t x = INT32_MIN;        // −2 147 483 648

    printf("%d\n", -x);           // «хотіли» +2147483648 — його НЕМА в int32
    printf("%d\n", abs(x));       // те саме: abs(INT_MIN) — UB, часто друкує INT_MIN
    return 0;
}
