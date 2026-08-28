// Умкнути регулятор БЕЗ стрибка: підігнати інтеграл так, щоб перший вихід
// дорівнював u_hold (тому, що видавало керування досі).
// meas — поточний вимір (щоб коректно підхопити стан похідної).
void pid_engage_bumpless(pid_t *p, float u_hold, float setpoint, float meas)
{
    // підхопити вимір — щоб перша похідна не стрибнула:
    p->meas_prev   = meas;
    p->deriv_filt  = 0.0f;
    p->initialized = true;

    // хочемо: Kp·e_p + integral + 0 == u_hold  (похідна щойно обнулена)
    float e_p = p->b * setpoint - meas;
    p->integral = u_hold - p->Kp * e_p;   // integral уже містить Ki — тож просто вольти
}
