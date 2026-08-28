/* Чи влізе бажана телеметрія у повітряний канал модема?
   Серійна швидкість тут НЕ важить — обмежує повітряна. */
#include <stdio.h>

int fits(double air_bps, double need_bps) {
    double usable = air_bps * 0.90;     /* ~90% без корекції помилок */
    return need_bps <= usable;
}

int main(void) {
    double air  = 64000.0;              /* повітряна швидкість SiK, біт/с */
    double need = 8000.0;               /* кілька потоків телеметрії      */
    printf("повітряна:    %.0f б/с\n", air);
    printf("корисна:      %.0f б/с\n", air * 0.90);   /* 57600 */
    printf("влізе? %s\n", fits(air, need) ? "так" : "ні");  /* так */
    return 0;
}
