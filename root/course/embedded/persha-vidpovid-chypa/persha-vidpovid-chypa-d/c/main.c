/* Програмна модель кристала, у яку по черзі вносимо описані в статті
 * дефекти монтажу. Кожен сценарій має очікуваний вердикт — так модуль
 * валідації перевіряє сам себе, не потребуючи плати на столі. */
#include "bringup.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum {
    SIM_HEALTHY = 0,
    SIM_CHIP_ABSENT,        /* чип не пропаяний: ніхто не підтверджує адресу */
    SIM_SLOW_POR,           /* кремній прокидається пізніше, ніж ми починаємо питати */
    SIM_MISO_PULLUP,        /* CS не падає в нуль: на лінії лише резистор до VDD */
    SIM_SHORT_TO_GND,       /* крапля припою між лінією даних і полігоном землі */
    SIM_I2C_BUS_HANG,       /* слейв утримує SDA після скидання ведучого */
    SIM_SPI_MODE_MISMATCH,  /* хибний CPHA: біти зсунуто вліво */
    SIM_MOSI_BREAK,         /* мікротріщина на лінії запису */
    SIM_SCRATCHPAD_BRIDGE   /* злиті сусідні тригери конфігураційного регістра */
} sim_defect_t;

typedef struct {
    sim_defect_t defect;
    uint8_t      reg[256];
    uint32_t     clock_ms;  /* модельний час від подачі живлення */
    uint32_t     por_ms;    /* коли внутрішній автомат чипа справді прокидається */
    unsigned     reads;
    unsigned     writes;
} sim_chip_t;

static void sim_init(sim_chip_t *chip, sim_defect_t defect)
{
    memset(chip, 0, sizeof *chip);
    chip->defect = defect;
    chip->por_ms = (defect == SIM_SLOW_POR) ? 40u : 5u;
    chip->reg[0x75] = 0x68u;  /* WHO_AM_I: зашитий у кремній паспорт MPU-6050 */
    chip->reg[0x19] = 0x07u;  /* SMPLRT_DIV: робоче значення дільника частоти */
}

static bool sim_read(void *ctx, uint8_t reg, uint8_t *out)
{
    sim_chip_t *chip = (sim_chip_t *)ctx;
    uint8_t value;

    chip->reads++;

    switch (chip->defect) {
    case SIM_CHIP_ABSENT:
        return false;              /* адресу ніхто не підтвердив: NACK */
    case SIM_MISO_PULLUP:
        *out = 0xFFu;              /* вихід чипа у Z-стані, читаємо саму підтяжку */
        return true;
    case SIM_SHORT_TO_GND:
    case SIM_I2C_BUS_HANG:
        *out = 0x00u;              /* лінію тримає припій або завислий слейв */
        return true;
    default:
        break;
    }

    if (chip->clock_ms < chip->por_ms) {
        return false;              /* цифрове ядро ще під внутрішнім скиданням */
    }

    value = chip->reg[reg];

    if (chip->defect == SIM_SPI_MODE_MISMATCH) {
        /* Ведучий стробує на пів такту пізніше: старший біт губиться, решта
         * з'їжджає вліво, а знизу підтягується стан спокою лінії. */
        value = (uint8_t)(value << 1);
    }

    *out = value;
    return true;
}

static bool sim_write(void *ctx, uint8_t reg, uint8_t value)
{
    sim_chip_t *chip = (sim_chip_t *)ctx;

    chip->writes++;

    switch (chip->defect) {
    case SIM_CHIP_ABSENT:
        return false;
    case SIM_SHORT_TO_GND:
    case SIM_I2C_BUS_HANG:
        return false;              /* на притиснутій SDA не видати навіть умови СТАРТ */
    default:
        break;
    }

    if (chip->clock_ms < chip->por_ms) {
        return false;
    }

    if (chip->defect == SIM_MOSI_BREAK) {
        /* Периферія ведучого відтактувала кадр і рапортує успіх, але байт
         * до кристала не доїхав: регістр лишається старим. */
        return true;
    }

    if (chip->defect == SIM_SCRATCHPAD_BRIDGE) {
        const uint8_t pair = 0x30u;  /* злиті розряди 4 і 5 комірки конфігурації */
        if ((value & pair) != 0u) {
            value |= pair;
        }
    }

    chip->reg[reg] = value;
    return true;
}

