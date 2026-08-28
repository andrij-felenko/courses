/* Userspace Controller на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

struct policy_command {
    uint32_t target_pid;
    uint8_t  block_action;
};

int main(int argc, char **argv)
{
    int map_fd = bpf_obj_get("/sys/fs/bpf/cmd_ringbuf_map");
    if (map_fd < 0) {
        perror("Не вдалося відкрити мапу /sys/fs/bpf/cmd_ringbuf_map");
        return 1;
    }

    /* Ініціалізація User Ring Buffer */
    struct user_ring_buffer *urb = user_ring_buffer__new(map_fd, NULL);
    if (!urb) {
        fprintf(stderr, "Помилка створення user_ring_buffer\n");
        close(map_fd);
        return 1;
    }

    /* Читання BPF ітератора */
    int iter_fd = open("/sys/fs/bpf/task_inspector", O_RDONLY);
    if (iter_fd < 0) {
        perror("Не вдалося відкрити ітератор /sys/fs/bpf/task_inspector");
        user_ring_buffer__free(urb);
        close(map_fd);
        return 1;
    }

    char buf[512];
    ssize_t bytes_read = read(iter_fd, buf, sizeof(buf) - 1);
    if (bytes_read > 0) {
        buf[bytes_read] = '\0';
        printf("Звіт BPF Iter:\n%s", buf);

        /* Парсимо виявлений PID */
        uint32_t bad_pid = 0;
        if (sscanf(buf, "PID:%u", &bad_pid) == 1 && bad_pid > 0) {
            printf("Надсилаємо команду блокування для PID %u (Zero-Syscall)...\n", bad_pid);

            /* Резервуємо слот у кільцевому буфері без системного виклику */
            struct policy_command *cmd = user_ring_buffer__reserve(urb, sizeof(*cmd));
            if (cmd) {
                cmd->target_pid = bad_pid;
                cmd->block_action = 1;

                /* Фіксуємо транзакцію у спільній пам'яті mmap */
                user_ring_buffer__submit(urb, cmd);
                printf("Команду успішно надіслано в ядро.\n");
            }
        }
    }

    close(iter_fd);
    user_ring_buffer__free(urb);
    close(map_fd);
    return 0;
}
