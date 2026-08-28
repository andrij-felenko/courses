#include <stdio.h>

#define MAKE_FN_NAME(prefix, name) prefix##_##name

void api_v1_init(void) {
    printf("Ініціалізація API v1\n");
}

int main(void) {
    void (*init_ptr)(void) = MAKE_FN_NAME(api_v1, init);
    init_ptr();
    return 0;
}
