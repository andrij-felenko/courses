// Головна функція: тягне байти з кільцевого буфера. Коли готовий валідний кадр —
// заповнює out (сирі канали + прапорці) і us[16] (мікросекунди) та повертає 1.
int sbus_read(sbus_data_t *out, int us[16]) {
    uint8_t frame[SBUS_LEN];
    if (!sbus_poll(frame)) return 0;      // цілого кадру ще нема

    sbus_unpack_channels(&frame[1], out->ch);   // 16 каналів із frame[1..22]
    sbus_read_flags(frame[23], out);            // прапорці з байта 23

    for (int i = 0; i < 16; i++)
        us[i] = sbus_raw_to_us(out->ch[i]);     // сире → мкс

    return 1;
}
