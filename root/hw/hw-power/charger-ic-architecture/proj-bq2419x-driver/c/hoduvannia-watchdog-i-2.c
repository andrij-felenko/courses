/* Викликати періодично, з періодом < вікна watchdog (тут ~10 с). */
void bq_service(void)
{
    bq_watchdog_kick();

    bq_status_t st;
    if (bq_read_status(&st) == 0) {
        if (st.phase == CHG_FAST && st.in_dpm) {
            /* Заряд упирається у ВХІД, не в ICHG:
               слабке джерело або тонкий кабель — не «поламаний» заряд. */
        }
    }
}
