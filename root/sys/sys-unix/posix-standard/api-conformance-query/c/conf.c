/* conf.c — усі чотири способи спитати систему.
   збірка: cc -std=c17 -D_POSIX_C_SOURCE=200809L -o conf conf.c */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/* 1. Час компіляції: що обіцяли заголовки */
static void compile_time(void) {
#ifdef _POSIX_VERSION
    printf("_POSIX_VERSION  = %ldL\n", (long)_POSIX_VERSION);
#else
    printf("_POSIX_VERSION  не визначено\n");
#endif
#if !defined(_POSIX_SPAWN) || _POSIX_SPAWN == -1
    printf("posix_spawn     : немає\n");
#elif _POSIX_SPAWN == 0
    printf("posix_spawn     : питати на виконанні\n");
#else
    printf("posix_spawn     : є завжди (%ldL)\n", (long)_POSIX_SPAWN);
#endif
}

/* 2. Час виконання: система */
static void ask_sys(int name, const char *label) {
    errno = 0;
    long v = sysconf(name);
    if (v != -1)          printf("%-16s: %ld\n", label, v);
    else if (errno == 0)  printf("%-16s: межі немає\n", label);
    else                  printf("%-16s: %s\n", label, strerror(errno));
}

/* 3. Час виконання: конкретний шлях */
static void ask_path(const char *path, int name, const char *label) {
    errno = 0;
    long v = pathconf(path, name);
    if (v != -1)          printf("%-16s(%s): %ld\n", label, path, v);
    else if (errno == 0)  printf("%-16s(%s): межі немає\n", label, path);
    else                  printf("%-16s(%s): %s\n", label, path, strerror(errno));
}

/* 4. Час виконання: рядкові значення */
static void ask_str(int name, const char *label) {
    errno = 0;
    size_t n = confstr(name, NULL, 0);
    if (n == 0) {
        printf("%-16s: %s\n", label, errno ? "невідома назва" : "значення немає");
        return;
    }
    char *buf = malloc(n);
    if (buf == NULL) { perror("malloc"); return; }
    confstr(name, buf, n);
    printf("%-16s: %s\n", label, buf);
    free(buf);
}

int main(void) {
    compile_time();
    ask_sys(_SC_VERSION,  "_SC_VERSION");
    ask_sys(_SC_PAGESIZE, "_SC_PAGESIZE");
    ask_sys(_SC_OPEN_MAX, "_SC_OPEN_MAX");
    ask_sys(_SC_THREADS,  "_SC_THREADS");
    ask_path("/", _PC_NAME_MAX, "_PC_NAME_MAX");
    ask_path("/", _PC_PIPE_BUF, "_PC_PIPE_BUF");
    ask_str(_CS_PATH, "_CS_PATH");
    return 0;
}
