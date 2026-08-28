/* Зупинка DMA потоку таймера моторів */
DMA2_Stream5->CR &= ~DMA_SxCR_EN;
while (DMA2_Stream5->CR & DMA_SxCR_EN) {
    /* Очікування завершення поточного транзакційного циклу */
}
/* Заповнення буфера значенням DShot 0 (Motor Stop) */
for (size_t i = 0; i < DSHOT_BUFFER_SIZE; ++i) {
    dshot_dma_raw_buffer[i] = DSHOT_CMD_MOTOR_STOP_PATTERN;
}
/* Перезапуск DMA для неперервної передачі нульової тяги */
DMA2_Stream5->NDTR = DSHOT_BUFFER_SIZE;
DMA2_Stream5->CR |= DMA_SxCR_EN;
