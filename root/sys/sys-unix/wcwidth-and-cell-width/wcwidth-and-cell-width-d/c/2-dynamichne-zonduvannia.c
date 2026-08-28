#include <stdio.h>
#include <termios.h>
#include <unistd.h>

/* Визначення точної фізичної ширини символу шляхом опитування термінала */
int probe_actual_terminal_width(const char *utf8_char) {
    struct termios old_term, raw_term;
    tcgetattr(STDIN_FILENO, &old_term);
    raw_term = old_term;
    raw_term.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &raw_term);

    /* 1. Запитуємо початкову позицію курсора */
    printf("\033[6n");
    fflush(stdout);
    int r1, c1;
    scanf("\033[%d;%dR", &r1, &c1);

    /* 2. Друкуємо досліджуваний символ */
    printf("%s", utf8_char);
    fflush(stdout);

    /* 3. Запитуємо кінцеву позицію курсора */
    printf("\033[6n");
    fflush(stdout);
    int r2, c2;
    scanf("\033[%d;%dR", &r2, &c2);

    /* Відновлюємо налаштування термінала */
    tcsetattr(STDIN_FILENO, TCSANOW, &old_term);

    /* Затираємо надрукований тестовий символ */
    printf("\r\033[K");
    fflush(stdout);

    return c2 - c1;
}
