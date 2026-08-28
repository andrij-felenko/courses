/* whence.c — звідки прийшла відповідь про користувача.
 * збірка: cc -O2 -o whence whence.c
 * вжиток: ./whence <повторів> <ім'я> [ім'я ...]           */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <pwd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

enum answer { FOUND, ABSENT, NO_ANSWER };

static long long now_ns(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (long long)t.tv_sec * 1000000000LL + t.tv_nsec;
}

/* один пошук із чесним розрізненням трьох результатів */
static enum answer lookup(const char *name, uid_t *uid, int *err)
{
    long hint = sysconf(_SC_GETPW_R_SIZE_MAX);
    size_t size = (hint > 0) ? (size_t)hint : 1024;
    char *buf = NULL;

    for (;;) {
        char *bigger = realloc(buf, size);
        if (bigger == NULL) { free(buf); *err = ENOMEM; return NO_ANSWER; }
        buf = bigger;

        struct passwd pw;
        struct passwd *res = NULL;
        int rc = getpwnam_r(name, &pw, buf, size, &res);

        if (rc == ERANGE && size < (1u << 20)) {   /* тісний буфер — не відповідь */
            size *= 2;
            continue;
        }

        enum answer out;
        if (rc != 0)          { *err = rc;         out = NO_ANSWER; }
        else if (res == NULL) {                    out = ABSENT;    }
        else                  { *uid = res->pw_uid; out = FOUND;    }

        free(buf);          /* res указує в buf — uid уже скопійовано */
        return out;
    }
}

int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "вжиток: %s <повторів> <ім'я> [ім'я ...]\n", argv[0]);
        return 2;
    }
    int reps = atoi(argv[1]);
    uid_t uid = 0;
    int err = 0;

    /* 1. міряємо сам секундомір */
    long long t0 = now_ns();
    for (int i = 0; i < 1000; i++) (void)now_ns();
    printf("сам замір часу: %lld нс на виклик\n\n", (now_ns() - t0) / 1000);

    /* 2. розігрів на імені, якого напевно нема: перший виклик у процесі ще й
     *    відображає файли кеша в пам'ять, і ця одноразова ціна нам не потрібна
     *    у вимірюваних числах                                                */
    (void)lookup("nemaje-takoho-91731", &uid, &err);

    /* 3. власне вимірювання: кожен виклик окремим рядком, без усереднення */
    for (int a = 2; a < argc; a++) {
        for (int r = 0; r < reps; r++) {
            long long t = now_ns();
            enum answer ans = lookup(argv[a], &uid, &err);
            long long dt = now_ns() - t;

            printf("%-12s %2d  %9.1f мкс  %s", argv[a], r, dt / 1000.0,
                   ans == FOUND ? "знайшов" :
                   ans == ABSENT ? "нема такого" : "не зміг спитати");
            if (ans == FOUND)     printf("  (uid %u)", (unsigned)uid);
            if (ans == NO_ANSWER) printf("  (%s)", strerror(err));
            putchar('\n');
        }
    }
    return 0;
}
