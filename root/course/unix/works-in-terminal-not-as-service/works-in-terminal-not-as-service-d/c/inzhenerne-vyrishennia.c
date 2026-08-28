#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <limits.h>
#include <libgen.h>
#include <string.h>

int get_executable_dir(char *out_path, size_t max_len) {
    char exe_path[PATH_MAX];
    ssize_t len = readlink("/proc/self/exe", exe_path, sizeof(exe_path) - 1);
    if (len == -1) {
        return -1;
    }
    exe_path[len] = '\0';

    char *dir = dirname(exe_path);
    if (strlen(dir) >= max_len) {
        return -1;
    }
    strncpy(out_path, dir, max_len - 1);
    out_path[max_len - 1] = '\0';
    return 0;
}
