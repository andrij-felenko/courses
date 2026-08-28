/* Завести SiK у режим AT-команд і прочитати версію.
   uart_write/uart_read_line/delay_ms — платформні обгортки UART. */
#include <string.h>

int sik_enter_at_mode(void) {
    char line[64];

    delay_ms(1100);             /* guard time ПЕРЕД: ≥1 с тиші        */
    uart_write("+++", 3);       /* без CR/LF! саме три плюси          */
    delay_ms(1100);             /* guard time ПІСЛЯ: ще ≥1 с тиші     */

    if (uart_read_line(line, sizeof line, 500) <= 0)
        return -1;              /* модем не відповів                  */
    if (strncmp(line, "OK", 2) != 0)
        return -2;              /* очікували "OK" — не той стан/швидкість */

    uart_write("ATI\r", 4);     /* запит версії прошивки              */
    uart_read_line(line, sizeof line, 500);   /* напр. "SiK 2.0 on HM-TRP" */
    /* ... розібрати рядок версії за потреби ... */

    uart_write("ATZ\r", 4);     /* перезавантажити → назад у прозорий режим */
    return 0;
}
