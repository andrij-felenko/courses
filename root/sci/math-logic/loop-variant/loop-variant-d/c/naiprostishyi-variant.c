#include <assert.h>

int gcd(int a, int b) {
    while (b != 0) {
        int v = b;                 /* варіант — поточне значення b */
        int r = a % b;
        a = b;
        b = r;
        assert(0 <= b && b < v);   /* b невід'ємне й строго впало */
    }
    return a;
}
