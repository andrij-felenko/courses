/* Приклад зчитування регістрів з трансивера Semtech SX1276 (C) */
int8_t raw_snr = read_spi_register(REG_PKT_SNR_VALUE);
int16_t raw_rssi = read_spi_register(REG_PKT_RSSI_VALUE);

/* Перерахунок SNR: регістр зберігає знакову величину у чвертях дБ */
float measured_snr_db = (float)raw_snr / 4.0f;

/* Перерахунок RSSI у dBm (для частот High-Band > 779 МГц) */
float measured_rssi_dbm = -157.0f + (float)raw_rssi;

/* Якщо SNR < 0, корекція RSSI за рекомендацією виробника (Semtech Datasheet) */
if (measured_snr_db < 0.0f) {
    measured_rssi_dbm += measured_snr_db;
}

/* Розрахунок фактичного запасу лінії на основі реального SNR */
float measured_margin_db = measured_snr_db - required_snr_min_db;
