#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define EVENT_BUFFER_SIZE 32 // Кількість збережених подій у пам'яті RAM

// Структура збереженого кадру події в оперативній пам'яті автопілота
typedef struct {
    uint32_t id;                    // 32-бітний хеш події (event_id)
    uint32_t time_boot_ms;          // Часова мітка від старту процесора (мс)
    uint16_t sequence;              // Порядковий номер у черзі
    uint8_t  destination_component; // Цільовий компонент (0 = broadcast)
    uint8_t  destination_system;    // Цільова система (0 = broadcast)
    uint8_t  log_levels;            // Бітове поле рівнів важливості
    uint8_t  arguments[40];         // Двійковий масив аргументів
    uint8_t  payload_length;        // Фактична довжина корисних даних
} stored_event_t;

// Стан кільцевого буфера подій польотного контролера
typedef struct {
    stored_event_t buffer[EVENT_BUFFER_SIZE];
    uint16_t       head_sequence;   // Номер наступної події для запису
    uint16_t       oldest_sequence; // Номер найстарішої доступної події
    bool           has_wrapped;     // Ознака циклічного заповнення масиву
} autopilot_event_buffer_t;

// Ініціалізація статичного буфера подій
void event_buffer_init(autopilot_event_buffer_t *eb) {
    memset(eb, 0, sizeof(autopilot_event_buffer_t));
    eb->head_sequence = 0;
    eb->oldest_sequence = 0;
    eb->has_wrapped = false;
}

// Додавання нової події до кільцевого буфера
uint16_t event_buffer_push(autopilot_event_buffer_t *eb,
                           uint32_t id,
                           uint32_t time_boot_ms,
                           uint8_t log_levels,
                           const uint8_t *args,
                           uint8_t args_len) {
    uint16_t seq = eb->head_sequence;
    size_t index = seq % EVENT_BUFFER_SIZE;

    stored_event_t *ev = &eb->buffer[index];
    ev->id = id;
    ev->time_boot_ms = time_boot_ms;
    ev->sequence = seq;
    ev->destination_component = 0;
    ev->destination_system = 0;
    ev->log_levels = log_levels;

    size_t copy_bytes = (args_len > 40) ? 40 : args_len;
    memcpy(ev->arguments, args, copy_bytes);
    if (copy_bytes < 40) {
        memset(&ev->arguments[copy_bytes], 0, 40 - copy_bytes);
    }
    ev->payload_length = (uint8_t)(13 + copy_bytes);

    // Оновлення монотонного лічильника та меж доступності
    eb->head_sequence = (uint16_t)((seq + 1) & 0xFFFF);
    if (eb->has_wrapped) {
        eb->oldest_sequence = (uint16_t)((eb->oldest_sequence + 1) & 0xFFFF);
    } else if (eb->head_sequence >= EVENT_BUFFER_SIZE) {
        eb->has_wrapped = true;
        eb->oldest_sequence = 0;
    }

    return seq;
}

// Пошук події за номером послідовності для повторного відправлення
bool event_buffer_get(const autopilot_event_buffer_t *eb,
                      uint16_t sequence,
                      stored_event_t *out_event) {
    uint16_t diff = (uint16_t)(eb->head_sequence - sequence);
    if (diff == 0 || diff > EVENT_BUFFER_SIZE) {
        return false; // Подія ще не настала або вже витіснена з пам'яті
    }

    size_t index = sequence % EVENT_BUFFER_SIZE;
    if (eb->buffer[index].sequence == sequence) {
        memcpy(out_event, &eb->buffer[index], sizeof(stored_event_t));
        return true;
    }
    return false;
}
