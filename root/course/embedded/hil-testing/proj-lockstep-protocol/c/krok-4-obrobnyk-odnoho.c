// Стан такту: що ми бачили востаннє, щоб упізнати дубль і розсинхрон.
static uint16_t g_last_seq;
static uint32_t g_last_t_us;
static bool     g_stream_started = false;

static volatile uint32_t g_model_time_us;   // «зараз» для now_us()
static volatile imu_sample_t g_injected;    // вимір для imu_read()

uint32_t now_us(void) { return g_model_time_us; }  // час — з моделі, не з кварцу

// Викликаємо, коли sensor_rx_byte() віддав повний CRC-цілий кадр.
void hil_on_sensor_frame(const hil_sensors_t *f) {
    // ── ЗАХИСТ 1: дубль. Той самий seq, що й минулого разу?
    if (g_stream_started && f->seq == g_last_seq)
        return;                         // повтор — НЕ робимо другий крок на тому ж виміри

    // ── ЗАХИСТ 2: монотонність часу. Модельний час мусить лише зростати.
    if (g_stream_started && f->t_us <= g_last_t_us)
        return;                         // мітка стрибнула назад/стала — кадр підозрілий, викид

    // (втрату кадру — стрибок seq через число — у lockstep НЕ караємо: див. нижче)
    g_last_seq = f->seq;
    g_last_t_us = f->t_us;
    g_stream_started = true;

    // ── Такт: підставляємо модельні час і вимір, робимо РІВНО один крок.
    g_model_time_us = f->t_us;          // модельний час стає «зараз»
    g_injected.roll = f->roll; g_injected.pitch = f->pitch; g_injected.yaw = f->yaw;
    g_injected.ax = f->ax; g_injected.ay = f->ay; g_injected.az = f->az;
    g_injected.t_us = f->t_us;

    float thr[HIL_N_MOTORS];
    control_step(thr);                  // один крок петлі: imu_read → фільтр → мікшер

    // ── Відповідь: ехо seq/t_us, щоб модель знала, на що це відповідь.
    hil_send_actuators_framed(thr, HIL_N_MOTORS, f->seq, f->t_us);
}
