#include "atecc608.h"

#include <string.h>

/* Перший байт кожної транзакції — Word Address: він каже чипу, що робити
 * з рештою пакета або, коли пакета немає, змінює режим живлення. */
#define WA_RESET 0x00u
#define WA_SLEEP 0x01u
#define WA_IDLE  0x02u
#define WA_CMD   0x03u

#define OP_READ 0x02u
#define OP_SIGN 0x41u

#define SIGN_MODE_EXTERNAL 0x80u /* Param1: підписати переданий дайджест */

/* Статус-байти з таблиці відповідей ATECC608. Чип відповідає таким пакетом
 * (Count=4) на будь-яку команду, яка не дала даних. */
#define ST_SUCCESS    0x00u
#define ST_MISCOMPARE 0x01u /* звірення не збіглося / команду відхилено */
#define ST_PARSE      0x03u /* незрозумілі параметри або заборонений доступ */
#define ST_ECC_FAULT  0x05u
#define ST_SELFTEST   0x07u
#define ST_EXEC       0x0Fu /* команду не вдалося виконати в поточному стані */
#define ST_AFTER_WAKE 0x11u /* чип щойно прокинувся і команди ще не бачив */
#define ST_WATCHDOG   0xEEu /* сторожовий таймер ось-ось вимкне генератор */
#define ST_COMM       0xFFu /* CRC або інша помилка зв'язку */

#define WAKE_DELAY_MS  2u   /* t_WHI ≥ 1.5 мс */
#define POLL_STEP_MS   4u

/* Час виконання (мс): мінімум чекаємо мовчки, далі опитуємо до стелі.
 * Стеля тримається значно нижче за сторожовий таймер чипа (1.7 с). */
#define SIGN_EXEC_MIN_MS 50u
#define SIGN_EXEC_MAX_MS 250u
#define READ_EXEC_MIN_MS 1u
#define READ_EXEC_MAX_MS 50u

/* Найдовший командний пакет тут: 1 Word Address + 39 байтів команди Sign. */
#define TX_MAX 40u
/* Найдовша відповідь: 1 Count + 64 байти (R, S) + 2 байти CRC. */
#define RX_MAX 67u

uint16_t atecc_crc16(const uint8_t *data, size_t len)
{
    uint16_t crc = 0x0000u;

    for (size_t i = 0; i < len; i++) {
        /* Біти кожного байта заходять від молодшого — так рахує сам чип. */
        for (uint8_t mask = 0x01u; mask != 0x00u; mask = (uint8_t)(mask << 1)) {
            uint8_t data_bit = (data[i] & mask) ? 1u : 0u;
            uint8_t crc_bit = (uint8_t)((crc >> 15) & 0x01u);
            crc = (uint16_t)(crc << 1);
            if (data_bit != crc_bit) {
                crc ^= 0x8005u;
            }
        }
    }
    return crc;
}

void atecc_init(atecc_dev *dev, const atecc_hal *hal, uint8_t addr7)
{
    dev->hal = *hal;
    dev->addr7 = addr7;
    dev->awake = false;
    dev->status = ST_SUCCESS;
}

/* Складання командного пакета. Count рахує сам себе, заголовок, дані й CRC,
 * але не рахує байт Word Address — той живе поза командою. */
static size_t build_cmd(uint8_t *buf, uint8_t opcode, uint8_t param1,
                        uint16_t param2, const uint8_t *data, size_t data_len)
{
    uint8_t count = (uint8_t)(7u + data_len);

    buf[0] = WA_CMD;
    buf[1] = count;
    buf[2] = opcode;
    buf[3] = param1;
    buf[4] = (uint8_t)(param2 & 0xFFu);
    buf[5] = (uint8_t)((param2 >> 8) & 0xFFu);
    if (data_len != 0) {
        memcpy(&buf[6], data, data_len);
    }

    /* CRC рахується від байта Count до останнього байта даних. */
    uint16_t crc = atecc_crc16(&buf[1], (size_t)count - 2u);
    buf[6 + data_len] = (uint8_t)(crc & 0xFFu);
    buf[7 + data_len] = (uint8_t)((crc >> 8) & 0xFFu);

    return (size_t)count + 1u;
}

/* Читання пакета у два прийоми: спершу байт довжини, потім увесь пакет.
 * Так можна відрізнити 4-байтовий статус від 67-байтової відповіді, не
 * вгадуючи наперед: перезапуск читання змушує чип віддати буфер спочатку. */
