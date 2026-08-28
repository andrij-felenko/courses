// Скільки максимум чекати на підняття опори, перш ніж визнати відмову.
// Запас над паспортним часом прокидання bandgap (типово десятки–сотні мкс).
#define VREF_TIMEOUT_US    5000u    // 5 мс — щедрий запас навіть на повільний фронт
#define VREF_POLL_US        250u    // крок очікування між спробами

typedef enum {
    VREF_ALIVE = 0,   // опора піднялась, відлік у вікні
    VREF_DEAD         // таймаут вичерпано, опора так і не піднялась
} vref_status_t;

// Дочекатися живої опори АБО вичерпати таймаут.
static vref_status_t wait_for_reference(void)
{
    uint32_t waited = 0;
    while (waited < VREF_TIMEOUT_US) {
        delay_us(VREF_POLL_US);
        waited += VREF_POLL_US;

        uint16_t code = witness_average();
        if (witness_in_window(code)) {
            return VREF_ALIVE;        // опора жива — виходимо одразу
        }
        // Поки на краю — даємо ще шанс: можливо, опора повільно повзе вгору.
    }
    return VREF_DEAD;                  // час вийшов, опора так і не ожила
}
