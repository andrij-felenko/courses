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

void print_can_error(const struct can_frame *f) {
    if (!(f->can_id & CAN_ERR_FLAG)) {
        return;
    }

    uint32_t err_class = f->can_id & CAN_ERR_MASK;
    printf("[CAN ERROR] Клас: 0x%08X", err_class);

    if (err_class & CAN_ERR_TX_TIMEOUT) {
        printf(" | TX Timeout");
    }
    if (err_class & CAN_ERR_LOSTARB) {
        printf(" | Втрата арбітражу на біті %d", f->data[0]);
    }
    if (err_class & CAN_ERR_ACK) {
        printf(" | ACK Error (жоден вузол не відповів)");
    }
    if (err_class & CAN_ERR_BUSOFF) {
        printf(" | КРИТИЧНО: Стан BUS-OFF (ізоляція від шини)");
    }
    if (err_class & CAN_ERR_BUSERROR) {
        printf(" | Bus Error (фізичне спотворення лінії)");
    }
    if (err_class & CAN_ERR_RESTARTED) {
        printf(" | Відновлення контролера (Restarted)");
    }

    if (err_class & CAN_ERR_CRTL) {
        printf(" | Зміна стану:");
        if (f->data[1] & CAN_ERR_CRTL_RX_WARNING) printf(" RxWarn(REC>=96)");
        if (f->data[1] & CAN_ERR_CRTL_TX_WARNING) printf(" TxWarn(TEC>=96)");
        if (f->data[1] & CAN_ERR_CRTL_RX_PASSIVE) printf(" RxPassive(REC>=128)");
        if (f->data[1] & CAN_ERR_CRTL_TX_PASSIVE) printf(" TxPassive(TEC>=128)");
        if (f->data[1] & CAN_ERR_CRTL_ACTIVE)     printf(" Error-Active");
    }

    if (err_class & CAN_ERR_PROT) {
        printf(" | Протокол:");
        if (f->data[2] & CAN_ERR_PROT_BIT)   printf(" Bit-Error");
        if (f->data[2] & CAN_ERR_PROT_FORM)  printf(" Form-Error");
        if (f->data[2] & CAN_ERR_PROT_STUFF) printf(" Stuff-Error");
        if (f->data[2] & CAN_ERR_PROT_TX)    printf(" (при передачі)");
        else                                 printf(" (при прийомі)");
    }

    if (f->data[6] != 0 || f->data[7] != 0) {
        printf(" | Лічильники: TEC=%u, REC=%u", f->data[6], f->data[7]);
    }
    printf("\n");
}

int main(int argc, char *argv[]) {
    const char *ifname = (argc > 1) ? argv[1] : "can0";
    int s = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (s < 0) {
        perror("Помилка відкриття сокета CAN");
        return 1;
    }

    struct ifreq ifr;
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    if (ioctl(s, SIOCGIFINDEX, &ifr) < 0) {
        perror("Не знайдено CAN інтерфейс");
        close(s);
        return 1;
    }

    struct sockaddr_can addr;
    memset(&addr, 0, sizeof(addr));
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    can_err_mask_t err_mask = CAN_ERR_MASK; // перехоплювати всі класи помилок
    if (setsockopt(s, SOL_CAN_RAW, CAN_RAW_ERR_FILTER, &err_mask, sizeof(err_mask)) < 0) {
        perror("Помилка налаштування фільтра помилок");
        close(s);
        return 1;
    }

    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("Помилка прив'язки сокета");
        close(s);
        return 1;
    }

    printf("Діагностику запущено на інтерфейсі %s. Очікування подій...\n", ifname);

    struct can_frame frame;
    while (1) {
        ssize_t nbytes = read(s, &frame, sizeof(struct can_frame));
        if (nbytes < 0) {
            perror("Помилка читання з CAN сокета");
            break;
        }
        if (frame.can_id & CAN_ERR_FLAG) {
            print_can_error(&frame);
        }
    }

    close(s);
    return 0;
}
