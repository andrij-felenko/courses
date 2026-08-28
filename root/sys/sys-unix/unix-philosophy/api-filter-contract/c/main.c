#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <locale.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static size_t limit  = 80;   /* поріг довжини рядка */
static int    color  = 0;    /* чи фарбувати результат */
static int    found  = 0;    /* чи спрацювало хоч раз  */
static int    failed = 0;    /* чи була помилка        */

static void run(FILE *in, const char *name)
{
    char   *line = NULL;
    size_t  cap  = 0;
    ssize_t n;

    while ((n = getline(&line, &cap, in)) > 0) {
        if (line[n - 1] == '\n') line[--n] = '\0';
        if ((size_t)n <= limit) continue;
        found = 1;
        if (color) printf("\033[1m%s\033[0m\n", line);
        else       printf("%s\n", line);
    }
    if (ferror(in)) {                       /* збій читання — це код 2 */
        fprintf(stderr, "long: %s: %s\n", name, strerror(errno));
        failed = 1;
    }
    free(line);
}

int main(int argc, char **argv)
{
    const char *STDIN_NAME = "(стандартний ввід)";
    int i = 1;

    setlocale(LC_ALL, "");                  /* поважати локаль користувача */
    signal(SIGPIPE, SIG_DFL);               /* не покладатися на успадковану */
    const char *nc = getenv("NO_COLOR");     /* «присутня й непорожня» — саме так */
    color = isatty(1) && !(nc && *nc);

    for (; i < argc; i++) {                 /* ключі — до першого операнда */
        if (strcmp(argv[i], "--") == 0) { i++; break; }
        if (argv[i][0] != '-' || argv[i][1] == '\0') break;   /* «-» — операнд */
        if (argv[i][1] == 'n' && argv[i][2])
            limit = strtoul(argv[i] + 2, NULL, 10);
        else {
            fprintf(stderr, "вжиток: long [-nЧИСЛО] [--] [файл...]\n");
            return 2;                       /* 2 — помилка вжитку */
        }
    }

    if (i == argc)                          /* операндів немає → stdin */
        run(stdin, STDIN_NAME);

    for (; i < argc; i++) {
        if (strcmp(argv[i], "-") == 0) { run(stdin, STDIN_NAME); continue; }
        FILE *f = fopen(argv[i], "r");
        if (!f) {
            fprintf(stderr, "long: %s: %s\n", argv[i], strerror(errno));
            failed = 1;                     /* один поганий файл ≠ кінець роботи */
            continue;
        }
        run(f, argv[i]);
        fclose(f);
    }

    if (fclose(stdout) != 0 && errno != EPIPE) {   /* тут спливає ENOSPC */
        fprintf(stderr, "long: не вдалося дописати вивід: %s\n", strerror(errno));
        failed = 1;
    }
    return failed ? 2 : (found ? 0 : 1);    /* шкала grep */
}
