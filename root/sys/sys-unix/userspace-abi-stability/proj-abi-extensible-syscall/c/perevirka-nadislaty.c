static void test_forward_compat(int fd)
{
        /* об'єднання, а не масив char: інакше буфер може виявитися
           невирівняним, і структура ляже не на ту адресу */
        union {
                struct pacer_policy p;
                char                raw[sizeof(struct pacer_policy) + 16];
        } u = { 0 };
        const size_t tail = sizeof(struct pacer_policy);   /* перший байт «майбутнього» */

        u.p.size = sizeof(u.raw);   /* «я з майбутнього, у мене структура довша» */
        u.p.rate = 1000;

        /* хвіст нульовий — драйвер мусить спокійно спрацювати */
        assert(ioctl(fd, PACER_ARM, &u.p) == 0);

        /* у хвості щось є — драйвер мусить відмовити, і саме з E2BIG */
        u.raw[tail] = 1;
        assert(ioctl(fd, PACER_ARM, &u.p) == -1 && errno == E2BIG);

        /* біт, якого не існує, — EINVAL, а не тиха згода */
        u.raw[tail] = 0;
        u.p.flags   = 1ULL << 63;
        assert(ioctl(fd, PACER_ARM, &u.p) == -1 && errno == EINVAL);
}
