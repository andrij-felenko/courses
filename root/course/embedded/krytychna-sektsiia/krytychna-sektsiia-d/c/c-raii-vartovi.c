/* Типова помилка витоку критичної секції в C */
int process_sensor_buffer(uint8_t *buffer, size_t len) {
    uint32_t primask = __get_PRIMASK();
    __disable_irq();
    
    if (buffer == NULL || len == 0) {
        /* КАТАСТРОФА: Вихід без відновлення PRIMASK! 
         * Переривання залишаються вимкненими назавжди, система мертво зависає. */
        return -1; 
    }
    
    parse_data(buffer, len);
    
    __set_PRIMASK(primask);
    return 0;
}
