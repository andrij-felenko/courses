#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]) {
    if (strcmp(argv[0], "[") == 0 || strcmp(argv[0], "/bin/[") == 0) {
        if (argc < 2 || strcmp(argv[argc - 1], "]") != 0) {
            fprintf(stderr, "[: missing ]\n");
            exit(2);
        }
        /* Відкидаємо закриваючу дужку перед аналізом виразу */
        argc--;
        argv[argc] = NULL;
    }
    /* Подальший розбір предикатів test */
    return 0;
}
