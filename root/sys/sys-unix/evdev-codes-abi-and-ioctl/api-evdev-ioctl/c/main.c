#define BITS_PER_LONG (sizeof(unsigned long) * 8)
#define NBITS(x) ((((x) - 1) / BITS_PER_LONG) + 1)
#define OFF(x)  ((x) % BITS_PER_LONG)
#define BIT(x)  (1UL << OFF(x))
#define LONG(x) ((x) / BITS_PER_LONG)
#define test_bit(bit, array) ((array[LONG(bit)] >> OFF(bit)) & 1)

unsigned long keybit[NBITS(KEY_MAX)] = {0};
ioctl(fd, EVIOCGBIT(EV_KEY, sizeof(keybit)), keybit);

if (test_bit(KEY_ENTER, keybit)) {
    /* Пристрій підтримує клавішу ENTER */
}
