// ── Прив'язка до заліза (узагальнено; на вашому МК макроси інші) ──────────
#define SPK_PORT   GPIOA
#define SPK_PIN    5u
#define GPIO_SET(port, pin)   ((port)->BSRR = (1u << (pin)))          // ніжка → 1
#define GPIO_CLR(port, pin)   ((port)->BSRR = (1u << ((pin) + 16u)))  // ніжка → 0

// Виклик ІЗ переривання таймера на сталій частоті (напр. 250 кГц).
void TIMER_ISR(void)
{
    TIMER_CLEAR_FLAG();                  // ПЕРШИМ ділом — зняти прапор переривання

    uint8_t level = next_sine_level();   // 1) що видати цієї миті
    uint8_t bit   = sd1_tick(level);     // 2) як видати грубим бітом

    if (bit)                             // 3) кладемо біт на ніжку
        GPIO_SET(SPK_PORT, SPK_PIN);
    else
        GPIO_CLR(SPK_PORT, SPK_PIN);
}
