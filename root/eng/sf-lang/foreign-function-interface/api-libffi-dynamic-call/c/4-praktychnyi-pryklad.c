#include <stdio.h>
#include <ffi.h>

int main(void) {
    ffi_cif cif;
    ffi_type *args[1];
    void *values[1];

    /* Опис аргументів: один покажчик (const char*) */
    args[0] = &ffi_type_pointer;

    /* Підготовка дескриптора виклику */
    if (ffi_prep_cif(&cif, FFI_DEFAULT_ABI, 1, &ffi_type_sint32, args) != FFI_OK) {
        fprintf(stderr, "Помилка ініціалізації CIF\n");
        return 1;
    }

    const char *message = "Привіт зі світу libffi!";
    values[0] = &message; /* Покажчик на комірку з аргументом */

    int result = 0;

    /* Динамічний виклик puts */
    ffi_call(&cif, FFI_FN(puts), &result, values);

    printf("puts повернув код: %d\n", result);
    return 0;
}
