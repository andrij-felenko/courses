/* Реалізація CLI-парсера мовою C за допомогою POSIX getopt_long */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <getopt.h>

typedef struct {
    const char *output_file;
    bool force;
} Config;

static void print_usage(const char *progname) {
    printf("Використання: %s [ОПЦІЇ] [ФАЙЛ ...]\n"
           "  -h, --help            Показати довідку\n"
           "  -v, --version         Показати версію\n"
           "  -o, --output FILE     Файл виводу\n"
           "  -f, --force           Примусовий перезапис\n",
           progname);
}

int main(int argc, char *argv[]) {
    Config cfg = { .output_file = NULL, .force = false };

    static struct option long_options[] = {
        {"help",    no_argument,       NULL, 'h'},
        {"version", no_argument,       NULL, 'v'},
        {"output",  required_argument, NULL, 'o'},
        {"force",   no_argument,       NULL, 'f'},
        {NULL,      0,                 NULL, 0}
    };

    int opt;
    while ((opt = getopt_long(argc, argv, "hvo:f", long_options, NULL)) != -1) {
        switch (opt) {
        case 'h':
            print_usage(argv[0]);
            return 0;
        case 'v':
            puts("cli_parser 1.4.0");
            return 0;
        case 'o':
            cfg.output_file = optarg;
            break;
        case 'f':
            cfg.force = true;
            break;
        case '?':
            /* getopt_long уже надрукував повідомлення про помилку в stderr */
            return 2;
        default:
            return 2;
        }
    }

    if (cfg.output_file == NULL) {
        fprintf(stderr, "%s: Помилка: опція -o/--output є обов'язковою\n", argv[0]);
        return 2;
    }

    printf("Вивід: %s, Force: %s\n", cfg.output_file, cfg.force ? "true" : "false");
    printf("Кількість позиційних файлів: %d\n", argc - optind);

    for (int i = optind; i < argc; ++i) {
        printf("  -> Операнд: [%s]\n", argv[i]);
    }

    return 0;
}
