#include <stdio.h>
#include <stdlib.h>

static void __attribute__((constructor)) init_stdbuf(void) {
    const char *out_mode = getenv("_STDBUF_O");
    if (out_mode) {
        if (out_mode[0] == '0') {
            setvbuf(stdout, NULL, _IONBF, 0);
        } else if (out_mode[0] == 'L') {
            setvbuf(stdout, NULL, _IOLBF, 0);
        } else {
            size_t sz = strtoul(out_mode, NULL, 10);
            if (sz > 0) setvbuf(stdout, NULL, _IOFBF, sz);
        }
    }
}
