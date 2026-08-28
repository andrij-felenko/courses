#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/mman.h>
#include <sys/eventfd.h>
#include <sys/wait.h>
#include <linux/fcntl.h>

#define BUFFER_SIZE (1024 * 1024) /* 1 МБ спільного буфера для даних */

/* Структура протокольного заголовка площини керування */
typedef struct {
    uint32_t command_id;
    uint32_t payload_size;
} control_header_t;

/* Відправка масиву дескрипторів разом із керуючим заголовком */
static int send_control_with_fds(int sock_fd, const control_header_t *hdr, int mem_fd, int evt_fd) {
    struct msghdr mh;
    struct iovec iov[1];
    char cmsg_buf[CMSG_SPACE(sizeof(int) * 2)];

    memset(&mh, 0, sizeof(mh));
    memset(cmsg_buf, 0, sizeof(cmsg_buf));

    /* Основне корисне навантаження повідомлення: бінарний заголовок */
    iov[0].iov_base = (void*)hdr;
    iov[0].iov_len = sizeof(control_header_t);
    mh.msg_iov = iov;
    mh.msg_iovlen = 1;

    /* Допоміжні керуючі дані: передача двох файлових дескрипторів */
    mh.msg_control = cmsg_buf;
    mh.msg_controllen = sizeof(cmsg_buf);

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&mh);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int) * 2);

    int *fds_ptr = (int*)CMSG_DATA(cmsg);
    fds_ptr[0] = mem_fd;
    fds_ptr[1] = evt_fd;

    ssize_t sent = sendmsg(sock_fd, &mh, 0);
    if (sent < 0) {
        perror("sendmsg(SCM_RIGHTS)");
        return -1;
    }
    return 0;
}

/* Отримання заголовка та витягнення переданих ядром дескрипторів */
static int recv_control_with_fds(int sock_fd, control_header_t *hdr, int *out_mem_fd, int *out_evt_fd) {
    struct msghdr mh;
    struct iovec iov[1];
    char cmsg_buf[CMSG_SPACE(sizeof(int) * 2)];

    memset(&mh, 0, sizeof(mh));
    memset(cmsg_buf, 0, sizeof(cmsg_buf));

    iov[0].iov_base = (void*)hdr;
    iov[0].iov_len = sizeof(control_header_t);
    mh.msg_iov = iov;
    mh.msg_iovlen = 1;

    mh.msg_control = cmsg_buf;
    mh.msg_controllen = sizeof(cmsg_buf);

    ssize_t recvd = recvmsg(sock_fd, &mh, 0);
    if (recvd <= 0) {
        return (recvd == 0) ? 0 : -1;
    }

    /* Пошук блоку SCM_RIGHTS у допоміжних даних */
    for (struct cmsghdr *cmsg = CMSG_FIRSTHDR(&mh); cmsg != NULL; cmsg = CMSG_NXTHDR(&mh, cmsg)) {
        if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_RIGHTS) {
            int *fds_ptr = (int*)CMSG_DATA(cmsg);
            *out_mem_fd = fds_ptr[0];
            *out_evt_fd = fds_ptr[1];
            return 1;
        }
    }

    return -1; /* Повідомлення прийшло, але дескрипторів у ньому немає */
}

