/* include/event_types.h — універсальний тип події системи.
 * Це спільний словник усіх шарів: обробник переривання складає подію,
 * головний цикл її розбирає. Подія навмисно легковагова (16 байтів на
 * 32-бітному ядрі) і не тримає покажчиків на дані, що можуть зникнути
 * до обробки; єдиний виняток — прийнятий пакет, який лежить у власному
 * кільцевому буфері служби зв'язку й живе довше за подію. */
#ifndef EVENT_TYPES_H
#define EVENT_TYPES_H

#include <stdint.h>

typedef enum {
    EVT_ID_NONE = 0,
    EVT_ID_TICK_100MS,       /* системний тік від таймера */
    EVT_ID_BUTTON_CLICK,     /* натиск кнопки, джерело — переривання EXTI */
    EVT_ID_SENSOR_DATA_READY,
    EVT_ID_SENSOR_FAULT,     /* давач не відповів або дав нісенітницю */
    EVT_ID_ALARM_OVERTEMP,
    EVT_ID_ALARM_VIBRATION,
    EVT_ID_ALARM_CLEARED,
    EVT_ID_COMMS_PACKET_RX
} event_id_t;

typedef struct {
    event_id_t id;
    uint32_t   timestamp_ms;
    union {
        uint8_t button_pin;

        struct {
            float temp_c;
            float pressure_kpa;
        } sensor_payload;

        struct {
            float peak_g;
        } vibration_payload;

        struct {
            uint16_t       len;
            const uint8_t *p_data;
        } rx_packet;

        struct {
            int32_t code;         /* статус шини, з якою не склалося */
            uint8_t device_addr;
        } fault_payload;
    } data;
} sys_event_t;

/* Конструктор події з порожнім навантаженням: обнуляє найбільший член
 * об'єднання, тож у черзі не лишається сміття з попередньої події. */
static inline sys_event_t sys_event_make(event_id_t id, uint32_t timestamp_ms)
{
    sys_event_t evt;
    evt.id = id;
    evt.timestamp_ms = timestamp_ms;
    evt.data.rx_packet.len = 0;
    evt.data.rx_packet.p_data = 0;
    return evt;
}

/* Ім'я події для журналу. Реалізація — у services/event_queue.c. */
const char *sys_event_name(event_id_t id);

#endif /* EVENT_TYPES_H */
