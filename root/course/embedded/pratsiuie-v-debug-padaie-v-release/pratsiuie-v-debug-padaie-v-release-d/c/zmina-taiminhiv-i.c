uint8_t rx_buffer[64];

void start_sensor_read(void) {
    dma_start_transfer(rx_buffer, 64);
    
    // Помилка: відсутнє очікування прапорця завершення DMA!
    // У Debug: процесор виконує парсинг заголовка за 150 мкс.
    // За цей час DMA вже встигає завантажити всі 64 байти.
    parse_packet(rx_buffer); 
}
