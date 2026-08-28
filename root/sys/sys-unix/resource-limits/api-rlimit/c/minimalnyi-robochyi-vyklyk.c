#define _GNU_SOURCE
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>

static const struct { int res; const char *name; const char *unit; } LIMITS[] = {
    { RLIMIT_CPU,        "RLIMIT_CPU",        "с"       },
    { RLIMIT_FSIZE,      "RLIMIT_FSIZE",      "Б"       },
    { RLIMIT_DATA,       "RLIMIT_DATA",       "Б"       },
    { RLIMIT_STACK,      "RLIMIT_STACK",      "Б"       },
    { RLIMIT_CORE,       "RLIMIT_CORE",       "Б"       },
    { RLIMIT_RSS,        "RLIMIT_RSS",        "(мертвий)"},
    { RLIMIT_NPROC,      "RLIMIT_NPROC",      "задач"   },
    { RLIMIT_NOFILE,     "RLIMIT_NOFILE",     "шт."     },
    { RLIMIT_MEMLOCK,    "RLIMIT_MEMLOCK",    "Б"       },
    { RLIMIT_AS,         "RLIMIT_AS",         "Б"       },
    { RLIMIT_LOCKS,      "RLIMIT_LOCKS",      "(мертвий)"},
    { RLIMIT_SIGPENDING, "RLIMIT_SIGPENDING", "шт."     },
    { RLIMIT_MSGQUEUE,   "RLIMIT_MSGQUEUE",   "Б"       },
    { RLIMIT_NICE,       "RLIMIT_NICE",       "20−nice" },
    { RLIMIT_RTPRIO,     "RLIMIT_RTPRIO",     "пріор."  },
    { RLIMIT_RTTIME,     "RLIMIT_RTTIME",     "мкс"     },
};

static void fmt(rlim_t v, char *buf, size_t n)
{
    if (v == RLIM_INFINITY)             /* НЕ порівнювати з -1 чи ~0 */
        snprintf(buf, n, "unlimited");
    else
        snprintf(buf, n, "%llu", (unsigned long long)v);
}

int main(int argc, char **argv)
{
    pid_t pid = (argc > 1) ? (pid_t)atoi(argv[1]) : 0;   /* 0 — я сам */

    for (size_t i = 0; i < sizeof LIMITS / sizeof *LIMITS; i++) {
        struct rlimit rl;
        char soft[32], hard[32];

        if (prlimit(pid, LIMITS[i].res, NULL, &rl) != 0) {
            printf("%-18s  %s\n", LIMITS[i].name, strerror(errno));
            continue;
        }
        fmt(rl.rlim_cur, soft, sizeof soft);
        fmt(rl.rlim_max, hard, sizeof hard);
        printf("%-18s %12s %12s  %s\n",
               LIMITS[i].name, soft, hard, LIMITS[i].unit);
    }
    return 0;
}
