#define _POSIX_C_SOURCE 200809L

#include "modbus_rtu.h"

#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <pthread.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <time.h>
#include <unistd.h>

#define MB_FC_READ_HOLDING 0x03
#define MB_FC_WRITE_COIL   0x05
#define MB_MAX_ADU         256

struct modbus_port {
    int fd;
    unsigned timeout_ms;
    uint8_t last_exception;
    pthread_mutex_t lock;
};

static int64_t now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

/* Класичний Modbus CRC-16 (поліном 0xA001, початкове значення 0xFFFF). */
static uint16_t crc16(const uint8_t *buf, size_t len)
{
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= buf[i];
        for (int bit = 0; bit < 8; bit++)
            crc = (crc & 1) ? (uint16_t)((crc >> 1) ^ 0xA001) : (uint16_t)(crc >> 1);
    }
    return crc;
}

static bool write_all(int fd, const uint8_t *buf, size_t len)
{
    size_t off = 0;
    while (off < len) {
        ssize_t n = write(fd, buf + off, len - off);
        if (n > 0) {
            off += (size_t)n;
            continue;
        }
        if (n < 0 && errno == EINTR)
            continue;
        if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
            struct pollfd pfd = { fd, POLLOUT, 0 };
            if (poll(&pfd, 1, 100) <= 0)
                return false;
            continue;
        }
        return false;
    }
    return true;
}

/* Читає рівно len байтів або здається за спільним дедлайном обміну.
 * Modbus RTU не має ознаки кінця кадру в потоці — довжину відповіді ми
 * знаємо з функції, тому читаємо саме стільки, скільки маємо отримати. */
static mb_status_t read_exact(int fd, uint8_t *buf, size_t len, int64_t deadline)
{
    size_t off = 0;
    while (off < len) {
        int64_t left = deadline - now_ms();
        if (left <= 0)
            return MB_ERR_TIMEOUT;

        struct pollfd pfd = { fd, POLLIN, 0 };
        int pr = poll(&pfd, 1, (int)left);
        if (pr == 0)
            return MB_ERR_TIMEOUT;
        if (pr < 0) {
            if (errno == EINTR)
                continue;
            return MB_ERR_IO;
        }

        ssize_t n = read(fd, buf + off, len - off);
        if (n > 0) {
            off += (size_t)n;
            continue;
        }
        if (n < 0 && (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK))
            continue;
        /* n == 0 на послідовному порту означає, що пристрій зник:
         * висмикнули перехідник USB-RS485. */
        return MB_ERR_IO;
    }
    return MB_OK;
}

/* Повний обмін: дописати CRC, віддати кадр, вичитати відповідь, звірити CRC.
 * req мусить мати запас на два байти CRC понад body_len. */
static mb_status_t transact(modbus_port_t *p, uint8_t *req, size_t body_len,
                            uint8_t *resp, size_t resp_cap, size_t *out_len)
{
    uint16_t crc = crc16(req, body_len);
    req[body_len] = (uint8_t)(crc & 0xFF);        /* CRC іде молодшим байтом уперед */
    req[body_len + 1] = (uint8_t)(crc >> 8);

    /* Луна попереднього обміну або сміття від наводки нам не потрібні. */
    tcflush(p->fd, TCIFLUSH);
    if (!write_all(p->fd, req, body_len + 2))
        return MB_ERR_IO;

    int64_t deadline = now_ms() + (int64_t)p->timeout_ms;
    mb_status_t st = read_exact(p->fd, resp, 2, deadline);
    if (st != MB_OK)
        return st;
    if (resp[0] != req[0])
        return MB_ERR_FRAME;

    size_t len = 2;
    if (resp[1] & 0x80) {
        /* Виняток: адреса, функція|0x80, код, CRC. */
        st = read_exact(p->fd, resp + len, 3, deadline);
        if (st != MB_OK)
            return st;
        len += 3;
    } else if (resp[1] != req[1]) {
        return MB_ERR_FRAME;
    } else if (resp[1] == MB_FC_READ_HOLDING) {
        st = read_exact(p->fd, resp + len, 1, deadline);
        if (st != MB_OK)
            return st;
        size_t byte_count = resp[2];
        len += 1;
        if (len + byte_count + 2 > resp_cap)
            return MB_ERR_FRAME;
        st = read_exact(p->fd, resp + len, byte_count + 2, deadline);
        if (st != MB_OK)
            return st;
        len += byte_count + 2;
    } else {
        /* FC 05 відповідає точною луною запиту: адреса, функція, 4 байти, CRC. */
        st = read_exact(p->fd, resp + len, 6, deadline);
        if (st != MB_OK)
            return st;
        len += 6;
    }

    uint16_t got = (uint16_t)(resp[len - 2] | ((uint16_t)resp[len - 1] << 8));
    if (crc16(resp, len - 2) != got)
        return MB_ERR_CRC;

    if (resp[1] & 0x80) {
        p->last_exception = resp[2];
        return MB_ERR_EXCEPTION;
    }
    *out_len = len;
    return MB_OK;
}

