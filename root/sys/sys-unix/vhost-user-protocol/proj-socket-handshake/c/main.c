#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/mman.h>

#define VHOST_USER_SET_MEM_TABLE 5
#define VHOST_MEMORY_MAX_NREGIONS 8
#define VHOST_USER_VERSION 0x1

struct vhost_user_memory_region {
    uint64_t guest_phys_addr;
    uint64_t memory_size;
    uint64_t userspace_addr;
    uint64_t mmap_offset;
};

struct vhost_user_memory {
    uint32_t nregions;
    uint32_t padding;
    struct vhost_user_memory_region regions[VHOST_MEMORY_MAX_NREGIONS];
};

struct vhost_user_msg {
    uint32_t request;
    uint32_t flags;
    uint32_t size;
    union {
        uint64_t u64;
        struct vhost_user_memory memory;
        uint8_t raw[1024];
    } payload;
} __attribute__((packed));

struct mapped_region {
    uint64_t gpa;
    uint64_t size;
    uint64_t qemu_va;
    uint64_t mmap_offset;
    void *mmap_addr;
};

struct backend_state {
    struct mapped_region regions[VHOST_MEMORY_MAX_NREGIONS];
    uint32_t nregions;
};

/* Зчитування повідомлення з сокета разом із файловими дескрипторами SCM_RIGHTS */
static ssize_t recv_vhost_msg(int sock_fd, struct vhost_user_msg *msg,
                              int *fds, size_t *num_fds) {
    struct msghdr msgh;
    struct iovec iov[1];
    /* Виділяємо буфер під масив файлових дескрипторів із правильним вирівнюванням */
    char cmsg_buf[CMSG_SPACE(sizeof(int) * VHOST_MEMORY_MAX_NREGIONS)];
    
    memset(&msgh, 0, sizeof(msgh));
    memset(cmsg_buf, 0, sizeof(cmsg_buf));
    *num_fds = 0;

    /* Читаємо спочатку 12 байтів фіксованого заголовка */
    iov[0].iov_base = msg;
    iov[0].iov_len = 12;

    msgh.msg_iov = iov;
    msgh.msg_iovlen = 1;
    msgh.msg_control = cmsg_buf;
    msgh.msg_controllen = sizeof(cmsg_buf);

    ssize_t ret = recvmsg(sock_fd, &msgh, 0);
    if (ret <= 0) return ret;

    /* Витягуємо передані дескриптори з керуючого повідомлення ядра */
    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msgh);
    if (cmsg && cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_RIGHTS) {
        size_t fd_bytes = cmsg->cmsg_len - CMSG_LEN(0);
        *num_fds = fd_bytes / sizeof(int);
        memcpy(fds, CMSG_DATA(cmsg), fd_bytes);
    }

    /* Якщо повідомлення містить корисне навантаження — дочитуємо тіло з потоку */
    if (msg->size > 0) {
        if (msg->size > sizeof(msg->payload)) {
            errno = EINVAL;
            return -1;
        }
        size_t received = 0;
        while (received < msg->size) {
            ssize_t n = read(sock_fd, (char *)&msg->payload + received, msg->size - received);
            if (n <= 0) return -1;
            received += (size_t)n;
        }
    }

    return ret + (ssize_t)msg->size;
}

/* Відображення отриманих регіонів у пам'ять сервера через mmap() */
static int handle_set_mem_table(struct backend_state *state,
                                const struct vhost_user_memory *mem,
                                const int *fds, size_t num_fds) {
    if (mem->nregions != num_fds || mem->nregions > VHOST_MEMORY_MAX_NREGIONS) {
        fprintf(stderr, "Помилка: кількість регіонів (%u) != кількості fd (%zu)\n",
                mem->nregions, num_fds);
        return -1;
    }

    /* Звільняємо попередні відображення, якщо вони були активні */
    for (uint32_t i = 0; i < state->nregions; ++i) {
        if (state->regions[i].mmap_addr) {
            munmap(state->regions[i].mmap_addr, state->regions[i].size + state->regions[i].mmap_offset);
        }
    }

    state->nregions = mem->nregions;
    for (uint32_t i = 0; i < mem->nregions; ++i) {
        const struct vhost_user_memory_region *r = &mem->regions[i];
        size_t total_size = r->memory_size + r->mmap_offset;
        
        void *addr = mmap(NULL, total_size, PROT_READ | PROT_WRITE,
                          MAP_SHARED, fds[i], 0);
        if (addr == MAP_FAILED) {
            perror("mmap failed");
            return -1;
        }

        state->regions[i].gpa = r->guest_phys_addr;
        state->regions[i].size = r->memory_size;
        state->regions[i].qemu_va = r->userspace_addr;
        state->regions[i].mmap_offset = r->mmap_offset;
        state->regions[i].mmap_addr = addr;

        printf("Регіон [%u]: GPA=0x%lx..0x%lx -> HVA=%p (fd=%d)\n",
               i, r->guest_phys_addr, r->guest_phys_addr + r->memory_size,
               (void *)((char *)addr + r->mmap_offset), fds[i]);
        
        /* Закриваємо дескриптор: mmap утримує внутрішнє посилання ядра на файл */
        close(fds[i]);
    }
    return 0;
}

/* Трансляція фізичної адреси гостя (GPA) у покажчик у просторі сервера (HVA) */
static void *gpa_to_hva(const struct backend_state *state, uint64_t gpa) {
    for (uint32_t i = 0; i < state->nregions; ++i) {
        const struct mapped_region *r = &state->regions[i];
        if (gpa >= r->gpa && gpa < (r->gpa + r->size)) {
            uint64_t offset = gpa - r->gpa;
            return (char *)r->mmap_addr + r->mmap_offset + offset;
        }
    }
    return NULL;
}
