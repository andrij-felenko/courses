/* Розбір аргументів мовою C за допомогою POSIX getopt_long */
#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>

int main(int argc, char *argv[]) {
    int opt;
    const char *output = NULL;
    int verbose = 0;

    static struct option long_options[] = {
        {"help",    no_argument,       NULL, 'h'},
        {"verbose", no_argument,       NULL, 'v'},
        {"output",  required_argument, NULL, 'o'},
        {NULL,      0,                 NULL, 0}
    };

    while ((opt = getopt_long(argc, argv, ":hvo:", long_options, NULL)) != -1) {
        switch (opt) {
        case 'h':
            printf("Використання: %s [-v] [-o FILE] [OPERANDS...]\n", argv[0]);
            return 0;
        case 'v':
            verbose = 1;
            break;
        case 'o':
            output = optarg;
            break;
        case ':':
            fprintf(stderr, "%s: опція '-%c' вимагає значення\n", argv[0], optopt);
            return 1;
        case '?':
            fprintf(stderr, "%s: невідома опція\n", argv[0]);
            return 1;
        default:
            return 1;
        }
    }

    /* Обробка залишкових операндів */
    for (int i = optind; i < argc; ++i) {
        printf("Позиційний операнд: %s\n", argv[i]);
    }
    return 0;
}
