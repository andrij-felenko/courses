typedef enum { PH_CHARGE, PH_DUMP } phase_t;

static struct {
    volatile bool run;
    uint8_t donor, recipient;
    phase_t phase;
} sh;

void shuttle_start(uint8_t donor, uint8_t recipient)
{
    sh.donor = donor; sh.recipient = recipient;
    sh.phase = PH_CHARGE;
    sh.run   = true;
    timer_set_hz(SHUTTLE_HZ * 2u);        // дві фази на один цикл переносу
}

void shuttle_stop(void)
{
    sh.run = false;
    timer_stop();
    sw_all_open();                        // безпечний стан: усе розімкнено
}

// ISR таймера шатла: рівно ОДНА фаза за виклик, break-before-make.
void shuttle_timer_isr(void)
{
    sw_all_open();                        // 1) розімкнути ВСЕ
    delay_ns(DEADTIME_NS);                // 2) мертвий час: жоден ключ не встиг
    if (!sh.run) return;

    uint8_t cell = (sh.phase == PH_CHARGE) ? sh.donor : sh.recipient;
    sw_set(0u, cell,        true);        // 3) верх цапа → n[cell]
    sw_set(1u, cell + 1u,   true);        //    низ цапа  → n[cell+1]

    sh.phase = (sh.phase == PH_CHARGE) ? PH_DUMP : PH_CHARGE;
}
