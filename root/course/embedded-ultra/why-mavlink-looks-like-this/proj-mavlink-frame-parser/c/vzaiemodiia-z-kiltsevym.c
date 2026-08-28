// Типовий цикл обробки телеметрії в задачі RTOS
void telemetry_task_loop(mavlink_parser_t *parser, uart_dma_ring_t *ring) {
    uint8_t byte;
    while (uart_dma_ring_pop(ring, &byte)) {
        // Отримуємо MSG_ID на кроці заголовка для вибору правильного CRC_EXTRA
        uint8_t crc_extra = mavlink_get_crc_extra(parser->frame.msgid);
        
        if (mavlink_parse_byte(parser, byte, crc_extra)) {
            // Пакет успішно прийнято та верифіковано
            handle_mavlink_message(&parser->frame);
        }
    }
}
