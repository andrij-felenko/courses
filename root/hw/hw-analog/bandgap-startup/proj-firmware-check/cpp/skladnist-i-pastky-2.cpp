// Перезавантаження з лічильником спроб — проти нескінченної петлі reset.
// boot_attempts лежить у пам'яті, що переживає скидання (backup-регістр,
// noinit-секція ОЗП тощо) — її НЕ чистить системний старт.
#define MAX_VREF_RETRIES   3u
extern uint32_t boot_attempts;   // переживає reset; чиститься лише при штатному старті

static void handle_dead_reference(void)
{
    fault_latch(FAULT_VREF_DEAD);

    if (boot_attempts < MAX_VREF_RETRIES) {
        boot_attempts++;
        system_reset();              // ще один чесний шанс прокинутись
    } else {
        // Кілька спроб поспіль провалились → це не випадковість, а апаратна біда.
        boot_attempts = 0;
        enter_degraded_mode();       // лишитись живим, але без довіри до АЦП
    }
}
