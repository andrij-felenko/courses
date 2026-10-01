#include "esp01_uart.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <sys/ioctl.h>
#include <sys/select.h>

#define RX_BUFFER_SIZE 512

/* Внутрішня функція перетворення числового baudrate у константу termios */
static speed_t get_termios_baud(uint32_t baud) {
    switch (baud) {
        case 9600:   return B9600;
        case 19200:  return B19200;
        case 38400:  return B38400;
        case 57600:  return B57600;
        case 115200: return B115200;
        case 230400: return B230400;
        default:     return B115200;
    }
}

/* Перевірка наявності даних у буфері прийому з таймаутом за допомогою select */
static esp01_err_t wait_for_data(int fd, uint32_t timeout_ms) {
    fd_set readfds;
    struct timeval tv;

    FD_ZERO(&readfds);
    FD_SET(fd, &readfds);

    tv.tv_sec = timeout_ms / 1000;
    tv.tv_usec = (timeout_ms % 1000) * 1000;

    int ret = select(fd + 1, &readfds, NULL, NULL, &tv);
    if (ret < 0) {
        return ESP01_ERR_PORT_CONFIG;
    } else if (ret == 0) {
        return ESP01_ERR_TIMEOUT;
    }

    return ESP01_OK;
}

/* Відправка рядка команди у послідовний порт та зчитування відповіді */
static esp01_err_t send_cmd_read_resp(esp01_driver_t *driver, const char *cmd, char *response_buf, size_t buf_size) {
    if (!driver || !driver->is_initialized || driver->port_fd < 0) {
        return ESP01_ERR_PORT_OPEN;
    }

    /* Очищення буферів вводу/виводу перед відправкою */
    tcflush(driver->port_fd, TCIOFLUSH);

    /* Запис AT-команди у порт з додаванням символів переведення рядка \r\n */
    size_t cmd_len = strlen(cmd);
    if (write(driver->port_fd, cmd, cmd_len) < 0) {
        return ESP01_ERR_PORT_CONFIG;
    }

    memset(response_buf, 0, buf_size);
    size_t total_read = 0;
    uint32_t elapsed_ms = 0;

    while (total_read < buf_size - 1) {
        esp01_err_t status = wait_for_data(driver->port_fd, 100);
        if (status == ESP01_ERR_TIMEOUT) {
            elapsed_ms += 100;
            if (elapsed_ms >= driver->config.timeout_ms) {
                break;
            }
            continue;
        } else if (status != ESP01_OK) {
            return status;
        }

        ssize_t bytes = read(driver->port_fd, response_buf + total_read, buf_size - 1 - total_read);
        if (bytes > 0) {
            total_read += bytes;
            response_buf[total_read] = '\0';
            /* Зупиняємо зчитування при виявленні маркерів завершення "OK" або "ERROR" */
            if (strstr(response_buf, "OK\r\n") || strstr(response_buf, "ERROR\r\n")) {
                break;
            }
        } else if (bytes < 0 && errno != EAGAIN) {
            return ESP01_ERR_PORT_CONFIG;
        }
    }

    return (total_read > 0) ? ESP01_OK : ESP01_ERR_TIMEOUT;
}

esp01_err_t esp01_init(esp01_driver_t *driver, const esp01_config_t *config) {
    if (!driver || !config || !config->port_name) {
        return ESP01_ERR_PORT_CONFIG;
    }

    driver->config = *config;
    driver->is_initialized = false;

    /* Відкриття порту у неблокуючому режимі без призначення керуючого термінала */
    driver->port_fd = open(config->port_name, O_RDWR | O_NOCTTY | O_NDELAY);
    if (driver->port_fd < 0) {
        perror("Помилка відкриття POSIX UART порту");
        return ESP01_ERR_PORT_OPEN;
    }

    /* Відновлення блокуючого режиму читання після успішного відкриття */
    fcntl(driver->port_fd, F_SETFL, 0);

    /* Налаштування атрибутів POSIX termios */
    struct termios options;
    if (tcgetattr(driver->port_fd, &options) < 0) {
        close(driver->port_fd);
        driver->port_fd = -1;
        return ESP01_ERR_PORT_CONFIG;
    }

    speed_t speed = get_termios_baud(config->baud_rate);
    cfsetispeed(&options, speed);
    cfsetospeed(&options, speed);

    /* Конфігурація 8N1 (8 біт даних, без парності, 1 стоп-біт) */
    options.c_cflag &= ~PARENB;
    options.c_cflag &= ~CSTOPB;
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;
    options.c_cflag &= ~CRTSCTS; /* Вимкнення апаратного керування потоком RTS/CTS */
    options.c_cflag |= CREAD | CLOCAL;

    /* Вимкнення канонічного режиму та спеціальної обробки символів */
    options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
    options.c_iflag &= ~(IXON | IXOFF | IXANY | IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL);
    options.c_oflag &= ~OPOST;

    options.c_cc[VMIN] = 0;
    options.c_cc[VTIME] = 10;

    if (tcsetattr(driver->port_fd, TCSANOW, &options) < 0) {
        close(driver->port_fd);
        driver->port_fd = -1;
        return ESP01_ERR_PORT_CONFIG;
    }

    driver->is_initialized = true;
    return ESP01_OK;
}

esp01_err_t esp01_close(esp01_driver_t *driver) {
    if (driver && driver->is_initialized && driver->port_fd >= 0) {
        close(driver->port_fd);
        driver->port_fd = -1;
        driver->is_initialized = false;
    }
    return ESP01_OK;
}

esp01_err_t esp01_ping(esp01_driver_t *driver) {
    char rx_buf[RX_BUFFER_SIZE];
    esp01_err_t err = send_cmd_read_resp(driver, "AT\r\n", rx_buf, sizeof(rx_buf));
    if (err != ESP01_OK) {
        return err;
    }
    return strstr(rx_buf, "OK") ? ESP01_OK : ESP01_ERR_NO_RESPONSE;
}

esp01_err_t esp01_get_status(esp01_driver_t *driver, esp01_status_t *status) {
    if (!status) {
        return ESP01_ERR_PORT_CONFIG;
    }

    memset(status, 0, sizeof(esp01_status_t));

    /* 1. Перевірка базового з'єднання тестовою командою AT */
    if (esp01_ping(driver) == ESP01_OK) {
        status->is_connected = true;
    } else {
        status->is_connected = false;
        return ESP01_ERR_NO_RESPONSE;
    }

    /* 2. Запит версії прошивки через команду AT+GMR */
    char rx_buf[RX_BUFFER_SIZE];
    if (send_cmd_read_resp(driver, "AT+GMR\r\n", rx_buf, sizeof(rx_buf)) == ESP01_OK) {
        char *start = strstr(rx_buf, "AT+GMR\r\n");
        if (start) {
            start += strlen("AT+GMR\r\n");
        } else {
            start = rx_buf;
        }

        char *end = strstr(start, "OK");
        if (end) {
            size_t rev_len = (size_t)(end - start);
            if (rev_len >= sizeof(status->firmware_rev)) {
                rev_len = sizeof(status->firmware_rev) - 1;
            }
            strncpy(status->firmware_rev, start, rev_len);
            status->firmware_rev[rev_len] = '\0';
        } else {
            strncpy(status->firmware_rev, "Невідома ревізія", sizeof(status->firmware_rev) - 1);
        }
        status->is_ready = true;
    }

    return ESP01_OK;
}
