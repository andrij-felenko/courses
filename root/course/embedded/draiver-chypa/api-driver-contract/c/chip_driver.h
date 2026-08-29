/*
 * Публічний контракт драйвера акселерометра: повний життєвий цикл від
 * розпізнавання мікросхеми до вимкнення.
 *
 * Дескриптор розміщує викликач — у .bss, у пулі обʼєктів чи на стеку
 * ініціалізатора. Драйвер не має ані статичних змінних стану, ані власних
 * потоків, ані мʼютексів, і ніколи не викликає malloc().
 */
#ifndef CHIP_DRIVER_H
#define CHIP_DRIVER_H

#include <stdint.h>
#include <stdbool.h>

#include "chip_bus.h"
#include "chip_status.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Глибина апаратної черги: 32 відліки по 6 байтів. */
#define CHIP_FIFO_DEPTH     32u
#define CHIP_SAMPLE_BYTES   6u

/*
 * Дескриптор одного екземпляра мікросхеми. Чотири однакові датчики на двох
 * різних шинах — це чотири такі структури: адреса й хендл платформи лежать
 * усередині, спільного стану між ними немає.
 */
typedef struct {
    const chip_bus_ops_t *bus_ops;         /* транспорт платформи (не володіє) */
    void                 *user_ctx;        /* непрозорий хендл платформи */
    float                 lsb_to_ms2;      /* ціна молодшого розряду, м/с² */
    uint8_t               dev_addr;        /* 7-бітна адреса на шині */
    uint8_t               range_g;         /* чинний діапазон: 2, 4, 8, 16 */
    uint8_t               shadow_ctrl1;    /* тінь CTRL_REG1 — RMW без читання шини */
    uint8_t               shadow_ctrl4;    /* тінь CTRL_REG4 */
    uint8_t               shadow_ctrl5;    /* тінь CTRL_REG5 */
    bool                  is_initialized;
    volatile bool         sample_pending;  /* виставляє ISR лінії DRDY */
} chip_dev_t;

CHIP_STATIC_ASSERT(sizeof(chip_dev_t) <= 128, "дескриптор мусить лишатися дешевим для Cortex-M0+");
CHIP_STATIC_ASSERT(_Alignof(chip_dev_t) >= 4, "структура вирівнюється за 32-бітною межею");

/* Відлік у одиницях SI: прикладний код ціни розряду за даташитом не рахує. */
typedef struct {
    float x;  /* м/с² */
    float y;  /* м/с² */
    float z;  /* м/с² */
} chip_axes_data_si_t;

/*
 * Сирий буфер під пакетне вичитування черги. Вирівняний за рядком кешу,
 * розмір кратний йому ж — щоб інвалідація D-Cache після DMA не зачепила
 * сусідніх змінних. Розміщує його викликач, у пам'яті, доступній DMA.
 */
typedef struct {
    CHIP_DMA_ALIGNED uint8_t raw[CHIP_FIFO_DEPTH * CHIP_SAMPLE_BYTES];
} chip_fifo_buf_t;

CHIP_STATIC_ASSERT(sizeof(chip_fifo_buf_t) % CHIP_CACHE_LINE == 0,
                   "розмір DMA-буфера мусить бути кратним рядку кешу");

typedef struct {
    uint8_t count;      /* скільки відліків насправді розкодовано */
    bool    overrun;    /* черга переповнилася, найстаріші відліки втрачено */
    bool    watermark;  /* досягнуто порогу FTH */
} chip_fifo_status_t;

/*
 * Ініціалізація: перевіряє аргументи, впізнає мікросхему за WHO_AM_I,
 * піднімає заводські коефіцієнти з NVM і виставляє відомий робочий режим —
 * 100 Гц, високий роздільний, BDU увімкнено, діапазон ±2 g.
 * Дескриптор перед викликом обнуляти не треба: функція робить це сама.
 */
chip_status_t chip_init(chip_dev_t *dev,
                        const chip_bus_ops_t *bus_ops,
                        void *user_ctx,
                        uint8_t dev_addr);

/* Скидання в заводський стан. Після нього дескриптор вважається
 * неініціалізованим — щоб знову читати, потрібен chip_init(). */
chip_status_t chip_soft_reset(chip_dev_t *dev);

/* Перепідняття коефіцієнтів підстроювання з NVM із перевіркою, що вони
 * справді піднялися. CHIP_ERR_CALIBRATION_INVALID — вміст NVM пошкоджено. */
chip_status_t chip_reload_trim(chip_dev_t *dev);

/* Діапазон: 2, 4, 8 або 16 g. Заразом перераховує ціну розряду. */
chip_status_t chip_set_range(chip_dev_t *dev, uint8_t range_g);

/* Частота відліків: 1, 10, 25, 50, 100, 200 або 400 Гц. */
chip_status_t chip_set_odr_hz(chip_dev_t *dev, uint16_t odr_hz);

/*
 * Один відлік у SI. Не блокує: якщо ZYXDA скинутий, повертає
 * CHIP_ERR_DATA_NOT_READY. Читання пакетне, під BDU — три осі належать
 * одному моментові часу, а не двом сусіднім.
 */
chip_status_t chip_read_sample_si(chip_dev_t *dev, chip_axes_data_si_t *data_si);

/* Апаратна черга: увімкнути (режим Stream) або вимкнути (Bypass). */
chip_status_t chip_fifo_enable(chip_dev_t *dev, bool enable);

/*
 * Вичитує чергу однією пакетною транзакцією через scratch і розкладає
 * відліки в out[] у SI. max_samples обмежує обидва масиви.
 */
chip_status_t chip_fifo_read(chip_dev_t *dev,
                             chip_fifo_buf_t *scratch,
                             chip_axes_data_si_t *out,
                             uint8_t max_samples,
                             chip_fifo_status_t *fifo_status);

/*
 * Вбудований самотест: порівнює відліки з увімкненим і вимкненим збудженням
 * і перевіряє, що різниця по кожній осі влучає в паспортне вікно
 * 17…360 мg. Блокує на ~1 с; викликати лише на старті, не в циклі.
 */
chip_status_t chip_self_test(chip_dev_t *dev);

/* Перевести в режим спокою (ODR = 0). */
chip_status_t chip_shutdown(chip_dev_t *dev);

/*
 * Єдина функція, яку можна викликати з обробника переривання лінії DRDY:
 * жодної шинної транзакції й жодної затримки — лише позначка в дескрипторі.
 */
void chip_drdy_from_isr(chip_dev_t *dev);

/* Чи є непрочитаний відлік — теж без звертання до шини. */
bool chip_sample_pending(const chip_dev_t *dev);

#ifdef __cplusplus
}
#endif

#endif /* CHIP_DRIVER_H */
