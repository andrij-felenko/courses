#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define RTC_I2C_ADDR         0x68

/* Адреси основних регістрів */
#define RTC_REG_SECONDS      0x00
#define RTC_REG_MINUTES      0x01
#define RTC_REG_HOURS        0x02
#define RTC_REG_DAY_OF_WEEK  0x03
#define RTC_REG_DATE         0x04
#define RTC_REG_MONTH        0x05
#define RTC_REG_YEAR         0x06
#define RTC_REG_ALARM1_SEC   0x07
#define RTC_REG_CONTROL      0x0E
#define RTC_REG_STATUS       0x0F
#define RTC_REG_AGING_OFFSET 0x10
#define RTC_REG_TEMP_MSB     0x11
#define RTC_REG_TEMP_LSB     0x12

/* Біти статусу та контролю */
#define RTC_STATUS_OSF       (1 << 7) /* Прапорець зупинки кварцу */
#define RTC_CTRL_INTCN       (1 << 2) /* Керування виводом INT */
#define RTC_CTRL_A1IE        (1 << 0) /* Дозвіл переривання Alarm 1 */

/* Структура для зберігання календарного часу */
typedef struct {
    uint16_t year;       /* Повний рік, наприклад 2026 */
    uint8_t  month;      /* 1..12 */
    uint8_t  day;        /* 1..31 */
    uint8_t  day_of_week;/* 1..7 (1 = Понеділок) */
    uint8_t  hours;      /* 0..23 */
    uint8_t  minutes;    /* 0..59 */
    uint8_t  seconds;    /* 0..59 */
} rtc_datetime_t;

/* Функції апаратного рівня (HAL) I2C */
typedef bool (*rtc_i2c_read_fn)(uint8_t dev_addr, uint8_t reg_addr, uint8_t *data, size_t len);
typedef bool (*rtc_i2c_write_fn)(uint8_t dev_addr, uint8_t reg_addr, const uint8_t *data, size_t len);

typedef struct {
    rtc_i2c_read_fn  read;
    rtc_i2c_write_fn write;
    uint8_t          addr;
} rtc_handle_t;

/* Допоміжні функції BCD конвертації */
static inline uint8_t rtc_bcd_to_bin(uint8_t bcd) {
    return (uint8_t)(((bcd >> 4) * 10) + (bcd & 0x0F));
}

static inline uint8_t rtc_bin_to_bcd(uint8_t bin) {
    return (uint8_t)(((bin / 10) << 4) | (bin % 10));
}

/* Ініціалізація та перевірка прапорця цілісності часу */
bool rtc_init(rtc_handle_t *rtc, rtc_i2c_read_fn r_fn, rtc_i2c_write_fn w_fn) {
    if (!rtc || !r_fn || !w_fn) return false;
    rtc->read = r_fn;
    rtc->write = w_fn;
    rtc->addr = RTC_I2C_ADDR;

    uint8_t status = 0;
    if (!rtc->read(rtc->addr, RTC_REG_STATUS, &status, 1)) {
        return false;
    }

    /* Якщо прапорець OSF встановлено — живлення скидалося */
    if (status & RTC_STATUS_OSF) {
        return false; /* Годинник потребує первинного встановлення часу */
    }
    return true;
}

/* Атомарне зчитування дати й часу пакетом */
bool rtc_get_datetime(rtc_handle_t *rtc, rtc_datetime_t *dt) {
    if (!rtc || !dt) return false;

    uint8_t buf[7];
    /* Пакетне зчитування 7 байтів починаючи з регістра SECONDS */
    if (!rtc->read(rtc->addr, RTC_REG_SECONDS, buf, 7)) {
        return false;
    }

    dt->seconds     = rtc_bcd_to_bin(buf[0] & 0x7F);
    dt->minutes     = rtc_bcd_to_bin(buf[1] & 0x7F);
    dt->hours       = rtc_bcd_to_bin(buf[2] & 0x3F); /* 24-годинний формат */
    dt->day_of_week = buf[3] & 0x07;
    dt->day         = rtc_bcd_to_bin(buf[4] & 0x3F);
    dt->month       = rtc_bcd_to_bin(buf[5] & 0x1F);
    
    /* Облік століття (Century bit у 7-му біті регістра місяця) */
    uint16_t century = (buf[5] & 0x80) ? 2100 : 2000;
    dt->year        = century + rtc_bcd_to_bin(buf[6]);

    return true;
}

