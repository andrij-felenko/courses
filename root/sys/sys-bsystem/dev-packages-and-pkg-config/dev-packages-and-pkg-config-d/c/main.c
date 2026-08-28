/* src/main.c */
#include <png.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    /* Отримання версії бібліотеки через публічне C API */
    const char* header_ver = PNG_LIBPNG_VER_STRING;
    const char* runtime_ver = png_get_header_version(NULL);

    printf("Версія заголовків libpng: %s\n", header_ver);
    printf("Версія бінарного runtime: %s\n", runtime_ver);

    /* Ініціалізація внутрішньої структури читання PNG */
    png_structp png_ptr = png_create_read_struct(
        PNG_LIBPNG_VER_STRING, NULL, NULL, NULL
    );

    if (!png_ptr) {
        fprintf(stderr, "Помилка: не вдалося виділити пам'ять під png_struct\n");
        return EXIT_FAILURE;
    }

    png_infop info_ptr = png_create_info_struct(png_ptr);
    if (!info_ptr) {
        fprintf(stderr, "Помилка: не вдалося виділити пам'ять під png_info\n");
        png_destroy_read_struct(&png_ptr, NULL, NULL);
        return EXIT_FAILURE;
    }

    printf("Структури libpng успішно ініціалізовано.\n");

    /* Звільнення виділених системних ресурсів */
    png_destroy_read_struct(&png_ptr, &info_ptr, NULL);
    return EXIT_SUCCESS;
}
