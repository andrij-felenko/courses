#include <stdint.h>
#include <stdio.h>

typedef __uint128_t word72;         /* 72-бітове кодове слово: біт i = позиція i */

enum { N = 72, HAM = 71 };          /* N — уся ширина; 1..HAM — код Геммінга */

/* Позиція контрольна ⟺ це степінь двійки (1,2,4,8,16,32,64). */
static int is_check(unsigned p) {
    return p != 0 && (p & (p - 1)) == 0;   /* рівно один біт у номері */
}
