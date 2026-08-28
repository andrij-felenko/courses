// Поточний стан (оновлюється з loop або ISR)
static hid_mouse_report_t g_state;

// Прапорець: стек TinyUSB готовий слати наступний звіт
static volatile bool g_can_send = true;

// Callback: хост забрав попередній звіт, можна готувати наступний
void tud_hid_report_complete_cb(uint8_t instance,
                                uint8_t const *report,
                                uint16_t len)
{
    (void)instance; (void)report; (void)len;
    g_can_send = true;
}

// Виклик у loop() або по таймеру — НЕ частіше, ніж раз на bInterval мс
void hid_send_if_ready(void)
{
    if (!tud_hid_ready() || !g_can_send) return;
    g_can_send = false;
    tud_hid_report(0, &g_state, sizeof(g_state));
    // Реальний вихід на дріт станеться в IN-токені від хоста, не тут
}
