/* Файл: socketcan_demo.c
   Компіляція: gcc -Wall -Wextra socketcan_demo.c -o socketcan_demo */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <linux/can/error.h>

int main(void) {
    int s;
    struct sockaddr_can addr;
    struct ifreq ifr;
    struct can_frame frame;

    /* 1. Створення сирого сокета CAN */
    if ((s = socket(PF_CAN, SOCK_RAW, CAN_RAW)) < 0) {
        perror("Помилка відкриття сокета CAN");
        return EXIT_FAILURE;
    }

    /* 2. Пошук індексу мережевого інтерфейсу за іменем "vcan0" або "can0" */
    const char *ifname = "vcan0";
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    ifr.ifr_name[IFNAMSIZ - 1] = '\0';

    if (ioctl(s, SIOCGIFINDEX, &ifr) < 0) {
        perror("Помилка ioctl (SIOCGIFINDEX)");
        close(s);
        return EXIT_FAILURE;
    }

    /* 3. Прив'язка сокета до інтерфейсу */
    memset(&addr, 0, sizeof(addr));
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("Помилка bind сокета");
        close(s);
        return EXIT_FAILURE;
    }

    /* 4. Налаштування апаратного фільтра кадрових ID.
       Приймаємо лише ID = 0x123 та маскуємо ID 0x200..0x20F */
    struct can_filter rfilter[2];
    rfilter[0].can_id   = 0x123;
    rfilter[0].can_mask = CAN_SFF_MASK; /* Точний збіг 11 бітів */

    rfilter[1].can_id   = 0x200;
    rfilter[1].can_mask = 0x7F0;        /* Перевіряти біти 0x7F0 (від 0x200 до 0x20F) */

    if (setsockopt(s, SOL_CAN_RAW, CAN_RAW_FILTER, &rfilter, sizeof(rfilter)) < 0) {
        perror("Помилка встановлення фільтра setsockopt");
        close(s);
        return EXIT_FAILURE;
    }

    /* Налаштування маски кадрів помилок шини */
    can_err_mask_t err_mask = (CAN_ERR_CRIT | CAN_ERR_BUSOFF);
    setsockopt(s, SOL_CAN_RAW, CAN_RAW_ERR_FILTER, &err_mask, sizeof(err_mask));

    printf("SocketCAN успішно ініціалізовано на %s. Очікування кадрів...\n", ifname);

    /* 5. Цикл прийому та декодування кадрів */
    for (int i = 0; i < 5; ++i) {
        ssize_t nbytes = read(s, &frame, sizeof(struct can_frame));
        if (nbytes < 0) {
            perror("Помилка читання кадру з сокета");
            break;
        }

        if (nbytes < (ssize_t)sizeof(struct can_frame)) {
            fprintf(stderr, "Помилка: отримано неповний кадр CAN (%zd байтів)\n", nbytes);
            continue;
        }

        /* Парсинг ідентифікатора та прапорців */
        can_id_t raw_id = frame.can_id;
        int is_extended = (raw_id & CAN_EFF_FLAG) != 0;
        int is_rtr      = (raw_id & CAN_RTR_FLAG) != 0;
        int is_error    = (raw_id & CAN_ERR_FLAG) != 0;

        uint32_t clean_id = is_extended ? (raw_id & CAN_EFF_MASK) : (raw_id & CAN_SFF_MASK);

        printf("[%s] ID: 0x%08X | DLC: %d | Тип: %s%s\n  Дані: ",
               ifname, clean_id, frame.can_dlc,
               is_extended ? "EFF (29-bit)" : "SFF (11-bit)",
               is_rtr ? " [RTR]" : (is_error ? " [ERR]" : ""));

        if (!is_rtr) {
            for (int j = 0; j < frame.can_dlc; ++j) {
                printf("%02X ", frame.data[j]);
            }
        }
        printf("\n");
    }

    close(s);
    return EXIT_SUCCESS;
}
