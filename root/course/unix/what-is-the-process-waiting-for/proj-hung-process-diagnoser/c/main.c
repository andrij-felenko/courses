#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

// Трансляція найпоширеніших системних викликів x86_64
static const char* decode_syscall_x86_64(long nr) {
    switch (nr) {
        case 0:   return "read";
        case 1:   return "write";
        case 7:   return "poll";
        case 23:  return "select";
        case 35:  return "nanosleep";
        case 42:  return "connect";
        case 43:  return "accept";
        case 45:  return "recvfrom";
        case 74:  return "fsync";
        case 202: return "futex";
        case 232: return "epoll_wait";
        case 288: return "accept4";
        case -1:  return "RUNNING_IN_USERSPACE";
        default:  return "other_syscall";
    }
}

// Зчитування однорядкового псевдофайлу
static void read_proc_line(const char* path, char* buf, size_t max_len) {
    buf[0] = '\0';
    int fd = open(path, O_RDONLY);
    if (fd < 0) return;
    ssize_t n = read(fd, buf, max_len - 1);
    if (n > 0) {
        buf[n] = '\0';
        char* nl = strchr(buf, '\n');
        if (nl) *nl = '\0';
    }
    close(fd);
}

// Інспекція цільового дескриптора через readlink
static void inspect_fd(pid_t pid, long fd_num, char* out_target, size_t out_len) {
    char path[128];
    snprintf(path, sizeof(path), "/proc/%d/fd/%ld", pid, fd_num);
    ssize_t len = readlink(path, out_target, out_len - 1);
    if (len > 0) {
        out_target[len] = '\0';
    } else {
        snprintf(out_target, out_len, "unknown/closed (errno: %d)", errno);
    }
}

// Діагностика окремого потоку
static void inspect_thread(pid_t tgid, pid_t tid) {
    char path[256];
    char wchan[64] = "unknown";
    char syscall_raw[256] = "";
    char status_line[256];
    char thread_name[64] = "unknown";
    char state_char = '?';
    long vol_switches = -1, nonvol_switches = -1;

    // Читання /proc/[tgid]/task/[tid]/status
    snprintf(path, sizeof(path), "/proc/%d/task/%d/status", tgid, tid);
    FILE* sf = fopen(path, "r");
    if (sf) {
        while (fgets(status_line, sizeof(status_line), sf)) {
            if (strncmp(status_line, "Name:", 5) == 0) {
                sscanf(status_line + 5, "%63s", thread_name);
            } else if (strncmp(status_line, "State:", 6) == 0) {
                sscanf(status_line + 6, " %c", &state_char);
            } else if (strncmp(status_line, "voluntary_ctxt_switches:", 24) == 0) {
                sscanf(status_line + 24, "%ld", &vol_switches);
            } else if (strncmp(status_line, "nonvoluntary_ctxt_switches:", 27) == 0) {
                sscanf(status_line + 27, "%ld", &nonvol_switches);
            }
        }
        fclose(sf);
    }

    // Читання /proc/[tgid]/task/[tid]/wchan
    snprintf(path, sizeof(path), "/proc/%d/task/%d/wchan", tgid, tid);
    read_proc_line(path, wchan, sizeof(wchan));

    // Читання /proc/[tgid]/task/[tid]/syscall
    snprintf(path, sizeof(path), "/proc/%d/task/%d/syscall", tgid, tid);
    read_proc_line(path, syscall_raw, sizeof(syscall_raw));

    long syscall_nr = -1;
    unsigned long arg0 = 0, arg1 = 0, arg2 = 0;
    if (strlen(syscall_raw) > 0 && syscall_raw[0] != 'r') {
        sscanf(syscall_raw, "%ld 0x%lx 0x%lx 0x%lx", &syscall_nr, &arg0, &arg1, &arg2);
    }

    printf("  [+] Потік TID: %d (%s) | Стан: %c\n", tid, thread_name, state_char);
    printf("      Перемикання контексту: добровільні=%ld, примусові=%ld\n", vol_switches, nonvol_switches);
    printf("      Символ wchan: %s\n", wchan);
    printf("      Системний виклик: #%ld (%s)\n", syscall_nr, decode_syscall_x86_64(syscall_nr));

    // Якщо це блокуючий ввід-вивід на файловому дескрипторі
    if (syscall_nr == 0 || syscall_nr == 1 || syscall_nr == 45 || syscall_nr == 232) {
        char fd_target[256];
        inspect_fd(tgid, (long)arg0, fd_target, sizeof(fd_target));
        printf("      -> Блокування на FD %lu: %s\n", arg0, fd_target);
    } else if (syscall_nr == 202) {
        printf("      -> Блокування FUTEX на адресі пам'яті: 0x%lx (опція op=0x%lx, val=%lu)\n", arg0, arg1, arg2);
    }

    // Читання ядерного стека /proc/[tgid]/task/[tid]/stack
    snprintf(path, sizeof(path), "/proc/%d/task/%d/stack", tgid, tid);
    FILE* stf = fopen(path, "r");
    if (stf) {
        printf("      Ядерний стек (Kernel Call Stack):\n");
        char stack_line[256];
        int frame_idx = 0;
        while (fgets(stack_line, sizeof(stack_line), stf)) {
            char* nl = strchr(stack_line, '\n');
            if (nl) *nl = '\0';
            printf("        #%d %s\n", frame_idx++, stack_line);
        }
        fclose(stf);
    }
    printf("\n");
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <PID>\n", argv[0]);
        return 1;
    }

    pid_t pid = (pid_t)atoi(argv[1]);
    char task_dir_path[128];
    snprintf(task_dir_path, sizeof(task_dir_path), "/proc/%d/task", pid);

    DIR* dir = opendir(task_dir_path);
    if (!dir) {
        perror("Не вдалося відкрити /proc/[pid]/task");
        return 1;
    }

    printf("=== Діагностичний зріз процесу PID: %d ===\n\n", pid);

    struct dirent* entry;
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') continue;
        pid_t tid = (pid_t)atoi(entry->d_name);
        if (tid > 0) {
            inspect_thread(pid, tid);
        }
    }

    closedir(dir);
    return 0;
}
