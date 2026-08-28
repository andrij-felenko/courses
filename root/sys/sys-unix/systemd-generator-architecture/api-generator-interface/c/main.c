/* Приклад використання внутрішніх C-функцій systemd generator API */
#include "generator.h"

int main(int argc, char *argv[]) {
    const char *normal_dir, *early_dir, *late_dir;
    int r;

    /* Автоматична перевірка argc та витяг каталогів */
    r = generator_open_output_dirs(argc, argv, &normal_dir, &early_dir, &late_dir);
    if (r < 0)
        return EXIT_FAILURE;

    /* Створення unit-файла у normal_dir з автоматичним закриттям файлу */
    _cleanup_fclose_ FILE *f = NULL;
    r = generator_open_unit_file(normal_dir, NULL, "my-gen.service", &f);
    if (r < 0)
        return EXIT_FAILURE;

    fprintf(f,
        "[Unit]\n"
        "Description=Generated via sd-generator API\n");

    /* Автоматичне створення відносного symlink у каталозі .wants/ */
    r = generator_add_symlink(normal_dir, "multi-user.target", "wants", "my-gen.service");
    if (r < 0)
        return EXIT_FAILURE;

    return EXIT_SUCCESS;
}