/* Запис нового часу та очищення прапорця OSF */
bool rtc_set_datetime(rtc_handle_t *rtc, const rtc_datetime_t *dt) {
    if (!rtc || !dt) return false;
    if (dt->seconds > 59 || dt->minutes > 59 || dt->hours > 23 ||
        dt->day == 0 || dt->day > 31 || dt->month == 0 || dt->month > 12) {
        return false;
    }

    uint8_t buf[7];
    buf[0] = rtc_bin_to_bcd(dt->seconds);
    buf[1] = rtc_bin_to_bcd(dt->minutes);
    buf[2] = rtc_bin_to_bcd(dt->hours); /* Біт 12/24 = 0 (24h) */
    buf[3] = dt->day_of_week & 0x07;
    buf[4] = rtc_bin_to_bcd(dt->day);
    
    uint8_t century_flag = (dt->year >= 2100) ? 0x80 : 0x00;
    buf[5] = rtc_bin_to_bcd(dt->month) | century_flag;
    buf[6] = rtc_bin_to_bcd((uint8_t)(dt->year % 100));

    /* Пакетний запис регістрів часу */
    if (!rtc->write(rtc->addr, RTC_REG_SECONDS, buf, 7)) {
        return false;
    }

    /* Очищення прапорця OSF у регістрі статусу */
    uint8_t status = 0;
    if (rtc->read(rtc->addr, RTC_REG_STATUS, &status, 1)) {
        status &= (uint8_t)(~RTC_STATUS_OSF);
        rtc->write(rtc->addr, RTC_REG_STATUS, &status, 1);
    }
    return true;
}

/* Зчитування внутрішньої температури TCXO (°C з точністю 0.25 °C) */
bool rtc_get_temperature(rtc_handle_t *rtc, float *temp) {
    if (!rtc || !temp) return false;

    uint8_t raw[2];
    if (!rtc->read(rtc->addr, RTC_REG_TEMP_MSB, raw, 2)) {
        return false;
    }

    int8_t temp_msb = (int8_t)raw[0];
    uint8_t temp_lsb = (raw[1] >> 6) & 0x03; /* Старші 2 біти LSB дають 0.25 °C */

    *temp = (float)temp_msb + ((float)temp_lsb * 0.25f);
    return true;
}

/* Встановлення будильника на точний час (щоденне спрацьовування) */
bool rtc_set_daily_alarm(rtc_handle_t *rtc, uint8_t hours, uint8_t minutes, uint8_t seconds) {
    if (!rtc || hours > 23 || minutes > 59 || seconds > 59) return false;

    uint8_t alarm_buf[4];
    alarm_buf[0] = rtc_bin_to_bcd(seconds);       /* A1M1 = 0: порівнювати секунди */
    alarm_buf[1] = rtc_bin_to_bcd(minutes);       /* A1M2 = 0: порівнювати хвилини */
    alarm_buf[2] = rtc_bin_to_bcd(hours);         /* A1M3 = 0: порівнювати години */
    alarm_buf[3] = 0x80;                          /* A1M4 = 1: маскувати дату (щодня) */

    if (!rtc->write(rtc->addr, RTC_REG_ALARM1_SEC, alarm_buf, 4)) {
        return false;
    }

    /* Дозвіл виходу переривання INTCN та Alarm 1 */
    uint8_t ctrl = 0;
    if (!rtc->read(rtc->addr, RTC_REG_CONTROL, &ctrl, 1)) return false;
    ctrl |= (RTC_CTRL_INTCN | RTC_CTRL_A1IE);
    return rtc->write(rtc->addr, RTC_REG_CONTROL, &ctrl, 1);
}
