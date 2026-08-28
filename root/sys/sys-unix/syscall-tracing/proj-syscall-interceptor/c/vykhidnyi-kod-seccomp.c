#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <linux/seccomp.h>
#include <linux/filter.h>

/* Створення та завантаження Seccomp BPF фільтра */
static int install_seccomp_filter(void) {
    struct sock_filter filter[] = {
        /* 1. Завантажуємо номер системного виклику в акумулятор BPF */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
        
        /* 2. Перевіряємо чи дорівнює номер виклику __NR_mkdirat */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_mkdirat, 0, 1),
        
        /* 3. Повертаємо USER_NOTIF для перехоплення супервізором */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_USER_NOTIF),
        
        /* 4. Дозволяємо всі інші системні виклики */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };
    
    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    /* Забороняємо отримання нових привілеїв */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) {
        perror("prctl(PR_SET_NO_NEW_PRIVS)");
        return -1;
    }

    /* Реєструємо фільтр та отримуємо listener_fd */
    return syscall(__NR_seccomp, SECCOMP_SET_MODE_FILTER, SECCOMP_FILTER_FLAG_NEW_LISTENER, &prog);
}

/* Робочий цикл супервізора Seccomp */
static void run_supervisor(int notify_fd) {
    struct seccomp_notif req = {0};
    struct seccomp_notif_resp resp = {0};

    printf("[Supervisor C] Слухач активовано на notify_fd=%d. Чекаємо подій...\n", notify_fd);

    while (1) {
        memset(&req, 0, sizeof(req));
        
        /* Читаємо сповіщення з черги ядра */
        if (ioctl(notify_fd, SECCOMP_IOCTL_NOTIF_RECV, &req) < 0) {
            if (errno == EINTR) continue;
            if (errno == ENOENT) break; // Усі трасовані процеси завершилися
            perror("ioctl(SECCOMP_IOCTL_NOTIF_RECV)");
            break;
        }

        printf("[Supervisor C] УСПІШНО ПЕРЕХОПЛЕНО mkdirat() від PID=%d (Syscall NR=%d)\n",
               req.pid, req.data.nr);

        /* Перевірка дійсності ID для захисту від TOCTOU */
        __u64 check_id = req.id;
        if (ioctl(notify_fd, SECCOMP_IOCTL_NOTIF_ID_VALID, &check_id) < 0) {
            printf("[Supervisor C] Запит id=%llu скасовано (процес перервано)\n",
                   (unsigned long long)req.id);
            continue;
        }

        /* Формуємо відповідь про симульований успіх */
        memset(&resp, 0, sizeof(resp));
        resp.id = req.id;
        resp.val = 0;      /* Симулюємо успішне виконання (повертаємо 0) */
        resp.error = 0;    /* Код помилки відсутній */
        resp.flags = 0;

        /* Надсилаємо відповідь ядру */
        if (ioctl(notify_fd, SECCOMP_IOCTL_NOTIF_SEND, &resp) < 0) {
            perror("ioctl(SECCOMP_IOCTL_NOTIF_SEND)");
            break;
        }
        
        printf("[Supervisor C] Надіслано симульований результат для req.id=%llu\n",
               (unsigned long long)req.id);
        break; // Завершуємо роботу після першого перехопленого виклику
    }
}

int main(void) {
    int notify_fd = install_seccomp_filter();
    if (notify_fd < 0) {
        fprintf(stderr, "Не вдалося встановити Seccomp-фільтр\n");
        return EXIT_FAILURE;
    }

    pid_t child = fork();
    if (child < 0) {
        perror("fork");
        close(notify_fd);
        return EXIT_FAILURE;
    }

    if (child == 0) {
        /* Дочірній процес викликає mkdir(), який перехоплюється супервізором */
        printf("[Target C] Спроба виконати mkdir('/tmp/virtual_c_dir', 0755)...\n");
        int res = mkdir("/tmp/virtual_c_dir", 0755);
        printf("[Target C] Результат mkdir: %d (errno: %d, status: %s)\n",
               res, errno, strerror(errno));
        close(notify_fd);
        return EXIT_SUCCESS;
    } else {
        run_supervisor(notify_fd);
        close(notify_fd);
        waitpid(child, NULL, 0);
    }

    return EXIT_SUCCESS;
}
