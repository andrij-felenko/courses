// Давач як крихітний автомат: два стани, жодного чекання в циклі.
enum { S_IDLE, S_MEASURING };
static uint8_t s_state = S_IDLE;
static uint32_t s_t_cmd = 0;          // коли послали команду «зміряй»
#define CONV_MS  15                   // із запасом над 12 мс перетворення

// Викликається щоразу зі швидкої петлі; ніколи не блокує.
// Повертає true й кладе значення в *out, коли готове свіже число.
static bool sensor_poll(uint32_t now, float *out) {
    switch (s_state) {
    case S_IDLE:
        sensor_start_conversion();     // тільки надсилаємо команду — миттєво
        s_t_cmd = now;
        s_state = S_MEASURING;
        return false;                  // числа ще нема, але й не чекаємо
    case S_MEASURING:
        if (now - s_t_cmd < CONV_MS) return false;  // ще рахує — виходимо
        *out = sensor_read_result();   // готово: забираємо без чекання
        s_state = S_IDLE;
        return true;
    }
    return false;
}
