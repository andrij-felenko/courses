#include "i2c_scan.h"

#include <string.h>

/* Стільки апаратних збоїв поспіль — і далі стукати немає сенсу:
   на розваленій фізиці решта проходу однаково нічого не скаже. */
#define ERROR_STREAK_LIMIT 4u

/* Реальна плата має одиниці пристроїв на шині, а не десятки. */
#define SANE_DEVICE_LIMIT 8u

/* Одна спроба й 5 мс на кадр: NACK повертається швидко, а більший таймаут
   перетворив би прохід на 112 адрес у хвилини очікування. */
#define PROBE_TRIALS  1u
#define PROBE_TIMEOUT 5u

static void drop_error_state(I2C_HandleTypeDef *bus)
{
    /* NACK від порожньої адреси HAL позначає прапорцем AF — для сканера це
       штатна відповідь шини, а не поломка. Не прибереш залишковий стан —
       наступна проба впаде ще до виставляння START. */
    __HAL_I2C_CLEAR_FLAG(bus, I2C_FLAG_AF);
    bus->ErrorCode = HAL_I2C_ERROR_NONE;
    if (HAL_I2C_GetState(bus) == HAL_I2C_STATE_ERROR) {
        bus->State = HAL_I2C_STATE_READY;
    }
}

i2c_probe_t i2c_probe(I2C_HandleTypeDef *bus, uint8_t addr7)
{
    if (addr7 < I2C_ADDR_FIRST || addr7 > I2C_ADDR_LAST) {
        return I2C_PROBE_ERROR; /* службовий діапазон: стукати туди не можна */
    }

    /* HAL чекає ВЖЕ ЗСУНУТИЙ 8-бітний байт кадру. Це та сама пастка
       «7 проти 8 біт», але тут зсув робимо ми самі й рівно один раз. */
    const uint16_t dev_addr = (uint16_t)((uint16_t)addr7 << 1);

    const HAL_StatusTypeDef st =
        HAL_I2C_IsDeviceReady(bus, dev_addr, PROBE_TRIALS, PROBE_TIMEOUT);
    const uint32_t err = HAL_I2C_GetError(bus);
    drop_error_state(bus);

    if (st == HAL_OK) {
        return I2C_PROBE_ACK;
    }
    if (st == HAL_BUSY || st == HAL_TIMEOUT) {
        /* Кадр навіть не почався або застряг: хтось тримає SDA чи SCL
           у нулі — сам ведений, зупинений налагоджувачем, або коротке. */
        return I2C_PROBE_BUSY;
    }
    if ((err & (HAL_I2C_ERROR_BERR | HAL_I2C_ERROR_ARLO | HAL_I2C_ERROR_OVR)) != 0u) {
        return I2C_PROBE_ERROR;
    }
    return I2C_PROBE_NACK; /* HAL_ERROR і самий лише AF: адреса порожня */
}

bool i2c_scan(I2C_HandleTypeDef *bus, i2c_scan_report_t *report)
{
    memset(report, 0, sizeof *report);

    /* Якщо шина зайнята ще до першого START — сканувати нічого. Апаратний
       блок бачить SDA у нулі, вважає передачу чужою й START не видасть. */
    if (__HAL_I2C_GET_FLAG(bus, I2C_FLAG_BUSY) != RESET) {
        report->bus_stuck = true;
        return false;
    }

    uint8_t streak = 0;
    for (uint8_t addr = I2C_ADDR_FIRST; addr <= I2C_ADDR_LAST; ++addr) {
        const i2c_probe_t probe = i2c_probe(bus, addr);
        report->probed++;

        switch (probe) {
        case I2C_PROBE_ACK: {
            i2c_device_t *slot = &report->found[report->found_count++];
            slot->addr7 = addr;
            slot->write_byte = (uint8_t)(addr << 1);
            slot->read_byte = (uint8_t)((addr << 1) | 1u);
            streak = 0;
            break;
        }
        case I2C_PROBE_NACK:
            streak = 0;
            break;
        case I2C_PROBE_BUSY:
            report->bus_stuck = true;
            return false;
        case I2C_PROBE_ERROR:
        default:
            report->errors++;
            if (++streak >= ERROR_STREAK_LIMIT) {
                report->bus_stuck = true;
                return false;
            }
            break;
        }

        /* Пауза між кадрами: слабка підтяжка піднімає лінію не миттєво,
           а START по не піднятій SDA — це вже арбітражна помилка ARLO. */
        HAL_Delay(1);
    }
    return true;
}

bool i2c_scan_looks_fake(const i2c_scan_report_t *report)
{
    return report->found_count > SANE_DEVICE_LIMIT;
}
