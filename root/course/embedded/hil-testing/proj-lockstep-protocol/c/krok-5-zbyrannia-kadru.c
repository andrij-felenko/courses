extern void link_write(const uint8_t *data, size_t n);  // UART/USB — байти в лінк

void hil_send_actuators_framed(const float thr[], int n,
                               uint16_t echo_seq, uint32_t echo_t_us) {
    hil_actuators_t f;
    f.sync0 = HIL_SYNC0;
    f.sync1 = HIL_SYNC1;
    f.seq   = echo_seq;                 // ЕХО: на цей вимір відповідаємо
    f.t_us  = echo_t_us;
    for (int i = 0; i < HIL_N_MOTORS; i++)
        f.thr[i] = (i < n) ? thr[i] : 0.0f;
    f.crc = actuators_crc(&f);          // CRC над усім, окрім себе

    link_write((const uint8_t *)&f, sizeof(f));  // 26 байтів у лінк
}
