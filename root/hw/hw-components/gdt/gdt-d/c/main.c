// Лічильник спрацювань GDT за сигналом компаратора на падінні напруги лінії.
// Виклик — з переривання на фронті від компаратора (лінія просіла в дугу).
#define GDT_RATED_STRIKES  300U   // паспортний ресурс важких ударів

static volatile uint32_t gdt_strikes = 0;

void gdt_strike_isr(void)         // фронт від компаратора «лінія в дузі»
{
    if (gdt_strikes < UINT32_MAX)
        gdt_strikes++;
}

bool gdt_worn_out(void)           // опитувати в фоні
{
    return gdt_strikes >= GDT_RATED_STRIKES;   // час перевірити/замінити GDT
}
