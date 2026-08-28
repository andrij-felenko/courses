#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Підрахунок суми другого стовпця у файлі з пробілами мовою C
int main(int argc, char **argv) {
    FILE *fp = (argc > 1) ? fopen(argv[1], "r") : stdin;
    if (!fp) { perror("fopen"); return 1; }

    char *line = NULL;
    size_t len = 0;
    ssize_t read_bytes;
    double total = 0.0;

    while ((read_bytes = getline(&line, &len, fp)) != -1) {
        char *saveptr;
        char *token = strtok_r(line, " \t\n", &saveptr); // $1
        if (token) {
            token = strtok_r(NULL, " \t\n", &saveptr);   // $2
            if (token) {
                total += atof(token);
            }
        }
    }

    free(line);
    if (fp != stdin) fclose(fp);
    printf("Total: %.2f\n", total);
    return 0;
}
