#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    // 1. Перевірка наявності дефіса на початку argv[0]
    int is_login = (argc > 0 && argv[0] != NULL && argv[0][0] == '-');

    // 2. Перевірка підключення стандартного потоку вводу до TTY
    int is_interactive = isatty(STDIN_FILENO);

    printf("Ідентифікація оболонки:\n");
    printf("  argv[0]         = %s\n", (argc > 0 && argv[0]) ? argv[0] : "(null)");
    printf("  Login Shell     = %s\n", is_login ? "ТАК (ініціалізація сеансу)" : "НІ (вторинний процес)");
    printf("  Interactive     = %s\n", is_interactive ? "ТАК (підключено до термінала)" : "НІ (виконання скрипта)");

    return 0;
}
