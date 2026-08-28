#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/eventfd.h>
#include <net/if.h>
#include <linux/if_tun.h>
#include <linux/vhost.h>

#define GUEST_MEM_SIZE (1024 * 1024 * 64) // 64 MB віртуальної пам'яті гостя
#define VRING_SIZE 256                     // Кількість дескрипторів у черзі

int open_tap_device(const char *dev_name) {
    int tap_fd = open("/dev/net/tun", O_RDWR);
    if (tap_fd < 0) {
        perror("Помилка відкриття /dev/net/tun");
        return -1;
    }

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    ifr.ifr_flags = IFF_TAP | IFF_NO_PI;
    snprintf(ifr.ifr_name, IFNAMSIZ, "%s", dev_name);

    if (ioctl(tap_fd, TUNSETIFF, (void *)&ifr) < 0) {
        perror("Помилка налаштування TUNSETIFF");
        close(tap_fd);
        return -1;
    }

    return tap_fd;
}

int setup_vhost_net(int tap_fd, void *guest_mem, size_t mem_size) {
    int vhost_fd = open("/dev/vhost-net", O_RDWR);
    if (vhost_fd < 0) {
        perror("Помилка відкриття /dev/vhost-net");
        return -1;
    }

    // 1. Прив'язка власника
    if (ioctl(vhost_fd, VHOST_SET_OWNER, NULL) < 0) {
        perror("VHOST_SET_OWNER failed");
        close(vhost_fd);
        return -1;
    }

    // 2. Налаштування карти пам'яті
    size_t mem_table_size = sizeof(struct vhost_memory) + sizeof(struct vhost_memory_region);
    struct vhost_memory *mem = (struct vhost_memory *)calloc(1, mem_table_size);
    if (!mem) {
        perror("Помилка виділення пам'яті під vhost_memory");
        close(vhost_fd);
        return -1;
    }

    mem->nregions = 1;
    mem->regions[0].guest_phys_addr = 0x0;
    mem->regions[0].memory_size = mem_size;
    mem->regions[0].userspace_addr = (uint64_t)guest_mem;

    if (ioctl(vhost_fd, VHOST_SET_MEM_TABLE, mem) < 0) {
        perror("VHOST_SET_MEM_TABLE failed");
        free(mem);
        close(vhost_fd);
        return -1;
    }
    free(mem);

    // 3. Створення dummy-структур vring у мапованій пам'яті
    // У реальній ВМ ці структури виділяє гостьове ядро або гіпервізор
    uint8_t *vring_buf = (uint8_t *)guest_mem + 0x10000;
    
    // 4. Конфігурація черг (0 = RX, 1 = TX)
    for (int q = 0; q < 2; q++) {
        struct vhost_vring_state state = { .index = q, .num = VRING_SIZE };
        if (ioctl(vhost_fd, VHOST_SET_VRING_NUM, &state) < 0) {
            perror("VHOST_SET_VRING_NUM failed");
            close(vhost_fd);
            return -1;
        }

        // Задаємо адреси vring у HVA
        struct vhost_vring_addr addr = {
            .index = q,
            .flags = 0,
            .desc_user_addr = (uint64_t)(vring_buf + q * 0x4000),
            .avail_user_addr = (uint64_t)(vring_buf + q * 0x4000 + 0x1000),
            .used_user_addr = (uint64_t)(vring_buf + q * 0x4000 + 0x2000),
            .log_guest_addr = 0
        };

        if (ioctl(vhost_fd, VHOST_SET_VRING_ADDR, &addr) < 0) {
            perror("VHOST_SET_VRING_ADDR failed");
            close(vhost_fd);
            return -1;
        }

        // Створення та прив'язка eventfd для KICK та CALL
        int kick_fd = eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC);
        int call_fd = eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC);

        struct vhost_vring_file kick_file = { .index = q, .fd = kick_fd };
        struct vhost_vring_file call_file = { .index = q, .fd = call_fd };

        if (ioctl(vhost_fd, VHOST_SET_VRING_KICK, &kick_file) < 0 ||
            ioctl(vhost_fd, VHOST_SET_VRING_CALL, &call_file) < 0) {
            perror("VHOST_SET_VRING_KICK/CALL failed");
            close(kick_fd); close(call_fd); close(vhost_fd);
            return -1;
        }

        // 5. Прив'язка TAP-дескриптора як бекенду черги
        struct vhost_vring_file backend = { .index = q, .fd = tap_fd };
        if (ioctl(vhost_fd, VHOST_NET_SET_BACKEND, &backend) < 0) {
            perror("VHOST_NET_SET_BACKEND failed");
            close(vhost_fd);
            return -1;
        }
    }

    printf("vhost-net успішно ініціалізований та прив'язаний до TAP!\n");
    return vhost_fd;
}

int main(void) {
    void *guest_memory = mmap(NULL, GUEST_MEM_SIZE, PROT_READ | PROT_WRITE,
                              MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (guest_memory == MAP_FAILED) {
        perror("mmap failed");
        return 1;
    }

    int tap_fd = open_tap_device("vhost-tap0");
    if (tap_fd < 0) {
        munmap(guest_memory, GUEST_MEM_SIZE);
        return 1;
    }

    int vhost_fd = setup_vhost_net(tap_fd, guest_memory, GUEST_MEM_SIZE);
    if (vhost_fd >= 0) {
        printf("Натисніть Enter для завершення роботи...\n");
        getchar();
        close(vhost_fd);
    }

    close(tap_fd);
    munmap(guest_memory, GUEST_MEM_SIZE);
    return 0;
}
