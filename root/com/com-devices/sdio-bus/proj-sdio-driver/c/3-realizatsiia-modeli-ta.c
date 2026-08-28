#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CCCR_SDIO_REV       0x00
#define CCCR_IO_ENABLE      0x02
#define CCCR_IO_READY       0x03
#define CCCR_INT_ENABLE     0x04
#define CCCR_INT_PENDING    0x05
#define CCCR_BUS_IF_CTRL    0x07

#define FBR_FUNC1_BASE      0x100
#define FBR_BLK_SIZE_L      (FBR_FUNC1_BASE + 0x10)
#define FBR_BLK_SIZE_H      (FBR_FUNC1_BASE + 0x11)

#define FUNC1_RX_FIFO_REG   0x00050
#define FUNC1_STATUS_REG    0x00054

/* ── 1. Емулятор апаратної частини SDIO-пристрою ─────────────────────────── */
typedef struct {
    uint8_t cccr[0x100];
    uint8_t func1_regs[0x20000];
    uint8_t rx_fifo[4096];
    size_t  rx_fifo_head;
    size_t  rx_fifo_tail;
    bool    dat1_irq_asserted;
} sdio_device_sim_t;

/* Обчислення контрольної суми CRC7 для кадру команд */
static uint8_t calc_crc7(const uint8_t *data, size_t len) {
    uint8_t crc = 0;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int b = 0; b < 8; ++b) {
            if (crc & 0x80)
                crc = (uint8_t)((crc << 1) ^ 0x12); /* Поліном x^7 + x^3 + 1 */
            else
                crc <<= 1;
        }
    }
    return (uint8_t)(crc >> 1);
}

void sdio_device_init(sdio_device_sim_t *dev) {
    memset(dev, 0, sizeof(*dev));
    dev->cccr[CCCR_SDIO_REV] = 0x32; /* SDIO 3.00, CCCR 2.00 */
    dev->cccr[CCCR_BUS_IF_CTRL] = 0x00; /* 1-бітний режим за замовчуванням */
}

/* Обробка команди прямого доступу CMD52 (1 байт) */
int sdio_device_cmd52(sdio_device_sim_t *dev, bool write, uint8_t func,
                      uint32_t addr, uint8_t val, uint8_t *resp_val) {
    if (func == 0) {
        if (addr >= sizeof(dev->cccr)) return -1;
        if (write) {
            if (addr == CCCR_IO_ENABLE) {
                dev->cccr[CCCR_IO_ENABLE] = val;
                dev->cccr[CCCR_IO_READY] |= (uint8_t)(val & 0xFE); /* Апаратна готовність */
            } else if (addr == CCCR_INT_ENABLE) {
                dev->cccr[CCCR_INT_ENABLE] = val;
            } else if (addr == CCCR_BUS_IF_CTRL) {
                dev->cccr[CCCR_BUS_IF_CTRL] = val;
            }
        }
        if (resp_val) *resp_val = dev->cccr[addr];
        return 0;
    } else if (func == 1) {
        if (addr >= sizeof(dev->func1_regs)) return -1;
        if (write) dev->func1_regs[addr] = val;
        if (resp_val) *resp_val = dev->func1_regs[addr];
        return 0;
    }
    return -1;
}

/* Обробка команди розширеного доступу CMD53 (пакети) */
int sdio_device_cmd53(sdio_device_sim_t *dev, bool write, uint8_t func,
                      bool block_mode, bool inc_addr, uint32_t addr,
                      uint8_t *buf, size_t len) {
    if (func != 1) return -1;

    if (!write) { /* Читання з пристрою в пам'ять хоста */
        if (!inc_addr && addr == FUNC1_RX_FIFO_REG) {
            /* Потоковий вивід із порту FIFO без зміни адреси */
            for (size_t i = 0; i < len; ++i) {
                if (dev->rx_fifo_tail != dev->rx_fifo_head) {
                    buf[i] = dev->rx_fifo[dev->rx_fifo_tail++];
                    if (dev->rx_fifo_tail >= sizeof(dev->rx_fifo)) dev->rx_fifo_tail = 0;
                } else {
                    buf[i] = 0x00; /* Заповнення нулями при спустошенні */
                }
            }
            /* Якщо черга порожня — скидаємо переривання на лінії DAT1 */
            if (dev->rx_fifo_tail == dev->rx_fifo_head) {
                dev->dat1_irq_asserted = false;
                dev->cccr[CCCR_INT_PENDING] &= (uint8_t)~0x02;
            }
            return 0;
        } else if (inc_addr) {
            /* Читання масиву пам'яті з автоінкрементом адреси */
            if (addr + len > sizeof(dev->func1_regs)) return -1;
            memcpy(buf, &dev->func1_regs[addr], len);
            return 0;
        }
    }
    return -1;
}

