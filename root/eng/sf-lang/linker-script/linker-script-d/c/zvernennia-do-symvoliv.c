/* Отримання адрес символів лінкера мовою C */
#include <stdint.h>

/* Варіант 1: Оголошення як змінної та взяття адреси через & */
extern uint32_t _sdata;
extern uint32_t _edata;

/* Варіант 2: Оголошення як масиву без розміру (ім'я масиву є адресою) */
extern uint32_t _sbss[];
extern uint32_t _ebss[];

void memory_audit(void) {
    /* Отримання числових адрес початку та кінця .data */
    uint32_t *p_data_start = &_sdata;
    uint32_t *p_data_end   = &_edata;
    uint32_t data_bytes    = (uint8_t*)p_data_end - (uint8_t*)p_data_start;

    /* Отримання числових адрес початку та кінця .bss */
    uint32_t *p_bss_start  = _sbss;
    uint32_t *p_bss_end    = _ebss;
    uint32_t bss_bytes     = (uint8_t*)p_bss_end - (uint8_t*)p_bss_start;
}
