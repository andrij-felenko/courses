// Коди відмов для журналу/індикації.
typedef enum {
    FAULT_NONE = 0,
    FAULT_VREF_DEAD        // bandgap-опора не піднялась у відведений час
} fault_code_t;

extern void fault_latch(fault_code_t code);   // зафіксувати відмову (журнал, світлодіод)
extern void enter_normal_mode(void);          // штатний робочий режим
extern void enter_degraded_mode(void);        // обмежений безпечний режим (див. нижче)
extern void system_reset(void);               // програмне перезавантаження

void system_bringup(void)
{
    adc_init();

    // Дати bandgap час прокинутись після подачі живлення.
    // Перша груба затримка — менша за таймаут, далі добиратиме wait_for_reference().
    delay_us(500);

    if (wait_for_reference() == VREF_ALIVE) {
        enter_normal_mode();                  // опора доведено жива — повна довіра АЦП
        return;
    }

    // Опора мертва: НЕ виходити в робочий режим зі сліпими вимірами.
    fault_latch(FAULT_VREF_DEAD);

    // Що далі — питання архітектури (див. «пастки»):
    //   або спробувати вилікувати перезавантаженням,
    //   або працювати в деградованому режимі без довіри до АЦП.
    system_reset();                           // тут обрано перезавантаження
}
