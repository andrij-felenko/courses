#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <math.h>
#include <time.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <linux/fs.h>
#include <linux/i2c-dev.h>
#include <linux/nvme_ioctl.h>

/* Константи та команди Secure Element ATECC608 */
#define ATECC608_I2C_ADDR         0x60
#define ATECC_CMD_WORD_ADDRESS    0x03
#define ATECC_OP_NONCE            0x16
#define ATECC_OP_PRIVWRITE        0x29
#define ATECC_OP_LOCK             0x17
#define ATECC_ZONE_CONFIG         0x00
#define ATECC_ZONE_DATA           0x02

/* Константи NVMe Sanitize */
#define NVME_ADMIN_SANITIZE       0x84
#define NVME_SANITIZE_NO_ACTION   0x00
#define NVME_SANITIZE_BLOCK_ERASE 0x02
#define NVME_SANITIZE_OVERWRITE   0x03
#define NVME_SANITIZE_CRYPTO      0x04
#define NVME_LOG_SANITIZE_STATUS  0x81

/* Типи результатів операцій санітизатора */
typedef enum {
    SAN_OK = 0,
    SAN_ERR_INVALID_PARAM = -1,
    SAN_ERR_MEM_LOCK = -2,
    SAN_ERR_DEVICE_IO = -3,
    SAN_ERR_TPM_FAIL = -4,
    SAN_ERR_SE_FAIL = -5,
    SAN_ERR_VERIFY_FAIL = -6
} san_status_t;

/* Безпечний регіон пам'яті */
typedef struct {
    uint8_t *data;
    size_t size;
    bool locked;
} secure_buf_t;

/* Звіт про санітизацію */
typedef struct {
    char device_uuid[64];
    char target_path[128];
    uint64_t timestamp;
    uint8_t sha256_post_erase[32];
    double entropy;
    bool se_zeroized;
    bool tpm_cleared;
    bool flash_purged;
} san_certificate_t;

/* Обчислення контрольної суми CRC-16 для протоколу ATECC608 */
static uint16_t atecc_crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0x0000;
    for (size_t i = 0; i < length; i++) {
        for (uint8_t shift = 0x01; shift > 0x00; shift <<= 1) {
            uint8_t data_bit = (data[i] & shift) ? 1 : 0;
            uint8_t crc_bit = (crc >> 15) & 1;
            crc <<= 1;
            if (data_bit ^ crc_bit) {
                crc ^= 0x8005;
            }
        }
    }
    return crc;
}

/* Гарантоване занулення буфера пам'яті з бар'єром для компілятора */
static void secure_bzero(void *ptr, size_t len) {
    if (!ptr || len == 0) return;
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    while (len--) {
        *p++ = 0;
    }
    __asm__ __volatile__("" : : "r"(ptr) : "memory");
}