static speed_t baud_constant(int baud)
{
    switch (baud) {
    case 9600:   return B9600;
    case 19200:  return B19200;
    case 38400:  return B38400;
    case 57600:  return B57600;
    case 115200: return B115200;
    default:     return 0;
    }
}

modbus_port_t *mb_open(const char *device, int baud, unsigned response_timeout_ms)
{
    speed_t speed = baud_constant(baud);
    if (speed == 0) {
        errno = EINVAL;
        return NULL;
    }

    int fd = open(device, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0)
        return NULL;

    struct termios tio;
    if (tcgetattr(fd, &tio) != 0) {
        close(fd);
        return NULL;
    }
    cfmakeraw(&tio);                       /* без канонічного режиму й ехо */
    tio.c_cflag &= ~(unsigned)(CSIZE | CSTOPB | PARODD | CRTSCTS);
    tio.c_cflag |= CS8 | PARENB | CLOCAL | CREAD;   /* 8E1, без модемних ліній */
    tio.c_iflag |= INPCK;                  /* хай апарат сам ловить збій парності */
    tio.c_cc[VMIN] = 0;                    /* усе чекання робить poll() */
    tio.c_cc[VTIME] = 0;
    if (cfsetispeed(&tio, speed) != 0 || cfsetospeed(&tio, speed) != 0 ||
        tcsetattr(fd, TCSANOW, &tio) != 0) {
        close(fd);
        return NULL;
    }

    modbus_port_t *p = calloc(1, sizeof(*p));
    if (!p) {
        close(fd);
        return NULL;
    }
    p->fd = fd;
    p->timeout_ms = response_timeout_ms;
    pthread_mutex_init(&p->lock, NULL);
    return p;
}

void mb_close(modbus_port_t *p)
{
    if (!p)
        return;
    close(p->fd);
    pthread_mutex_destroy(&p->lock);
    free(p);
}

mb_status_t mb_read_holding(modbus_port_t *p, uint8_t slave, uint16_t start,
                            uint16_t count, uint16_t *out_regs)
{
    if (count == 0 || count > 125)
        return MB_ERR_FRAME;

    uint8_t req[MB_MAX_ADU];
    req[0] = slave;
    req[1] = MB_FC_READ_HOLDING;
    req[2] = (uint8_t)(start >> 8);
    req[3] = (uint8_t)(start & 0xFF);
    req[4] = (uint8_t)(count >> 8);
    req[5] = (uint8_t)(count & 0xFF);

    uint8_t resp[MB_MAX_ADU];
    size_t resp_len = 0;

    pthread_mutex_lock(&p->lock);
    mb_status_t st = transact(p, req, 6, resp, sizeof(resp), &resp_len);
    pthread_mutex_unlock(&p->lock);
    if (st != MB_OK)
        return st;

    if (resp[2] != (uint8_t)(count * 2))
        return MB_ERR_FRAME;
    for (uint16_t i = 0; i < count; i++)
        out_regs[i] = (uint16_t)(((uint16_t)resp[3 + i * 2] << 8) | resp[4 + i * 2]);
    return MB_OK;
}

mb_status_t mb_write_coil(modbus_port_t *p, uint8_t slave, uint16_t addr, bool on)
{
    uint8_t req[MB_MAX_ADU];
    req[0] = slave;
    req[1] = MB_FC_WRITE_COIL;
    req[2] = (uint8_t)(addr >> 8);
    req[3] = (uint8_t)(addr & 0xFF);
    req[4] = on ? 0xFF : 0x00;      /* 0xFF00 — увімкнути, 0x0000 — вимкнути */
    req[5] = 0x00;

    uint8_t resp[MB_MAX_ADU];
    size_t resp_len = 0;

    pthread_mutex_lock(&p->lock);
    mb_status_t st = transact(p, req, 6, resp, sizeof(resp), &resp_len);
    pthread_mutex_unlock(&p->lock);
    if (st != MB_OK)
        return st;

    /* Луна мусить збігтися побайтово — інакше ми не знаємо, що саме спрацювало. */
    if (memcmp(req + 2, resp + 2, 4) != 0)
        return MB_ERR_FRAME;
    return MB_OK;
}

uint8_t mb_last_exception(const modbus_port_t *p)
{
    return p->last_exception;
}

float mb_regs_to_float(const uint16_t *regs)
{
    uint32_t raw = ((uint32_t)regs[0] << 16) | regs[1];
    float value;
    memcpy(&value, &raw, sizeof(value));
    return value;
}

const char *mb_strerror(mb_status_t st)
{
    switch (st) {
    case MB_OK:            return "ok";
    case MB_ERR_IO:        return "збій вводу-виводу на порту";
    case MB_ERR_TIMEOUT:   return "підлеглий не відповів";
    case MB_ERR_CRC:       return "CRC відповіді не збігся";
    case MB_ERR_FRAME:     return "неочікуваний кадр відповіді";
    case MB_ERR_EXCEPTION: return "виняток Modbus від підлеглого";
    default:               return "невідомий стан";
    }
}
