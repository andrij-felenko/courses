#define _DEFAULT_SOURCE
#define _BSD_SOURCE
#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <termios.h>
#include <sys/ioctl.h>
#include <signal.h>
#include <errno.h>

enum EditorKey {
    ARROW_LEFT = 1000,
    ARROW_RIGHT,
    ARROW_UP,
    ARROW_DOWN,
    DEL_KEY,
    HOME_KEY,
    END_KEY,
    PAGE_UP,
    PAGE_DOWN
};

struct TermConfig {
    int cx, cy;
    int screen_rows;
    int screen_cols;
    struct termios orig_termios;
};

static struct TermConfig E;

static void disable_raw_mode(void) {
    tcsetattr(STDIN_FILENO, TCSAFLUSH, &E.orig_termios);
}

static void enable_raw_mode(void) {
    if (tcgetattr(STDIN_FILENO, &E.orig_termios) == -1) {
        perror("tcgetattr");
        exit(EXIT_FAILURE);
    }
    atexit(disable_raw_mode);

    struct termios raw = E.orig_termios;
    // Вхідні прапорці: вимкнення XON/XOFF (IXON), перетворення CR->NL (ICRNL), перевірки парності
    raw.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
    // Вихідні прапорці: вимкнення автоматичного перетворення рядків (\n -> \r\n)
    raw.c_oflag &= ~(OPOST);
    // Прапорці керування: 8 біт на символ
    raw.c_cflag |= (CS8);
    // Локальні прапорці: вимкнення відлуння (ECHO), канонічного режиму (ICANON), сигналів (ISIG), розширень (IEXTEN)
    raw.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
    // Контрольні символи: читати негайно або по таймауту 100 мс (1/10 секунди)
    raw.c_cc[VMIN] = 0;
    raw.c_cc[VTIME] = 1;

    if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) == -1) {
        perror("tcsetattr");
        exit(EXIT_FAILURE);
    }
}

static int editor_read_key(void) {
    int nread;
    char c;
    while ((nread = read(STDIN_FILENO, &c, 1)) != 1) {
        if (nread == -1 && errno != EAGAIN && errno != EINTR) {
            perror("read");
            exit(EXIT_FAILURE);
        }
    }

    if (c == '\x1b') {
        char seq[3];
        if (read(STDIN_FILENO, &seq[0], 1) != 1) return '\x1b';
        if (read(STDIN_FILENO, &seq[1], 1) != 1) return '\x1b';

        if (seq[0] == '[') {
            if (seq[1] >= '0' && seq[1] <= '9') {
                if (read(STDIN_FILENO, &seq[2], 1) != 1) return '\x1b';
                if (seq[2] == '~') {
                    switch (seq[1]) {
                        case '1': return HOME_KEY;
                        case '3': return DEL_KEY;
                        case '4': return END_KEY;
                        case '5': return PAGE_UP;
                        case '6': return PAGE_DOWN;
                        case '7': return HOME_KEY;
                        case '8': return END_KEY;
                    }
                }
            } else {
                switch (seq[1]) {
                    case 'A': return ARROW_UP;
                    case 'B': return ARROW_DOWN;
                    case 'C': return ARROW_RIGHT;
                    case 'D': return ARROW_LEFT;
                    case 'H': return HOME_KEY;
                    case 'F': return END_KEY;
                }
            }
        } else if (seq[0] == 'O') {
            switch (seq[1]) {
                case 'H': return HOME_KEY;
                case 'F': return END_KEY;
            }
        }
        return '\x1b';
    }
    return c;
}

static int get_window_size(int *rows, int *cols) {
    struct winsize ws;
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) == -1 || ws.ws_col == 0) {
        return -1;
    }
    *cols = ws.ws_col;
    *rows = ws.ws_row;
    return 0;
}

// Динамічний акумулюючий буфер для рендерингу
struct ABuffer {
    char *b;
    int len;
};

#define ABUF_INIT { NULL, 0 }

static void ab_append(struct ABuffer *ab, const char *s, int len) {
    char *new_buf = realloc(ab->b, ab->len + len);
    if (!new_buf) return;
    memcpy(&new_buf[ab->len], s, len);
    ab->b = new_buf;
    ab->len += len;
}

static void ab_free(struct ABuffer *ab) {
    free(ab->b);
}

static void editor_draw_rows(struct ABuffer *ab) {
    for (int y = 0; y < E.screen_rows; y++) {
        if (y == E.screen_rows / 3) {
            char welcome[80];
            int welcomelen = snprintf(welcome, sizeof(welcome),
                "Minimal Terminal Editor -- v0.1");
            if (welcomelen > E.screen_cols) welcomelen = E.screen_cols;
            int padding = (E.screen_cols - welcomelen) / 2;
            if (padding) {
                ab_append(ab, "~", 1);
                padding--;
            }
            while (padding-- > 0) ab_append(ab, " ", 1);
            ab_append(ab, welcome, welcomelen);
        } else {
            ab_append(ab, "~", 1);
        }

        // Очищення рядка праворуч від курсора
        ab_append(ab, "\x1b[K", 3);
        if (y < E.screen_rows - 1) {
            ab_append(ab, "\r\n", 2);
        }
    }
}

static void editor_refresh_screen(void) {
    struct ABuffer ab = ABUF_INIT;

    // Приховати курсор перед оновленням
    ab_append(&ab, "\x1b[?25l", 6);
    // Перемістити курсор у лівий верхній кут (1, 1)
    ab_append(&ab, "\x1b[H", 3);

    editor_draw_rows(&ab);

    // Встановити курсор у позицію редактора
    char buf[32];
    snprintf(buf, sizeof(buf), "\x1b[%d;%dH", E.cy + 1, E.cx + 1);
    ab_append(&ab, buf, strlen(buf));

    // Показати курсор
    ab_append(&ab, "\x1b[?25h", 6);

    write(STDOUT_FILENO, ab.b, ab.len);
    ab_free(&ab);
}

static void editor_move_cursor(int key) {
    switch (key) {
        case ARROW_LEFT:
            if (E.cx > 0) E.cx--;
            break;
        case ARROW_RIGHT:
            if (E.cx < E.screen_cols - 1) E.cx++;
            break;
        case ARROW_UP:
            if (E.cy > 0) E.cy--;
            break;
        case ARROW_DOWN:
            if (E.cy < E.screen_rows - 1) E.cy++;
            break;
    }
}

static void editor_process_keypress(void) {
    int c = editor_read_key();
    switch (c) {
        case ('q' & 0x1f): // Ctrl+Q вихід
            write(STDOUT_FILENO, "\x1b[2J\x1b[H", 7);
            exit(EXIT_SUCCESS);
            break;
        case ARROW_UP:
        case ARROW_DOWN:
        case ARROW_LEFT:
        case ARROW_RIGHT:
            editor_move_cursor(c);
            break;
    }
}

int main(void) {
    enable_raw_mode();
    if (get_window_size(&E.screen_rows, &E.screen_cols) == -1) {
        perror("get_window_size");
        exit(EXIT_FAILURE);
    }
    E.cx = 0;
    E.cy = 0;

    // Вхід в альтернативний екран
    write(STDOUT_FILENO, "\x1b[?1049h", 8);

    while (1) {
        editor_refresh_screen();
        editor_process_keypress();
    }
    return 0;
}
