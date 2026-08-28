/* Демонстрація суворого POSIX-розбору аргументів без використання пермутацій */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char *argv[])
{
    int opt;
    int verbose_flag = 0;
    char *output_file = NULL;

    /* Рядок специфікації опцій: "v" (без аргументу), "o:" (обов'язковий аргумент) */
    while ((opt = getopt(argc, argv, "vo:")) != -1) {
        switch (opt) {
        case 'v':
            verbose_flag = 1;
            break;
        case 'o':
            output_file = optarg;
            break;
        case '?':
            fprintf(stderr, "Використання: %s [-v] [-o output] file1 [file2 ...]\n", argv[0]);
            return 1;
        default:
            abort();
        }
    }

    printf("Прапорець verbose: %s\n", verbose_flag ? "увімкнено" : "вимкнено");
    printf("Файл виводу: %s\n", output_file ? output_file : "(за замовчуванням)");

    /* Усі елементи, починаючи з optind — позиційні аргументи (файли) */
    printf("Позиційні аргументи (файли):\n");
    for (int index = optind; index < argc; index++) {
        printf("  argv[%d] = %s\n", index, argv[index]);
    }

    return 0;
}
