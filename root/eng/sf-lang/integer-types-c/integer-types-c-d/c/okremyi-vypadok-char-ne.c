#include <stdio.h>

int main(void) {
    char c = 200;          // на x86: знаковий → −56;  на ARM: беззнаковий → 200
    if (c > 100) {
        printf("більше 100\n");   // ТІЛЬКИ на ARM (200 > 100)
    } else {
        printf("менше 100\n");    // на x86: −56 < 100 — інша відповідь!
    }
    return 0;
}
