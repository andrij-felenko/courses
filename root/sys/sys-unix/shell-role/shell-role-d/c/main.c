/* Мінімальний запускач конвеєрів: те, що оболонка робить після розбору рядка.
 *
 *   ./pipeline "ls -l" "grep txt" -o out.txt
 *   ./pipeline --spawn "ps aux" "sort -rn"
 *   ./pipeline -b "sleep 5"
 *
 * Розбору лапок тут немає навмисно: ланки конвеєра беруться готовими
 * аргументами, бо предмет — не лексер, а комутація процесів.
 */
#define _GNU_SOURCE
#include "jobs.h"
#include "pipeline.h"

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define STAGES_MAX 8
#define ARGS_MAX  32

static void free_words(char **words)
{
    if (words == NULL) {
        return;
    }
    for (int i = 0; words[i] != NULL; i++) {
        free(words[i]);
    }
    free(words);
}

static char **split_words(const char *text)
{
    char *copy = strdup(text);
    char **words;
    char *save = NULL;
    int n = 0;

    if (copy == NULL) {
        return NULL;
    }
    words = calloc(ARGS_MAX + 1, sizeof *words);
    if (words == NULL) {
        free(copy);
        return NULL;
    }

    for (char *tok = strtok_r(copy, " \t", &save);
         tok != NULL && n < ARGS_MAX;
         tok = strtok_r(NULL, " \t", &save)) {
        words[n] = strdup(tok);
        if (words[n] == NULL) {
            free(copy);
            free_words(words);
            return NULL;
        }
        n++;
    }
    free(copy);
    return words;
}

static void usage(const char *prog)
{
    fprintf(stderr,
            "вжиток: %s [-o файл | -a файл] [--spawn] [-b] \"ланка\" [\"ланка\" ...]\n"
            "  -o файл   stdout останньої ланки у файл (перезапис)\n"
            "  -a файл   те саме, але дописуванням\n"
            "  --spawn   запускати ланки через posix_spawn замість fork+exec\n"
            "  -b        запустити конвеєр у фоні\n",
            prog);
}

int main(int argc, char **argv)
{
    const char *outfile = NULL;
    bool append = false;
    bool background = false;
    bool use_spawn = false;
    char **stages[STAGES_MAX];
    char text[512] = { 0 };
    struct pipeline_spec spec;
    int nstages;
    int code;
    int i = 1;

    for (; i < argc; i++) {
        if (strcmp(argv[i], "-o") == 0 || strcmp(argv[i], "-a") == 0) {
            if (i + 1 >= argc) {
                usage(argv[0]);
                return 2;
            }
            append = (argv[i][1] == 'a');
            outfile = argv[++i];
        } else if (strcmp(argv[i], "--spawn") == 0) {
            use_spawn = true;
        } else if (strcmp(argv[i], "-b") == 0) {
            background = true;
        } else {
            break;
        }
    }

    nstages = argc - i;
    if (nstages <= 0) {
        usage(argv[0]);
        return 2;
    }
    if (nstages > STAGES_MAX) {
        fprintf(stderr, "щонайбільше %d ланок у конвеєрі\n", STAGES_MAX);
        return 2;
    }

    for (int k = 0; k < nstages; k++) {
        stages[k] = split_words(argv[i + k]);
        if (stages[k] == NULL || stages[k][0] == NULL) {
            fprintf(stderr, "порожня або нерозібрана ланка #%d\n", k + 1);
            for (int f = 0; f <= k; f++) {
                free_words(stages[f]);
            }
            return 2;
        }
        if (k > 0) {
            strncat(text, " | ", sizeof text - strlen(text) - 1);
        }
        strncat(text, argv[i + k], sizeof text - strlen(text) - 1);
    }

    jobs_init(STDIN_FILENO);

    memset(&spec, 0, sizeof spec);
    spec.stages = (char *const *const *)stages;
    spec.nstages = nstages;
    spec.outfile = outfile;
    spec.append = append;
    spec.foreground = !background;
    spec.use_spawn = use_spawn;
    spec.text = text;

    code = run_pipeline(&spec);

    if (background) {
        jobs_wait_all();           /* без цього фонове завдання лишилося б сиротою */
    }
    jobs_report();

    for (int k = 0; k < nstages; k++) {
        free_words(stages[k]);
    }
    return code;
}
