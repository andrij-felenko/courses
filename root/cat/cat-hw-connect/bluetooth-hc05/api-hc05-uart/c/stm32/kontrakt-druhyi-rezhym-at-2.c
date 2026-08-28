#include <string.h>

// Те саме на HAL: тайм-аут відлічуємо системним тіком HAL_GetTick().
bool send_at(const char *cmd, char *resp, size_t cap, uint32_t timeout_ms) {
    // 1) вичитати «хвіст» минулої відповіді (тайм-аут 0 — доки є байти)
    uint8_t junk;
    while (HAL_UART_Receive(&huart1, &junk, 1, 0) == HAL_OK) { }
    __HAL_UART_CLEAR_OREFLAG(&huart1);   // і скинути прапорець переповнення

    // 2) надіслати команду + ОБОВ'ЯЗКОВІ \r\n
    HAL_UART_Transmit(&huart1, (uint8_t *)cmd, strlen(cmd), 100);
    HAL_UART_Transmit(&huart1, (uint8_t *)"\r\n", 2, 100);

    // 3) збирати відповідь, доки не побачимо кінець рядка або не вийде час
    size_t n = 0;
    uint32_t start = HAL_GetTick();                // мілісекунди від старту
    while (HAL_GetTick() - start < timeout_ms) {
        uint8_t c;
        if (HAL_UART_Receive(&huart1, &c, 1, 10) != HAL_OK) continue;
        if (n < cap - 1) resp[n++] = (char)c;
        if (c == '\n') {                           // рядок готовий
            resp[n] = '\0';
            return strstr(resp, "OK") != NULL;     // є "OK" → успіх
        }
    }
    resp[n] = '\0';
    return false;   // час вийшов, повного рядка так і не прийшло
}
