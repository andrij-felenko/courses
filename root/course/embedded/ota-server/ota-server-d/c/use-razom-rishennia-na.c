#include <stdio.h>
#include <string.h>
#include <stdbool.h>

// Розкласти рядок "2.4.1" на три числа.
typedef struct { int major, minor, patch; } version_t;

static version_t parse_version(const char *s) {
    version_t v = {0, 0, 0};
    sscanf(s, "%d.%d.%d", &v.major, &v.minor, &v.patch);
    return v;
}

// > 0  якщо a новіша за b;  0 — рівні;  < 0 — a старіша.
// Саме ПОЛЯМИ, а не рядком: "2.10.0" новіша за "2.9.0", хоч текстово менша.
static int version_cmp(version_t a, version_t b) {
    if (a.major != b.major) return a.major - b.major;
    if (a.minor != b.minor) return a.minor - b.minor;
    return a.patch - b.patch;
}
