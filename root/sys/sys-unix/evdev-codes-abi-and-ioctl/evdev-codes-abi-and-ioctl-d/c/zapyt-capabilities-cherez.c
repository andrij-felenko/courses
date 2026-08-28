#define BITS_PER_LONG (sizeof(unsigned long) * 8)
#define NBITS(x) ((((x) - 1) / BITS_PER_LONG) + 1)
#define test_bit(bit, array) ((array[(bit) / BITS_PER_LONG] >> ((bit) % BITS_PER_LONG)) & 1)

unsigned long evbit[NBITS(EV_MAX)] = {0};
ioctl(fd, EVIOCGBIT(0, sizeof(evbit)), evbit);

if (test_bit(EV_KEY, evbit) && test_bit(EV_ABS, evbit)) {
    /* Пристрій є сенсорним екраном або планшетом */
}
