/* Приклад використання в задачі мережевої синхронізації */
void telemetry_sync_task(flash_ring_t *ring, network_client_t *net) {
    uint8_t payload[256];
    uint16_t len = 0;
    uint32_t seq = 0;

    while (1) {
        /* 1. Підглядаємо найстаріше повідомлення без видалення */
        flash_ring_status_t status = flash_ring_peek(ring, payload, sizeof(payload), &len, &seq);
        if (status == FLASH_RING_ERR_EMPTY) {
            vTaskDelay(pdMS_TO_TICKS(1000)); /* Черга порожня — чекаємо */
            continue;
        }

        /* 2. Відправляємо пакет по мережі з таймаутом */
        int net_res = network_send_packet(net, payload, len);
        if (net_res == 0) {
            /* 3. Тільки після успішного ACK від сервера видаляємо запис з Flash */
            flash_ring_commit_pop(ring);
        } else {
            /* Помилка мережі: робимо експоненційний відступ, запис залишається в черзі */
            vTaskDelay(pdMS_TO_TICKS(5000));
        }
    }
}