static void sim_delay(void *ctx, uint32_t ms)
{
    ((sim_chip_t *)ctx)->clock_ms += ms;
}

typedef struct {
    const char      *title;
    sim_defect_t     defect;
    bringup_status_t expected;
} scenario_t;

static const scenario_t SCENARIOS[] = {
    { "Справна плата",                                  SIM_HEALTHY,           BRINGUP_OK              },
    { "Чип не пропаяний: NACK на адресу",               SIM_CHIP_ABSENT,       BRINGUP_NO_ANSWER       },
    { "Старт раніше за готовність кремнію (t_POR)",     SIM_SLOW_POR,          BRINGUP_NO_ANSWER       },
    { "CS не падає: на MISO сама підтяжка",             SIM_MISO_PULLUP,       BRINGUP_BUS_STUCK_HIGH  },
    { "Крапля припою: лінія даних на землі",            SIM_SHORT_TO_GND,      BRINGUP_BUS_STUCK_LOW   },
    { "Зависла шина I2C після скидання ведучого",       SIM_I2C_BUS_HANG,      BRINGUP_BUS_STUCK_LOW   },
    { "Хибний режим SPI: CPHA=1 замість 0",             SIM_SPI_MODE_MISMATCH, BRINGUP_BIT_SHIFT       },
    { "Мікротріщина на MOSI: запис не доходить",        SIM_MOSI_BREAK,        BRINGUP_WRITE_PATH_DEAD },
    { "Місток між розрядами конфігураційного регістра", SIM_SCRATCHPAD_BRIDGE, BRINGUP_SCRATCHPAD_BAD  },
};

int main(void)
{
    static const chip_config_t MPU6050 = {
        "InvenSense MPU-6050",
        0x75u,   /* WHO_AM_I */
        0x68u,   /* заводське значення */
        0x19u,   /* SMPLRT_DIV: вісім живих тригерів без побічних ефектів */
        15u,     /* t_POR із запасом для MEMS */
        5u,      /* спроб читання */
        2u       /* пауза між спробами, мс */
    };

    unsigned failures = 0u;
    unsigned i;

    printf("Первинна валідація %s на модельній платі\n", MPU6050.name);

    for (i = 0u; i < sizeof SCENARIOS / sizeof SCENARIOS[0]; ++i) {
        sim_chip_t chip;
        bus_driver_t bus;
        diagnostic_report_t report;
        bool matched;

        sim_init(&chip, SCENARIOS[i].defect);

        bus.read_reg = sim_read;
        bus.write_reg = sim_write;
        bus.delay_ms = sim_delay;
        bus.ctx = &chip;

        printf("\n[%u] %s\n", i + 1u, SCENARIOS[i].title);
        report = bringup_validate(&bus, &MPU6050);
        bringup_print_report(&report, &MPU6050);
        printf("  кадрів шини  : читань %u, записів %u; модельний час %u мс\n",
               chip.reads, chip.writes, chip.clock_ms);

        matched = (report.status == SCENARIOS[i].expected);
        if (!matched) {
            failures++;
            printf("  !! класифікатор помилився: чекали \"%s\"\n",
                   bringup_status_text(SCENARIOS[i].expected));
        }
    }

    printf("\nСценаріїв: %u, розбіжностей класифікації: %u\n",
           (unsigned)(sizeof SCENARIOS / sizeof SCENARIOS[0]), failures);
    return failures == 0u ? EXIT_SUCCESS : EXIT_FAILURE;
}
