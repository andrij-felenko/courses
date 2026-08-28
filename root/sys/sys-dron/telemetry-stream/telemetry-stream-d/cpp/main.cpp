/* Бюджет телеметрійного каналу — груба, але чесна оцінка.
   Рахуємо біти на секунду й порівнюємо з повітряною пропускною. */
#include <cstdio>

/* біт/с, які з'їдає один потік повідомлень */
static double stream_bps(int payload_bytes, double hz) {
    int frame = payload_bytes + 12;   /* +12 байт обрамлення MAVLink v2 */
    return frame * 8 * hz;            /* байти → біти, × частота */
}

int main() {
    double air      = 64000.0;        /* повітряна швидкість, біт/с      */
    double usable   = air * 0.90;     /* ~90 % без корекції помилок      */

    double attitude = stream_bps(28, 20.0);   /* (28+12)*8*20 = 6400 б/с */
    double position = stream_bps(28,  5.0);   /* (28+12)*8*5  = 1600 б/с */
    double total    = attitude + position;    /* = 8000 б/с              */

    printf("корисна смуга: %.0f б/с\n", usable);   /* 57600 */
    printf("потрібно:      %.0f б/с\n", total);     /*  8000 */
    printf("завантаження:  %.0f%%\n", 100.0 * total / usable);  /* 14% */
    return 0;
}