/* Додавання вхідного бездротового кадру в чергу FIFO */
void sdio_device_inject_packet(sdio_device_sim_t *dev, const uint8_t *pkt, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        dev->rx_fifo[dev->rx_fifo_head++] = pkt[i];
        if (dev->rx_fifo_head >= sizeof(dev->rx_fifo)) dev->rx_fifo_head = 0;
    }
    if (dev->cccr[CCCR_INT_ENABLE] & 0x02) {
        dev->cccr[CCCR_INT_PENDING] |= 0x02;
        dev->dat1_irq_asserted = true; /* Стягуємо лінію DAT1 до GND */
    }
}

/* ── 2. Драйвер хост-контролера та клієнтський модуль ─────────────────────── */
typedef struct {
    sdio_device_sim_t *target;
    bool host_locked;
    uint16_t func1_block_size;
} sdio_host_driver_t;

void sdio_claim_host(sdio_host_driver_t *drv) {
    drv->host_locked = true;
}

void sdio_release_host(sdio_host_driver_t *drv) {
    drv->host_locked = false;
}

int sdio_init_func1(sdio_host_driver_t *drv) {
    sdio_claim_host(drv);

    uint8_t rev = 0;
    sdio_device_cmd52(drv->target, false, 0, CCCR_SDIO_REV, 0, &rev);
    printf("[Host C] SDIO Spec Rev: 0x%02X\n", rev);

    /* 1. Активація живлення логіки Функції 1 */
    sdio_device_cmd52(drv->target, true, 0, CCCR_IO_ENABLE, 0x02, NULL);

    /* 2. Опитування прапорця готовності IO_READY */
    uint8_t ready = 0;
    for (int retry = 0; retry < 5; ++retry) {
        sdio_device_cmd52(drv->target, false, 0, CCCR_IO_READY, 0, &ready);
        if (ready & 0x02) break;
    }
    if (!(ready & 0x02)) {
        sdio_release_host(drv);
        return -1;
    }

    /* 3. Встановлення розміру блока 512 байтів */
    drv->func1_block_size = 512;
    sdio_device_cmd52(drv->target, true, 0, FBR_BLK_SIZE_L, 0x00, NULL);
    sdio_device_cmd52(drv->target, true, 0, FBR_BLK_SIZE_H, 0x02, NULL);

    /* 4. Дозвіл переривань для Функції 1 та Master Enable */
    sdio_device_cmd52(drv->target, true, 0, CCCR_INT_ENABLE, 0x03, NULL);

    printf("[Host C] Функція 1 готова, BlockSize=%u байтів, IRQ увімкнено\n",
           drv->func1_block_size);

    sdio_release_host(drv);
    return 0;
}

void sdio_poll_irq_and_service(sdio_host_driver_t *drv) {
    if (!drv->target->dat1_irq_asserted) return;

    sdio_claim_host(drv);
    uint8_t pending = 0;
    sdio_device_cmd52(drv->target, false, 0, CCCR_INT_PENDING, 0, &pending);

    if (pending & 0x02) {
        uint8_t packet_buffer[512];
        /* Зчитування 512-байтового блока через CMD53 Fixed Address */
        sdio_device_cmd53(drv->target, false, 1, true, false,
                          FUNC1_RX_FIFO_REG, packet_buffer, sizeof(packet_buffer));

        printf("[Host C IRQ] Зчитано мережевий кадр: \"%s\" (довжина %zu байтів)\n",
               (char*)packet_buffer, strlen((char*)packet_buffer));
    }
    sdio_release_host(drv);
}

int main(void) {
    sdio_device_sim_t dev;
    sdio_device_init(&dev);

    sdio_host_driver_t host = { .target = &dev, .host_locked = false };
    if (sdio_init_func1(&host) != 0) {
        printf("Помилка ініціалізації SDIO\n");
        return 1;
    }

    /* Симуляція надходження кадру Wi-Fi */
    const char *test_frame = "IEEE 802.11 Beacon: SSID=Lab_Network, Ch=6, RSSI=-42dBm";
    sdio_device_inject_packet(&dev, (const uint8_t*)test_frame, strlen(test_frame) + 1);

    /* Обробка запиту переривання */
    sdio_poll_irq_and_service(&host);

    return 0;
}
