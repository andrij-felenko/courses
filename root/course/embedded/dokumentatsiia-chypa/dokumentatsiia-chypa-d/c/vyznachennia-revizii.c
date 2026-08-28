/* Зчитування ідентифікатора та ревізії чипа в STM32 */
uint32_t idcode = DBGMCU->IDCODE;
uint16_t dev_id = (uint16_t)(idcode & 0x0FFFUL);        /* Номер сімейства (Device ID) */
uint16_t rev_id = (uint16_t)((idcode >> 16) & 0xFFFFUL); /* Ревізія кремнію (Silicon Revision) */

if (rev_id == 0x1000U) {
    /* Ревізія Rev A: застосовуємо обхід апаратного дефекту */
    apply_errata_workaround();
} else {
    /* Ревізія Rev B або новіша: використовуємо швидкий апаратний шлях */
    use_standard_hardware_path();
}
