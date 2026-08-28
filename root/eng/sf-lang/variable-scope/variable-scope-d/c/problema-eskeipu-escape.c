// В чистому C замикання реалізують вручну через пару: покажчик на функцію + void* контекст
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int factor; // Стан, виділений у купі для уникнення dangling pointer
} MultiplierContext;

typedef int (*TransformFn)(void* context, int value);

int multiply_impl(void* context, int value) {
    MultiplierContext* ctx = (MultiplierContext*)context;
    return value * ctx->factor;
}

int main(void) {
    MultiplierContext* ctx = (MultiplierContext*)malloc(sizeof(MultiplierContext));
    if (!ctx) return 1;
    ctx->factor = 5;

    TransformFn fn = multiply_impl;
    printf("Result: %d\n", fn(ctx, 10)); // 50

    free(ctx);
    return 0;
}
