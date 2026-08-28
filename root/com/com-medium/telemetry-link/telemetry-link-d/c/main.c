/* Бюджет лінії земля-борт: чи долетить сигнал і з яким запасом.
   Уся арифметика в децибелах — множення потужностей стає додаванням. */
#include <stdio.h>
#include <math.h>

/* Загасання у вільному просторі, дБ.  d — км, f — МГц. */
static double fspl_db(double d_km, double f_mhz) {
    return 32.44 + 20.0 * log10(d_km) + 20.0 * log10(f_mhz);
}

int main(void) {
    double p_tx = 20.0;    /* потужність передавача, дБм (100 мВт) */
    double g_tx = 2.0;     /* виграш антени передавача, дБі        */
    double g_rx = 2.0;     /* виграш антени приймача, дБі          */
    double sens = -110.0;  /* чутливість приймача, дБм             */

    double loss = fspl_db(3.0, 915.0);            /* ≈ 101.2 дБ    */
    double p_rx = p_tx + g_tx - loss + g_rx;      /* прийнято, дБм */
    double margin = p_rx - sens;                  /* запас, дБ     */

    printf("загасання (3 км): %.1f дБ\n", loss);   /* 101.2  */
    printf("прийнято:         %.1f дБм\n", p_rx);  /* -77.2  */
    printf("запас:            %.1f дБ\n", margin); /*  32.8  */
    return 0;
}
