#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <sys/un.h>

#if defined(__x86_64__) || defined(__i386__)
#include <cpuid.h>

static void probe_cpuid_hypervisor(void) {
    unsigned int eax = 0, ebx = 0, ecx = 0, edx = 0;
    
    /* Листок 1: ECX біт 31 позначає наявність гіпервізора */
    if (__get_cpuid(1, &eax, &ebx, &ecx, &edx)) {
        bool is_hypervisor = (ecx & (1U << 31)) != 0;
        printf("[CPUID] Біт гіпервізора (Leaf 1, ECX.31): %s\n",
               is_hypervisor ? "1 (Виявлено віртуалізацію)" : "0 (Пряме залізо / Bare Metal)");
        
        if (is_hypervisor) {
            /* Листок 0x40000000: Підпис виробника гіпервізора */
            if (__get_cpuid(0x40000000, &eax, &ebx, &ecx, &edx)) {
                char sig[13] = {0};
                memcpy(sig + 0, &ebx, 4);
                memcpy(sig + 4, &ecx, 4);
                memcpy(sig + 8, &edx, 4);
                printf("[CPUID] Сигнатура гіпервізора: \"%s\"\n", sig);
            }
        }
    }
}
#else
static void probe_cpuid_hypervisor(void) {
    printf("[CPUID] Архітектура не x86_64 (зондування CPUID пропущено)\n");
}
#endif

static void probe_proc_kernel_version(void) {
    int fd = open("/proc/version", O_RDONLY);
    if (fd < 0) {
        printf("[PROC] /proc/version: НЕ ЗНАЙДЕНО (можлива емуляція Windows / Cygwin)\n");
        return;
    }
    
    char buf[512];
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    
    if (n > 0) {
        buf[n] = '\0';
        printf("[PROC] /proc/version знайдено:\n       %.120s...\n", buf);
        
        if (strstr(buf, "microsoft-standard-WSL2")) {
            printf("[ІДЕНТИФІКАЦІЯ] Виявлено середовище: WSL2 (Windows Hyper-V Micro-VM)\n");
        } else if (strstr(buf, "Microsoft")) {
            printf("[ІДЕНТИФІКАЦІЯ] Виявлено середовище: WSL1 (Емуляція ядра NT lxcore.sys)\n");
        }
    }
}

static void probe_dmi_product(void) {
    int fd = open("/sys/class/dmi/id/product_name", O_RDONLY);
    if (fd >= 0) {
        char buf[128];
        ssize_t n = read(fd, buf, sizeof(buf) - 1);
        close(fd);
        if (n > 0) {
            buf[n] = '\0';
            /* Прибираємо символ нового рядка */
            char *nl = strchr(buf, '\n');
            if (nl) *nl = '\0';
            printf("[SYSFS] DMI product_name: \"%s\"\n", buf);
        }
    } else {
        printf("[SYSFS] DMI таблиці недоступні у /sys/class/dmi/id/\n");
    }
}

static void probe_container_markers(void) {
    bool is_docker = (access("/.dockerenv", F_OK) == 0);
    bool is_containerenv = (access("/run/.containerenv", F_OK) == 0);
    
    printf("[CONTAINER] Маркери контейнеризації:\n");
    printf("            /.dockerenv: %s\n", is_docker ? "ТАК (Docker)" : "НІ");
    printf("            /run/.containerenv: %s\n", is_containerenv ? "ТАК (Podman)" : "НІ");
    
    int fd = open("/proc/1/environ", O_RDONLY);
    if (fd >= 0) {
        char buf[1024];
        ssize_t n = read(fd, buf, sizeof(buf) - 1);
        close(fd);
        if (n > 0) {
            buf[n] = '\0';
            /* Змінні середовища розділені нульовими байтами */
            for (ssize_t i = 0; i < n; i += strlen(buf + i) + 1) {
                if (strncmp(buf + i, "container=", 10) == 0) {
                    printf("            /proc/1/environ: %s\n", buf + i);
                    break;
                }
            }
        }
    }
}

