#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/* Емуляція оператора ${var:-default} */
const char* expand_default(const char *val, const char *def) {
    if (val == NULL || val[0] == '\0') {
        return def;
    }
    return val;
}

/* Емуляція оператора ${path##*/} (basename) через адресну арифметику */
const char* trim_longest_prefix_slash(const char *path) {
    if (path == NULL) return "";
    const char *last_slash = strrchr(path, '/');
    if (last_slash != NULL) {
        return last_slash + 1; /* Повертаємо покажчик на символ після '/' без алокацій */
    }
    return path;
}

/* Емуляція оператора ${path%/*} (dirname) у виділений буфер */
char* trim_shortest_suffix_slash(const char *path) {
    if (path == NULL || path[0] == '\0') {
        return strdup(".");
    }
    const char *last_slash = strrchr(path, '/');
    if (last_slash == NULL) {
        return strdup(".");
    }
    if (last_slash == path) {
        return strdup("/"); /* Кореневий каталог */
    }
    size_t len = (size_t)(last_slash - path);
    char *result = (char*)malloc(len + 1);
    if (!result) return NULL;
    memcpy(result, path, len);
    result[len] = '\0';
    return result;
}

int main(void) {
    const char *env_port = NULL;
    printf("PORT: %s\n", expand_default(env_port, "8080"));

    const char *file_path = "/var/log/nginx/access.log";
    printf("Basename: %s\n", trim_longest_prefix_slash(file_path));

    char *dir = trim_shortest_suffix_slash(file_path);
    if (dir) {
        printf("Dirname: %s\n", dir);
        free(dir);
    }
    return 0;
}
