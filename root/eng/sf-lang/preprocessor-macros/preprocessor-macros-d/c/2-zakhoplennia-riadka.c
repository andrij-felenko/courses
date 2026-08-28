#include <stdio.h>
#include <stdlib.h>

#define CUSTOM_ASSERT(expr) \
    do { \
        if (!(expr)) { \
            fprintf(stderr, "ASSERT FAILED: (%s) at %s:%d in %s()\n", \
                    #expr, __FILE__, __LINE__, __func__); \
            abort(); \
        } \
    } while (0)

int main(void) {
    int valid_handle = 1;
    CUSTOM_ASSERT(valid_handle != 0);
    printf("Перевірку інваріанта пройдено успішно.\n");
    return 0;
}
