#include <stdio.h>

// У мові C перевірка можливостей спирається на монолітний макрос __STDC_VERSION__
#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 201112L
    // Підтримка стандарту C11: статичні перевірки та анонімні структури
    _Static_assert(sizeof(int) >= 4, "Помилка: int занадто малий!");
#elif defined(__STDC_VERSION__) && __STDC_VERSION__ >= 199901L
    // Підтримка стандарту C99: масиви змінної довжини та змішані оголошення
    #warning "Використовується діалект C99 без підтримки _Static_assert"
#else
    // Застарілий стандарт C89 / C90
    #warning "Застарілий стандарт C89"
#endif

int main(void) {
    printf("Компіляція програми на чистому C\n");
    return 0;
}
