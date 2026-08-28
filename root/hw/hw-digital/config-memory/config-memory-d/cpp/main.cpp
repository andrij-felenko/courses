#include <stdint.h>
#include <stdbool.h>

// Чекаємо, поки FPGA наповнить свою (летку) конфігураційну пам'ять.
// Поки DONE=0 — кристал іще без схеми: комірки заповнюються, виходи невизначені.
bool wait_fpga_ready(uint32_t timeout_ms)
{
    uint32_t t = 0;
    while (!gpio_read(FPGA_DONE_PIN)) {      // DONE підніметься, коли всі комірки залито
        if (t >= timeout_ms) {               // не дочекалися — конфігурація зірвалася:
            report_error(ERR_CFG_FAILED);    //   порожнє чи побите джерело бітстріму
            return false;                    //   (працювати з чипом НЕ можна)
        }
        delay_ms(1);
        ++t;
    }
    return true;                              // DONE=1 — пам'ять повна, схема існує, чип готовий
}
