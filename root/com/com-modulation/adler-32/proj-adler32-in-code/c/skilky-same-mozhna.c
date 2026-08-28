/* do length NMAX blocks -- requires just one modulo operation */
while (len >= NMAX) {
    len -= NMAX;
    n = NMAX / 16;          /* NMAX is divisible by 16 */
    do {
        DO16(buf);          /* 16 sums unrolled */
        buf += 16;
    } while (--n);
    MOD(adler);
    MOD(sum2);
}
