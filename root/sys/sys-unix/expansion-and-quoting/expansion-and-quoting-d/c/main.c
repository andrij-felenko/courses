#include <stdio.h>
#include <stdlib.h>
#include <wordexp.h>

void safe_expand_example(const char *input_pattern) {
    wordexp_t result;
    /* WRDE_NOCMD блокує виклик $(cmd) та `cmd` для безпеки */
    int status = wordexp(input_pattern, &result, WRDE_NOCMD);
    
    if (status == 0) {
        for (size_t i = 0; i < result.we_wordc; i++) {
            printf("argv[%zu] = %s\n", i, result.we_wordv[i]);
        }
        wordfree(&result);
    } else if (status == WRDE_CMDSUB) {
        fprintf(stderr, "Помилка безпеки: спроба виконання команди всередині рядка!\n");
    } else {
        fprintf(stderr, "Помилка розгортання: %d\n", status);
    }
}

int main(void) {
    safe_expand_example("$HOME/documents/*.txt \"проект 2026\"");
    return 0;
}