static atecc_err read_packet(atecc_dev *dev, uint8_t *buf, size_t cap, size_t *out_len)
{
    uint8_t count = 0;

    if (!dev->hal.read(dev->hal.ctx, dev->addr7, &count, 1)) {
        return ATECC_ERR_IO;
    }
    if (count < 4u || (size_t)count > cap) {
        return ATECC_ERR_PROTOCOL;
    }
    if (!dev->hal.read(dev->hal.ctx, dev->addr7, buf, count)) {
        return ATECC_ERR_IO;
    }
    if (buf[0] != count) {
        return ATECC_ERR_PROTOCOL;
    }

    uint16_t got = (uint16_t)(buf[count - 2] | ((uint16_t)buf[count - 1] << 8));
    if (got != atecc_crc16(buf, (size_t)count - 2u)) {
        return ATECC_ERR_CRC;
    }

    *out_len = count;
    return ATECC_OK;
}

/* Повний цикл однієї команди: запис, пауза на час виконання, опитування шини
 * до появи відповіді, розбір статус-пакета. */
static atecc_err transact(atecc_dev *dev, const uint8_t *cmd, size_t cmd_len,
                          uint32_t exec_min_ms, uint32_t exec_max_ms,
                          uint8_t *resp, size_t cap, size_t *resp_len)
{
    if (!dev->awake) {
        atecc_err err = atecc_wake(dev);
        if (err != ATECC_OK) {
            return err;
        }
    }

    dev->status = ST_SUCCESS;
    if (!dev->hal.write(dev->hal.ctx, dev->addr7, cmd, cmd_len)) {
        /* Команда не дійшла — стан чипа невідомий, наступного разу будимо. */
        dev->awake = false;
        return ATECC_ERR_IO;
    }

    dev->hal.delay_ms(dev->hal.ctx, exec_min_ms);

    uint32_t waited = exec_min_ms;
    unsigned crc_retries = 0;

    for (;;) {
        size_t len = 0;
        atecc_err err = read_packet(dev, resp, cap, &len);

        if (err == ATECC_OK) {
            if (len == 4u) {
                dev->status = resp[1];
                if (resp[1] == ST_SUCCESS) {
                    *resp_len = len;
                    return ATECC_OK;
                }
                if (resp[1] == ST_AFTER_WAKE) {
                    /* Чип перезапустився й забув команду. */
                    dev->awake = false;
                }
                return ATECC_ERR_DEVICE;
            }
            *resp_len = len;
            return ATECC_OK;
        }

        if (err == ATECC_ERR_CRC) {
            /* Побитий пакет чип віддає повторно, поки хост не забрав його
             * цілим; двох спроб досить, далі це вже не перешкода на лінії. */
            if (++crc_retries > 2u) {
                return ATECC_ERR_CRC;
            }
            continue;
        }

        if (err != ATECC_ERR_IO) {
            return err;
        }

        /* NACK на адресу: криптоядро ще рахує. Чекаємо далі. */
        if (waited >= exec_max_ms) {
            return ATECC_ERR_TIMEOUT;
        }
        dev->hal.delay_ms(dev->hal.ctx, POLL_STEP_MS);
        waited += POLL_STEP_MS;
    }
}

atecc_err atecc_wake(atecc_dev *dev)
{
    static const uint8_t zero = 0x00u;
    uint8_t resp[4] = {0};

    /* Імпульс пробудження. Запис нульового байта на зарезервовану адресу 0x00
     * тримає SDA внизу дев'ять бітових інтервалів — на 100 кГц це ≈90 мкс,
     * тобто більше за потрібні 60 мкс (t_WLO). Жоден пристрій цю адресу не
     * підтверджує, тому результат запису свідомо ігноруємо. */
    (void)dev->hal.write(dev->hal.ctx, 0x00u, &zero, 1);
    dev->hal.delay_ms(dev->hal.ctx, WAKE_DELAY_MS);

    dev->awake = false;
    if (!dev->hal.read(dev->hal.ctx, dev->addr7, resp, sizeof resp)) {
        return ATECC_ERR_IO;
    }
    if (resp[0] != 0x04u) {
        return ATECC_ERR_PROTOCOL;
    }

    uint16_t got = (uint16_t)(resp[2] | ((uint16_t)resp[3] << 8));
    if (got != atecc_crc16(resp, 2)) {
        return ATECC_ERR_CRC;
    }

    dev->status = resp[1];
    if (resp[1] != ST_AFTER_WAKE) {
        return ATECC_ERR_DEVICE;
    }

    dev->awake = true;
    return ATECC_OK;
}

