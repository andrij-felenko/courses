/* tools/schema_compiler.c */
#include <stdio.h>

int main(int argc, char* argv[]) {
    if (argc < 5) return 1;
    FILE* f = fopen(argv[4], "w");
    if (!f) return 1;
    fprintf(f, "/* Автоматично згенерований C-файл */\n");
    fprintf(f, "const char* get_schema_version(void) { return \"1.0.0\"; }\n");
    fclose(f);
    return 0;
}
