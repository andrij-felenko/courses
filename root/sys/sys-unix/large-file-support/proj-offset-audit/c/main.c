/* main.c — «застосунок» */
#include "audit.h"
#include <stdio.h>
#include <string.h>
#include <stdint.h>

int main(void)
{
    printf("[main.c] sizeof(off_t)=%zu  sizeof(struct span)=%zu\n",
           sizeof(off_t), sizeof(struct span));

    off_t size = 1000000, back = 4096;
    off_t got = tail_offset(size, back);
    printf("  tail_offset(%jd, %jd) → %jd   (мало бути %jd)\n",
           (intmax_t)size, (intmax_t)back, (intmax_t)got,
           (intmax_t)(size - back));

    struct span s;
    memset(&s, 0, sizeof s);
    fill_span(&s);
    printf("  span: start=%jd  records=%ld  truncated=%d   (мало бути 4096/7/1)\n",
           (intmax_t)s.start, s.records, s.truncated);
    return 0;
}
