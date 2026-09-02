/* phases.c — увесь конвеєр за один прогін: рядок → argv[].
 *
 * Фаза 1 живе в braces.c, фази 2, 3 і 6 — у word.c, фаза 4 — у field.c,
 * фаза 5 лишилася тут, бо це кілька рядків навколо glob(3). Підстановки
 * команд і арифметики свідомо немає: перше запускає процеси, друге це
 * окремий обчислювач виразів. Те й те показує приклад на wordexp(3).
 *
 * Збірка: cc -Wall -Wextra -o phases phases.c braces.c word.c field.c \
 *             quoting.c strvec.c
 * Запуск:  ./phases '$HOME/*.txt'   або ./phases (вбудований набір)
 */
#include "braces.h"
#include "field.h"
#include "quoting.h"
#include "strvec.h"
#include "word.h"

#include <glob.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Друкує слово в кутових лапках, роблячи видимими службові символи. */
static void print_word(size_t index, const char *text)
{
    printf("  argv[%zu] = «", index);
    for (const unsigned char *p = (const unsigned char *)text; *p != '\0'; ++p) {
        switch (*p) {
        case '\n': fputs("\\n", stdout); break;
        case '\t': fputs("\\t", stdout); break;
        default:   putchar(*p);          break;
        }
    }
    puts("»");
}

/* Фаза 5. Слово без живих метасимволів іде далі як є — жодного звертання
   до файлової системи для нього не буде. */
static int glob_step(const word *w, strvec *out)
{
    if (!word_has_active(w, "*?[")) {
        return strvec_push_n(out, word_text(w), w->len);
    }

    char *pattern = word_glob_pattern(w);
    if (pattern == NULL) {
        return -1;
    }

    glob_t found;
    memset(&found, 0, sizeof found);

    int status = 0;
    if (glob(pattern, 0, NULL, &found) == 0) {
        for (size_t i = 0; status == 0 && i < found.gl_pathc; ++i) {
            status = strvec_push(out, found.gl_pathv[i]);
        }
    } else {
        /* POSIX: маска без збігів лишається в argv[] сама собою. Саме це
           поводження міняють shopt -s nullglob і failglob. */
        status = strvec_push_n(out, word_text(w), w->len);
    }

    globfree(&found);
    free(pattern);
    return status;
}

static int run(const char *line)
{
    printf("рядок: %s\n", line);

    strvec raw;
    strvec braced;
    strvec final;
    strvec_init(&raw);
    strvec_init(&braced);
    strvec_init(&final);

    int failed = 0;
    int oom = (quoting_split_words(line, &raw) != 0);

    for (size_t i = 0; !oom && i < raw.count; ++i) {
        const int rc = braces_expand(raw.item[i], &braced);
        if (rc == -1) {
            oom = 1;
        } else if (rc != 0) {
            printf("  «%s»: %s\n", raw.item[i], braces_strerror(rc));
            failed = 1;
        }
    }
    printf("  слів після лексики: %zu, після дужок: %zu\n", raw.count, braced.count);

    for (size_t i = 0; !oom && i < braced.count; ++i) {
        word w;
        char err[192];

        const int rc = word_expand(braced.item[i], &w, err, sizeof err);
        if (rc == -1) {
            oom = 1;
            break;
        }
        if (rc == -2) {
            printf("  «%s» відхилено: %s\n", braced.item[i], err);
            failed = 1;
            continue;   /* word_expand уже прибрав за собою */
        }

        wordlist fields;
        wordlist_init(&fields);
        if (field_split(&w, getenv("IFS"), &fields) != 0) {
            oom = 1;
        }
        for (size_t f = 0; !oom && f < fields.count; ++f) {
            if (glob_step(&fields.item[f], &final) != 0) {
                oom = 1;
            }
        }
        wordlist_free(&fields);
        word_free(&w);
    }

    if (oom) {
        fputs("  бракує пам'яті\n", stderr);
        failed = 1;
    } else {
        if (final.count == 0) {
            puts("  (жодного слова — усе розгорнулося в порожнечу)");
        }
        for (size_t i = 0; i < final.count; ++i) {
            print_word(i, final.item[i]);
        }
        printf("  усього в argv[]: %zu\n", final.count);
    }
    putchar('\n');

    strvec_free(&raw);
    strvec_free(&braced);
    strvec_free(&final);
    return failed;
}

int main(int argc, char **argv)
{
    /* Значення з подвійними пробілами всередині — щоб фаза 4 мала що ділити. */
    setenv("REPORT", "zvit  za  traven", 1);
    unsetenv("MISSING");

    static const char *const demo[] = {
        "file_{A,B}.txt",              /* фаза 1: список */
        "{src,test}/{main,util}.c",    /* добуток двох списків */
        "{01..05}",                    /* діапазон із шириною поля */
        "{a..e}",                      /* символьний діапазон */
        "{single} {a{b,c}}",           /* без коми дужки лишаються текстом */
        "'{A,B}'",                     /* лапки скасовують фазу 1 */
        "~/.bashrc",                   /* фаза 2 */
        "$HOME/*.txt",                 /* фази 3 і 5 разом */
        "\"$REPORT\"",                 /* у лапках поділу немає */
        "$REPORT",                     /* а тут фаза 4 дає три слова */
        "${MISSING:-zapasne znachennia}",
        "${REPORT%% *}",               /* обрізання маскою з кінця */
        "${#HOME}",                    /* довжина значення */
        "\"\" tail",                   /* порожні лапки — теж аргумент */
        "$MISSING kinets",             /* незадана змінна зникає зі слова */
        "$(date)",                     /* відмова: підстановки команд немає */
        "'nezakryta lapka",            /* відмова: синтаксис */
    };

    int failures = 0;

    if (argc > 1) {
        for (int i = 1; i < argc; ++i) {
            failures += run(argv[i]);
        }
    } else {
        for (size_t i = 0; i < sizeof demo / sizeof demo[0]; ++i) {
            failures += run(demo[i]);
        }
    }

    /* У вбудованому наборі дві відмови очікувані — статус це показує. */
    return failures > 0 ? 1 : 0;
}
