void vMacRxTaskCpp(void *pvParameters) {
    radio_packet_t rx_packet{};
    LinkQualityMonitor<32> link_mon(0.125f);

    for (;;) {
        if (xQueueReceive(xRadioRxQueue, &rx_packet, portMAX_DELAY) == pdTRUE) {
            /* Зчитування метаданих у C++ об'єкт */
            const auto raw_rssi = static_cast<float>(rx_packet.header.rssi);
            const auto raw_snr  = static_cast<float>(rx_packet.header.snr);
            const auto raw_lqi  = static_cast<float>(rx_packet.header.lqi);
            const bool crc_ok   = rx_packet.header.crc_valid;

            /* Оновлення стану через метод класу */
            link_mon.processPacket(raw_rssi, raw_snr, raw_lqi, crc_ok);

            /* Реагування на критичний стан через сильно типізований enum */
            if (link_mon.healthStatus() == LinkHealth::Critical) {
                vRadioSetPowerTx(TX_POWER_MAX);
            }
        }
    }
}
