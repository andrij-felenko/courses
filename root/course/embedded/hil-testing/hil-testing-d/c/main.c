#ifdef HIL_LOCKSTEP

static volatile uint32_t g_model_time_us;   // «зараз» = мітка з моделі
static volatile imu_sample_t g_injected;    // вимір із моделі

uint32_t now_us(void) { return g_model_time_us; }   // час — з моделі, не з кварцу

// Викликається, коли по лінку прийшов повний HIL-кадр із міткою часу.
void hil_on_sensor_frame(const hil_sensors_t *f) {
    g_model_time_us = f->t_us;          // 3a. беремо модельний час за «зараз»
    g_injected      = f->imu;           //     і модельний вимір

    float thr[4];
    control_step(thr);                  // 3b. РІВНО один крок петлі керування
                                        //     (усередині: imu_read → фільтр → мікшер)

    hil_send_actuators(thr, 4);         // 4.  віддаємо команди назад у модель
    // на цьому такт завершено; наступний кадр моделі прийде, коли ВОНА
    // проінтегрує фізику до T+Δt — плата доти просто НЕ РОБИТЬ кроків
}
#endif
