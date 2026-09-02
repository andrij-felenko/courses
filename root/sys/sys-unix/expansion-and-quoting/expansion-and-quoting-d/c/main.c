/* main.c — показує, на які саме елементи argv[] розпадається рядок
 * після розгортання. Без аргументів проганяє вбудований набір прикладів,
 * з аргументами — розгортає кожен переданий рядок.
 *
 * Збірка: cc -Wall -Wextra -o expand main.c expand.c
 */
#include "expand.h"

#include <stdio.h>

/* Друкує слово в кутових лапках і робить видимими службові символи:
   інакше межі аргументів на терміналі не розгледіти. */
static void print_word(size_t index, const char *word)
{
    printf("  argv[%zu] = «", index);
    for (const unsigned char *p = (const unsigned char *)word; *p != '\0'; ++p) {
        switch (*p) {
        case '\n': fputs("\\n", stdout); break;
        case '\t': fputs("\\t", stdout); break;
        default:   putchar(*p);          break;
        }
    }
    puts("»");
}

/* Розгортає один рядок і друкує результат. Повертає 1, якщо не вийшло. */
static int show(const char *line)
{
    expansion ex;

    printf("рядок: %s\n", line);

    int status = expand_line(line, &ex);
    if (status != 0) {
        fprintf(stderr, "  відхилено (%d): %s\n\n", status, expand_strerror(status));
        return 1;
    }

    if (ex.count == 0) {
        puts("  (жодного слова — усе розгорнулося в порожнечу)");
    }
    for (size_t i = 0; i < ex.count; ++i) {
        print_word(i, ex.words[i]);
    }
    printf("  усього слів: %zu\n\n", ex.count);

    expansion_free(&ex);
    return 0;
}

int main(int argc, char **argv)
{
    static const char *const demo[] = {
        "$HOME/*.txt",                /* параметр і глобінг */
        "~/.bashrc",                  /* розгортання тильди */
        "'одне слово з пробілами' і ще два",
        "$((6 * 7)) — відповідь",     /* арифметичне розгортання */
        "\"$HOME\"/*.txt",            /* у лапках глобінгу немає */
        "file_{A,B}.txt",             /* дужки НЕ POSIX: wordexp(3) лишає їх як є */
        "$(date)",                    /* WRDE_NOCMD: підстановку команди відхилено */
        "`date`",                     /* застаріла форма блокується так само */
        "$NO_SUCH_VAR_12345/архів",   /* WRDE_UNDEF: невизначена змінна */
        "звіт | wc",                  /* WRDE_BADCHAR: метасимвол поза лапками */
        "незакрита 'лапка",           /* WRDE_SYNTAX */
    };

    int failures = 0;

    if (argc > 1) {
        for (int i = 1; i < argc; ++i) {
            failures += show(argv[i]);
        }
    } else {
        for (size_t i = 0; i < sizeof demo / sizeof demo[0]; ++i) {
            failures += show(demo[i]);
        }
    }

    /* Ненульовий статус — якщо бодай один рядок не розгорнувся. У наборі
       прикладів відмови очікувані, тож це нормальний результат прогону. */
    return failures > 0 ? 1 : 0;
}
