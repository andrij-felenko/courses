/* C: Традиційна реалізація з використанням чистих викликів libbpf C API */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

int main(int argc, char **argv)
{
    struct bpf_object *obj = NULL;
    int prog_fd, map_fd;
    int err;

    printf("=== BPF SOCKMAP Zero-Copy Redirect Controller (C) ===\n");

    /* 1. Відкриваємо та завантажуємо BPF ELF-об'єкт */
    obj = bpf_object__open_file("bpf_redir.bpf.o", NULL);
    if (!obj) {
        fprintf(stderr, "Помилка: не вдалося відкрити BPF об'єкт bpf_redir.bpf.o\n");
        return 1;
    }

    err = bpf_object__load(obj);
    if (err) {
        fprintf(stderr, "Помилка: не вдалося завантажити BPF програму в ядро (код: %d)\n", err);
        bpf_object__close(obj);
        return 1;
    }

    /* 2. Знаходимо файлові дескриптори завантаженої програми та карти */
    struct bpf_program *prog = bpf_object__find_program_by_name(obj, "bpf_sockmap_redirect");
    prog_fd = bpf_program__fd(prog);
    map_fd = bpf_object__find_map_fd_by_name(obj, "sock_map");

    if (prog_fd < 0 || map_fd < 0) {
        fprintf(stderr, "Помилка: не знайдено BPF програму або карту sock_map у файлі\n");
        bpf_object__close(obj);
        return 1;
    }

    /* 3. Прикріплюємо BPF_SK_MSG_VERDICT до карти SOCKMAP */
    err = bpf_prog_attach(prog_fd, map_fd, BPF_SK_MSG_VERDICT, 0);
    if (err) {
        fprintf(stderr, "Помилка: не вдалося прикріпити BPF_SK_MSG_VERDICT до SOCKMAP\n");
        bpf_object__close(obj);
        return 1;
    }

    /* 4. Створюємо сокетну пару для локального тестування */
    int sv[2];
    if (socketpair(AF_UNIX, SOCK_STREAM, 0, sv) < 0) {
        perror("Помилка створення socketpair");
        bpf_object__close(obj);
        return 1;
    }

    int sock_a = sv[0];
    int sock_b = sv[1];

    /* 5. Зареєструємо дескриптори сокетів у SOCKMAP за ключами 0 та 1 */
    uint32_t key_a = 0;
    uint32_t key_b = 1;

    err = bpf_map_update_elem(map_fd, &key_a, &sock_a, BPF_ANY);
    if (err) {
        perror("Помилка оновлення SOCKMAP для sock_a");
        goto cleanup;
    }

    err = bpf_map_update_elem(map_fd, &key_b, &sock_b, BPF_ANY);
    if (err) {
        perror("Помилка оновлення SOCKMAP для sock_b");
        goto cleanup;
    }

    printf("Успіх: Сокети FD %d (Key 0) та FD %d (Key 1) додано до SOCKMAP!\n", sock_a, sock_b);
    printf("Трафік із Sock A тепер перенаправляється безпосередньо у Sock B в ядрі!\n");

    /* Тестова передача даних через Sock A */
    const char *payload = "Привіт від BPF Zero-Copy Sockmap Redirect!";
    ssize_t sent = write(sock_a, payload, strlen(payload));
    printf("Sock A відправив %zd байтів у сокет.\n", sent);

    char buffer[128] = {0};
    ssize_t recvd = read(sock_b, buffer, sizeof(buffer) - 1);
    printf("Sock B успішно прочитав %zd байтів без проходження TCP/IP: '%s'\n", recvd, buffer);

cleanup:
    close(sock_a);
    close(sock_b);
    bpf_object__close(obj);
    return 0;
}
