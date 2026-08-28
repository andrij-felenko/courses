/* У C ідіома RAII не підтримується на рівні мови (якщо не використовувати GCC cleanup attribute).
 * Класичний безпечний підхід у C — єдина точка виходу (Single Exit Point) через goto: */
int process_sensor_buffer_c_safe(uint8_t *buffer, size_t len) {
    int status = 0;
    uint32_t primask = __get_PRIMASK();
    __disable_irq();
    __asm volatile("" ::: "memory");
    
    if (buffer == NULL || len == 0) {
        status = -1;
        goto cleanup;
    }
    
    parse_data(buffer, len);

cleanup:
    __asm volatile("" ::: "memory");
    __set_PRIMASK(primask);
    return status;
}
