#include <stdlib.h>
#include <stdio.h>

/* Небезпечний підхід: вказівник залишається завислим */
void legacy_unsafe_flow(void) {
    int *data = (int *)malloc(sizeof(int) * 10);
    if (!data) return;

    data[0] = 42;
    free(data);

    /* Небезпека: вказівник не обнулено, можливе помилкове звернення */
    /* data[0] = 100; -- Use-After-Free! */
}

/* Захищений підхід: безпечне вивільнення з обнуленням */
void safe_c_free(void **ptr_ref) {
    if (ptr_ref && *ptr_ref) {
        free(*ptr_ref);
        *ptr_ref = NULL;
    }
}
