#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <stdbool.h>

#define BUFFER_CAPACITY (64 * 1024)

typedef struct {
    size_t shift_table[256];
    const char *pattern;
    size_t pattern_len;
} HorspoolMatcher;

static void matcher_init(HorspoolMatcher *m, const char *pattern) {
    m->pattern = pattern;
    m->pattern_len = strlen(pattern);
    const size_t len = m->pattern_len;

    for (size_t i = 0; i < 256; ++i) {
        m->shift_table[i] = len;
    }

    if (len > 0) {
        for (size_t i = 0; i < len - 1; ++i) {
            uint8_t byte = (uint8_t)pattern[i];
            m->shift_table[byte] = len - 1 - i;
        }
    }
}

static bool matcher_find(const HorspoolMatcher *m, const char *text, size_t text_len) {
    const size_t p_len = m->pattern_len;
    if (p_len == 0) return true;
    if (text_len < p_len) return false;

    const char *p = m->pattern;
    size_t i = p_len - 1;

    while (i < text_len) {
        size_t k = 0;
        while (k < p_len && p[p_len - 1 - k] == text[i - k]) {
            k++;
        }
        if (k == p_len) {
            return true;
        }
        uint8_t bad_byte = (uint8_t)text[i];
        i += m->shift_table[bad_byte];
    }
    return false;
}

static int process_stream(int fd, const HorspoolMatcher *matcher) {
    char buffer[BUFFER_CAPACITY + 1];
    size_t carryover = 0;
    bool any_match_found = false;

    while (1) {
        ssize_t bytes_read = read(fd, buffer + carryover, BUFFER_CAPACITY - carryover);
        if (bytes_read < 0) {
            perror("read");
            return 2;
        }
        if (bytes_read == 0 && carryover == 0) {
            break;
        }

        size_t total_in_buffer = carryover + (size_t)bytes_read;
        size_t line_start = 0;

        while (line_start < total_in_buffer) {
            char *newline_ptr = memchr(buffer + line_start, '\n', total_in_buffer - line_start);
            if (!newline_ptr) {
                if (bytes_read == 0) {
                    /* Кінець потоку без завершального \n */
                    size_t line_len = total_in_buffer - line_start;
                    if (matcher_find(matcher, buffer + line_start, line_len)) {
                        write(STDOUT_FILENO, buffer + line_start, line_len);
                        write(STDOUT_FILENO, "\n", 1);
                        any_match_found = true;
                    }
                    line_start = total_in_buffer;
                }
                break;
            }

            size_t line_end = (size_t)(newline_ptr - buffer);
            size_t line_len = line_end - line_start;

            if (matcher_find(matcher, buffer + line_start, line_len)) {
                write(STDOUT_FILENO, buffer + line_start, line_len + 1);
                any_match_found = true;
            }

            line_start = line_end + 1;
        }

        carryover = total_in_buffer - line_start;
        if (carryover > 0) {
            memmove(buffer, buffer + line_start, carryover);
        }

        if (carryover == BUFFER_CAPACITY) {
            /* Рядок довший за буфер — скидаємо та продовжуємо */
            if (matcher_find(matcher, buffer, carryover)) {
                write(STDOUT_FILENO, buffer, carryover);
                write(STDOUT_FILENO, "\n", 1);
                any_match_found = true;
            }
            carryover = 0;
        }

        if (bytes_read == 0) {
            break;
        }
    }

    return any_match_found ? 0 : 1;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        const char msg[] = "Використання: mini_grep <шаблон>\n";
        write(STDERR_FILENO, msg, sizeof(msg) - 1);
        return 2;
    }

    HorspoolMatcher matcher;
    matcher_init(&matcher, argv[1]);

    return process_stream(STDIN_FILENO, &matcher);
}
