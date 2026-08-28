#include <stdio.h>
#include <string.h>

void run_diff_example(void) {
    const char* text_old = "int main() {\n    printf(\"Hello\\n\");\n    return 0;\n}\n";
    const char* text_new = "int main() {\n    puts(\"Hello, World!\");\n    return 0;\n}\n";

    diff_config_t cfg;
    diff_config_init_default(&cfg);
    cfg.algorithm = DIFF_ALGO_MYERS;
    cfg.context_lines = 2;

    diff_result_t* res = NULL;
    diff_error_t err = diff_compare_buffers(
        text_old, strlen(text_old),
        text_new, strlen(text_new),
        &cfg, &res
    );

    if (err != DIFF_OK) {
        fprintf(stderr, "Помилка порівняння: код %d\n", err);
        return;
    }

    char* formatted = NULL;
    size_t fmt_len = 0;
    if (diff_format_unified(res, "a/main.c", "b/main.c", &formatted, &fmt_len) == DIFF_OK) {
        printf("%s\n", formatted);
        diff_free_string(formatted);
    }

    diff_free_result(res);
}
