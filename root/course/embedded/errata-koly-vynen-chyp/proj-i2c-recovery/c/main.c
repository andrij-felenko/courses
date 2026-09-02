#include "delay.h"
#include "i2c1.h"
#include "i2c_recovery.h"

#include "stm32f10x.h"

#define SENSOR_ADDR    0x68U      /* давач на шині зв'язкового модуля */
#define REG_WHO_AM_I   0x75U      /* регістр-візитівка: значення відоме наперед */
#define BUS_SPEED_HZ   100000U

/* Лічильники навмисно volatile і глобальні: о другій ночі єдиний спосіб побачити
   картину — спинити налагоджувач і подивитися, скільки разів шину рятували. */
static volatile struct {
    uint32_t reads_ok;
    uint32_t nacks;
    uint32_t recoveries;
    uint32_t recovery_pulses;
    uint32_t fatal;
    uint8_t  last_who_am_i;
} g_stats;

static void bring_bus_up(void) {
    const i2c_bus_report_t report = i2c1_bus_recover();

    g_stats.recoveries++;
    g_stats.recovery_pulses += report.pulses;

    if (report.status != I2C_BUS_OK) {
        /* Модуль лишився у скиданні. Далі має йти людина з осцилографом:
           програмно з короткого замикання шину не витягнути. */
        g_stats.fatal++;
        return;
    }

    i2c1_init(BUS_SPEED_HZ);
}

int main(void) {
    delay_init();

    /* Починаємо з відновлення, ще не спробувавши жодної транзакції: скидання від
       сторожового таймера посеред читання байта лишає ведений чип із притиснутою
       SDA, і перше ж звертання стане в BUSY. */
    bring_bus_up();

    for (;;) {
        uint8_t who = 0U;
        const i2c_status_t st = i2c1_read_register(SENSOR_ADDR, REG_WHO_AM_I, &who);

        switch (st) {
        case I2C_OK:
            g_stats.reads_ok++;
            g_stats.last_who_am_i = who;
            break;

        case I2C_ERR_NACK:
            /* Шина жива, просто ніхто не озвався на цю адресу — рятувати нічого */
            g_stats.nacks++;
            break;

        case I2C_ERR_BUSY:
        case I2C_ERR_TIMEOUT:
        case I2C_ERR_BUS:
        default:
            bring_bus_up();
            break;
        }

        delay_us(100000U);   /* 100 мс між опитуваннями */
    }
}
