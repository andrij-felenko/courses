volatile char line[64];          // спільний сирий буфер (тому volatile)
volatile bool ready = false;     // прапорець «рядок готовий»
volatile uint8_t rx;             // сюди HAL кладе черговий прийнятий байт

// HAL кличе це з контексту переривання USART — верхня половина
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    static uint8_t i = 0;
    char c = (char)rx;               // байт уже в пам'яті — реентерабельно
    if (c == '\n') {
        line[i] = 0;
        ready = true;                // сигнал нижній половині
        i = 0;
    } else if (i < sizeof(line) - 1) {
        line[i++] = c;               // складаємо байти по одному
    }
    HAL_UART_Receive_IT(huart, (uint8_t *)&rx, 1);  // знову озброїти прийом
}

int main(void) {                 // нижня половина — тут можна ВСЕ
    HAL_Init(); MX_USART2_UART_Init();
    HAL_UART_Receive_IT(&huart2, (uint8_t *)&rx, 1);
    while (1) {
        if (!ready) continue;
        ready = false;
        char tmp[64];
        __disable_irq();
        strncpy(tmp, (const char *)line, sizeof(tmp)); // атомарний знімок буфера
        __enable_irq();
        char *tok = strtok(tmp, ",");   // strtok — але лише в одному місці!
        printf("%s\r\n", tok);          // друк — у main(), де безпечно
    }
}
