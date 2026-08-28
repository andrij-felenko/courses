#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>

#define ACK_BYTE   0x79
#define NACK_BYTE  0x1F

#define CMD_GET_ID 0x02
#define CMD_ERASE  0x44
#define CMD_WRITE  0x31
#define CMD_GO     0x21

// Налаштування послідовного порту: 115200 бод, 8E1 (парний контроль)
static int serial_open(const char *port_name)
{
    int fd = open(port_name, O_RDWR | O_NOCTTY | O_SYNC);
    if (fd < 0) return -1;

    struct termios tty;
    if (tcgetattr(fd, &tty) != 0) {
        close(fd);
        return -1;
    }

    cfsetospeed(&tty, B115200);
    cfsetispeed(&tty, B115200);

    tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8; // 8 біт даних
    tty.c_cflag |= PARENB;                      // Увімкнути контроль парності
    tty.c_cflag &= ~PARODD;                     // Even parity (парний)
    tty.c_cflag &= ~CSTOPB;                     // 1 стоп-біт
    tty.c_cflag &= ~CRTSCTS;                    // Без апаратного керування лініями
    tty.c_cflag |= (CLOCAL | CREAD);            // Локальне підключення та прийом

    tty.c_iflag &= ~(IXON | IXOFF | IXANY);     // Без програмного XON/XOFF
    tty.c_lflag = 0;                            // Сирий (raw) не канонічний режим
    tty.c_oflag = 0;

    tty.c_cc[VMIN]  = 0;
    tty.c_cc[VTIME] = 10;                       // Посимвольний таймаут 1.0 с

    if (tcsetattr(fd, TCSANOW, &tty) != 0) {
        close(fd);
        return -1;
    }
    return fd;
}

// Очікування квитанції ACK (0x79)
static bool wait_ack(int fd, int timeout_seconds)
{
    uint8_t rx_byte = 0;
    int max_attempts = timeout_seconds * 10;
    for (int i = 0; i < max_attempts; ++i) {
        if (read(fd, &rx_byte, 1) == 1) {
            if (rx_byte == ACK_BYTE) return true;
            if (rx_byte == NACK_BYTE) return false;
        }
        usleep(100000); // Інтервал опитування 100 мс
    }
    return false;
}

// Крок 1: Синхронізація бітрейту через надсилання 0x7F
bool bootloader_sync(int fd)
{
    uint8_t sync_byte = 0x7F;
    tcflush(fd, TCIOFLUSH); // Очищення залишків у буфері після скидання
    if (write(fd, &sync_byte, 1) != 1) return false;
    return wait_ack(fd, 2);
}

// Крок 2: Отримання Product ID (PID)
bool bootloader_get_pid(int fd, uint16_t *out_pid)
{
    uint8_t cmd[2] = {CMD_GET_ID, (uint8_t)(~CMD_GET_ID)};
    if (write(fd, cmd, 2) != 2) return false;
    if (!wait_ack(fd, 1)) return false;

    uint8_t len = 0;
    if (read(fd, &len, 1) != 1 || len != 1) return false; // Очікуємо 2 байти PID (N = 1)

    uint8_t pid_bytes[2];
    if (read(fd, pid_bytes, 2) != 2) return false;
    if (!wait_ack(fd, 1)) return false;

    *out_pid = ((uint16_t)pid_bytes[0] << 8) | pid_bytes[1];
    return true;
}

// Крок 3: Глобальне стирання всієї Flash-пам'яті (Mass Erase)
bool bootloader_mass_erase(int fd)
{
    uint8_t cmd[2] = {CMD_ERASE, (uint8_t)(~CMD_ERASE)};
    if (write(fd, cmd, 2) != 2) return false;
    if (!wait_ack(fd, 1)) return false;

    // Спеціальний код 0xFFFF та його XOR чексума 0x00
    uint8_t erase_params[3] = {0xFF, 0xFF, 0x00};
    if (write(fd, erase_params, 3) != 3) return false;

    // Масове стирання може тривати до 20-25 секунд на великих кристалах
    return wait_ack(fd, 25);
}

// Крок 4: Запис одного блоку пам'яті (до 256 байтів)
bool bootloader_write_block(int fd, uint32_t address, const uint8_t *data, size_t length)
{
    if (length == 0 || length > 256) return false;

    // 1. Надсилання команди Write
    uint8_t cmd[2] = {CMD_WRITE, (uint8_t)(~CMD_WRITE)};
    if (write(fd, cmd, 2) != 2) return false;
    if (!wait_ack(fd, 1)) return false;

    // 2. Надсилання 4-байтової адреси та її XOR чексуми
    uint8_t addr_buf[5];
    addr_buf[0] = (address >> 24) & 0xFF;
    addr_buf[1] = (address >> 16) & 0xFF;
    addr_buf[2] = (address >> 8) & 0xFF;
    addr_buf[3] = address & 0xFF;
    addr_buf[4] = addr_buf[0] ^ addr_buf[1] ^ addr_buf[2] ^ addr_buf[3];

    if (write(fd, addr_buf, 5) != 5) return false;
    if (!wait_ack(fd, 1)) return false;

    // 3. Надсилання кількості байтів N (len-1), корисних даних та XOR чексуми
    uint8_t payload[258];
    uint8_t n = (uint8_t)(length - 1);
    payload[0] = n;
    uint8_t checksum = n;

    for (size_t i = 0; i < length; ++i) {
        payload[1 + i] = data[i];
        checksum ^= data[i];
    }
    payload[1 + length] = checksum;

    if (write(fd, payload, length + 2) != (ssize_t)(length + 2)) return false;
    return wait_ack(fd, 2);
}

// Крок 5: Передача керування завантаженій програмі (Go)
bool bootloader_go(int fd, uint32_t address)
{
    uint8_t cmd[2] = {CMD_GO, (uint8_t)(~CMD_GO)};
    if (write(fd, cmd, 2) != 2) return false;
    if (!wait_ack(fd, 1)) return false;

    uint8_t addr_buf[5];
    addr_buf[0] = (address >> 24) & 0xFF;
    addr_buf[1] = (address >> 16) & 0xFF;
    addr_buf[2] = (address >> 8) & 0xFF;
    addr_buf[3] = address & 0xFF;
    addr_buf[4] = addr_buf[0] ^ addr_buf[1] ^ addr_buf[2] ^ addr_buf[3];

    if (write(fd, addr_buf, 5) != 5) return false;
    return wait_ack(fd, 1);
}
