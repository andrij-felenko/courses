#include "chip_status.h"

const char *chip_status_str(chip_status_t status)
{
    switch (status) {
    case CHIP_OK:                return "OK";
    case CHIP_ERR_INVALID_PARAM: return "невірний параметр";
    case CHIP_ERR_COMM:          return "помилка шини";
    case CHIP_ERR_TIMEOUT:       return "тайм-аут очікування";
    case CHIP_ERR_NOT_FOUND:     return "чип не відповідає своїм ID";
    case CHIP_ERR_NOT_INIT:      return "драйвер не ініціалізовано";
    case CHIP_ERR_NO_DATA:       return "нових даних немає";
    default:                     return "невідомий код";
    }
}
