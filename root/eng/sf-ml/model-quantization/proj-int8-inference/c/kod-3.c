/* y = округл(x / 2^exp), round-half-up; для від'ємних x поправка на 1,
   щоб напрям округлення був симетричний і не зсував середнє. */
static inline int32_t round_shift_right(int32_t x, int32_t exp)
{
    if (exp <= 0) return x;
    int32_t mask      = (1 << exp) - 1;          /* біти, що відкидаємо        */
    int32_t remainder = x & mask;                /* сам відкинутий залишок     */
    int32_t threshold = (mask >> 1) + (x < 0);   /* половина; для x<0 зсув на 1 */
    return (x >> exp) + (remainder > threshold); /* арифм. зсув + округлення +1 */
}
