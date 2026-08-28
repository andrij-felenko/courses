/* initramfs-keycheck.c — C реалізація для раннього простору користувача */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>

#define EXPECTED_MAGIC "SECUREKEY2026"
#define MAGIC_LEN 13
#define CMDLINE_PATH "/proc/cmdline"

static void log_msg(const char *level, const char *msg) {
    fprintf(stderr, "[keycheck:%s] %s\n", level, msg);
}

int check_token_file(const char *keypath) {
    struct stat st;

    if (stat(keypath, &st) != 0) {
        fprintf(stderr, "[keycheck:ERR] Cannot stat %s: %s\n", keypath, strerror(errno));
        return 2;
    }

    if (!S_ISREG(st.st_mode)) {
        log_msg("ERR", "Target path is not a regular file");
        return 3;
    }

    if (st.st_size < MAGIC_LEN) {
        log_msg("ERR", "Keyfile size is smaller than required header length");
        return 4;
    }

    int fd = open(keypath, O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "[keycheck:ERR] Open failed for %s: %s\n", keypath, strerror(errno));
        return 5;
    }

    char buffer[MAGIC_LEN + 1];
    ssize_t bytes_read = read(fd, buffer, MAGIC_LEN);
    close(fd);

    if (bytes_read != MAGIC_LEN) {
        log_msg("ERR", "Failed to read required header bytes from keyfile");
        return 6;
    }
    buffer[MAGIC_LEN] = '\0';

    if (memcmp(buffer, EXPECTED_MAGIC, MAGIC_LEN) != 0) {
        log_msg("FAIL", "Invalid magic token sequence inside keyfile!");
        return 7;
    }

    printf("[keycheck:OK] SUCCESS: Valid token verified at %s\n", keypath);
    return 0;
}

int main(int argc, char *argv[]) {
    const char *keypath = NULL;

    if (argc >= 2) {
        keypath = argv[1];
    } else {
        /* Якщо аргумент не передано, пробуємо зчитати keycheck.path з /proc/cmdline */
        int fd = open(CMDLINE_PATH, O_RDONLY);
        if (fd >= 0) {
            char cmdline[1024];
            ssize_t n = read(fd, cmdline, sizeof(cmdline) - 1);
            close(fd);
            if (n > 0) {
                cmdline[n] = '\0';
                char *token = strstr(cmdline, "keycheck.path=");
                if (token) {
                    token += 14;
                    char *end = strchr(token, ' ');
                    if (end) *end = '\0';
                    end = strchr(token, '\n');
                    if (end) *end = '\0';
                    keypath = token;
                }
            }
        }
    }

    if (!keypath || strlen(keypath) == 0) {
        log_msg("WARN", "No keypath specified via CLI or keycheck.path in cmdline");
        return 1;
    }

    return check_token_file(keypath);
}
