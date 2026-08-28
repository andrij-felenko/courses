#include <unistd.h>
#include <stdint.h>

/* Програмна послідовність відновлення шини (Bus Recovery Sequence) */
void i2c_bus_recovery_sequence(void (*set_scl)(int), int (*get_sda)(void), void (*set_sda)(int), void (*delay_us)(int)) {
    /* 1. Переконуємося, що SDA відпущено ведучим */
    set_sda(1);
    delay_us(5);

    /* 2. Якщо лінія SDA притягнута веденим до 0, генеруємо до 9 тактів SCL */
    for (int i = 0; i < 9; i++) {
        if (get_sda() == 1) {
            break; /* Ведений відпустив лінію SDA */
        }
        set_scl(0);
        delay_us(5);
        set_scl(1);
        delay_us(5);
    }

    /* 3. Формуємо сигнал STOP: перехід SDA з 0 в 1 при високому SCL */
    set_sda(0);
    delay_us(5);
    set_scl(1);
    delay_us(5);
    set_sda(1);
    delay_us(5);
}
