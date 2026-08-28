/* src/main.c */
#include <png.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    printf("Версія libpng у системі: %s\n", PNG_LIBPNG_VER_STRING);
    png_structp png_ptr = png_create_read_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
    if (!png_ptr) {
        fprintf(stderr, "Не вдалося ініціалізувати структуру png_struct\n");
        return EXIT_FAILURE;
    }
    printf("Структуру libpng успішно створено.\n");
    png_destroy_read_struct(&png_ptr, NULL, NULL);
    return EXIT_SUCCESS;
}
