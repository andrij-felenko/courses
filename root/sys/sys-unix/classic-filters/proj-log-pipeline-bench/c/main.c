#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

#define BUF_SIZE (64 * 1024)
#define HASH_SIZE 65536

typedef struct Node {
    char ip[48];
    uint32_t count;
    struct Node *next;
} Node;

static Node* table[HASH_SIZE];

static uint32_t hash_str(const char *str, size_t len) {
    uint32_t h = 5381;
    for (size_t i = 0; i < len; ++i)
        h = ((h << 5) + h) + (unsigned char)str[i];
    return h % HASH_SIZE;
}

static void record_ip(const char *ip, size_t len) {
    uint32_t idx = hash_str(ip, len);
    for (Node *curr = table[idx]; curr; curr = curr->next) {
        if (strncmp(curr->ip, ip, len) == 0 && curr->ip[len] == '\0') {
            curr->count++;
            return;
        }
    }
    Node *n = (Node*)malloc(sizeof(Node));
    strncpy(n->ip, ip, len);
    n->ip[len] = '\0';
    n->count = 1;
    n->next = table[idx];
    table[idx] = n;
}

int main(int argc, char **argv) {
    int fd = (argc > 1) ? open(argv[1], O_RDONLY) : STDIN_FILENO;
    if (fd < 0) { perror("open"); return 1; }

    char buf[BUF_SIZE + 1];
    ssize_t n;
    size_t carry = 0;

    while ((n = read(fd, buf + carry, BUF_SIZE - carry)) > 0) {
        size_t total = carry + n;
        buf[total] = '\0';
        char *line_start = buf;
        char *nl;

        while ((nl = memchr(line_start, '\n', buf + total - line_start)) != NULL) {
            *nl = '\0';
            // Парсинг: IP (до першого пробілу) та Статус ($9)
            char *sp1 = strchr(line_start, ' ');
            if (sp1) {
                // Пошук 9-го поля
                char *p = sp1 + 1;
                int field = 2;
                while (field < 9 && p) {
                    p = strchr(p, ' ');
                    if (p) p++;
                    field++;
                }
                if (p && p[0] == '5' && p[1] >= '0' && p[1] <= '9' && p[2] >= '0' && p[2] <= '9') {
                    record_ip(line_start, sp1 - line_start);
                }
            }
            line_start = nl + 1;
        }
        carry = buf + total - line_start;
        memmove(buf, line_start, carry);
    }

    if (fd != STDIN_FILENO) close(fd);
    return 0;
}
