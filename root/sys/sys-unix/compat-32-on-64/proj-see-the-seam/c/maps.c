/* maps.c — програма друкує власну карту пам'яті */
#include <stdio.h>
#include <stdint.h>

int main(void)
{
    char line[512];
    FILE *f = fopen("/proc/self/maps", "r");
    if (!f) { perror("/proc/self/maps"); return 1; }
    while (fgets(line, sizeof line, f))
        fputs(line, stdout);
    fclose(f);

    int local = 0;
    printf("--\n");
    printf("покажчик, байтів : %zu\n", sizeof(void *));
    printf("локальна змінна  : %p\n", (void *) &local);
    printf("код main         : %p\n", (void *) (uintptr_t) main);
    return 0;
}
