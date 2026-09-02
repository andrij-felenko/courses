/* pattern.c — глобінг очима програми. Те саме, що робить рядок
 *     rm !(*.txt|*.md)
 * у Bash з увімкненим extglob: glob(3) добирає імена за маскою,
 * fnmatch(3) відсіює ті, що підпали під маски-винятки.
 *
 * Збірка: cc -Wall -Wextra -o globfilter pattern.c
 * Запуск: ./globfilter '/tmp/demo/*' '*.txt' '*.md'
 */
#include <fnmatch.h>
#include <glob.h>
#include <stdio.h>
#include <string.h>

/* Ім'я без каталогу: маски винятків стосуються імені файла, а не всього шляху. */
static const char *base_name(const char *path)
{
    const char *slash = strrchr(path, '/');
    return (slash != NULL) ? slash + 1 : path;
}

/* 1, якщо ім'я підпадає бодай під один виняток. */
static int is_excluded(const char *path, char **patterns, int count)
{
    const char *name = base_name(path);

    for (int i = 0; i < count; ++i) {
        /* FNM_PERIOD повторює правило POSIX: провідна крапка не збігається
           з '*' і '?'. Саме воно ховає .bashrc від маски * в оболонці. */
        if (fnmatch(patterns[i], name, FNM_PERIOD) == 0) {
            return 1;
        }
    }
    return 0;
}

/* glob(3) кличе це на нечитанному каталозі. Повертаємо 0 — обхід триває далі;
   з прапором GLOB_ERR він натомість спинився б на першій же перепоні. */
static int on_error(const char *path, int errnum)
{
    fprintf(stderr, "  пропущено %s: %s\n", path, strerror(errnum));
    return 0;
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "вжиток: %s <маска> [виняток…]\n", argv[0]);
        return 2;
    }

    /* Обнуляємо структуру заздалегідь: тоді globfree(3) безпечний за будь-якого
       результату glob(3), бо дивиться на gl_pathv. Після невдачі стандарт
       вмісту glob_t не описує, і покладатися на нього не можна. */
    glob_t found;
    memset(&found, 0, sizeof found);

    int status = glob(argv[1], 0, on_error, &found);
    if (status == GLOB_NOMATCH) {
        /* Оболонка за POSIX лишила б у цьому місці саму маску; порожній
           результат — це те, що вмикає shopt -s nullglob. */
        printf("маска «%s» не збіглася з жодним іменем\n", argv[1]);
        globfree(&found);
        return 1;
    }
    if (status != 0) {
        fprintf(stderr, "glob(3) не впорався: %s\n",
                status == GLOB_NOSPACE ? "бракує пам'яті" : "обхід перервано");
        globfree(&found);
        return 1;
    }

    char **excludes = argv + 2;
    int    nexcludes = argc - 2;

    size_t kept = 0;
    size_t dropped = 0;

    /* glob(3) віддає імена вже впорядкованими — так само, як оболонка. */
    puts("лишається:");
    for (size_t i = 0; i < found.gl_pathc; ++i) {
        if (!is_excluded(found.gl_pathv[i], excludes, nexcludes)) {
            printf("  %s\n", found.gl_pathv[i]);
            ++kept;
        }
    }

    puts("відсіяно винятками:");
    for (size_t i = 0; i < found.gl_pathc; ++i) {
        if (is_excluded(found.gl_pathv[i], excludes, nexcludes)) {
            printf("  %s\n", found.gl_pathv[i]);
            ++dropped;
        }
    }

    printf("маска дала %zu імен: %zu лишається, %zu відсіяно\n",
           found.gl_pathc, kept, dropped);

    globfree(&found);
    return 0;
}
