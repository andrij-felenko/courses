/* Приклад низькорівневого коду мовою C (ioctl ABI v2) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <poll.h>
#include <linux/gpio.h>

int main(void) {
    int chip_fd = open("/dev/gpiochip0", O_RDWR | O_CLOEXEC);
    if (chip_fd < 0) {
        perror("Не вдалося відкрити /dev/gpiochip0");
        return EXIT_FAILURE;
    }

    struct gpio_v2_line_request req;
    memset(&req, 0, sizeof(req));

    /* Налаштування ліній: offset 17 (OUT), offset 27 (IN з IRQ) */
    req.offsets[0] = 17;
    req.offsets[1] = 27;
    req.num_lines = 2;
    snprintf(req.consumer, sizeof(req.consumer), "raw-ioctl-demo");

    /* Глобальні прапори за замовчуванням: вхід з перехопленням фронтів */
    req.config.flags = GPIO_V2_LINE_FLAG_INPUT |
                       GPIO_V2_LINE_FLAG_EDGE_RISING |
                       GPIO_V2_LINE_FLAG_EDGE_FALLING;

    /* Перевизначення для лінії 17: вихід із підтяжкою PULL_UP */
    req.config.num_attrs = 2;
    
    /* Атрибут 0: Прапори для лінії 17 (маска 0x01 = перший елемент offsets[]) */
    req.config.attrs[0].attr.id = GPIO_V2_LINE_ATTR_ID_FLAGS;
    req.config.attrs[0].attr.flags = GPIO_V2_LINE_FLAG_OUTPUT | GPIO_V2_LINE_FLAG_BIAS_PULL_UP;
    req.config.attrs[0].mask = 0x01;

    /* Атрибут 1: Фільтрація брязкоту 5 мс (5000 мкс) для лінії 27 (маска 0x02 = другий елемент) */
    req.config.attrs[1].attr.id = GPIO_V2_LINE_ATTR_ID_DEBOUNCE;
    req.config.attrs[1].attr.debounce_period_us = 5000;
    req.config.attrs[1].mask = 0x02;

    if (ioctl(chip_fd, GPIO_V2_GET_LINE_IOCTL, &req) < 0) {
        perror("Помилка виконання GPIO_V2_GET_LINE_IOCTL");
        close(chip_fd);
        return EXIT_FAILURE;
    }

    int line_fd = req.fd;
    printf("Отримано Line FD: %d. Встановлюємо HIGH на лінії 17...\n", line_fd);

    /* Встановлення логічної 1 на лінії 17 (маска 0x01) */
    struct gpio_v2_line_values vals;
    memset(&vals, 0, sizeof(vals));
    vals.mask = 0x01;
    vals.bits = 0x01;

    if (ioctl(line_fd, GPIO_V2_LINE_SET_VALUES_IOCTL, &vals) < 0) {
        perror("Помилка виконання GPIO_V2_LINE_SET_VALUES_IOCTL");
    }

    /* Очікування подій переривання на лінії 27 за допомогою poll() */
    struct pollfd pfd;
    pfd.fd = line_fd;
    pfd.events = POLLIN;

    printf("Очікування подій на лінії 27 (натисніть кнопку або змініть рівень)...\n");
    int ret = poll(&pfd, 1, 10000); /* таймаут 10 секунд */

    if (ret > 0 && (pfd.revents & POLLIN)) {
        struct gpio_v2_line_event event;
        ssize_t bytes = read(line_fd, &event, sizeof(event));
        if (bytes == sizeof(event)) {
            printf("ПОДІЯ! Час: %llu нс, Фронт: %s, Лінія: %u, SeqNo: %u\n",
                   (unsigned long long)event.timestamp_ns,
                   (event.id == GPIO_V2_LINE_EVENT_RISING_EDGE) ? "RISING" : "FALLING",
                   event.offset, event.seqno);
        }
    } else if (ret == 0) {
        printf("Таймаут очікування події.\n");
    }

    /* Автоматичне вивільнення ліній ядром при закритті дескрипторів */
    close(line_fd);
    close(chip_fd);
    return EXIT_SUCCESS;
}
