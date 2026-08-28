// Зчитування ідентифікатора та ревізії чипа в STM32
const uint32_t idcode = dbgmcu->idcode;
const auto dev_id = static_cast<uint16_t>(idcode & 0x0FFFUL);
const auto rev_id = static_cast<uint16_t>((idcode >> 16) & 0xFFFFUL);

if (rev_id == 0x1000U) {
    // Ревізія Rev A: застосовуємо обхід апаратного дефекту
    apply_errata_workaround();
} else {
    // Ревізія Rev B або новіша: використовуємо швидкий апаратний шлях
    use_standard_hardware_path();
}
