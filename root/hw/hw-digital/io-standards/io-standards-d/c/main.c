#include <stdio.h>

// напруги в мілівольтах, щоб не морочитися з float
typedef struct { int voh, vol; } driver_t;   // що вихід ГАРАНТУЄ
typedef struct { int vih, vil; } receiver_t;  // що вхід ВИМАГАЄ

int link_ok(driver_t d, receiver_t r, int *margin_hi, int *margin_lo) {
    *margin_hi = d.voh - r.vih;   // запас у стані «1»
    *margin_lo = r.vil - d.vol;   // запас у стані «0»
    return (*margin_hi > 0) && (*margin_lo > 0);
}

int main(void) {
    driver_t   lvcmos18 = { .voh = 1700, .vol = 100 };  // 1.8 В LVCMOS
    receiver_t lvttl33  = { .vih = 2000, .vil = 800 };  // 3.3 В LVTTL-вхід

    int mh, ml;
    if (link_ok(lvcmos18, lvttl33, &mh, &ml))
        printf("OK: запас +%d/%d мВ\n", mh, ml);
    else
        printf("НІ: запас %d/%d мВ — «1» не читається\n", mh, ml);
    return 0;
}
