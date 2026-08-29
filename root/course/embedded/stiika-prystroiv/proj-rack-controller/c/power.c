/* Керування силовими лініями слота через символьний інтерфейс GPIO ядра (uAPI v2). */
#include "power.h"

#include <fcntl.h>
#include <linux/gpio.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

/* Релейна плата слота — це розширювач на шині I2C (PCF8574 і подібні реєструються
   в ядрі власним gpiochip), тому udev дає симлінк на КОЖЕН слот окремо, а зміщення
   ліній усередині чипа фіксовані: 0 — силовий ключ, 1 — ключ BOOT0. */
#define LINE_VCC   0u
#define LINE_BOOT0 1u

#define BIT_VCC   (1ULL << LINE_VCC)
#define BIT_BOOT0 (1ULL << LINE_BOOT0)

void rack_power_init(rack_power_t *pwr)
{
    pwr->lines_fd = -1;
}

rack_status_t rack_power_open(rack_power_t *pwr, int slot_id)
{
    char path[64];
    snprintf(path, sizeof path, "/dev/dut-slot-%02d-pwr", slot_id);

    int chip_fd = open(path, O_RDWR | O_CLOEXEC);
    if (chip_fd < 0) {
        fprintf(stderr, "слот %02d: не відкривається %s: %s\n", slot_id, path, strerror(errno));
        return RACK_FAIL;
    }

    struct gpio_v2_line_request req;
    memset(&req, 0, sizeof req);
    req.offsets[0] = LINE_VCC;
    req.offsets[1] = LINE_BOOT0;
    req.num_lines = 2;
    snprintf(req.consumer, sizeof req.consumer, "rack-slot-%02d", slot_id);
    req.config.flags = GPIO_V2_LINE_FLAG_OUTPUT;

    /* Початкові рівні задаємо тим самим запитом: ядро зробить лінії виходами вже
       з нулем. Інакше між зміною напрямку і першим записом плата ловить короткий
       імпульс живлення — і ми ловимо чужий, недоладний банер завантаження. */
    req.config.num_attrs = 1;
    req.config.attrs[0].attr.id = GPIO_V2_LINE_ATTR_ID_OUTPUT_VALUES;
    req.config.attrs[0].attr.values = 0;
    req.config.attrs[0].mask = BIT_VCC | BIT_BOOT0;

    if (ioctl(chip_fd, GPIO_V2_GET_LINE_IOCTL, &req) < 0) {
        fprintf(stderr, "слот %02d: GPIO_V2_GET_LINE: %s\n", slot_id, strerror(errno));
        close(chip_fd);
        return RACK_FAIL;
    }

    /* Далі чип не потрібен: лінії за нами тримає саме дескриптор запиту,
       і ядро віддасть їх іншому процесу лише коли ми його закриємо. */
    close(chip_fd);
    pwr->lines_fd = req.fd;
    return RACK_OK;
}

static rack_status_t set_lines(rack_power_t *pwr, uint64_t mask, uint64_t bits)
{
    if (pwr->lines_fd < 0) {
        fprintf(stderr, "спроба керувати живленням незахопленого слота\n");
        return RACK_FAIL;
    }

    struct gpio_v2_line_values vals;
    memset(&vals, 0, sizeof vals);
    vals.mask = mask; /* маска каже ядру чіпати лише названі лінії, друга лишається як була */
    vals.bits = bits;

    if (ioctl(pwr->lines_fd, GPIO_V2_LINE_SET_VALUES_IOCTL, &vals) < 0) {
        fprintf(stderr, "GPIO_V2_LINE_SET_VALUES: %s\n", strerror(errno));
        return RACK_FAIL;
    }
    return RACK_OK;
}

rack_status_t rack_power_vcc(rack_power_t *pwr, bool on)
{
    return set_lines(pwr, BIT_VCC, on ? BIT_VCC : 0);
}

rack_status_t rack_power_boot0(rack_power_t *pwr, bool high)
{
    return set_lines(pwr, BIT_BOOT0, high ? BIT_BOOT0 : 0);
}

void rack_power_close(rack_power_t *pwr)
{
    if (pwr->lines_fd < 0) {
        return;
    }
    /* Знеструмлюємо явно ДО закриття: після звільнення ліній їхній стан визначає
       драйвер розширювача, а не ми, і слот міг би лишитися під напругою. */
    (void)set_lines(pwr, BIT_VCC | BIT_BOOT0, 0);
    close(pwr->lines_fd);
    pwr->lines_fd = -1;
}
