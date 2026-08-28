volatile uint8_t  buf[64];        // кільцевий буфер
volatile uint8_t  head = 0, tail = 0;   // індекси: пише переривання, читає main
static   uint8_t  rx;             // куди HAL кладе черговий байт

// верхня половина: HAL кличе це з переривання, коли байт прийнято
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    uint8_t next = (head + 1) % sizeof(buf);
    if (next != tail) {           // є місце?
        buf[head] = rx;
        head = next;
    }                             // переповнення — мовчки відкидаємо
    HAL_UART_Receive_IT(huart, &rx, 1);   // одразу замовити наступний байт
}

int main(void) {
    /* … HAL_Init(), MX_USART2_UART_Init() … */
    HAL_UART_Receive_IT(&huart2, &rx, 1); // запустити ланцюжок прийому
    while (1) {                   // нижня половина
        while (tail != head) {    // поки є непрочитане
            uint8_t b = buf[tail];
            tail = (tail + 1) % sizeof(buf);
            parse(b);             // розбір, друк, математика — без поспіху
        }
    }
}
