#include <stdint.h>
#include <stdbool.h>

// Стан приймача: який номер чекаємо наступним (0 або 1).
static uint8_t expected_seq = 0;

// Виклик на кожен цілий (CRC зійшовся) кадр. Повертає true, якщо це
// СВІЖІ дані, які слід віддати застосунку; false — якщо це дублікат.
bool rx_accept(uint8_t frame_seq, const uint8_t *payload, int len) {
    send_ack(frame_seq);                 // ACK шлемо ЗАВЖДИ — і на дублікат теж
    if (frame_seq != expected_seq)       // номер не той, що чекали → це повтор
        return false;                    // дані вже маємо, мовчки відкидаємо
    deliver_to_app(payload, len);        // свіжий кадр — віддаємо вище
    expected_seq ^= 1;                   // чекаємо наступний: 0→1, 1→0
    return true;
}
