#include <stdint.h>
#include <stdio.h>

#define BIT(n)   (1ULL << (n))
#define PFN_MASK 0x000FFFFFFFFFF000ULL   /* біти 51…12 */

static void decode_pte(uint64_t e)
{
    if (!(e & BIT(0))) {                       /* P = 0 */
        uint64_t type   = e >> 59;             /* біти 63…59 */
        uint64_t offset = (~e << 5) >> 14;     /* інверсія, біти 58…9 */

        printf("відсутній: тип=%llu зміщення=%llu%s%s%s\n",
               (unsigned long long)type, (unsigned long long)offset,
               (e & BIT(1)) ? " soft-dirty" : "",
               (e & BIT(2)) ? " uffd-wp"    : "",
               (e & BIT(3)) ? " exclusive"  : "");
        return;
    }

    printf("кадр=0x%llx %s %s %s %s%s%s ключ=%llu\n",
           (unsigned long long)((e & PFN_MASK) >> 12),
           (e & BIT(1))  ? "rw"   : "ro",
           (e & BIT(2))  ? "user" : "kernel",
           (e & BIT(63)) ? "nx"   : "x",
           (e & BIT(5))  ? "A" : "-",
           (e & BIT(6))  ? "D" : "-",
           (e & BIT(8))  ? "G" : "-",
           (unsigned long long)((e >> 59) & 0xF));
}
