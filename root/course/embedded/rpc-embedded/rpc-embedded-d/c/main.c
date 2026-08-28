#include <stdint.h>
#include <stddef.h>

// Кожен обробник — звичайна функція тієї самої форми.
typedef int32_t (*rpc_handler)(int32_t arg);

static int32_t h_ping(int32_t a)       { (void)a; return 0; }          // живий?
static int32_t h_read_sensor(int32_t n){ return adc_read((int)n); }    // значення АЦП
static int32_t h_set_motor(int32_t d)  { motor_set((int)d); return d; }// статус

// Таблиця: номер функції → вказівник на обробник.
static const rpc_handler TABLE[] = {
    h_ping,          // 0
    h_read_sensor,   // 1
    h_set_motor,     // 2
};
#define RPC_COUNT (sizeof(TABLE) / sizeof(TABLE[0]))

// Виклик диспетчера на цілий (CRC уже зійшовся) запит.
// func — номер функції з кадру, arg — її аргумент, out — куди класти результат.
// Повертає true, якщо команду знайдено й виконано.
bool rpc_dispatch(uint8_t func, int32_t arg, int32_t *out) {
    if (func >= RPC_COUNT)      // невідома команда — НЕ викликаємо нічого
        return false;           // (інакше — вихід за межі масиву, аварія)
    *out = TABLE[func](arg);    // увесь диспетчер — цей один рядок
    return true;
}
