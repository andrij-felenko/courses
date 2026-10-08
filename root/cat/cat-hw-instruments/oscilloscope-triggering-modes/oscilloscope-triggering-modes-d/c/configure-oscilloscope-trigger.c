/* C (VISA / SCPI): Налаштування тригера для захоплення шумного пакетного сигналу */
#include <stdio.h>
#include <visa.h>

void configure_oscilloscope_trigger(ViSession vi) {
    /* Встановлення режиму Normal та джерела CH1 */
    viPrintf(vi, "TRIGger:A:MODE NORMal\n");
    viPrintf(vi, "TRIGger:A:SOURce CH1\n");
    
    /* Вибір фронту та порогового рівня 1.5 В */
    viPrintf(vi, "TRIGger:A:EDGE:SLOPe POSitive\n");
    viPrintf(vi, "TRIGger:A:LEVel 1.5\n");
    
    /* Увімкнення фільтрації шуму та налаштування часу Holdoff (150 мкс) */
    viPrintf(vi, "TRIGger:A:COUPling HFRej\n");
    viPrintf(vi, "TRIGger:A:HOLDoff 150E-6\n");
}