static void probe_posix_unlink_semantics(void) {
    char tmppath[] = "/tmp/probe_unlink_XXXXXX";
    int fd = mkstemp(tmppath);
    if (fd < 0) {
        printf("[POSIX-ТЕСТ] Не вдалося створити тимчасовий файл: %s\n", strerror(errno));
        return;
    }
    
    const char *payload = "Справжнє ядро зберігає inode відкритого файлу!";
    write(fd, payload, strlen(payload));
    
    /* Видаляємо запис з каталогу, поки дескриптор відкритий */
    if (unlink(tmppath) != 0) {
        printf("[POSIX-ТЕСТ] unlink() відкритого файлу ПРОВАЛЕНО: %s\n", strerror(errno));
        close(fd);
        return;
    }
    
    /* Перевіряємо, чи файл зник із файлової системи */
    if (access(tmppath, F_OK) == 0) {
        printf("[POSIX-ТЕСТ] Файл лишився видимим після unlink (порушення семантики POSIX)\n");
    } else {
        /* Зчитуємо дані з відкритого дескриптора безіменного файлу */
        lseek(fd, 0, SEEK_SET);
        char readbuf[128] = {0};
        ssize_t rb = read(fd, readbuf, sizeof(readbuf) - 1);
        if (rb > 0 && strcmp(readbuf, payload) == 0) {
            printf("[POSIX-ТЕСТ] unlink() семантика: ВІДПОВІДАЄ POSIX (inode активний до close)\n");
        } else {
            printf("[POSIX-ТЕСТ] Не вдалося прочитати з безіменного дескриптора\n");
        }
    }
    
    close(fd);
}

static void probe_af_unix_fd_passing(void) {
    int sv[2];
    if (socketpair(AF_UNIX, SOCK_STREAM, 0, sv) < 0) {
        printf("[AF_UNIX] socketpair() провалено: %s\n", strerror(errno));
        return;
    }
    
    /* Створюємо тестовий файл для передачі його дескриптора */
    int test_fd = open("/dev/null", O_RDONLY);
    if (test_fd < 0) {
        close(sv[0]);
        close(sv[1]);
        return;
    }
    
    /* Формуємо повідомлення з SCM_RIGHTS */
    struct msghdr msg = {0};
    char iov_buf[1] = {'X'};
    struct iovec io = {.iov_base = iov_buf, .iov_len = sizeof(iov_buf)};
    msg.msg_iov = &io;
    msg.msg_iovlen = 1;
    
    char cmsg_buf[CMSG_SPACE(sizeof(int))];
    msg.msg_control = cmsg_buf;
    msg.msg_controllen = sizeof(cmsg_buf);
    
    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));
    memcpy(CMSG_DATA(cmsg), &test_fd, sizeof(int));
    
    if (sendmsg(sv[0], &msg, 0) < 0) {
        printf("[AF_UNIX] sendmsg(SCM_RIGHTS) провалено: %s (емуляція сокетів)\n", strerror(errno));
    } else {
        printf("[AF_UNIX] SCM_RIGHTS передача дескриптора: УСПІШНО (справжнє ядро IPC)\n");
    }
    
    close(test_fd);
    close(sv[0]);
    close(sv[1]);
}

int main(void) {
    printf("=== ДІАГНОСТИЧНИЙ ЗОНД АВТЕНТИЧНОСТІ ЯДРА ===\n\n");
    probe_cpuid_hypervisor();
    printf("\n");
    probe_proc_kernel_version();
    printf("\n");
    probe_dmi_product();
    printf("\n");
    probe_container_markers();
    printf("\n");
    probe_posix_unlink_semantics();
    printf("\n");
    probe_af_unix_fd_passing();
    printf("\n============================================\n");
    return 0;
}