void atecc_sleep(atecc_dev *dev)
{
    static const uint8_t sleep_word = WA_SLEEP;

    if (!dev->awake) {
        return;
    }
    (void)dev->hal.write(dev->hal.ctx, dev->addr7, &sleep_word, 1);
    dev->awake = false;
}

atecc_err atecc_sign_digest(atecc_dev *dev, uint8_t slot,
                            const uint8_t digest[ATECC_DIGEST_LEN],
                            uint8_t signature[ATECC_SIGNATURE_LEN])
{
    uint8_t tx[TX_MAX];
    uint8_t rx[RX_MAX];
    size_t rx_len = 0;

    if (slot > 15u) {
        return ATECC_ERR_ARG;
    }

    size_t tx_len = build_cmd(tx, OP_SIGN, SIGN_MODE_EXTERNAL, slot,
                              digest, ATECC_DIGEST_LEN);

    atecc_err err = transact(dev, tx, tx_len, SIGN_EXEC_MIN_MS, SIGN_EXEC_MAX_MS,
                             rx, sizeof rx, &rx_len);
    if (err != ATECC_OK) {
        return err;
    }
    /* 1 байт Count (0x43) + 32 байти R + 32 байти S + 2 байти CRC. */
    if (rx_len != RX_MAX) {
        return ATECC_ERR_PROTOCOL;
    }

    memcpy(signature, &rx[1], ATECC_SIGNATURE_LEN);
    return ATECC_OK;
}

atecc_err atecc_lock_state(atecc_dev *dev, bool *config_locked, bool *data_locked)
{
    uint8_t tx[TX_MAX];
    uint8_t rx[RX_MAX];
    size_t rx_len = 0;

    /* Read зони конфігурації, блок 2 — байти 64..95. Param1: біт 7 просить
     * 32 байти, молодші біти вибирають зону (0 — конфігурація).
     * Param2 = (номер блока << 3) | зсув слова всередині блока. */
    size_t tx_len = build_cmd(tx, OP_READ, 0x80u, (uint16_t)(2u << 3), NULL, 0);

    atecc_err err = transact(dev, tx, tx_len, READ_EXEC_MIN_MS, READ_EXEC_MAX_MS,
                             rx, sizeof rx, &rx_len);
    if (err != ATECC_OK) {
        return err;
    }
    if (rx_len != 35u) { /* 1 + 32 + 2 */
        return ATECC_ERR_PROTOCOL;
    }

    /* Байт 86 конфігурації — LockValue (зона даних), байт 87 — LockConfig.
     * У блоці, що починається з байта 64, це зсуви 22 і 23; у пакеті ще
     * попереду байт Count, тому +1. Значення 0x55 означає «розблоковано». */
    if (data_locked != NULL) {
        *data_locked = (rx[1 + 22] != 0x55u);
    }
    if (config_locked != NULL) {
        *config_locked = (rx[1 + 23] != 0x55u);
    }
    return ATECC_OK;
}

const char *atecc_strerror(atecc_err err)
{
    switch (err) {
    case ATECC_OK:            return "успіх";
    case ATECC_ERR_IO:        return "шина I2C не відповіла";
    case ATECC_ERR_CRC:       return "CRC16 відповіді не збіглася";
    case ATECC_ERR_TIMEOUT:   return "чип не відповів у межах часу виконання";
    case ATECC_ERR_PROTOCOL:  return "несподівана довжина пакета";
    case ATECC_ERR_DEVICE:    return "чип повернув код помилки";
    case ATECC_ERR_NOT_LOCKED:return "зони пам'яті не заблоковані";
    case ATECC_ERR_ARG:       return "хибний аргумент";
    default:                  return "невідома помилка";
    }
}

const char *atecc_status_str(uint8_t status)
{
    switch (status) {
    case ST_SUCCESS:    return "0x00 виконано";
    case ST_MISCOMPARE: return "0x01 звірення не збіглося або команду відхилено";
    case ST_PARSE:      return "0x03 хибні параметри або заборонений доступ";
    case ST_ECC_FAULT:  return "0x05 збій обчислення на кривій";
    case ST_SELFTEST:   return "0x07 не пройдено самоперевірку";
    case ST_EXEC:       return "0x0F команду неможливо виконати в цьому стані";
    case ST_AFTER_WAKE: return "0x11 чип щойно прокинувся";
    case ST_WATCHDOG:   return "0xEE сторожовий таймер ось-ось вимкне генератор";
    case ST_COMM:       return "0xFF помилка CRC або зв'язку";
    default:            return "невідомий статус";
    }
}
