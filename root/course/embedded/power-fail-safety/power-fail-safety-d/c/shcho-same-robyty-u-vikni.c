// Критичний стан, який треба врятувати при зникненні живлення
typedef struct {
    uint32_t magic;        // мітка «дані справжні» (перевіримо при старті)
    uint32_t work_counter; // лічильник напрацювання
    int32_t  last_value;   // останній вимір
    uint16_t op_position;  // де нас перервали в довгій операції
    uint16_t crc;          // контрольна сума решти полів
} CriticalState;

static volatile CriticalState g_state;   // живе в RAM, оновлюється на ходу

// Переривання PVD: напруга просіла до верхнього порога — РЯТУЄМОСЯ
void PVD_IRQHandler(void)
{
    // 1. Негайно вимкнути все, що жере струм і час:
    //    зупинити мотори, погасити дисплей, заглушити радіо.
    //    Менше споживання → повільніше падає напруга → ширше вікно.
    motors_emergency_stop();
    display_off();
    radio_off();

    // 2. Дорахувати контрольну суму й записати стан у FRAM.
    //    FRAM пише за наносекунди — встигаємо, поки тримають конденсатори.
    g_state.magic = STATE_MAGIC;
    g_state.crc   = crc16((const uint8_t *)&g_state,
                          offsetof(CriticalState, crc));
    fram_write(FRAM_STATE_ADDR, (const uint8_t *)&g_state, sizeof g_state);

    // 3. Більше нічого не починаємо. Якщо живлення повернеться —
    //    нас або скине BOD, або ми просто продовжимо. Якщо ні —
    //    стан уже в безпеці.
    pwr_clear_pvd_flag();   // зняти прапорець переривання
}
