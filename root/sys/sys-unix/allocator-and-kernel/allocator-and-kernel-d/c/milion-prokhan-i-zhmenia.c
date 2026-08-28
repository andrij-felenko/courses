#include <stdlib.h>

int main(void) {
    for (long i = 0; i < 1000000; i++) {
        void *p = malloc(32);
        if (!p) return 1;
        free(p);
    }
    return 0;
}
