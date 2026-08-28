void vMacRxTask(void *pvParameters) {
    radio_packet_t rx_packet;
    link_monitor_t link_mon;
    link_monitor_init(&link_mon);

    for (;;) {
        if (xQueueReceive(xRadioRxQueue, &rx_packet, portMAX_DELAY) == pdTRUE) {
            /* Зчитування апаратних метаданих кадру */
            int8_t raw_rssi = rx_packet.header.rssi;
            int8_t raw_snr  = rx_packet.header.snr;
            uint8_t raw_lqi = rx_packet.header.lqi;
            bool crc_ok     = rx_packet.header.crc_valid;

            /* Оновлення стану монітора */
            link_monitor_update(&link_mon, raw_rssi, raw_snr, raw_lqi, crc_ok);

            /* Якщо стан каналу критичний — відправляємо сигнали на зниження швидкості */
            if (link_mon.status == LINK_STATUS_CRITICAL) {
                vRadioSetPowerTx(TX_POWER_MAX);
            }
        }
    }
}
