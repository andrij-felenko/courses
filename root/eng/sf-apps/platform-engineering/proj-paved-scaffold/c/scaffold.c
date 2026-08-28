// scaffold.c — самообслуговний генератор скелета проєкту.
// Виклик: scaffold <ім'я-пристрою> <профіль>
// Результат: тека з main.c (кличе platform_boot), CMakeLists.txt
// (тягне ПЛАТФОРМУ зафіксованої версії) і конфігом на безпечних дефолтах.
#include <stdio.h>
#include <string.h>

// Версія платформи, яку скелет ПРИБИВАЄ у новий проєкт. Саме фіксація
// тут рятує від тихої розбіжності версій (див. пастки нижче):
// новий проєкт стартує на відомій, перевіреній версії, а не на «якій вийде».
#define SCAFFOLD_PLATFORM_TAG "platform-3.2.1"

static int write_main_c(const char *dir, const char *profile);
static int write_cmake (const char *dir, const char *device);
static int write_readme(const char *dir, const char *device);

int scaffold(const char *device, const char *profile) {
    if (make_project_dir(device) != 0) {
        fprintf(stderr, "scaffold: не вдалося створити теку '%s'\n", device);
        return 1;
    }
    // main.c, який УЖЕ на дорозі: кличе platform_boot з дефолтами.
    if (write_main_c(device, profile) != 0) return 1;
    // CMake, що тягне САМЕ SCAFFOLD_PLATFORM_TAG — не «останню», не «якусь».
    if (write_cmake(device, profile) != 0) return 1;
    write_readme(device, profile);

    printf("Готово: проєкт '%s' на профілі '%s'.\n", device, profile);
    printf("  платформа: %s (зафіксовано)\n", SCAFFOLD_PLATFORM_TAG);
    printf("  наступний крок: cd %s && зберіть як завжди\n", device);
    return 0;
}

// Скелетний main.c: продуктова команда відкриє його вже НА дорозі.
static int write_main_c(const char *dir, const char *profile) {
    FILE *f = open_in_dir(dir, "main.c");
    if (!f) return 1;
    fputs(
        "#include \"platform.h\"\n\n"
        "int main(void) {\n"
        "    platform_cfg_t cfg = PLATFORM_DEFAULT_CFG;\n"
        "    // За потреби зсуньтеся з дороги, змінивши поле cfg тут.\n"
        "    if (platform_boot(&cfg) != PB_OK) { for (;;) { } }\n\n"
        "    app_run();\n"
        "    return 0;\n"
        "}\n", f);
    fclose(f);
    return 0;
}
