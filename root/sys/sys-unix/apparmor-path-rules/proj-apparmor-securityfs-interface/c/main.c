#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

#define ATTR_CURRENT_PATH "/proc/self/attr/apparmor/current"
#define FALLBACK_PATH     "/proc/self/attr/current"
#define BUFFER_SIZE       256

int check_apparmor_status(char *profile_out, size_t out_len, int *is_complain) {
    int fd = open(ATTR_CURRENT_PATH, O_RDONLY);
    if (fd < 0 && errno == ENOENT) {
        fd = open(FALLBACK_PATH, O_RDONLY);
    }
    if (fd < 0) {
        return -errno;
    }

    ssize_t bytes_read = read(fd, profile_out, out_len - 1);
    close(fd);

    if (bytes_read < 0) {
        return -errno;
    }

    profile_out[bytes_read] = '\0';
    if (bytes_read > 0 && profile_out[bytes_read - 1] == '\n') {
        profile_out[bytes_read - 1] = '\0';
    }

    if (strcmp(profile_out, "unconfined") == 0) {
        *is_complain = 0;
        return 0; // Процес поза контролем AppArmor
    }

    char *mode_ptr = strstr(profile_out, " (complain)");
    if (mode_ptr != NULL) {
        *is_complain = 1;
        *mode_ptr = '\0';
    } else {
        mode_ptr = strstr(profile_out, " (enforce)");
        if (mode_ptr != NULL) {
            *is_complain = 0;
            *mode_ptr = '\0';
        } else {
            *is_complain = 0;
        }
    }

    return 1; // Профіль активний
}

int main(void) {
    char profile[BUFFER_SIZE];
    int complain_mode = 0;

    int res = check_apparmor_status(profile, sizeof(profile), &complain_mode);
    if (res < 0) {
        fprintf(stderr, "Помилка доступу до procfs: %s\n", strerror(-res));
        return EXIT_FAILURE;
    }

    if (res == 0) {
        printf("Процес працює в режимі unconfined (поза контролем AppArmor).\n");
    } else {
        printf("Активний профіль AppArmor: '%s' [%s]\n",
               profile, complain_mode ? "COMPLAIN" : "ENFORCE");
    }

    return EXIT_SUCCESS;
}