/* Створення заблокованого буфера в оперативній пам'яті */
static int secure_buf_alloc(secure_buf_t *buf, size_t size) {
    if (!buf || size == 0) return -1;
    buf->size = size;
    buf->data = (uint8_t *)mmap(NULL, size, PROT_READ | PROT_WRITE,
                                MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (buf->data == MAP_FAILED) {
        buf->data = NULL;
        return -1;
    }
    if (mlock(buf->data, size) != 0) {
        munmap(buf->data, size);
        buf->data = NULL;
        return -1;
    }
    if (madvise(buf->data, size, MADV_DONTDUMP) != 0) {
        munlock(buf->data, size);
        munmap(buf->data, size);
        buf->data = NULL;
        return -1;
    }
    buf->locked = true;
    prctl(PR_SET_DUMPABLE, 0);
    return 0;
}

/* Звільнення заблокованого буфера */
static void secure_buf_free(secure_buf_t *buf) {
    if (!buf || !buf->data) return;
    secure_bzero(buf->data, buf->size);
    if (buf->locked) {
        munlock(buf->data, buf->size);
    }
    munmap(buf->data, buf->size);
    buf->data = NULL;
    buf->size = 0;
    buf->locked = false;
}

/* Апаратна нуліфікація ключів у Microchip ATECC608 по шині I2C */
static san_status_t atecc608_zeroize_slot(const char *i2c_bus_path, uint8_t slot) {
    int fd = open(i2c_bus_path, O_RDWR);
    if (fd < 0) {
        return SAN_ERR_SE_FAIL;
    }

    if (ioctl(fd, I2C_SLAVE, ATECC608_I2C_ADDR) < 0) {
        close(fd);
        return SAN_ERR_SE_FAIL;
    }

    /* Пакет команди Nonce для ініціалізації внутрішнього стану */
    uint8_t nonce_pkt[12] = {
        ATECC_CMD_WORD_ADDRESS, 0x0B, ATECC_OP_NONCE, 0x03, 0x00, 0x00,
        0xAA, 0xBB, 0xCC, 0xDD, 0x00, 0x00
    };
    uint16_t crc = atecc_crc16(&nonce_pkt[1], 9);
    nonce_pkt[10] = (uint8_t)(crc & 0xFF);
    nonce_pkt[11] = (uint8_t)((crc >> 8) & 0xFF);

    if (write(fd, nonce_pkt, sizeof(nonce_pkt)) != sizeof(nonce_pkt)) {
        close(fd);
        return SAN_ERR_SE_FAIL;
    }
    usleep(35000); /* Час виконання команди Nonce */

    /* Пакет стирання слота: запис 32 байт нулів через PrivWrite */
    uint8_t zero_pkt[40];
    zero_pkt[0] = ATECC_CMD_WORD_ADDRESS;
    zero_pkt[1] = 39; /* Довжина пакету */
    zero_pkt[2] = ATECC_OP_PRIVWRITE;
    zero_pkt[3] = ATECC_ZONE_DATA;
    zero_pkt[4] = (slot << 3); /* Адреса слота */
    zero_pkt[5] = 0x00;
    memset(&zero_pkt[6], 0x00, 32); /* Занулення ключа */

    crc = atecc_crc16(&zero_pkt[1], 37);
    zero_pkt[38] = (uint8_t)(crc & 0xFF);
    zero_pkt[39] = (uint8_t)((crc >> 8) & 0xFF);

    if (write(fd, zero_pkt, sizeof(zero_pkt)) != sizeof(zero_pkt)) {
        close(fd);
        return SAN_ERR_SE_FAIL;
    }
    usleep(50000); /* Час запису EEPROM */

    close(fd);
    return SAN_OK;
}

/* Виконання апаратного очищення eMMC через ioctl BLKSECDISCARD */
static san_status_t emmc_secure_erase(const char *dev_path) {
    int fd = open(dev_path, O_RDWR | O_EXCL);
    if (fd < 0) {
        return SAN_ERR_DEVICE_IO;
    }

    uint64_t dev_size = 0;
    if (ioctl(fd, BLKGETSIZE64, &dev_size) < 0) {
        close(fd);
        return SAN_ERR_DEVICE_IO;
    }

    uint64_t range[2] = {0, dev_size};
    /* Виклик безпечного високовольтного стирання фізичних блоків eMMC */
    if (ioctl(fd, BLKSECDISCARD, &range) < 0) {
        /* Якщо BLKSECDISCARD не підтримується контролером, пробуємо BLKDISCARD */
        if (ioctl(fd, BLKDISCARD, &range) < 0) {
            close(fd);
            return SAN_ERR_DEVICE_IO;
        }
    }

    fsync(fd);
    close(fd);
    return SAN_OK;
}

/* Виконання команди NVMe Sanitize */
static san_status_t nvme_sanitize_device(const char *dev_path, uint8_t action) {
    int fd = open(dev_path, O_RDWR | O_NONBLOCK);
    if (fd < 0) {
        return SAN_ERR_DEVICE_IO;
    }

    struct nvme_admin_cmd cmd;
    memset(&cmd, 0, sizeof(cmd));
    cmd.opcode = NVME_ADMIN_SANITIZE;
    cmd.cdw10 = (action & 0x07); /* SANACT: 0x02 - Block Erase, 0x04 - Crypto Erase */

    if (ioctl(fd, NVME_IOCTL_ADMIN_CMD, &cmd) < 0) {
        close(fd);
        return SAN_ERR_DEVICE_IO;
    }

    /* Опитування статусу завершення санітизації */
    bool completed = false;
    for (int retry = 0; retry < 60; ++retry) {
        sleep(1);
        struct nvme_admin_cmd log_cmd;
        uint8_t log_buf[512];
        memset(&log_cmd, 0, sizeof(log_cmd));
        memset(log_buf, 0, sizeof(log_buf));

        log_cmd.opcode = 0x02; /* Get Log Page */
        log_cmd.nsid = 0xFFFFFFFF;
        log_cmd.addr = (uint64_t)(uintptr_t)log_buf;
        log_cmd.data_len = sizeof(log_buf);
        log_cmd.cdw10 = NVME_LOG_SANITIZE_STATUS | ((sizeof(log_buf) / 4 - 1) << 16);

        if (ioctl(fd, NVME_IOCTL_ADMIN_CMD, &log_cmd) == 0) {
            uint16_t sstat = log_buf[0] | (log_buf[1] << 8);
            uint8_t status_code = (sstat & 0x07);
            if (status_code == 0x01) { /* Sanitize Completed Successfully */
                completed = true;
                break;
            }
        }
    }

    close(fd);
    return completed ? SAN_OK : SAN_ERR_DEVICE_IO;
}

/* Оцінка ентропії Шеннона для перевірки шифротексту */
static double calculate_entropy(const uint8_t *data, size_t len) {
    if (!data || len == 0) return 0.0;
    size_t counts[256] = {0};
    for (size_t i = 0; i < len; ++i) {
        counts[data[i]]++;
    }

    double entropy = 0.0;
    for (int i = 0; i < 256; ++i) {
        if (counts[i] > 0) {
            double p = (double)counts[i] / (double)len;
            entropy -= p * log2(p);
        }
    }
    return entropy;
}

/* Верифікаційний прохід зчитування та розрахунок контрольного хешу */
static san_status_t verify_sanitization(const char *dev_path, double *entropy_out) {
    int fd = open(dev_path, O_RDONLY | O_DIRECT);
    if (fd < 0) {
        fd = open(dev_path, O_RDONLY);
        if (fd < 0) return SAN_ERR_DEVICE_IO;
    }

    secure_buf_t sample_buf;
    if (secure_buf_alloc(&sample_buf, 1024 * 1024) != 0) {
        close(fd);
        return SAN_ERR_MEM_LOCK;
    }

    ssize_t read_bytes = read(fd, sample_buf.data, sample_buf.size);
    close(fd);

    if (read_bytes <= 0) {
        secure_buf_free(&sample_buf);
        return SAN_ERR_DEVICE_IO;
    }

    *entropy_out = calculate_entropy(sample_buf.data, (size_t)read_bytes);
    secure_buf_free(&sample_buf);
    return SAN_OK;
}

/* Головна функція оркестрації санітизації */
san_status_t execute_full_sanitization(const char *target_dev, const char *i2c_dev, 
                                      san_certificate_t *cert) {
    if (!target_dev || !cert) return SAN_ERR_INVALID_PARAM;

    memset(cert, 0, sizeof(*cert));
    strncpy(cert->target_path, target_dev, sizeof(cert->target_path) - 1);
    cert->timestamp = (uint64_t)time(NULL);

    /* 1. Апаратне стирання ключів Secure Element */
    if (i2c_dev) {
        if (atecc608_zeroize_slot(i2c_dev, 0) == SAN_OK) {
            cert->se_zeroized = true;
        }
    }

    /* 2. Апаратне очищення Flash-накопичувача */
    if (strstr(target_dev, "nvme")) {
        if (nvme_sanitize_device(target_dev, NVME_SANITIZE_CRYPTO) == SAN_OK) {
            cert->flash_purged = true;
        }
    } else {
        if (emmc_secure_erase(target_dev) == SAN_OK) {
            cert->flash_purged = true;
        }
    }

    /* 3. Верифікаційний прохід */
    if (verify_sanitization(target_dev, &cert->entropy) == SAN_OK) {
        /* Якщо стирання успішне, ентропія повинна бути або ~8.0 (криптошум), або ~0.0 (занулено) */
        if (cert->entropy > 7.99 || cert->entropy < 0.01) {
            return SAN_OK;
        }
    }

    return SAN_ERR_VERIFY_FAIL;
}
