extern UART_HandleTypeDef huart1;        // SPP-модуль (HC-05) висить на UART1

static char     line[64];                // буфер для одного рядка-команди
static uint8_t  len = 0;                 // скільки символів уже зібрано
static uint8_t  rx;                      // приймальня на ОДИН байт
static volatile uint8_t ready = 0;       // рядок зібрано — цикл його забере

// 1. Переривання лише складає байти: чекати тут нема на що
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    char c = (char) rx;

    if (c == '\n' || c == '\r') {            // кінець рядка → команда готова
        if (len > 0) { line[len] = '\0'; ready = 1; }
    } else if (len < sizeof(line) - 1) {     // звичайний символ — у буфер
        line[len++] = c;
    } else {
        len = 0;                             // переповнення: скинути сміття
    }

    HAL_UART_Receive_IT(huart, &rx, 1);      // одразу замовити наступний байт
}

int main(void)
{
    HAL_Init();
    MX_USART1_UART_Init();
    HAL_UART_Receive_IT(&huart1, &rx, 1);    // запустити ланцюжок прийому

    while (1) {
        if (ready) { HandleCommand(line); len = 0; ready = 0; }

        // 2. Решта циклу біжить ЩОтакту, бо ми ніде не блокувалися
        UpdateMotors();
        CheckFailsafe();
    }
}