/* Логіка дочірнього процесу-клієнта */
static void run_client(int sock_fd) {
    control_header_t hdr;
    int mem_fd = -1, evt_fd = -1;

    printf("[Клієнт PID %d] Очікування ініціалізаційних дескрипторів...\n", getpid());
    int res = recv_control_with_fds(sock_fd, &hdr, &mem_fd, &evt_fd);
    if (res <= 0) {
        fprintf(stderr, "[Клієнт] Помилка отримання каналу від сервера\n");
        close(sock_fd);
        exit(1);
    }

    printf("[Клієнт] Успішно отримано дескриптори: memfd=%d, eventfd=%d (команда=%u, розмір=%u Б)\n",
           mem_fd, evt_fd, hdr.command_id, hdr.payload_size);

    /* Перевірка активних печаток пам'яті (захист від зміни розміру сервером) */
    int seals = fcntl(mem_fd, F_GET_SEALS);
    if (seals < 0 || !(seals & F_SEAL_SHRINK)) {
        fprintf(stderr, "[Клієнт] Попередження: буфер пам'яті не запечатано належним чином!\n");
    }

    /* Відображення анонімної пам'яті у віртуальний простір клієнта */
    void *shm_ptr = mmap(NULL, BUFFER_SIZE, PROT_READ, MAP_SHARED, mem_fd, 0);
    if (shm_ptr == MAP_FAILED) {
        perror("[Клієнт] mmap");
        exit(1);
    }

    /* Очікування сигналу готовності кадру через eventfd */
    uint64_t evt_val = 0;
    ssize_t bytes_read = read(evt_fd, &evt_val, sizeof(evt_val));
    if (bytes_read == sizeof(evt_val)) {
        printf("[Клієнт] Отримано сигнал готовності (лічильник: %lu).\n", (unsigned long)evt_val);
        printf("[Клієнт] Зміст буфера (без копіювання через ядро): \"%s\"\n", (const char*)shm_ptr);
    }

    /* Звільнення ресурсів */
    munmap(shm_ptr, BUFFER_SIZE);
    close(mem_fd);
    close(evt_fd);
    close(sock_fd);
    printf("[Клієнт] Обробку завершено успішно.\n");
    exit(0);
}

int main(void) {
    int sv[2];
    /* 1. Створення сокетної пари AF_UNIX типу SOCK_SEQPACKET */
    if (socketpair(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0, sv) == -1) {
        perror("socketpair");
        return 1;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return 1;
    }

    if (pid == 0) {
        /* Дочірній процес */
        close(sv[0]);
        run_client(sv[1]);
    }

    /* Батьківський процес (Сервер-диспетчер) */
    close(sv[1]);
    int client_sock = sv[0];

    /* 2. Верифікація облікових даних під'єднаного клієнта через SO_PEERCRED */
    struct ucred cred;
    socklen_t cred_len = sizeof(cred);
    if (getsockopt(client_sock, SOL_SOCKET, SO_PEERCRED, &cred, &cred_len) == 0) {
        printf("[Сервер] Клієнт верифікований ядром: PID=%d, UID=%d, GID=%d\n",
               cred.pid, cred.uid, cred.gid);
    }

    /* 3. Створення анонімної спільної пам'яті */
    int mem_fd = memfd_create("ipc_data_buffer", MFD_CLOEXEC | MFD_ALLOW_SEALING);
    if (mem_fd < 0) {
        perror("memfd_create");
        return 1;
    }
    if (ftruncate(mem_fd, BUFFER_SIZE) == -1) {
        perror("ftruncate");
        return 1;
    }

    /* Відображення для запису початкових даних */
    void *shm_ptr = mmap(NULL, BUFFER_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, mem_fd, 0);
    if (shm_ptr == MAP_FAILED) {
        perror("mmap server");
        return 1;
    }
    snprintf((char*)shm_ptr, BUFFER_SIZE, "Еталонне повідомлення високої чіткості від майстра [PID=%d]", getpid());
    munmap(shm_ptr, BUFFER_SIZE);

    /* 4. Запечатування пам'яті: заборона зміни розміру */
    fcntl(mem_fd, F_ADD_SEALS, F_SEAL_SHRINK | F_SEAL_GROW);

    /* 5. Створення дескриптора сигналізації */
    int evt_fd = eventfd(0, EFD_CLOEXEC | EFD_NONBLOCK);
    if (evt_fd < 0) {
        perror("eventfd");
        return 1;
    }

    /* 6. Передача дескрипторів memfd та eventfd клієнту через сокет */
    control_header_t hdr = { .command_id = 1001, .payload_size = BUFFER_SIZE };
    if (send_control_with_fds(client_sock, &hdr, mem_fd, evt_fd) == 0) {
        printf("[Сервер] Канал даних та сигналізацію успішно делеговано клієнту.\n");
    }

    /* Імітація підготовки даних та надсилання сповіщення */
    usleep(5000);
    uint64_t signal_val = 1;
    if (write(evt_fd, &signal_val, sizeof(signal_val)) == sizeof(signal_val)) {
        printf("[Сервер] Сигнал готовності відправлено в eventfd.\n");
    }

    /* Очікування завершення дочірнього процесу */
    close(mem_fd);
    close(evt_fd);
    close(client_sock);
    wait(NULL);
    printf("[Сервер] Роботу диспетчера завершено.\n");
    return 0;
}
